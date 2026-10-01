"""LLM-based decisions about information worth keeping in long-term memory."""

from dataclasses import dataclass
import json
import re


@dataclass(frozen=True)
class MemoryDecision:
    """A proposed memory update; this class never persists the information."""

    should_store: bool
    action: str = "ignore"
    key: str | None = None
    value: str | None = None
    reason: str = ""


class MemoryAnalyzer:
    """Use the configured Brain to decide whether a message belongs in memory."""

    def __init__(self, brain):
        self.brain = brain

    def analyze(self, user_message: str, existing_memory: dict | None = None) -> MemoryDecision:
        """Return a structured storage decision for one user message."""
        memory_context = json.dumps(
            existing_memory if isinstance(existing_memory, dict) else {},
            ensure_ascii=False,
        )
        prompt = f"""
Du analysierst Benutzernachrichten für ein langfristiges persönliches Memory.
Entscheide selbst, ob eine Nachricht stabile persönliche Angaben, Vorlieben,
Interessen oder Ziele enthält. Speichere keine Fragen, einmaligen Aktivitäten,
kurzfristigen Ereignisse oder situativen Angaben.

Aktuelles Memory (JSON):
{memory_context}

Nutze das bestehende Memory, um die Aktion zu bestimmen:
- "create": neue langfristige Information, für die noch kein passender Schlüssel besteht
- "update": eine vorhandene Information wird ausdrücklich korrigiert oder ersetzt
- "add": ein weiterer eigenständiger Wert gehört zu einer bestehenden Mehrfach-Kategorie
- "ignore": die Nachricht enthält keine langfristig relevante Information

Erfinde keine Informationen. Wiederverwende passende bestehende Schlüssel und
deren Bedeutung. Wenn kein Schlüssel passt, erstelle einen kurzen, eindeutigen
snake_case-Schlüssel für die neue Kategorie. Beschränke dich nicht auf eine
vorgegebene Kategorienliste und teile gleichartige Informationen nicht unnötig
auf. Bei "add" gib nur den neuen Wert zurück; Memory fügt ihn zum vorhandenen
Wert hinzu. Entscheide bei "update" anhand der Nachricht und des Memory-Kontexts,
welcher vorhandene Wert ersetzt wird.

Gib ausschließlich ein valides JSON-Objekt in diesem Format zurück:
{{"should_store": true, "action": "create", "key": "kurzer_snake_case_schlüssel", "value": "knappe Information", "reason": "kurze Begründung"}}
Bei nicht relevanten Nachrichten muss should_store false sein, action muss "ignore" sein und key sowie value müssen null sein. Bei speicherbaren Nachrichten muss should_store true sein und action "create", "update" oder "add" sein. Erfinde keine Informationen und übernimm nur Angaben aus der Nachricht. Beispiele:
- "Ich heiße Leo" -> action "create", key "name", value "Leo"
- Wenn das Memory bereits `{{"hobbies": ["Skateboarden"]}}` enthält und der Benutzer "Ich spiele auch Schlagzeug" sagt -> action "add", key "hobbies", value "Schlagzeug"
- Wenn das Memory `{{"name": "Leo"}}` enthält und der Benutzer seinen Namen ausdrücklich korrigiert -> action "update", key "name", value mit dem korrigierten Namen
- Eine neue, bisher nicht gespeicherte langfristige Angabe -> action "create" mit einem passenden neuen oder bestehenden Kategorie-Schlüssel
- "Ich war heute 3 Stunden skaten" -> should_store false, action "ignore"
- "Was für ein Wetter heute?" -> should_store false, action "ignore"

Benutzernachricht:
{user_message}
""".strip()

        try:
            response = self.brain.ask(prompt)
            data = self._parse_json(response)
        except (TypeError, ValueError, KeyError):
            return MemoryDecision(False, reason="Keine gültige Analyzer-Antwort")

        action = data.get("action")
        if not isinstance(action, str) or action not in {"create", "update", "add", "ignore"}:
            return MemoryDecision(False, reason="Ungültige Speicheraktion")

        if data.get("should_store") is not True:
            return MemoryDecision(False, reason=self._string(data.get("reason")))

        if action == "ignore":
            return MemoryDecision(False, reason="Ungültige Speicheraktion")

        key = self._string(data.get("key")).strip()
        value = self._string(data.get("value")).strip()
        if not key or not value:
            return MemoryDecision(False, reason="Speicherentscheidung unvollständig")

        return MemoryDecision(
            should_store=True,
            action=action,
            key=key,
            value=value,
            reason=self._string(data.get("reason")),
        )

    @staticmethod
    def _parse_json(response: str) -> dict:
        if not isinstance(response, str):
            raise TypeError("LLM-Antwort muss Text sein")

        text = response.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if fenced:
            text = fenced.group(1)

        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("LLM-Antwort muss ein JSON-Objekt sein")
        return data

    @staticmethod
    def _string(value) -> str:
        return value if isinstance(value, str) else ""
