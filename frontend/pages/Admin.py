import pandas as pd
import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"
PRIORITY_ORDER = {"Immediate": 0, "Critical": 1, "High": 2, "Medium": 3, "Low": 4}

st.set_page_config(page_title="Admin", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span,
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a p {
            font-size: 18px !important;
        }

        .stApp p,
        .stApp label,
        .stApp input,
        .stApp textarea,
        .stApp button,
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stCaptionContainer"] {
            font-size: 18px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Admin")

try:
    response = requests.get(f"{API_URL}/tickets", timeout=10)
    response.raise_for_status()
    tickets = response.json()
except requests.RequestException:
    st.error("Could not connect to backend.")
    st.stop()

if not tickets:
    st.info("No tickets available.")
    st.stop()

df = pd.DataFrame(tickets)

metric_columns = st.columns(4)
metric_columns[0].metric("Total Tickets", len(df))
metric_columns[1].metric("Pending", int((df["status"] == "Pending").sum()))
metric_columns[2].metric("High Priority", int((df["priority"] == "High").sum()))
metric_columns[3].metric("Immediate", int((df["priority"] == "Immediate").sum()))

st.divider()

filter_columns = st.columns(4)
subsystems = ["All"] + sorted(df["subsystem"].dropna().unique().tolist())

selected_subsystem = filter_columns[0].selectbox("Subsystem Queue", subsystems)
selected_priority = filter_columns[1].selectbox(
    "Priority", ["All", "Low", "Medium", "High", "Critical", "Immediate"]
)
selected_status = filter_columns[2].selectbox("Status", ["All", "Pending", "Resolved"])
sort_option = filter_columns[3].selectbox(
    "Sort By", ["Newest First", "Oldest First", "Priority"]
)

filtered = df.copy()
if selected_subsystem != "All":
    filtered = filtered[filtered["subsystem"] == selected_subsystem]
if selected_priority != "All":
    filtered = filtered[filtered["priority"] == selected_priority]
if selected_status != "All":
    filtered = filtered[filtered["status"] == selected_status]

if sort_option == "Priority":
    filtered = filtered.assign(_priority_order=filtered["priority"].map(PRIORITY_ORDER))
    filtered = filtered.sort_values("_priority_order")
else:
    filtered = filtered.sort_values(
        "created_at", ascending=sort_option == "Oldest First"
    )

st.subheader(f"{selected_subsystem} Tickets")
display_columns = ["id", "query", "subsystem", "priority", "status", "created_at"]
st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True)

st.subheader("Update Ticket Status")
ticket_ids = filtered["id"].tolist()
if ticket_ids:
    selected_ticket_id = st.selectbox("Ticket ID", ticket_ids)
    new_status = st.selectbox("New Status", ["Pending", "Resolved"])

    if st.button("Update Status"):
        try:
            update_response = requests.patch(
                f"{API_URL}/tickets/{selected_ticket_id}/status",
                json={"status": new_status},
                timeout=10,
            )
            update_response.raise_for_status()
            st.success("Ticket status updated.")
            st.rerun()
        except requests.RequestException:
            st.error("Could not update ticket status.")
else:
    st.info("No tickets match the selected filters.")