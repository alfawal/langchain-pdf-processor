from dotenv import load_dotenv
import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PERSIST_STORAGE_PATH = BASE_DIR / "storage"

load_dotenv(dotenv_path=BASE_DIR / ".env")

SOCOTRA_DOCS_URL = os.environ.get(
    "SOCOTRA_DOCS_URL", "https://docs.socotra.com/production/"
)
# if not (OPENAI_API_KEY := os.environ.get("OPENAI_API_KEY")):
#     raise ValueError("OPENAI_API_KEY environment variable is not set.")
