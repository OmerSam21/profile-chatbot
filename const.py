import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "")  # empty = file logging disabled
LOG_FILE_MAX_BYTES = int(os.getenv("LOG_FILE_MAX_BYTES", "10485760"))  # 10 MB
LOG_FILE_BACKUP_COUNT = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))

# LLM providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")

# Profile sources
PROFILE_DIR = Path(os.getenv("PROFILE_DIR", str(BASE_DIR / "profile")))
LINKEDIN_FILE = PROFILE_DIR / "linkedin.txt"
SUMMARY_FILE = PROFILE_DIR / "summary.txt"

# Actor
ACTOR_PROVIDER = os.getenv("ACTOR_PROVIDER", "openai")  # Options: "openai", "gemini"
ACTOR_MODEL = os.getenv("ACTOR_MODEL", "gpt-5.4-mini")
