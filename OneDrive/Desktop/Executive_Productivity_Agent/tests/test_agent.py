from datetime import date

from models import Action
from processor import classify_actions


def test_action_classification():

    actions = [
        Action(
            id="1",
            description="Send report",
            owner="Arjun",
            owner_type="me",
            status="open",
            due_date="2026-09-23",
            source_id="EMAIL-001"
        ),
        Action(
            id="2",
            description="Prepare presentation",
            owner="Neha",
            owner_type="other",
            status="open",
            due_date="2026-09-24",
            source_id="EMAIL-002"
        ),
        Action(
            id="3",
            description="Confirm owner",
            owner="",
            owner_type="unclear",
            status="unclear",
            due_date="2026-09-25",
            source_id="EMAIL-003"
        )
    ]

    result = classify_actions(
        actions,
        selected_date=date(2026, 9, 21),
        my_name="Arjun"
    )

    assert len(result["my_actions"]) == 1
    assert len(result["waiting_actions"]) == 1
    assert len(result["unclear_actions"]) == 1
    assert len(result["upcoming_actions"]) == 3