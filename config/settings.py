import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

EXA_API_KEY = os.getenv("EXA_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

BOOKING_URL = os.getenv("BOOKING_URL", "https://cal.com/leonidshvorob/fit-check-call")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "leo@systemhustle.com")
WEBSITE_URL = os.getenv("WEBSITE_URL", "https://systemhustle.com")
WHATSAPP = os.getenv("WHATSAPP", "+628175755953")

MAX_ICPS_SELECTABLE = 3
MIN_ICPS_SELECTABLE = 2
MAX_COMPANIES_TOTAL = 6
MAX_COMPANIES_PER_ICP = 3
MAX_SIGNALS_VISIBLE = 5
MAX_RESPONSE_TIME_SECONDS = 20

POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY", "")
POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
