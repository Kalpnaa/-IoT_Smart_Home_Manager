import os
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch Gemini API key securely from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini API client using the loaded API key
client = genai.Client(api_key=gemini_api_key)

class GeminiAgent:
    def __init__(self, name, model="gemini-2.5-flash"):
        self.name = name
        self.model = model
        # Create a persistent chat session per agent
        self.chat = client.chats.create(model=self.model)

    def ask_gemini(self, prompt):
        try:
            # Send prompt and receive response
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            # Handle potential API or network errors gracefully
            print(f"Error with {self.name} Gemini API call: {e}")
            return "Error: could not fetch response"

class SmartHomeOrchestrator:
    def __init__(self):
        self.lighting_agent = GeminiAgent("LightingAgent")
        self.hvac_agent = GeminiAgent("HVACAgent")
        self.security_agent = GeminiAgent("SecurityAgent")

    def run_cycle(self, sensor_data):
        # Construct context-aware prompts using sensor data for each agent
        prompt_lighting = f"Based on motion={sensor_data['motion']} and time_of_day={sensor_data['time_of_day']}, decide lighting action."
        prompt_hvac = f"Temperature is {sensor_data['temperature']} degrees and occupancy is {sensor_data['occupancy']}. Decide HVAC action."
        prompt_security = f"House empty status is {sensor_data['house_empty']}. Decide security action."

        # Query each agent and collect their decisions
        lighting_action = self.lighting_agent.ask_gemini(prompt_lighting)
        hvac_action = self.hvac_agent.ask_gemini(prompt_hvac)
        security_action = self.security_agent.ask_gemini(prompt_security)

        return {
            "Lighting": lighting_action,
            "HVAC": hvac_action,
            "Security": security_action
        }

if __name__ == "__main__":
    orchestrator = SmartHomeOrchestrator()

    # Example sensor data - modify or extend for realistic testing
    sensor_data_example = {
        "motion": True,
        "time_of_day": "morning",
        "temperature": 20,
        "occupancy": True,
        "house_empty": False
    }

    actions = orchestrator.run_cycle(sensor_data_example)
    for agent, action in actions.items():
        print(f"{agent} Agent decided: {action}")
