import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is set
if not API_KEY:
    st.error("⚠️ ERROR: GEMINI_API_KEY is not set in .env!")
    st.stop()

# Configure Google Gemini AI
client = genai.Client(api_key=API_KEY)

# AI Behavior Instructions
AI_INSTRUCTIONS = """You are a Solar Industry Expert AI Assistant. 
Provide accurate and professional information about:
- Solar Panel Technology
- Installation Processes
- Maintenance Requirements
- Cost & ROI Analysis
- Industry Regulations
- Market Trends

Only answer questions related to solar energy. If a question is not related to solar, politely refuse to answer."""

# List of Solar-Related Keywords
SOLAR_KEYWORDS = [
    "solar", "photovoltaic", "pv", "renewable energy", "sun",
    "solar panel", "net metering", "solar cell", "solar inverter",
    "solar energy", "solar power", "solar battery"
]

# Words that need context (like "it", "this", "that")
RELATED_WORDS = ["it", "this", "that", "they", "them", "these", "those"]

# Function to check if a question is solar-related
def is_solar_related(user_input, history):
    user_input_words = user_input.lower().split()
    if any(keyword in user_input_words for keyword in SOLAR_KEYWORDS):
        return True
    # If current input lacks a solar keyword, check previous context if available
    if history and any(word in user_input_words for word in RELATED_WORDS):
        previous_user_message = history[-1][0]
        return is_solar_related(previous_user_message, [])
    return False

# Function to call Google Gemini AI
def call_gemini(user_input, chat):
    try:
        response = chat.send_message(
            message=user_input,
            config=types.GenerateContentConfig(system_instruction=AI_INSTRUCTIONS)
        )
        return response.text
    except Exception as e:
        st.error(f"Error: {e}")
        return f"⚠️ Error: {e}"

# Streamlit UI setup
st.title("Solar AI Assistant")

# Initialize session state for chat history and chat object
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model='gemini-1.5-pro')

# Container for displaying chat history
chat_container = st.container()
if st.session_state.chat_history:
    for user_msg, model_msg in st.session_state.chat_history:
        chat_container.markdown(f"**User:** {user_msg}")
        chat_container.markdown(f"**AI:** {model_msg}")

# Input form for new chat messages
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask about solar technology...")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    if is_solar_related(user_input, st.session_state.chat_history):
        response = call_gemini(user_input, st.session_state.chat)
    else:
        response = "⚠️ Sorry, I can only answer questions related to solar energy."
    st.session_state.chat_history.append((user_input, response))
    st.rerun()

# Buttons for additional actions
col1, col2 = st.columns(2)

with col1:
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

with col2:
    if st.button("Check History"):
        st.subheader("🔍 Previous Chat History")
        if st.session_state.chat_history:
            for user_msg, model_msg in st.session_state.chat_history:
                with st.expander(f"User: {user_msg[:50]}..."):
                    st.markdown(f"**User:** {user_msg}")
                    st.markdown(f"**AI:** {model_msg}")
        else:
            st.info("No previous chat history available.")