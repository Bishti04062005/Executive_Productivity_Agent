from datetime import date, datetime
from typing import List, Dict, Any


def convert_to_date(value):
    """
    Convert string, datetime, or date into datetime.date.

    Supported formats:
    - 2026-09-21
    - 2026-09-21T15:00:00
    - 2026-09-21 15:00:00
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        value = value.strip()

        # Try ISO datetime
        try:
            return datetime.fromisoformat(
                value.replace("Z", "")
            ).date()
        except ValueError:
            pass

        # Try ISO date
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None

    return None


def extract_deadline_date(due_date):
    """
    Extract only the date from a deadline.
    """
    return convert_to_date(due_date)


def get_action_data(action):
    """
    Convert an Action object or dictionary into a dictionary.
    """

    if hasattr(action, "model_dump"):
        return action.model_dump()

    if hasattr(action, "dict"):
        return action.dict()

    if isinstance(action, dict):
        return action

    return vars(action)


def classify_actions(
    actions: List[Any],
    selected_date,
    my_name: str = "Arjun"
) -> Dict[str, List[Any]]:
    """
    Classify actions by:

    - Ownership
    - Overdue status
    - Due today
    - Upcoming deadlines
    """

    # Convert selected date into date object
    selected_date = convert_to_date(selected_date)

    if selected_date is None:
        selected_date = date.today()

    # Ownership lists
    my_actions = []
    waiting_on_others = []
    unclear_ownership = []

    # Deadline lists
    overdue_actions = []
    due_today_actions = []
    upcoming_actions = []

    for action in actions:

        data = get_action_data(action)

        owner = str(
            data.get("owner", "") or ""
        ).strip()

        owner_type = str(
            data.get("owner_type", "unclear") or "unclear"
        ).lower()

        status = str(
            data.get("status", "open") or "open"
        ).lower()

        due_date_value = data.get("due_date")
        due_date = extract_deadline_date(due_date_value)

        # ---------------------------------
        # OWNERSHIP CLASSIFICATION
        # ---------------------------------

        unclear_values = {
            "",
            "unclear",
            "unknown",
            "tbd",
            "none",
            "null"
        }

        if (
            owner_type == "unclear"
            or owner.lower() in unclear_values
        ):
            unclear_ownership.append(action)

        elif owner.lower() == my_name.lower():
            my_actions.append(action)

        else:
            waiting_on_others.append(action)

        # ---------------------------------
        # DEADLINE CLASSIFICATION
        # ---------------------------------

        completed_statuses = {
            "completed",
            "complete",
            "done",
            "cancelled",
            "canceled"
        }

        # Do not include completed actions
        # in overdue, due today, or upcoming
        if status in completed_statuses:
            continue

        # Skip actions without a valid deadline
        if due_date is None:
            continue

        # Overdue
        if due_date < selected_date:
            overdue_actions.append(action)

        # Due today
        elif due_date == selected_date:
            due_today_actions.append(action)

        # Upcoming
        elif due_date > selected_date:
            upcoming_actions.append(action)

    # Combine all actions
    all_actions = (
        my_actions
        + waiting_on_others
        + unclear_ownership
    )

    return {
        # ---------------------------------
        # MAIN CLASSIFICATION KEYS
        # ---------------------------------

        "all_actions": all_actions,
        "my_actions": my_actions,
        "waiting_on_others": waiting_on_others,
        "unclear_ownership": unclear_ownership,

        # ---------------------------------
        # COMPATIBILITY KEYS
        # ---------------------------------

        "waiting_actions": waiting_on_others,
        "unclear_actions": unclear_ownership,

        # ---------------------------------
        # DETAILED DEADLINE KEYS
        # ---------------------------------

        "overdue_actions": overdue_actions,
        "due_today_actions": due_today_actions,
        "upcoming_actions": upcoming_actions,

        # ---------------------------------
        # TEST COMPATIBILITY KEYS
        # ---------------------------------

        "overdue": overdue_actions,
        "due_today": due_today_actions,
        "upcoming": upcoming_actions
    }


def process_actions(
    actions,
    as_of_date=None,
    selected_date=None,
    my_name="Arjun"
):
    """
    Process actions using either:

    - as_of_date
    - selected_date

    as_of_date takes priority if both are provided.
    """

    # Use as_of_date if supplied
    if as_of_date is not None:
        selected_date = as_of_date

    # Use today's date if no date is supplied
    if selected_date is None:
        selected_date = date.today()

    # Convert to date object
    selected_date = convert_to_date(selected_date)

    if selected_date is None:
        selected_date = date.today()

    return classify_actions(
        actions=actions,
        selected_date=selected_date,
        my_name=my_name
    )