from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LeadStatus(str, Enum):
    new = "new"
    enriched = "enriched"
    scored = "scored"
    email_draft = "email_draft"
    email_approved = "email_approved"
    email_sent = "email_sent"
    replied = "replied"
    discarded = "discarded"
    opted_out = "opted_out"


class BookingPlatform(str, Enum):
    none = "none"
    treatwell = "treatwell"
    booksy = "booksy"
    fresha = "fresha"
    simplybook = "simplybook"
    calendly = "calendly"
    acuity = "acuity"
    reservio = "reservio"
    other_platform = "other_platform"
    unknown = "unknown"


class EstimatedSize(str, Enum):
    solo = "solo"        # 1 persona
    small = "small"      # 2-5 personas
    medium = "medium"    # 6-15 personas
    large = "large"      # cadena / franquicia


class LeadScore(BaseModel):
    score: int = Field(ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class LeadCreate(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    community: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    google_place_id: Optional[str] = None
    google_maps_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    hours_text: Optional[str] = None
    social_instagram: Optional[str] = None
    social_facebook: Optional[str] = None
    booking_platform: str = BookingPlatform.unknown.value
    has_online_booking: bool = False
    uses_whatsapp: Optional[bool] = None
    estimated_size: Optional[str] = None
    source: str = "manual"
    score: int = 0
    score_reasons: Optional[str] = None  # JSON string
    status: str = LeadStatus.new.value
    do_not_contact: bool = False
    notes: Optional[str] = None


class LeadRead(LeadCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    email_sent_at: Optional[datetime] = None
    email_status: Optional[str] = None

    model_config = {"from_attributes": True}


class EmailDraftCreate(BaseModel):
    lead_id: str
    subject: str
    body_text: str
    body_html: Optional[str] = None


class EmailDraftRead(EmailDraftCreate):
    id: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class WhatsAppDraftCreate(BaseModel):
    lead_id: str
    phone: str
    message_text: str
    wa_link: str


class WhatsAppDraftRead(WhatsAppDraftCreate):
    id: str
    whatsapp_status: str
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
