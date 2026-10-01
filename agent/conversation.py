from agent.prompts import SYSTEM_PROMPT
from agent.memory_analyzer import MemoryAnalyzer

class Conversation:

    def __init__(self, brain, memory):
        self.brain = brain
        self.memory = memory
        self.memory_analyzer = MemoryAnalyzer(brain)
        self.history = []

    def ask(self, user_input: str):

        self.history.append(
            f"User: {user_input}"
        )

        decision = self.memory_analyzer.analyze(user_input, self.memory.load())
        self.memory.apply_decision(decision)

        context = "\n".join(self.history)
        memory_data = self.memory.load()

        prompt = f"""
{SYSTEM_PROMPT}

Gespeichertes Wissen:
{memory_data}

Gespräch:
{context}

JARVIS:
"""

        response = self.brain.ask(prompt)

        self.history.append(
            f"JARVIS: {response}"
        )

        return response
    def clear(self):
        self.history = []