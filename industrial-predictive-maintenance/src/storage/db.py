import asyncio
import asyncpg
from typing import List, Dict, Any, Optional
from src.config import settings
from src.utils.logger import get_logger, telemetry

logger = get_logger("db")

class DatabaseManager:
    """
    Manages connections to PostgreSQL/TimescaleDB.
    Supports administrative initialization and runtime pool management with restricted permissions.
    """
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def initialize_database(self):
        """
        Connects as superuser to set up the DB, create application user, 
        load TimescaleDB extension, and set up schema.
        """
        logger.info("Initializing database schema and privileges...")
        
        # Connect to default postgres DB first to create factory_db if not exists
        try:
            admin_conn = await asyncpg.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_ADMIN_USER,
                password=settings.DB_ADMIN_PASSWORD,
                database="postgres"
            )
        except Exception as e:
            logger.error(f"Failed to connect to database as admin: {e}")
            telemetry.record_error()
            raise e

        # Create database
        db_exists = await admin_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", settings.DB_NAME
        )
        if not db_exists:
            # CREATE DATABASE cannot run inside a transaction block
            await admin_conn.execute(f'CREATE DATABASE "{settings.DB_NAME}"')
            logger.info(f"Database {settings.DB_NAME} created.")
        await admin_conn.close()

        # Reconnect to factory_db to set up tables and users
        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_ADMIN_USER,
            password=settings.DB_ADMIN_PASSWORD,
            database=settings.DB_NAME
        )

        try:
            # Create application user/role if it doesn't exist
            role_exists = await conn.fetchval(
                "SELECT 1 FROM pg_roles WHERE rolname = $1", settings.DB_USER
            )
            if not role_exists:
                # Use parameterized role generation if possible or execute format
                await conn.execute(
                    f"CREATE ROLE {settings.DB_USER} WITH LOGIN PASSWORD '{settings.DB_PASSWORD}'"
                )
                logger.info(f"Role {settings.DB_USER} created.")

            # Create TimescaleDB extension
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
                logger.info("TimescaleDB extension verified/created.")
            except Exception as e:
                logger.warning(f"Could not load TimescaleDB extension (falling back to standard PG): {e}")

            # Create tables
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS machines (
                    machine_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    model VARCHAR(100),
                    install_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'healthy'
                );

                CREATE TABLE IF NOT EXISTS sensor_readings (
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    machine_id VARCHAR(50) NOT NULL REFERENCES machines(machine_id),
                    vibration DOUBLE PRECISION NOT NULL,
                    temperature DOUBLE PRECISION NOT NULL,
                    rpm DOUBLE PRECISION NOT NULL,
                    pressure DOUBLE PRECISION NOT NULL
                );

                CREATE TABLE IF NOT EXISTS anomalies (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    machine_id VARCHAR(50) NOT NULL REFERENCES machines(machine_id),
                    vibration_status VARCHAR(20) NOT NULL,
                    temperature_status VARCHAR(20) NOT NULL,
                    rpm_status VARCHAR(20) NOT NULL,
                    pressure_status VARCHAR(20) NOT NULL,
                    anomaly_score DOUBLE PRECISION NOT NULL,
                    failure_probability DOUBLE PRECISION NOT NULL,
                    estimated_window_hours DOUBLE PRECISION,
                    ai_explanation TEXT,
                    action_taken BOOLEAN DEFAULT FALSE
                );

                CREATE TABLE IF NOT EXISTS maintenance_logs (
                    id SERIAL PRIMARY KEY,
                    machine_id VARCHAR(50) NOT NULL REFERENCES machines(machine_id),
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    action VARCHAR(250) NOT NULL,
                    notes TEXT
                );
            """)

            # Convert sensor_readings to hypertable if TimescaleDB is loaded
            is_timescale = await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb')"
            )
            if is_timescale:
                try:
                    await conn.execute("""
                        SELECT create_hypertable('sensor_readings', 'timestamp', if_not_exists => TRUE);
                    """)
                    logger.info("TimescaleDB hypertable 'sensor_readings' verified/created.")
                except Exception as e:
                    logger.warning(f"Failed to create TimescaleDB hypertable: {e}")

            # Grant privileges to the restricted application user
            await conn.execute(f"""
                GRANT CONNECT ON DATABASE "{settings.DB_NAME}" TO {settings.DB_USER};
                GRANT USAGE ON SCHEMA public TO {settings.DB_USER};
                GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {settings.DB_USER};
                GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {settings.DB_USER};
            """)
            logger.info("Privileges successfully granted to restricted application user.")
            
        finally:
            await conn.close()

    async def start_pool(self):
        """Starts a connection pool using the restricted application user credentials."""
        if not self.pool:
            logger.info(f"Starting database connection pool for user: {settings.DB_USER}")
            self.pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                min_size=2,
                max_size=10
            )

    async def close_pool(self):
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed.")

    async def execute(self, query: str, *args) -> str:
        """Executes a non-query command (INSERT/UPDATE/DELETE) using the connection pool."""
        if not self.pool:
            raise RuntimeError("Database pool has not been started.")
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetches rows using the connection pool."""
        if not self.pool:
            raise RuntimeError("Database pool has not been started.")
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, *args)
            return [dict(record) for record in records]

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetches a single row using the connection pool."""
        if not self.pool:
            raise RuntimeError("Database pool has not been started.")
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(query, *args)
            return dict(record) if record else None

    async def fetchval(self, query: str, *args) -> Any:
        """Fetches a single value using the connection pool."""
        if not self.pool:
            raise RuntimeError("Database pool has not been started.")
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


db_manager = DatabaseManager()
