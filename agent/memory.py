import json
from pathlib import Path


class Memory:

    def __init__(self):
        self.file = Path("data/memory.json")

        if not self.file.exists():
            self.file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    def load(self):

        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)