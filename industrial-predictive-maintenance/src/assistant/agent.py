import asyncio
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from src.config import settings
from src.utils.logger import get_logger, telemetry

logger = get_logger("assistant")

class AIDiagnosticAssistant:
    """
    AI assistant to analyze machine anomalies and answer queries about machine status.
    Uses Gemini API if configured; otherwise, falls back to a rule-based mock engine.
    """
    def __init__(self):
        self.use_api = False
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.use_api = True
                logger.info("Gemini API assistant initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API assistant: {e}. Falling back to Mock.")
                telemetry.record_error()

    def _generate_mock_explanation(
        self, 
        machine_id: str,
        name: str, 
        model_name: str, 
        readings: dict, 
        failure_prob: float, 
        window: Optional[float]
    ) -> str:
        """Generates realistic rule-based diagnostic analysis if LLM is unavailable."""
        prob_pct = int(failure_prob * 100)
        
        if machine_id == "M-102":
            # Hydraulic pump profile
            return (
                f"**Diagnostic Summary (MOCK MODE):**\n"
                f"Machine **{name}** ({machine_id}, Model: {model_name}) is showing high risk of hydraulic pump failure ({prob_pct}% probability).\n\n"
                f"**Sensor Anomalies Detected:**\n"
                f"- **Vibration:** {readings['vibration']} mm/s (normal: ~2.2 mm/s, deviation: critical spike)\n"
                f"- **Temperature:** {readings['temperature']} °C (normal: ~65.0 °C, deviation: severe thermal build-up)\n\n"
                f"**Root Cause Analysis:**\n"
                f"The combination of elevated vibration and rising temperature indicates hydraulic fluid degradation "
                f"or mechanical cavitation inside the pump impeller. This is generating excessive friction, leading to thermal stress.\n\n"
                f"**Recommended Actions:**\n"
                f"1. Schedule inspection of hydraulic fluid levels and check for aeration/foaming.\n"
                f"2. Check seals and couplings for physical wear.\n"
                f"3. Perform corrective maintenance within the next **{window or 18} hours** to prevent complete seizure."
            )
        elif machine_id == "M-104":
            # Turbine generator profile
            return (
                f"**Diagnostic Summary (MOCK MODE):**\n"
                f"Machine **{name}** ({machine_id}, Model: {model_name}) is exhibiting signs of turbine degradation ({prob_pct}% probability of failure).\n\n"
                f"**Sensor Anomalies Detected:**\n"
                f"- **Pressure:** {readings['pressure']} PSI (normal: ~60.0 PSI, deviation: rapid loss of pressure)\n"
                f"- **RPM:** {readings['rpm']} RPM (normal: ~3000 RPM, deviation: deceleration drift)\n"
                f"- **Temperature:** {readings['temperature']} °C (normal: ~75.0 °C, deviation: slight thermal increase)\n\n"
                f"**Root Cause Analysis:**\n"
                f"The sharp drop in pressure combined with decreasing shaft RPM suggests a high-pressure casing leak or "
                f"internal thrust bearing friction. The turbine is struggling to maintain structural velocity due to fluid power loss.\n\n"
                f"**Recommended Actions:**\n"
                f"1. Perform immediate casing pressure tests to locate leakage points.\n"
                f"2. Inspect the thrust bearings for physical lubrication quality and wear.\n"
                f"3. Reduce turbine load immediately and coordinate emergency maintenance within **{window or 12} hours**."
            )
        else:
            return (
                f"**Diagnostic Summary (MOCK MODE):**\n"
                f"Machine **{name}** ({machine_id}) is reporting an anomalous pattern ({prob_pct}% failure probability).\n\n"
                f"**Sensors:** Vibration: {readings['vibration']} mm/s, Temp: {readings['temperature']} °C, "
                f"RPM: {readings['rpm']}, Pressure: {readings['pressure']} PSI.\n\n"
                f"**Recommendation:** Schedule a general physical inspection and review sensor calibration settings. "
                f"Address within {window or 24} hours."
            )

    async def explain_anomaly(
        self, 
        machine_id: str,
        name: str, 
        model_name: str, 
        readings: dict, 
        failure_prob: float, 
        window: Optional[float]
    ) -> str:
        """
        Explains why an anomaly occurred and recommends actions.
        Uses Gemini API or falls back to mock logic.
        """
        if not self.use_api:
            return self._generate_mock_explanation(machine_id, name, model_name, readings, failure_prob, window)

        prompt = f"""
        You are an expert Reliability and Industrial Maintenance Engineer.
        Analyze the following telemetry anomaly from a factory floor:
        
        Machine ID: {machine_id}
        Machine Name: {name}
        Model: {model_name}
        
        Current Sensor Readings:
        - Vibration: {readings['vibration']} mm/s
        - Temperature: {readings['temperature']} °C
        - RPM: {readings['rpm']} RPM
        - Pressure: {readings['pressure']} PSI
        
        Algorithm Assessment:
        - Failure Probability: {int(failure_prob * 100)}%
        - Estimated Maintenance Window: {window} hours
        
        Provide a concise, professional diagnostic report:
        1. Explain what is happening physically/mechanically, referencing the sensor patterns that triggered this.
        2. Identify the likely root cause (e.g. bearing failure, fluid leak, cavitation).
        3. Recommend specific, prioritized next steps for field technicians.
        
        Format your response in professional Markdown. Keep it brief and highly actionable.
        """
        try:
            # Run model in a thread pool if calling a sync method to avoid blocking the loop
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}. Falling back to Mock.")
            telemetry.record_error()
            return self._generate_mock_explanation(machine_id, name, model_name, readings, failure_prob, window)

    async def answer_query(self, user_query: str, context: List[Dict[str, Any]]) -> str:
        """
        Answers a user query like "what's wrong with machine M-102?" using the contextual state of the machines.
        """
        formatted_context = ""
        for m in context:
            formatted_context += (
                f"- Machine {m['machine_id']} ({m['name']}): Status = {m['status']}. "
                f"Latest readings: Vibration={m['vibration']} mm/s, Temp={m['temperature']} °C, "
                f"RPM={m['rpm']}, Pressure={m['pressure']} PSI. "
                f"Failure Prob={int(m.get('failure_probability', 0.0) * 100)}%. "
                f"Est. Window={m.get('estimated_window_hours', 'N/A')} hours.\n"
            )
            
        if not self.use_api:
            # High-quality mock query answering
            query_lower = user_query.lower()
            for m in context:
                if m["machine_id"].lower() in query_lower or m["name"].lower() in query_lower:
                    if m["status"] == "anomalous":
                        return (
                            f"**AI Assistant Response (MOCK MODE):**\n"
                            f"Machine **{m['name']}** ({m['machine_id']}) is currently flagged as **{m['status']}** with a "
                            f"**{int(m.get('failure_probability', 0.0) * 100)}%** probability of failure.\n\n"
                            f"Telemetry values indicate deviations in the sensors. "
                            f"Vibration is at {m['vibration']} mm/s and Temperature is {m['temperature']} °C. "
                            f"I recommend dispatching a technician to verify the lubrication/bearings and review the pressure casing. "
                            f"Target maintenance within **{m.get('estimated_window_hours', 24)} hours**."
                        )
                    else:
                        return (
                            f"**AI Assistant Response (MOCK MODE):**\n"
                            f"Machine **{m['name']}** ({m['machine_id']}) appears to be operating normally with a stable status of **healthy**.\n"
                            f"All sensor parameters (Vibration: {m['vibration']} mm/s, Temperature: {m['temperature']} °C, "
                            f"RPM: {m['rpm']}, Pressure: {m['pressure']} PSI) are within nominal operating envelopes. No action is required."
                        )
            return (
                f"**AI Assistant Response (MOCK MODE):**\n"
                f"I received your query: '{user_query}'.\n"
                f"Currently, I have data on: " + ", ".join([m["machine_id"] for m in context]) + ". "
                f"Please specify a valid machine ID (like M-102 or M-104) to request a detailed reliability report."
            )

        prompt = f"""
        You are an AI Factory Reliability Assistant. Answer the user's question about the factory machinery.
        
        Here is the current live status of the factory floor:
        {formatted_context}
        
        User Query: "{user_query}"
        
        Synthesize the state and answer their question clearly. If they ask about a specific machine, provide the latest status, telemetry anomalies if any, and maintenance recommendation. If they ask about a healthy machine, confirm its nominal status.
        Keep it direct, professional, and friendly.
        """
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API query answer failed: {e}.")
            telemetry.record_error()
            return f"Error connecting to AI Assistant. Telemetry status displays that machine is anomalous. Please inspect sensors manually."

ai_assistant = AIDiagnosticAssistant()
