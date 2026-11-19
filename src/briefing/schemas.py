"""Data shapes for the briefing engine. Source of truth for DB, API and LLM structured output."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

RoleType = Literal["PR_Comms", "Gov_Relations", "Stakeholder_Relations", "Executive_Strategy"]
SourceType = Literal["news", "broadcast", "social", "legislative", "regulatory", "stakeholder"]
Urgency = Literal["immediate", "today", "this_week", "monitor"]
Jurisdiction = Literal["CA", "UK", "EU", "US", "GLOBAL"]


# ---------- Profiles ----------

class OrgProfile(BaseModel):
    tenant_id: str
    name: str
    mission: str
    strategic_priorities: list[str]
    live_issues: list[str] = Field(description="Issues currently being managed, incl. crises.")
    known_risks: list[str]
    competitors: list[str] = []
    tracked_entities: list[str] = Field(default=[], description="Org-wide: bills, regulators, NGOs, etc.")
    tone_of_voice: str = ""
    spokespeople: list[str] = Field(default=[], description="Who may speak on the record, on what.")
    issue_owners: dict[str, str] = Field(default={}, description="Issue -> user_id for escalation.")


class RoleProfile(BaseModel):
    user_id: str
    tenant_id: str
    role_type: RoleType
    title: str
    mandates: list[str] = Field(description="What this person is measured on.")
    tracked_entities: list[str] = Field(
        description="Committees, ministers/MPs, officials, journalists, NGOs, bills, competitors."
    )
    authority: str = Field(description="What they can do without sign-off, e.g. 'can issue holding statements'.")
    risk_tolerance: Literal["low", "medium", "high"] = "medium"
    relevance_threshold: float = 0.7
    jurisdictions: list[Jurisdiction] = Field(default=["GLOBAL"])
    language: str = Field(default="en", description="Language briefs are written in, e.g. 'en', 'fr'.")
    timezone: str = Field(default="Europe/London", description="IANA zone, for digest timing.")
    data_region: Literal["UK", "EU", "US", "CA"] = Field(default="UK", description="Where this user's context card is stored.")
    context_source: Literal["email_and_calendar", "role_only"] = Field(
        default="email_and_calendar",
        description="'role_only' = no email-derived context (users who haven't opted in).",
    )


# ---------- Internal context (distilled from email/calendar; raw text never stored) ----------

class CardItem(BaseModel):
    card_item_id: str
    kind: Literal["active_issue", "stakeholder", "upcoming_event", "commitment"]
    summary: str = Field(description="One or two sentences, no verbatim email text.")
    people: list[str] = []
    due: date | None = None
    source_refs: list[str] = Field(default=[], description="Graph message/event IDs, for provenance links.")
    pinned_by_user: bool = False


class WorkContextCard(BaseModel):
    user_id: str
    generated_at: datetime
    items: list[CardItem]


# ---------- External signals ----------

class Signal(BaseModel):
    signal_id: str
    source_type: SourceType
    source_name: str = Field(description="Outlet, chamber, regulator or platform.")
    jurisdiction: Jurisdiction = "GLOBAL"
    language: str = "en"
    headline: str
    excerpt: str = Field(description="Licensed excerpt or abstract, original language.")
    excerpt_en: str | None = Field(default=None, description="English translation, if excerpt is not English.")
    url: str
    published_at: datetime
    author: str | None = None
    entities: list[str] = []
    topics: list[str] = Field(default=[], description="Cross-source tags, e.g. 'china'.")
    reach: int | None = None


class Story(BaseModel):
    story_id: str
    title: str
    signals: list[Signal]


# ---------- LLM outputs ----------

class TriageResult(BaseModel):
    score: float = Field(ge=0, le=1, description="Relevance of this story to this user.")
    urgency: Urgency
    reason: str = Field(description="One line on why, or why not.")


class Citation(BaseModel):
    claim: str
    signal_ids: list[str] = []
    card_item_ids: list[str] = []


class Brief(BaseModel):
    """The 'what / why / what to do' output for one story and one user."""

    headline: str = Field(description="Max 12 words, written for this user.")
    what_happened: str = Field(description="2-3 factual sentences, from the sources only.")
    why_it_matters_to_you: str = Field(
        description="Specific link to this user's mandates and work-context items. "
        "Name the thread, meeting or commitment. If the link is only to the role, say so."
    )
    implication: Literal["Opportunity", "Reputation_Risk", "Regulatory_Shift", "Competitor_Move",
                         "Stakeholder_Shift", "Monitor_Only"]
    severity: Literal["low", "medium", "high"]
    urgency: Urgency
    recommended_actions: list[str] = Field(description="1-3 concrete next steps within the user's authority.")
    draft_type: Literal["holding_statement", "outreach_email", "briefing_note", "board_paragraph",
                        "social_reply", "none"]
    draft: str = Field(description="Ready-to-edit draft, or empty if draft_type is 'none'.")
    draft_recipient_hint: str = Field(default="", description="Who the draft is for, if applicable.")
    possible_registrable_lobbying: bool = Field(
        default=False, description="True if the draft is outreach to an official that may be registrable."
    )
    lobbying_jurisdiction: Jurisdiction | None = None
    citations: list[Citation] = Field(description="Every factual or personal-context claim, with its sources.")
    confidence: Literal["low", "medium", "high"]
