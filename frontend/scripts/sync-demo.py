from pathlib import Path
from shutil import copy2

FRONTEND = Path(__file__).resolve().parents[1]
TARGET = FRONTEND / "assets" / "demo"
FILES = ["notices", "more-notices", "campus-notices", "sources", "requirements", "profile", "media"]
TARGET.mkdir(parents=True, exist_ok=True)
for name in FILES:
    copy2(FRONTEND.parent / "mock" / f"{name}.json", TARGET / f"{name}.json")
