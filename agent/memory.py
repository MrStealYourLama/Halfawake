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

    def get(self, key, default=None):
        data = self.load()
        return data.get(key, default)

    def set(self, key, value):
        data = self.load()
        data[key] = value
        self.save(data)

    def add(self, key, value):
        data = self.load()
        existing = data.get(key)

        if existing is None:
            values = []
        elif isinstance(existing, list):
            values = existing
        else:
            values = [existing]

        if value not in values:
            values.append(value)

        data[key] = values
        self.save(data)

    def delete(self, key):
        data = self.load()

        if key in data:
            del data[key]
            self.save(data)
