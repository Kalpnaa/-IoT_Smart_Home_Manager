import os
from google import genai

# Set your Google Gemini API key as environment variable before running
os.environ["GEMINI_API_KEY"] = "AIzaSyAo6pvIjhfZJo2zwCQd_1fVwLMnxJ15hmY"

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

class GeminiAgent:
    def __init__(self, name, model="gemini-2.5-flash"):
        self.name = name
        self.model = model
        self.chat = client.chats.create(model=self.model)

    def ask_gemini(self, prompt):
        response = self.chat.send_message(prompt)
        return response.text

class SmartHomeOrchestrator:
    def __init__(self):
        self.lighting_agent = GeminiAgent("LightingAgent")
        self.hvac_agent = GeminiAgent("HVACAgent")
        self.security_agent = GeminiAgent("SecurityAgent")

    def run_cycle(self, sensor_data):
        # Build prompt contextualizing current sensor readings
        prompt_lighting = f"Based on motion={sensor_data['motion']} and time_of_day={sensor_data['time_of_day']}, decide lighting action."
        prompt_hvac = f"Temperature is {sensor_data['temperature']} degrees and occupancy is {sensor_data['occupancy']}. Decide HVAC action."
        prompt_security = f"House empty status is {sensor_data['house_empty']}. Decide security action."

        lighting_action = self.lighting_agent.ask_gemini(prompt_lighting)
        hvac_action = self.hvac_agent.ask_gemini(prompt_hvac)
        security_action = self.security_agent.ask_gemini(prompt_security)

        actions = {
            "Lighting": lighting_action,
            "HVAC": hvac_action,
            "Security": security_action
        }
        return actions

if __name__ == "__main__":
    orchestrator = SmartHomeOrchestrator()
    sensor_data_example = {
        "motion": True,
        "time_of_day": "morning",
        "temperature": 20,
        "occupancy": True,
        "house_empty": False
    }
    result = orchestrator.run_cycle(sensor_data_example)
    for agent, action in result.items():
        print(f"{agent} Agent decided: {action}")
