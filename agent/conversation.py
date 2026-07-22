from agent.prompts import SYSTEM_PROMPT

class Conversation:

    def __init__(self, brain):
        self.brain = brain
        self.history = []

    def ask(self, user_input: str):

        self.history.append(
            f"User: {user_input}"
        )

        context = "\n".join(self.history)

        prompt = f"""
        {SYSTEM_PROMPT}

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