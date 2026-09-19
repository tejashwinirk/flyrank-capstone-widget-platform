from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.db.database import get_connection


router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


@router.post("/register", status_code=201)
def register(payload: RegisterRequest):
    password_hash = hash_password(payload.password)

    query = """
        INSERT INTO tenants (name, owner_email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING id, name, owner_email, created_at;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (
                        payload.name,
                        payload.email,
                        password_hash,
                    ),
                )
                row = cursor.fetchone()

            connection.commit()

    except Exception:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    return {
        "id": str(row[0]),
        "name": row[1],
        "owner_email": row[2],
        "created_at": row[3],
    }


@router.post("/login")
def login(payload: LoginRequest):
    query = """
        SELECT id, name, owner_email, password_hash
        FROM tenants
        WHERE owner_email = %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (payload.email,))
            row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    tenant_id, name, owner_email, password_hash = row

    if not password_hash or not verify_password(
        payload.password,
        password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(tenant_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "tenant": {
            "id": str(tenant_id),
            "name": name,
            "owner_email": owner_email,
        },
    }