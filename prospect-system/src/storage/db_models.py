from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String, index=True)
    province: Mapped[str | None] = mapped_column(String, index=True)
    community: Mapped[str | None] = mapped_column(String)
    postal_code: Mapped[str | None] = mapped_column(String)
    phone: Mapped[str | None] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)
    google_place_id: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    google_maps_url: Mapped[str | None] = mapped_column(String)
    rating: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int | None] = mapped_column(Integer)
    hours_text: Mapped[str | None] = mapped_column(Text)
    social_instagram: Mapped[str | None] = mapped_column(String)
    social_facebook: Mapped[str | None] = mapped_column(String)
    booking_platform: Mapped[str] = mapped_column(String, default="unknown")
    has_online_booking: Mapped[bool] = mapped_column(Boolean, default=False)
    uses_whatsapp: Mapped[bool | None] = mapped_column(Boolean)
    estimated_size: Mapped[str | None] = mapped_column(String)
    source: Mapped[str] = mapped_column(String, default="manual")
    score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    score_reasons: Mapped[str | None] = mapped_column(Text)  # JSON array
    status: Mapped[str] = mapped_column(String, default="new", index=True)
    do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    email_status: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String)
    body_text: Mapped[str] = mapped_column(Text)
    body_html: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(String)


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    message_text: Mapped[str] = mapped_column(Text)
    wa_link: Mapped[str] = mapped_column(Text)
    whatsapp_status: Mapped[str] = mapped_column(String, default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str | None] = mapped_column(String)
    data: Mapped[str | None] = mapped_column(Text)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SearchJob(Base):
    __tablename__ = "search_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")
    total_found: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
