"""WhatsApp message draft generator using Jinja2 templates."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.config.settings import get_settings
from src.models.lead import LeadRead, WhatsAppDraftCreate

_TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


def _get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,  # plain text for WhatsApp
        trim_blocks=True,
        lstrip_blocks=True,
    )


def generate_whatsapp_draft(lead: LeadRead) -> WhatsAppDraftCreate | None:
    """Generate a personalized WhatsApp message draft. Returns None if no phone."""
    if not lead.phone:
        return None

    settings = get_settings()
    env = _get_env()

    ctx = {
        "lead": lead,
        "sender": {
            "name": settings.sender_name,
            "landing_url": settings.landing_url,
        },
    }

    message_text = env.get_template("whatsapp_message.j2").render(**ctx).strip()
    wa_link = _build_wa_link(lead.phone, message_text)

    return WhatsAppDraftCreate(
        lead_id=lead.id,
        phone=lead.phone,
        message_text=message_text,
        wa_link=wa_link,
    )


def _build_wa_link(phone: str, message: str) -> str:
    """Build a wa.me link with URL-encoded pre-filled message."""
    clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    encoded = quote(message)
    return f"https://wa.me/{clean}?text={encoded}"
