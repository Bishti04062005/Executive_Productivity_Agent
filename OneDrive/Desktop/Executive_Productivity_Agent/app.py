import json
from pathlib import Path
from datetime import date

import streamlit as st

from models import Action
from processor import process_actions


# =====================================================
# PROJECT PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
SAMPLE_INPUTS_PATH = DATA_DIR / "sample_inputs.json"
OFFLINE_ACTIONS_PATH = DATA_DIR / "offline_actions.json"


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Executive Productivity Agent",
    page_icon="🤖",
    layout="wide"
)


# =====================================================
# PAGE HEADER
# =====================================================

st.title("🤖 Executive Productivity Agent")
st.write(
    "Extract commitments, identify ownership, "
    "and track deadlines from business communications."
)


# =====================================================
# OFFLINE DEMO DATA
# =====================================================

def create_offline_actions():
    """
    Create sample actions for Offline Demo Mode.
    """

    return [
        Action(
            id="OFFLINE-001",
            description="Send updated vendor list to Raghav",
            owner="Arjun",
            owner_type="self",
            status="open",
            due_date="2026-09-23",
            waiting_on=[],
            people=["Arjun", "Raghav"],
            source_id="EMAIL-VENDOR-004",
            evidence="Arjun promised to send the updated vendor list.",
            uncertainty="low"
        ),

        Action(
            id="OFFLINE-002",
            description="Confirm Meridian Logistics call time",
            owner="Arjun",
            owner_type="self",
            status="completed",
            due_date="2026-09-23 15:00",
            waiting_on=[],
            people=["Arjun"],
            source_id="EMAIL-MERIDIAN-005",
            evidence="Arjun needs to confirm the call time.",
            uncertainty="low"
        ),

        Action(
            id="OFFLINE-003",
            description="Prepare Q3 campaign deck for review",
            owner="Neha",
            owner_type="other",
            status="completed",
            due_date="2026-09-24 09:30",
            waiting_on=["Neha"],
            people=["Neha", "Arjun"],
            source_id="EMAIL-CAMPAIGN-005",
            evidence="Neha confirmed the campaign deck review.",
            uncertainty="low"
        ),

        Action(
            id="OFFLINE-004",
            description="Prepare and send July expense report",
            owner="Divya",
            owner_type="other",
            status="completed",
            due_date="2026-09-23",
            waiting_on=["Divya"],
            people=["Divya"],
            source_id="EMAIL-EXPENSE-004",
            evidence="Divya is responsible for the expense report.",
            uncertainty="low"
        ),

        Action(
            id="OFFLINE-005",
            description="Determine who will sign off Mumbai office lease renewal",
            owner="",
            owner_type="unclear",
            status="unclear",
            due_date="2026-09-25",
            waiting_on=[],
            people=["Facilities", "Raghav", "Divya"],
            source_id="EMAIL-LEASE-005",
            evidence="The authorized sign-off owner has not been confirmed.",
            uncertainty="high"
        )
    ]


# =====================================================
# JSON FILE FUNCTIONS
# =====================================================

def load_json_file(file_path):
    """
    Load JSON data from a file.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_offline_actions():
    """
    Save offline actions to offline_actions.json.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    actions = create_offline_actions()

    action_data = []

    for action in actions:
        if hasattr(action, "model_dump"):
            action_data.append(action.model_dump())
        else:
            action_data.append(action.dict())

    with open(
        OFFLINE_ACTIONS_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            action_data,
            file,
            indent=4
        )


# =====================================================
# ACTION CONVERSION
# =====================================================

def convert_to_actions(data):
    """
    Convert dictionaries into Action objects.
    """

    if isinstance(data, dict):
        if "actions" in data:
            data = data["actions"]
        else:
            data = [data]

    if not isinstance(data, list):
        return []

    actions = []

    for item in data:
        try:
            actions.append(Action(**item))
        except Exception as error:
            st.warning(
                f"Skipped invalid action: {error}"
            )

    return actions


# =====================================================
# OPTIONAL AI EXTRACTION
# =====================================================

def run_ai_extraction(input_data):
    """
    Run the extractor module.

    This function supports common extractor function names.
    """

    try:
        from extractor import extract_actions

        return extract_actions(input_data)

    except ImportError:
        try:
            from extractor import extract_commitments

            return extract_commitments(input_data)

        except ImportError:
            raise ImportError(
                "No supported extraction function was found "
                "in extractor.py."
            )


# =====================================================
# LOAD OFFLINE DATA
# =====================================================

def load_offline_demo():
    """
    Load offline actions.

    If offline_actions.json exists, use it.
    Otherwise, create built-in demo actions.
    """

    try:
        if OFFLINE_ACTIONS_PATH.exists():
            data = load_json_file(
                OFFLINE_ACTIONS_PATH
            )

            actions = convert_to_actions(data)

            if actions:
                return actions

    except Exception:
        pass

    return create_offline_actions()


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("⚙️ Settings")

my_name = st.sidebar.text_input(
    "Your name",
    value="Arjun"
)

selected_date = st.sidebar.date_input(
    "As-of date",
    value=date(2026, 9, 21)
)

mode = st.sidebar.radio(
    "Select mode",
    [
        "Offline Demo Mode",
        "AI Extraction Mode"
    ]
)


# =====================================================
# LOAD ACTIONS
# =====================================================

actions = []
extraction_error = None

if mode == "Offline Demo Mode":

    actions = load_offline_demo()

    st.sidebar.success(
        "Offline Demo Mode is active."
    )

