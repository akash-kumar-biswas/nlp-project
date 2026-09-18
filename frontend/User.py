import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="User",
    page_icon="🎫",
    layout="centered"
)

st.markdown(
    """
    <style>
        [data-testid="stToolbar"] {
            visibility: hidden;
        }

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


st.title("E-Commerce Customer Support")

st.write(
    "Describe your problem and our system "
    "will route it to the appropriate support department."
)


with st.form("customer_form"):

    query = st.text_area(
        "Describe your problem",
        height=150,
        placeholder="Example: amar order ekhono pai nai..."
    )

    submitted = st.form_submit_button(
        "Submit Query",
        use_container_width=True
    )


if submitted:

    if not query.strip():

        st.warning("Please enter your problem.")

    else:

        try:

            response = requests.post(
                f"{API_URL}/tickets",
                json={"query": query},
                timeout=10
            )

            response.raise_for_status()

            ticket = response.json()

            st.success(f"Your problem has been routed to {ticket['subsystem']} Support.")

            st.subheader("Query Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Subsystem:**", ticket["subsystem"])

            with col2:
                st.write("**Priority:**", ticket["priority"])
                st.write("**Status:**", ticket["status"])

            st.caption(
                f"Ticket ID: {ticket['id']}"
            )

        except requests.RequestException:

            st.error(
                "Backend server is not available."
            )