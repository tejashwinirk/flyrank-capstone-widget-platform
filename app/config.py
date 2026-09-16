import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
GEO_PROVIDER_A_URL = os.getenv("GEO_PROVIDER_A_URL")
GEO_PROVIDER_B_URL = os.getenv("GEO_PROVIDER_B_URL")


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

if not GEO_PROVIDER_A_URL:
    raise RuntimeError("GEO_PROVIDER_A_URL is not configured")

if not GEO_PROVIDER_B_URL:
    raise RuntimeError("GEO_PROVIDER_B_URL is not configured")