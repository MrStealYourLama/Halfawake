import logging
import os


def setup_logger():
    os.makedirs("data/logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("data/logs/jarvis.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("JARVIS")