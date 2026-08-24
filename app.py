import time
import pandas as pd
import streamlit as st

from modules.eda_engine import eda_insights
from modules.session_stored import save_completed_analysis
from modules.prompt_builder import assemble_prompt
from modules.llm_service import fetch_llm_response
from modules.output_parser import parse_response
from modules.evaluation_handler import save_user_evaluation

st.set_page_config(page_title="Data Analysis BI HAIC App", layout="wide")

st.title("Data Analysis BI HAIC App")
st.write("An app to demonstrate and document the use of AI in Business Intelligence through data analysis.")


def reset_analysis_state():
    """Clear results and evaluation widgets from the previous analysis."""
    st.session_state["session_id"] = None
    st.session_state["generation_id"] = None
    st.session_state["parsed_insights"] = None
    st.session_state["eda_final"] = None
    st.session_state["generation_status"] = "idle"
    st.session_state["evaluation_started"] = False
    st.session_state["current_insight_index"] = 0
    st.session_state["insight_start_times"] = {}
    st.session_state["evaluated_insight_ids"] = set()


    for key in list(st.session_state.keys()):
        if key.startswith(("action_", "edit_text_")):
            del st.session_state[key]


# Ηere we initialize session state variables to prevent re-running the LLM on every button click
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "generation_id" not in st.session_state:
    st.session_state["generation_id"] = None
if "parsed_insights" not in st.session_state:
    st.session_state["parsed_insights"] = None
if "eda_final" not in st.session_state:
    st.session_state["eda_final"] = None
if "generation_status" not in st.session_state:
    st.session_state["generation_status"] = "idle"
if "evaluation_started" not in st.session_state:
    st.session_state["evaluation_started"] = False
if "current_insight_index" not in st.session_state:
    st.session_state["current_insight_index"] = 0
if "insight_start_times" not in st.session_state:
    st.session_state["insight_start_times"] = {}
if "evaluated_insight_ids" not in st.session_state:
    st.session_state["evaluated_insight_ids"] = set()

# SECTION 1: DATA UPLOAD & CONTEXT
st.header("1. Upload Data & Define Context")

uploaded_file = st.file_uploader(
    "Upload Dataset (CSV)",
    type="csv",
    key="uploaded_csv",
    on_change=reset_analysis_state
)

with st.form("context_form"):
    participant_id = st.text_input("Participant ID (For User Study)", placeholder="Example: P001")
    domain = st.selectbox("Domain", ["Technology & Software", "Healthcare & Life Sciences", "Finance & Banking", "E-Commerce & Retail", "Education & EdTech", "Media & Marketing", "Supply Chain & Logistics", "Other"])
    audience = st.selectbox("Target Audience", ["Individual Consumers (B2C)", "Small & Medium Businesses (SMBs)", "Enterprise Companies (B2B)", "Startups & Founders", "Freelancers & Solopreneurs", "Executives & Decision Makers", "Students & Educators", "Government & Non-Profits (B2G)"])
    goal = st.text_input("What are you looking for?", placeholder="Example: Identify the most important patterns, issues, or areas that need attention in this dataset.")
    
    submit_button = st.form_submit_button("Generate Insights")

# THE CORE PIPELINE
if submit_button:
    # A new generation attempt must never reuse the previous session or insights.
    reset_analysis_state()
    st.session_state["generation_status"] = "running"

    validation_errors = []

    if uploaded_file is None:
        validation_errors.append("Please upload a CSV dataset.")
    if not participant_id.strip():
        validation_errors.append("Please enter your Participant ID.")
    if not goal.strip():
        validation_errors.append("Please describe what you want to investigate.")

    if validation_errors:
        st.session_state["generation_status"] = "error"
        for error in validation_errors:
            st.error(error)
    else:
         try:
            df = pd.read_csv(uploaded_file)

            if df.empty or len(df.columns) == 0:
                raise ValueError("The uploaded CSV contains no data rows.")

        except pd.errors.EmptyDataError:
            reset_analysis_state()
            st.session_state["generation_status"] = "error"
            st.error("The uploaded CSV is empty.")
        except pd.errors.ParserError:
            reset_analysis_state()
            st.session_state["generation_status"] = "error"
            st.error("The uploaded CSV could not be parsed.")
        except UnicodeDecodeError:
            reset_analysis_state()
            st.session_state["generation_status"] = "error"
            st.error("The uploaded CSV uses an unsupported text encoding.")
        except ValueError as error:
            reset_analysis_state()
            st.session_state["generation_status"] = "error"
            st.error(str(error))
        except Exception as error:
            reset_analysis_state()
            st.session_state["generation_status"] = "error"
            st.error(f"The uploaded CSV could not be read: {error}")
        else:
            st.success(
                f"Data loaded successfully! Extracted {len(df.columns)} columns."
            )

            # Build the complete result with temporary local variables. Nothing
            # is placed in session state until every stage has succeeded.
            try:
                with st.spinner("Running Exploratory Data Analysis..."):
                    candidate_eda = eda_insights(df)

                candidate_prompt = assemble_prompt(
                    domain,
                    audience,
                    goal.strip(),
                    candidate_eda
                )

                with st.spinner("Generating BI Insights via AI..."):
                    generation_started = time.perf_counter()
                    candidate_raw_response = fetch_llm_response(
                        candidate_prompt
                    )
                    candidate_generation_time_ms = int(
                        (time.perf_counter() - generation_started) * 1000
                    )
                    candidate_insights = parse_response(
                        candidate_raw_response
                    )

                storage_result = save_completed_analysis(
                    participant_id=participant_id.strip(),
                    dataset_name=uploaded_file.name,
                    domain=domain,
                    audience=audience,
                    goal=goal.strip(),
                    eda_package=candidate_eda,
                    insights=candidate_insights,
                    generation_time_ms=candidate_generation_time_ms,
                )

                for insight in candidate_insights:
                    insight_number = insight["insight_id"]
                    insight["database_insight_id"] = storage_result[
                        "insight_ids"
                    ][insight_number]

                # Commit the successful generation to session state as one unit.
                st.session_state["session_id"] = storage_result["session_id"]
                st.session_state["generation_id"] = storage_result[
                    "generation_id"
                ]
                st.session_state["eda_final"] = candidate_eda
                st.session_state["parsed_insights"] = candidate_insights
                st.session_state["generation_status"] = "success"
                st.session_state["evaluation_started"] = False
                st.session_state["current_insight_index"] = 0
                st.session_state["insight_start_times"] = {}
                st.session_state["evaluated_insight_ids"] = set()

                st.info(
                    "Context and analysis saved to the database. "
                    f"Session ID: {storage_result['session_id']}"
                )

            except Exception as error:
                reset_analysis_state()
                st.session_state["generation_status"] = "error"
                st.error(f"The analysis could not be completed: {error}")

