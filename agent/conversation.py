from agent.prompts import SYSTEM_PROMPT
from agent.memory_analyzer import MemoryAnalyzer
from agent.planner import Planner

class Conversation:

    def __init__(self, brain, memory):
        self.brain = brain
        self.memory = memory
        self.planner = Planner(brain)
        self.memory_analyzer = MemoryAnalyzer(brain)
        self.history = []

    def ask(self, user_input: str):
        self.history.append(f"User: {user_input}")

        plan = self.planner.plan(user_input)
        decision = self.memory_analyzer.analyze(user_input, self.memory.load())
        self.memory.apply_decision(decision)

        intent = plan.get("intent") if isinstance(plan, dict) else "unknown"
        if intent == "use_tool":
            tool = plan.get("tool")
            if isinstance(tool, str) and tool:
                response = (
                    f"[Interner Platzhalter: Tool '{tool}' erkannt; "
                    "Ausführung noch nicht implementiert.]"
                )
            else:
                response = (
                    "[Interner Platzhalter: Tool-Anfrage erkannt; "
                    "Ausführung noch nicht implementiert.]"
                )
        elif intent == "web_search":
            response = (
                "[Interner Platzhalter: Websuche erforderlich; "
                "Suchaufruf noch nicht implementiert.]"
            )
        elif intent != "answer":
            response = (
                "[Interner Platzhalter: Anfrage konnte nicht eindeutig "
                "eingeordnet werden.]"
            )
        else:
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

        self.history.append(f"JARVIS: {response}")
        return response
    def clear(self):
        self.history = []