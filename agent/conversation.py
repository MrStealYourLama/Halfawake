from agent.prompts import SYSTEM_PROMPT

class Conversation:

    def __init__(self, brain, memory):
        self.brain = brain
        self.memory = memory
        self.history = []

    def ask(self, user_input: str):

        self.history.append(
            f"User: {user_input}"
        )

        self.check_memory(user_input)

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


    def check_memory(self, user_input):

        if user_input.startswith("Ich heiße "):
            name = user_input[10:]
            self.memory.set("name", name)

        elif user_input.startswith("Meine Lieblingsfarbe ist "):
            color = user_input[25:]
            self.memory.set("favorite_color", color)

    def clear(self):
        self.history = []