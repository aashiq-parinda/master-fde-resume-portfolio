import asyncio
import logging
import asyncpg
from src.config import settings

logger = logging.getLogger("database")

DB_SCHEMA = """
-- 1. Clinical Guidelines Reference Database
CREATE TABLE IF NOT EXISTS clinical_guidelines (
    id SERIAL PRIMARY KEY,
    symptom_category VARCHAR(100) NOT NULL,
    red_flags TEXT NOT NULL,
    triage_level VARCHAR(20) NOT NULL, -- 'Emergency', 'Urgent', 'Routine'
    guideline_text TEXT NOT NULL
);

-- 2. Unstructured Patient Intakes
CREATE TABLE IF NOT EXISTS patient_intakes (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(200) NOT NULL,
    date_of_birth DATE NOT NULL,
    raw_symptoms TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending Review', -- 'Pending Review', 'Flagged', 'Cleared'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Structured Visit Summaries (never contains diagnosis, only flags & guidelines)
CREATE TABLE IF NOT EXISTS visit_summaries (
    id SERIAL PRIMARY KEY,
    intake_id INTEGER REFERENCES patient_intakes(id) ON DELETE CASCADE,
    summary_text TEXT NOT NULL,
    red_flags_extracted TEXT,
    triage_recommendation VARCHAR(20) NOT NULL,
    safety_attempts INTEGER DEFAULT 1,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Programmatic Safety Filter Infraction Logs
CREATE TABLE IF NOT EXISTS safety_logs (
    id SERIAL PRIMARY KEY,
    intake_id INTEGER REFERENCES patient_intakes(id) ON DELETE CASCADE,
    blocked_output TEXT NOT NULL,
    violation_reason TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

# Seed guidelines data for RAG matching
SEED_GUIDELINES = [
    ("Chest Pain", 
     "radiating chest pressure, left arm or jaw pain, sudden cold sweat, shortness of breath, history of heart condition", 
     "Emergency", 
     "Refer to nearest cardiac emergency facility. Do not discharge or delay. Immediate clinical triage required. Monitor ECG and vital signs."),
     
    ("Dyspnea", 
     "stridor, cyanosis, use of accessory muscles for breathing, oxygen saturation below 92%, history of asthma or anaphylaxis", 
     "Emergency", 
     "Administer oxygen and respiratory support. Immediate physician assessment required. Rule out anaphylaxis or pulmonary embolism."),
     
    ("Abdominal Pain", 
     "rebound tenderness, rigid abdomen, high fever, inability to keep fluids down, localized right lower quadrant pain", 
     "Urgent", 
     "Evaluate for acute surgical abdomen (appendicitis/cholecystitis). Keep patient NPO until surgical review is complete. Establish IV access."),
     
    ("Headache", 
     "thunderclap onset, sudden weakness on one side of the body, difficulty speaking, stiff neck with fever, vision changes", 
     "Emergency", 
     "Rule out subarachnoid hemorrhage, acute stroke, or meningitis. Immediate CT brain scan or lumbar puncture. Immediate physician review."),
     
    ("Fever", 
     "lethargy, stiff neck, petechial rash, confusion, temperature above 104F unresponsive to antipyretics", 
     "Urgent", 
     "Evaluate for sepsis or meningitis. Administer broad-spectrum antibiotics after blood cultures if sepsis is suspected."),
     
    ("Musculoskeletal Pain", 
     "none", 
     "Routine", 
     "Schedule regular outpatient consult. Recommend rest, ice, elevation, and over-the-counter NSAIDs if not contraindicated.")
]

class DatabaseManager:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Starts the asyncpg pool."""
        if self.pool is not None:
            return
        
        logger.info(f"Connecting to database at {settings.DB_HOST}:{settings.DB_PORT}...")
        try:
            self.pool = await asyncpg.create_pool(
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                min_size=2,
                max_size=10
            )
            logger.info("Database connection pool established successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise e

    async def initialize_database(self):
        """Creates tables and inserts seed data."""
        await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                logger.info("Executing database schema initialization...")
                await conn.execute(DB_SCHEMA)
                
                # Check if guidelines are seeded
                count = await conn.fetchval("SELECT COUNT(*) FROM clinical_guidelines")
                if count == 0:
                    logger.info("Seeding clinical guidelines...")
                    for category, flags, level, text in SEED_GUIDELINES:
                        await conn.execute("""
                            INSERT INTO clinical_guidelines (symptom_category, red_flags, triage_level, guideline_text)
                            VALUES ($1, $2, $3, $4)
                        """, category, flags, level, text)
                    logger.info("Clinical guidelines seeded.")
                else:
                    logger.info("Clinical guidelines already seeded.")
                    
                logger.info("Database schema successfully initialized.")

    async def execute(self, query: str, *args):
        """Execute a write/update statement."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch a single row."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Fetch a single scalar value."""
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed.")

db_manager = DatabaseManager()
