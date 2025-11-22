import os
import asyncio
from google import genai
from dotenv import load_dotenv
import logging
from typing import Dict, List

# Load environment variables from .env file
load_dotenv()

# Configure logging for observability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fetch Gemini API key securely from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini API client
client = genai.Client(api_key=gemini_api_key)

# In-memory session memory class for persistence across cycles
class SessionMemory:
    def __init__(self):
        self.memory = {}

    def remember(self, agent_name: str, data: str):
        if agent_name not in self.memory:
            self.memory[agent_name] = []
        self.memory[agent_name].append(data)
        logging.info(f"Memory updated for {agent_name}: {data}")

    def recall(self, agent_name: str) -> List[str]:
        return self.memory.get(agent_name, [])

# Base Gemini AI agent class
class GeminiAgent:
    def __init__(self, name: str, model="gemini-2.5-flash", session_memory: SessionMemory = None):
        self.name = name
        self.model = model
        self.chat = client.chats.create(model=self.model)
        self.session_memory = session_memory

    async def ask_gemini(self, prompt: str) -> str:
        try:
            # Simulating long-running operation by awaiting Gemini response asynchronously
            response = await asyncio.to_thread(self.chat.send_message, prompt)
            answer = response.text
            if self.session_memory:
                self.session_memory.remember(self.name, answer)
            logging.info(f"{self.name} responded: {answer}")
            return answer
        except Exception as e:
            logging.error(f"Error in {self.name} Gemini API call: {e}")
            return "Error: could not fetch response"

# Orchestrator managing sequential then parallel execution of agents
class SmartHomeOrchestrator:
    def __init__(self):
        self.session_memory = SessionMemory()
        self.lighting_agent = GeminiAgent("LightingAgent", session_memory=self.session_memory)
        self.hvac_agent = GeminiAgent("HVACAgent", session_memory=self.session_memory)
        self.security_agent = GeminiAgent("SecurityAgent", session_memory=self.session_memory)

    async def run_cycle(self, sensor_data: Dict) -> Dict[str, str]:
        # Context engineering with enriched prompt
        lighting_prompt = (
            f"You're the Lighting Agent. Based on sensor data: motion={sensor_data['motion']}, "
            f"time_of_day={sensor_data['time_of_day']}, and previous memory {self.session_memory.recall('LightingAgent')}. "
            f"Decide the appropriate lighting action."
        )
        hvac_prompt = (
            f"You're the HVAC Agent. Based on sensor data: temperature={sensor_data['temperature']}, "
            f"occupancy={sensor_data['occupancy']}, and previous memory {self.session_memory.recall('HVACAgent')}. "
            f"Decide the appropriate HVAC action."
        )
        security_prompt = (
            f"You're the Security Agent. Based on sensor data: house_empty={sensor_data['house_empty']}, "
            f"and previous memory {self.session_memory.recall('SecurityAgent')}. Decide the appropriate security action."
        )

        # Run Lighting agent sequentially to simulate ordered operation
        lighting_action = await self.lighting_agent.ask_gemini(lighting_prompt)

        # Run HVAC and Security agents in parallel since they are independent
        hvac_task = asyncio.create_task(self.hvac_agent.ask_gemini(hvac_prompt))
        security_task = asyncio.create_task(self.security_agent.ask_gemini(security_prompt))

        hvac_action, security_action = await asyncio.gather(hvac_task, security_task)

        # Basic agent evaluation: check for errors and fallback defaults
        actions = {}
        for name, action in zip(['Lighting', 'HVAC', 'Security'], [lighting_action, hvac_action, security_action]):
            if action.startswith("Error:"):
                default_action = "Maintain current state"
                logging.warning(f"{name} agent failed. Using fallback: {default_action}")
                actions[name] = default_action
            else:
                actions[name] = action

        logging.info(f"Cycle actions: {actions}")
        return actions

# Main entry point
async def main():
    orchestrator = SmartHomeOrchestrator()

    # Simulate sensor data updates with loop for long-running operation and session context
    sensor_data_simulation = [
        {
            "motion": True,
            "time_of_day": "morning",
            "temperature": 20,
            "occupancy": True,
            "house_empty": False
        },
        {
            "motion": False,
            "time_of_day": "afternoon",
            "temperature": 25,
            "occupancy": False,
            "house_empty": True
        },
        # Add more samples to simulate session memory growth
    ]

    for cycle, sensor_data in enumerate(sensor_data_simulation, start=1):
        logging.info(f"Starting cycle {cycle}")
        actions = await orchestrator.run_cycle(sensor_data)
        for agent, action in actions.items():
            print(f"{agent} Agent decided: {action}")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
