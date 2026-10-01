import json


class Planner:
	def __init__(self, brain):
		self.brain = brain

	def plan(self, user_message: str) -> dict:
		prompt = (
			"Ordne die Benutzernachricht einem Intent zu. Verwende answer für "
			"Fragen, die direkt beantwortet werden können oder deren Antwort aus "
			"dem langfristigen persönlichen Memory kommen kann. Fragen nach "
			"persönlichen Angaben, Vorlieben oder Interessen sind answer, auch wenn "
			"du den gespeicherten Wert nicht kennst; das Brain beantwortet sie später "
			"mit dem Memory-Kontext. Verwende web_search, wenn aktuelle Informationen, "
			"Nachrichten, unsichere Modellkenntnisse oder externe Quellen für konkrete "
			"Fakten sinnvoll sind. Auch zeitlose Sachfragen können web_search sein, "
			"wenn eine externe Quelle hilfreich ist. Bei stabilen, allgemein bekannten "
			"Themen kannst du answer wählen. Verwende use_tool, wenn eine andere "
			"externe Funktion benötigt wird. Verwende unknown nur, wenn sich die "
			"Anfrage nicht eindeutig einordnen lässt. Führe keine Tools oder Suche aus. "
			"Antworte ausschließlich mit gültigem JSON; bei use_tool darf ein Feld "
			'"tool" enthalten sein.\n'
			f"Benutzernachricht: {user_message}"
		)
		response = self.brain.ask(prompt)

		try:
			result = json.loads(response)
		except (TypeError, json.JSONDecodeError):
			return {"intent": "unknown"}

		if not isinstance(result, dict) or result.get("intent") not in {
			"answer",
			"use_tool",
			"web_search",
			"unknown",
		}:
			return {"intent": "unknown"}

		decision = {"intent": result["intent"]}
		if decision["intent"] == "use_tool" and isinstance(result.get("tool"), str):
			decision["tool"] = result["tool"]
		return decision