# --- SECTION 2: INSIGHTS DASHBOARD ---
generation_is_ready = (
    st.session_state.get("generation_status") == "success"
    and st.session_state.get("session_id") is not None
    and st.session_state.get("generation_id") is not None
    and bool(st.session_state.get("parsed_insights"))
)

if generation_is_ready:
    st.divider()
    st.header("2. Insights Dashboard")
    st.subheader("Evaluation instructions")
    st.write(
        "Three insights will be shown one at a time. Review each insight "
        "as soon as it appears and submit the response that best represents "
        "your initial assessment. Avoid leaving the page while evaluating. "
        "After submission, the next insight will appear. You cannot return "
        "to a previously submitted insight."
    )
    st.info(
        "Decision time is measured from when each insight appears until you "
        "select Submit Evaluation. If you choose Edit, the measurement also "
        "includes the time required to revise the narrative."
    )
    st.markdown(
        """
- **Accept:** The insight is accurate, relevant to your goal, and clearly written without requiring changes.
- **Edit:** The central insight is useful, but its wording, interpretation, or factual content needs correction.
- **Reject:** The insight is unsupported, irrelevant to your goal, or cannot be corrected without replacing its main meaning.
        """
    )

    action_mapping = {"Accept": 1, "Reject": 2, "Edit": 3}
    insights = st.session_state["parsed_insights"]
    total_insights = len(insights)

    if not st.session_state["evaluation_started"]:
        if st.button("Begin Evaluation", type="primary"):
            st.session_state["evaluation_started"] = True
            st.session_state["current_insight_index"] = 0
            st.session_state["insight_start_times"] = {}
            st.rerun()
    else:
        current_index = st.session_state["current_insight_index"]

        if current_index >= total_insights:
            st.progress(1.0)
            st.success(
                "Evaluation completed. All three insights have been "
                "submitted successfully."
            )
        else:
            insight = insights[current_index]
            insight_number = insight["insight_id"]
            database_insight_id = insight["database_insight_id"]

            st.progress(current_index / total_insights)
            st.caption(
                f"Insight {current_index + 1} of {total_insights} "
                f"({current_index} completed)"
            )

            st.session_state["insight_start_times"].setdefault(
                database_insight_id,
                time.perf_counter(),
            )

            with st.expander(
                f"Insight {insight_number}: {insight['title']}",
                expanded=True,
            ):
                st.write(f"**Type:** {insight['type']}")
                st.write(f"**Narrative:** {insight['narrative']}")

                with st.form(key=f"eval_form_{database_insight_id}"):
                    action_ui = st.radio(
                        "Choose an action:",
                        ["Accept", "Reject", "Edit"],
                        index=None,
                        key=f"action_{database_insight_id}",
                    )

                    edited_text = st.text_area(
                        "If editing, modify the narrative below:",
                        value=insight["narrative"],
                        key=f"edit_text_{database_insight_id}",
                    )

                    submit_eval = st.form_submit_button(
                        "Submit Evaluation"
                    )

                    if submit_eval:
                        if action_ui is None:
                            st.error(
                                "Please choose Accept, Reject, or Edit."
                            )
                        else:
                            final_edit = (
                                edited_text
                                if action_ui == "Edit"
                                else None
                            )

                            if (
                                action_ui == "Edit"
                                and not final_edit.strip()
                            ):
                                st.error(
                                    "Please provide edited text before "
                                    "submitting."
                                )
                            else:
                                decision_time_ms = int(
                                    (
                                        time.perf_counter()
                                        - st.session_state[
                                            "insight_start_times"
                                        ][database_insight_id]
                                    )
                                    * 1000
                                )

                                success = save_user_evaluation(
                                    insight_id=database_insight_id,
                                    user_action_id=action_mapping[action_ui],
                                    edited_text=final_edit,
                                    decision_time_ms=decision_time_ms,
                                )

                                if success:
                                    evaluated_ids = set(
                                        st.session_state[
                                            "evaluated_insight_ids"
                                        ]
                                    )
                                    evaluated_ids.add(database_insight_id)
                                    st.session_state[
                                        "evaluated_insight_ids"
                                    ] = evaluated_ids
                                    st.session_state[
                                        "current_insight_index"
                                    ] = current_index + 1
                                    st.rerun()
                                else:
                                    st.error(
                                        "This insight could not be "
                                        "evaluated. It may already have a "
                                        "submitted evaluation."
                                    )
