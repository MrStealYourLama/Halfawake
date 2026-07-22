import requests

from config import OLLAMA_URL, MODEL_NAME


class Brain:

    def __init__(self):
        self.url = f"{OLLAMA_URL}/api/generate"
        self.model = MODEL_NAME

    def ask(self, prompt: str):

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.url, json=payload)

        if response.status_code != 200:
            return f"Fehler: {response.status_code}"

        data = response.json()

        return data["response"].strip()