else:

    st.subheader("📂 AI Input")

    st.write(
        "The application will load "
        "`data/sample_inputs.json`."
    )

    if st.button("Run AI Extraction"):

        try:
            input_data = load_json_file(
                SAMPLE_INPUTS_PATH
            )

            with st.spinner(
                "Extracting actions using AI..."
            ):
                extracted_data = run_ai_extraction(
                    input_data
                )

            actions = convert_to_actions(
                extracted_data
            )

            if actions:
                st.session_state["actions"] = actions

                st.success(
                    "AI extraction completed successfully."
                )
            else:
                st.warning(
                    "AI extraction returned no actions."
                )

        except Exception as error:
            extraction_error = str(error)

            st.error(
                "AI extraction failed. "
                "Try Offline Demo Mode."
            )

            st.code(
                extraction_error
            )

    actions = st.session_state.get(
        "actions",
        []
    )


# =====================================================
# FALLBACK WHEN AI EXTRACTION FAILS
# =====================================================

if mode == "AI Extraction Mode" and not actions:

    st.info(
        "No extracted actions available. "
        "Switch to Offline Demo Mode to test the dashboard."
    )

    st.stop()


# =====================================================
# PROCESS ACTIONS
# =====================================================

if actions:

    result = process_actions(
        actions=actions,
        as_of_date=selected_date,
        my_name=my_name
    )

else:

    result = {
        "all_actions": [],
        "my_actions": [],
        "waiting_on_others": [],
        "unclear_ownership": [],
        "overdue": [],
        "due_today": [],
        "upcoming": []
    }


# =====================================================
# DASHBOARD METRICS
# =====================================================

st.subheader("📊 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Actions",
        len(result["all_actions"])
    )

with col2:
    st.metric(
        "My Actions",
        len(result["my_actions"])
    )

with col3:
    st.metric(
        "Waiting on Others",
        len(result["waiting_on_others"])
    )

with col4:
    st.metric(
        "Unclear Ownership",
        len(result["unclear_ownership"])
    )


col5, col6, col7 = st.columns(3)

with col5:
    st.metric(
        "Overdue",
        len(result["overdue"])
    )

with col6:
    st.metric(
        "Due Today",
        len(result["due_today"])
    )

with col7:
    st.metric(
        "Upcoming",
        len(result["upcoming"])
    )


# =====================================================
# ACTION DISPLAY FUNCTION
# =====================================================

def display_actions(title, action_list):
    """
    Display actions in expandable sections.
    """

    st.subheader(title)

    if not action_list:
        st.info("No actions in this category.")
        return

    for index, action in enumerate(action_list, start=1):

        if hasattr(action, "model_dump"):
            data = action.model_dump()
        else:
            data = action.dict()

        description = data.get(
            "description",
            "No description"
        )

        owner = data.get(
            "owner",
            "Unclear"
        )

        status = data.get(
            "status",
            "Unknown"
        )

        due_date = data.get(
            "due_date",
            "Not specified"
        )

        source_id = data.get(
            "source_id",
            "Unknown"
        )

        evidence = data.get(
            "evidence",
            ""
        )

        with st.expander(
            f"{index}. {description}"
        ):

            st.write(
                f"**Owner:** {owner or 'Unclear'}"
            )

            st.write(
                f"**Status:** {status}"
            )

            st.write(
                f"**Due Date:** {due_date or 'Not specified'}"
            )

            st.write(
                f"**Source:** {source_id}"
            )

            if evidence:
                st.write(
                    f"**Evidence:** {evidence}"
                )


# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "My Actions",
        "Waiting on Others",
        "Unclear Ownership",
        "Deadlines",
        "All Actions"
    ]
)


with tab1:
    display_actions(
        "👤 My Actions",
        result["my_actions"]
    )


with tab2:
    display_actions(
        "⏳ Waiting on Others",
        result["waiting_on_others"]
    )


with tab3:
    display_actions(
        "❓ Unclear Ownership",
        result["unclear_ownership"]
    )


with tab4:

    display_actions(
        "🔴 Overdue Actions",
        result["overdue"]
    )

    display_actions(
        "🟡 Due Today",
        result["due_today"]
    )

    display_actions(
        "🟢 Upcoming Actions",
        result["upcoming"]
    )


with tab5:
    display_actions(
        "📋 All Actions",
        result["all_actions"]
    )


# =====================================================
# DOWNLOAD RESULTS
# =====================================================

st.subheader("📥 Export Results")


def serialize_actions(action_list):
    """
    Convert Action objects into JSON-compatible data.
    """

    output = []

    for action in action_list:

        if hasattr(action, "model_dump"):
            output.append(action.model_dump())
        else:
            output.append(action.dict())

    return output


export_data = {
    "as_of_date": str(selected_date),
    "my_name": my_name,
    "all_actions": serialize_actions(
        result["all_actions"]
    ),
    "my_actions": serialize_actions(
        result["my_actions"]
    ),
    "waiting_on_others": serialize_actions(
        result["waiting_on_others"]
    ),
    "unclear_ownership": serialize_actions(
        result["unclear_ownership"]
    ),
    "overdue": serialize_actions(
        result["overdue"]
    ),
    "due_today": serialize_actions(
        result["due_today"]
    ),
    "upcoming": serialize_actions(
        result["upcoming"]
    )
}


st.download_button(
    label="Download Action Report",
    data=json.dumps(
        export_data,
        indent=4
    ),
    file_name="executive_productivity_report.json",
    mime="application/json"
)


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "Executive Productivity Agent | "
    "Offline Demo and AI Extraction"
)