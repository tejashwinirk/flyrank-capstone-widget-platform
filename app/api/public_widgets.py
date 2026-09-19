import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.database import get_connection
from app.services.auth_service import decode_access_token
from app.services.public_widget_service import get_public_widget


router = APIRouter(
    prefix="/public",
    tags=["Public Widgets"],
)

security = HTTPBearer()


def get_current_tenant(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    try:
        return decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


@router.get("/widgets/{widget_id}")
def get_public_widget_endpoint(widget_id: UUID):
    widget = get_public_widget(widget_id)

    if not widget:
        raise HTTPException(
            status_code=404,
            detail="Widget not found or inactive",
        )

    return {
        "widget": widget,
        "config": {
            "version": widget["version"],
            "type": widget["type"],
            "title": widget["title"],
            "description": widget["description"],
        },
    }


@router.get("/widgets/{widget_id}/embed")
def get_embed_snippet(
    widget_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
):
    query = """
        SELECT id
        FROM widgets
        WHERE id = %s
          AND tenant_id = %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (widget_id, tenant_id),
            )
            row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    snippet = (
        f'<script '
        f'src="http://127.0.0.1:8001/public/embed/{widget_id}.js" '
        f'data-widget-id="{widget_id}" '
        f'async></script>'
    )

    return {
        "widget_id": str(widget_id),
        "snippet": snippet,
    }


@router.get("/embed/{widget_id}.js")
def get_embed_script(widget_id: UUID):
    widget = get_public_widget(widget_id)

    if not widget:
        raise HTTPException(
            status_code=404,
            detail="Widget not found or inactive",
        )

    widget_id_json = json.dumps(str(widget_id))
    title_json = json.dumps(widget["title"])
    description_json = json.dumps(widget["description"] or "")

    javascript = f"""
(function () {{
    "use strict";

    const widgetId = {widget_id_json};
    const widgetTitle = {title_json};
    const widgetDescription = {description_json};

    const script =
        document.currentScript ||
        document.querySelector(
            'script[data-widget-id="' + widgetId + '"]'
        );

    if (!script) {{
        return;
    }}

    const container = document.createElement("div");

    container.id = "flyrank-widget-" + widgetId;

    const box = document.createElement("div");

    box.style.maxWidth = "420px";
    box.style.padding = "20px";
    box.style.border = "1px solid #ddd";
    box.style.borderRadius = "12px";
    box.style.fontFamily = "Arial,sans-serif";
    box.style.background = "#fff";
    box.style.boxShadow = "0 4px 12px rgba(0,0,0,0.08)";

    const title = document.createElement("h3");
    title.style.marginTop = "0";
    title.textContent = widgetTitle;

    const description = document.createElement("p");
    description.textContent = widgetDescription;

    const form = document.createElement("form");

    const nameInput = document.createElement("input");
    nameInput.name = "name";
    nameInput.type = "text";
    nameInput.placeholder = "Your name";
    nameInput.required = true;

    const emailInput = document.createElement("input");
    emailInput.name = "email";
    emailInput.type = "email";
    emailInput.placeholder = "Your email";
    emailInput.required = true;

    const messageInput = document.createElement("textarea");
    messageInput.name = "message";
    messageInput.placeholder = "Your message";

    const honeypot = document.createElement("input");
    honeypot.name = "website";
    honeypot.type = "text";
    honeypot.autocomplete = "off";
    honeypot.tabIndex = -1;

    honeypot.style.position = "absolute";
    honeypot.style.left = "-9999px";

    const submitButton = document.createElement("button");
    submitButton.type = "submit";
    submitButton.textContent = "Submit";

    const message = document.createElement("p");

    function styleInput(input) {{
        input.style.width = "100%";
        input.style.padding = "10px";
        input.style.marginBottom = "10px";
        input.style.boxSizing = "border-box";
    }}

    styleInput(nameInput);
    styleInput(emailInput);
    styleInput(messageInput);

    submitButton.style.width = "100%";
    submitButton.style.padding = "10px";
    submitButton.style.border = "0";
    submitButton.style.borderRadius = "8px";
    submitButton.style.cursor = "pointer";

    form.appendChild(nameInput);
    form.appendChild(emailInput);
    form.appendChild(messageInput);
    form.appendChild(honeypot);
    form.appendChild(submitButton);
    form.appendChild(message);

    box.appendChild(title);
    box.appendChild(description);
    box.appendChild(form);

    container.appendChild(box);

    script.parentNode.insertBefore(container, script);

    form.addEventListener("submit", async function (event) {{
        event.preventDefault();

        const payload = {{
            name: nameInput.value,
            email: emailInput.value,
            message: messageInput.value,
            website: honeypot.value
        }};

        message.textContent = "Submitting...";

        try {{
            const response = await fetch(
                "http://127.0.0.1:8001/public/widgets/"
                + widgetId
                + "/submissions",
                {{
                    method: "POST",
                    headers: {{
                        "Content-Type": "application/json"
                    }},
                    body: JSON.stringify(payload)
                }}
            );

            const result = await response.json();

            if (!response.ok) {{
                throw new Error(
                    result.detail || "Submission failed"
                );
            }}

            message.textContent =
                "Thank you! Your submission was received.";

            form.reset();

        }} catch (error) {{
            message.textContent =
                error.message || "Something went wrong.";
        }}
    }});
}})();
"""

    return Response(
        content=javascript,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=60",
        },
    )