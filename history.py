from datetime import datetime


class PredictionHistory:
    """Keeps the most recent predictions (in memory)."""

    def __init__(self, limit=50):
        self.limit = limit
        self._items = []

    def add(self, filename, label, confidence):
        self._items.append({
            "filename": filename,
            "label": label,
            "confidence": round(float(confidence), 4),
            "time": datetime.now().strftime("%H:%M:%S"),
        })
        self._items = self._items[-self.limit:]

    def all(self):
        return list(self._items)

    def count(self):
        return len(self._items)

    def clear(self):
        self._items = []
