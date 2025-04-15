import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from PIL import Image

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Customer Support Dashboard", page_icon="📊", layout="wide")

@st.cache_data
def load_tickets():
    try:
        response = requests.get(f"{API_URL}/tickets")
        response.raise_for_status()
        tickets = response.json()

        if isinstance(tickets, dict) and 'error' in tickets:
            st.warning("⚠️ No tickets found.")
            return pd.DataFrame()
        return pd.DataFrame(tickets)

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to load tickets: {e}")
        return pd.DataFrame()

def ask_ai_with_data(question, df):
    try:
        keywords = ["customer", "ticket", "status", "priority", "created", "open", "closed"]
        df_response = ""

        if any(keyword in question.lower() for keyword in keywords):
            if "customer" in question.lower():
                df_response = df[['customer_id', 'name', 'email']].to_string(index=False)
            elif "ticket" in question.lower() or "status" in question.lower():
                df_response = df[['ticket_id', 'subject', 'status', 'priority']].to_string(index=False)

            question += f"\n\nHere is the relevant data:\n{df_response}"

        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question}
        )
        response.raise_for_status()
        data = response.json()

        ai_response = data.get("response", "No AI response received.")
        
        final_response = (
            f"**🛠️ AI Insight:**\n{ai_response}\n\n**📊 Data Insight:**\n{df_response}"
            if df_response else ai_response
        )

        return final_response

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to get AI response: {e}")
        return "Failed to connect to AI."

def create_ticket(name, email, subject, description, priority):
    try:
        response = requests.post(
            f"{API_URL}/create_ticket",
            json={
                "name": name,
                "email": email,
                "subject": subject,
                "description": description,
                "priority": priority,
                "status": "open"
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to create ticket: {e}")
        return None

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/888/888879.png", width=100)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a Page", ["Dashboard", "Create Ticket", "AI Insights", "Analytics"])

if page == "Dashboard":
    st.title("🛠️ Customer Support Ticket Manager with AI")

    st.subheader("📌 Support Tickets")
    tickets = load_tickets()

    if not tickets.empty:
        st.dataframe(tickets.style.format(
            {
                "created_at": lambda x: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S')
            }
        ))
    else:
        st.warning("⚠️ No tickets to display.")

elif page == "Create Ticket":
    st.title("🆕 Create New Support Ticket")

    with st.form("ticket_creation_form"):
        st.subheader("📝 Ticket Details")

        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        subject = st.text_input("Subject")
        description = st.text_area("Description", height=200)
        priority = st.selectbox("Priority", ["low", "medium", "high"])

        submit_button = st.form_submit_button("Create Ticket")

        if submit_button:
 
            if not all([name, email, subject, description]):
                st.error("⚠️ Please fill in all required fields.")
            else:
                with st.spinner("Creating ticket..."):
                    result = create_ticket(name, email, subject, description, priority)
                    
                    if result:
                        st.success("✅ Ticket created successfully!")
                        st.json(result)
                    else:
                        st.error("❌ Failed to create ticket. Please try again.")

elif page == "AI Insights":
    st.title("🤖 AI-Powered Support Insights")

    question = st.text_input("Enter your query:")
    
    if st.button("Get AI Insights"):
        if question:
            with st.spinner("Fetching AI insights..."):
                response = ask_ai_with_data(question, load_tickets())
                st.success("✅ AI Response:")
                st.write(response)
        else:
            st.warning("⚠️ Please enter a question.")

elif page == "Analytics":
    st.title("📊 Analytics & Data Visualization")

    tickets = load_tickets()

    if not tickets.empty:
        st.subheader("📌 Ticket Status Distribution")
        status_count = tickets["status"].value_counts().reset_index()
        status_count.columns = ['Status', 'Count']

        status_chart = px.bar(
            status_count,
            x="Status",
            y="Count",
            title="Tickets by Status",
            color="Status",
            color_discrete_map={"open": "green", "in-progress": "orange", "closed": "red"},
            template="plotly_dark"
        )
        st.plotly_chart(status_chart, use_container_width=True)

        st.subheader("🔥 Ticket Priority Distribution")
        priority_count = tickets["priority"].value_counts().reset_index()
        priority_count.columns = ['Priority', 'Count']

        priority_chart = px.pie(
            priority_count,
            names="Priority",
            values="Count",
            title="Priority Breakdown",
            color="Priority",
            color_discrete_map={"low": "green", "medium": "blue", "high": "red"},
            template="plotly_dark"
        )
        st.plotly_chart(priority_chart, use_container_width=True)

        st.subheader("📅 Tickets Created Over Time")
        tickets['created_at'] = pd.to_datetime(tickets['created_at'])
        tickets_over_time = tickets.groupby(tickets['created_at'].dt.date).size().reset_index(name='Count')

        time_chart = px.line(
            tickets_over_time,
            x='created_at',
            y='Count',
            title='Ticket Creation Trend',
            markers=True,
            template="plotly_dark"
        )
        st.plotly_chart(time_chart, use_container_width=True)

    else:
        st.warning("⚠️ No tickets to display.")

st.sidebar.markdown("---")
st.sidebar.markdown("📊 **Customer Support Ticket Manager**")
st.sidebar.markdown("🔧 Powered by Flask, Streamlit, and Groq AI")