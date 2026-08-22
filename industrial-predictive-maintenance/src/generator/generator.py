import asyncio
import time
import random
from datetime import datetime, timezone
from typing import Dict, Any, List
from src.config import settings
from src.queue.streaming import stream_manager
from src.storage.db import db_manager
from src.utils.logger import get_logger, telemetry

logger = get_logger("generator")

# Define our mock machines and their normal operating parameters
MACHINE_PROFILES = {
    "M-101": {"name": "CNC Lathe", "model": "T-1000", "vibration_base": 1.8, "temp_base": 55.0, "rpm_base": 1500, "pressure_base": 30.0},
    "M-102": {"name": "Hydraulic Pump", "model": "H-400", "vibration_base": 2.2, "temp_base": 65.0, "rpm_base": 1800, "pressure_base": 45.0}, # Degrades
    "M-103": {"name": "Air Compressor", "model": "A-80", "vibration_base": 1.5, "temp_base": 50.0, "rpm_base": 1200, "pressure_base": 90.0},
    "M-104": {"name": "Turbine Generator", "model": "TG-2", "vibration_base": 2.5, "temp_base": 75.0, "rpm_base": 3000, "pressure_base": 60.0}, # Degrades
    "M-105": {"name": "Conveyor Motor", "model": "C-12", "vibration_base": 1.2, "temp_base": 45.0, "rpm_base": 800, "pressure_base": 15.0}
}

DEGRADING_MACHINES = {"M-102", "M-104"}

class MachineSimulator:
    """
    Simulates a synthetic factory environment.
    Machines emit data on a timer, with injected drifts.
    Responds to maintenance logs to reset state.
    """
    def __init__(self):
        self.degradation_states: Dict[str, float] = {m_id: 0.0 for m_id in DEGRADING_MACHINES}
        self.active = False

    async def register_machines(self):
        """Pre-populate the database with the machine profiles if they don't exist."""
        logger.info("Registering machines in database...")
        for machine_id, profile in MACHINE_PROFILES.items():
            exists = await db_manager.fetchrow(
                "SELECT machine_id FROM machines WHERE machine_id = $1", machine_id
            )
            if not exists:
                await db_manager.execute(
                    """
                    INSERT INTO machines (machine_id, name, model, status)
                    VALUES ($1, $2, $3, 'healthy')
                    """,
                    machine_id, profile["name"], profile["model"]
                )
                logger.info(f"Registered machine {machine_id}: {profile['name']}")

    async def check_maintenance_resets(self):
        """
        Queries DB for recent maintenance logs.
        If a machine was repaired, resets its degradation state and DB status to 'healthy'.
        """
        for machine_id in DEGRADING_MACHINES:
            if self.degradation_states[machine_id] > 0.0:
                # Check if there is an unhandled recent maintenance action
                latest_log = await db_manager.fetchrow(
                    """
                    SELECT id FROM maintenance_logs 
                    WHERE machine_id = $1 AND timestamp > NOW() - INTERVAL '30 seconds'
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    machine_id
                )
                if latest_log:
                    logger.info(f"Maintenance detected for {machine_id}! Resetting machine status to healthy.")
                    self.degradation_states[machine_id] = 0.0
                    await db_manager.execute(
                        "UPDATE machines SET status = 'healthy' WHERE machine_id = $1",
                        machine_id
                    )

    def generate_reading(self, machine_id: str) -> Dict[str, Any]:
        """Generates a single sensor reading record, factoring in random noise and drift."""
        profile = MACHINE_PROFILES[machine_id]
        
        # Base values
        vib = profile["vibration_base"]
        temp = profile["temp_base"]
        rpm = profile["rpm_base"]
        press = profile["pressure_base"]
        
        # Inject sinusoidal variations over time
        cycle = math_cycle = math_sin = 0.1 * random.random()
        
        # Calculate drift modifier
        drift = 0.0
        if machine_id in DEGRADING_MACHINES:
            drift = self.degradation_states[machine_id]
            # Increment drift slightly for next time
            self.degradation_states[machine_id] += 0.005 # Slow linear progression
            
        # Apply drift variations based on failure profile
        if machine_id == "M-102":
            # Hydraulic pump failure: rising vibration & overheating
            vib += (drift * 1.5) + random.normalvariate(0, 0.15)
            temp += (drift * 6.0) + random.normalvariate(0, 1.0)
            rpm += random.normalvariate(0, 15.0)
            press += random.normalvariate(0, 1.0)
        elif machine_id == "M-104":
            # Turbine Generator: pressure leak causing rpm drop and temperature spikes
            vib += (drift * 0.5) + random.normalvariate(0, 0.2)
            temp += (drift * 4.5) + random.normalvariate(0, 1.5)
            rpm -= (drift * 80.0) + random.normalvariate(0, 30.0)
            press -= (drift * 5.0) + random.normalvariate(0, 2.0)
        else:
            # Healthy machines have only random noise
            vib += random.normalvariate(0, 0.1)
            temp += random.normalvariate(0, 0.8)
            rpm += random.normalvariate(0, 10.0)
            press += random.normalvariate(0, 1.0)
            
        # Ensure values stay positive
        vib = max(0.1, vib)
        temp = max(10.0, temp)
        rpm = max(100.0, rpm)
        press = max(1.0, press)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "machine_id": machine_id,
            "vibration": round(vib, 2),
            "temperature": round(temp, 2),
            "rpm": round(rpm, 1),
            "pressure": round(press, 2)
        }

    async def run(self, interval_seconds: float = 2.0):
        """Continuous simulation loop."""
        self.active = True
        logger.info(f"Starting simulation loop (interval: {interval_seconds}s)...")
        await self.register_machines()
        
        while self.active:
            # Check if we should reset any machines due to maintenance activity
            try:
                await self.check_maintenance_resets()
            except Exception as e:
                logger.error(f"Error checking maintenance resets: {e}")
                telemetry.record_error()

            for machine_id in MACHINE_PROFILES.keys():
                reading = self.generate_reading(machine_id)
                # Stream via Redis Pub/Sub
                await stream_manager.publish_reading(reading)
                
            await asyncio.sleep(interval_seconds)

    def stop(self):
        self.active = False
        logger.info("Simulation loop stopped.")
