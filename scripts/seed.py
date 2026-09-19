import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import psycopg
from pwdlib import PasswordHash


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

password_hash = PasswordHash.recommended()

SEED_EMAIL = "seed@example.com"
SEED_PASSWORD = "SeedPass123"


def main():
    hashed_password = password_hash.hash(SEED_PASSWORD)

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tenants (
                    name,
                    owner_email,
                    password_hash
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (owner_email)
                DO UPDATE SET
                    password_hash = EXCLUDED.password_hash
                RETURNING id;
                """,
                (
                    "FlyRank Demo Tenant",
                    SEED_EMAIL,
                    hashed_password,
                ),
            )

            tenant_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO widgets (
                    tenant_id,
                    type,
                    title,
                    description,
                    status
                )
                SELECT
                    %s,
                    'signup',
                    'Demo Signup Widget',
                    'Seeded widget for local testing',
                    'active'
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM widgets
                    WHERE tenant_id = %s
                      AND title = 'Demo Signup Widget'
                )
                RETURNING id;
                """,
                (tenant_id, tenant_id),
            )

            widget = cursor.fetchone()

        connection.commit()

    print("Seed completed successfully.")
    print(f"Email: {SEED_EMAIL}")
    print(f"Password: {SEED_PASSWORD}")

    if widget:
        print(f"Widget ID: {widget[0]}")
    else:
        print("Demo widget already exists.")


if __name__ == "__main__":
    main()