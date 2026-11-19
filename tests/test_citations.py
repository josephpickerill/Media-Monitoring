from datetime import datetime, timezone

from briefing.schemas import Brief, CardItem, Citation, Signal, Story, WorkContextCard
from briefing.synthesis import citations_valid

NOW = datetime.now(timezone.utc)
STORY = Story(story_id="st1", title="t", signals=[Signal(
    signal_id="s1", source_type="news", source_name="Outlet", headline="h",
    excerpt="e", url="https://example.com", published_at=NOW)])
CARD = WorkContextCard(user_id="u1", generated_at=NOW, items=[
    CardItem(card_item_id="c1", kind="active_issue", summary="x")])


def brief(citations):
    return Brief(headline="h", what_happened="w", why_it_matters_to_you="y",
                 implication="Monitor_Only", severity="low", urgency="monitor",
                 recommended_actions=["Monitor"], draft_type="none", draft="",
                 citations=citations, confidence="high")


def test_valid():
    assert citations_valid(brief([Citation(claim="a", signal_ids=["s1"], card_item_ids=["c1"])]), STORY, CARD)


def test_rejects_unknown_card_item():
    # e.g. another user's card item leaking in
    assert not citations_valid(brief([Citation(claim="a", card_item_ids=["other-user-item"])]), STORY, CARD)


def test_rejects_uncited():
    assert not citations_valid(brief([Citation(claim="a")]), STORY, CARD)
    assert not citations_valid(brief([]), STORY, CARD)
