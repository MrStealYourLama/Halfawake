"""LLM-based decisions about information worth keeping in long-term memory."""

from dataclasses import dataclass
import json
import re


@dataclass(frozen=True)
class MemoryDecision:
    """A proposed memory update; this class never persists the information."""

    should_store: bool
    key: str | None = None
    value: str | None = None
    reason: str = ""


class MemoryAnalyzer:
    """Use the configured Brain to decide whether a message belongs in memory."""

    def __init__(self, brain):
        self.brain = brain

    def analyze(self, user_message: str) -> MemoryDecision:
        """Return a structured storage decision for one user message."""
        prompt = f"""
Du analysierst Benutzernachrichten für ein langfristiges persönliches Memory.
Entscheide selbst, ob die Nachricht langfristig relevante Information enthält
und welche knappe Information daraus gespeichert werden sollte. Speichere nur
stabile persönliche Angaben, Vorlieben, Interessen oder Ziele. Speichere keine
Fragen, einmaligen Aktivitäten, kurzfristigen Ereignisse oder situativen Angaben.

Wähle für speicherbare Informationen einen kurzen, eindeutigen snake_case-Schlüssel.
Der Schlüssel beschreibt die Art der Information, nicht ihren konkreten Wert.
Verwende bevorzugt eine passende Kategorie aus dieser Liste und nutze dieselbe
Kategorie für gleichartige Informationen:
- name: Name des Benutzers
- favorite_color: Lieblingsfarbe
- hobbies: dauerhafte Hobbys und Aktivitäten, die der Benutzer gerne ausübt
- music_preferences: bevorzugte Künstler, Bands und Musikrichtungen
- goals: persönliche Ziele und angestrebte Berufe

Beispiele für konsistente Kategorien:
- „Ich heiße Leo“ -> key „name“, value „Leo“
- „Meine Lieblingsfarbe ist Blau“ -> key „favorite_color“, value „Blau“
- „Ich skate sehr gerne“ -> key „hobbies“, value „Skateboarden“
- „Ich spiele gerne Schlagzeug“ -> key „hobbies“, value „Schlagzeug“
- „Ich liebe Måneskin“ -> key „music_preferences“, value „Måneskin“
- „Ich möchte später Ingenieur werden“ -> key „goals“, value „Ingenieur werden“

Wenn keine vorhandene Kategorie passt, darfst du eine neue sinnvolle Kategorie
erstellen. Teile Kategorien nicht unnötig auf, verwende keine Synonyme oder
verschiedene Schlüssel für dieselbe Kategorie und erfinde keine übermäßig
spezifischen Kategorien.

Gib ausschließlich ein JSON-Objekt in diesem Format zurück:
{{"should_store": true, "key": "kurzer_snake_case_schlüssel", "value": "knappe Information", "reason": "kurze Begründung"}}
Bei nicht relevanten Nachrichten muss should_store false sein und key sowie value
müssen null sein. Erfinde keine Informationen und übernimm nur Angaben aus der
Nachricht. Beispiele:
- "Ich heiße Leo" -> key "name", value "Leo"
- "Meine Lieblingsfarbe ist Blau" -> key "favorite_color", value "Blau"
- "Ich skate sehr gerne" -> key "hobbies", value "Skateboarden"
- "Ich war heute 3 Stunden skaten" -> nicht speichern
- "Was für ein Wetter heute?" -> nicht speichern

Benutzernachricht:
{user_message}
""".strip()

        try:
            response = self.brain.ask(prompt)
            data = self._parse_json(response)
        except (TypeError, ValueError, KeyError):
            return MemoryDecision(False, reason="Keine gültige Analyzer-Antwort")

        if data.get("should_store") is not True:
            return MemoryDecision(False, reason=self._string(data.get("reason")))

        key = self._string(data.get("key")).strip()
        value = self._string(data.get("value")).strip()
        if not key or not value:
            return MemoryDecision(False, reason="Speicherentscheidung unvollständig")

        return MemoryDecision(
            should_store=True,
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
