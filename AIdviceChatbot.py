#Spencer Kasbohm
#Project: AIdvice

import streamlit as st
import os
import re
from openai import OpenAI 

# --- Configuration (Replace with your actual API key and potentially move to environment variables) ---
# For demonstration purposes, we'll use a placeholder for the API key.
# In a real application, you should load this from environment variables or Streamlit secrets.

#I hid my API key when uploading this for security reasons.
#If you would like to run this code, please replace "test_key" with your actual OpenAI API key.
OPENAI_API_KEY = os.getenv("test_key", "placeholder_key") 

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize OpenAI client. Please ensure your API key is correct. Error: {e}")
    st.stop() # Stop the app if API client cannot be initialized


# --- System Prompt Definition ---
SYSTEM_PROMPT = """
You are AIdvice, a supportive, non-clinical AI tool designed to offer general advice and helpful perspectives.
You are not a substitute for professional medical, legal, financial, or psychological advice.
Always encourage users to seek qualified professionals for specific, personal concerns.
Your responses should be empathetic, encouraging, and focus on general principles or thought-provoking questions rather than direct solutions for complex personal problems.
Maintain a positive and respectful tone.
"""

# --- Keywords for detecting serious questions ---
SERIOUS_KEYWORDS = [
    "depress", "anxiety", "crisis", "suicidal", "harm", "abuse", "legal issue",
    "medical problem", "emergency", "financial trouble", "therapy", "counseling",
    "addiction", "divorce", "loss", "grief", "trauma"
]

def is_serious_question(text):
    """
    Checks if the user's input contains keywords suggesting a need for professional advice.
    """
    text_lower = text.lower()
    for keyword in SERIOUS_KEYWORDS:
        # Use word boundaries to match whole words (e.g., "depress" but not "depressionist")
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            return True
    return False

# --- Chat Function (Now with actual OpenAI API call) ---
def get_ai_response(user_message, conversation_history):
    """
    This function makes an API call to OpenAI.
    It constructs the messages payload, including the system prompt and conversation history.
    """
    # First, check for serious questions and respond with a disclaimer
    if is_serious_question(user_message):
        return (
            "It sounds like you're dealing with something very significant. "
            "AIdvice is a general AI tool and cannot offer the specialized, "
            "personal guidance you might need for concerns of this nature. "
            "Please consider reaching out to a qualified human professional "
            "(like a therapist, doctor, lawyer, or financial advisor) "
            "who can provide expert, tailored advice and support. "
            "Remember, seeking professional help is a sign of strength, and you don't have to face this alone."
        )

    # Prepare messages for the OpenAI API call
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Add previous conversation history
    for msg in conversation_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    # Add the current user message
    messages.append({"role": "user", "content": user_message})

    try:
        # Make the actual API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # You can change this to "gpt-4", "gpt-4o", etc., depending on your needs and access
            messages=messages,
            temperature=0.7, # Controls randomness. Lower values are more deterministic.
            max_tokens=500 # Max tokens in the response
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while fetching a response from AIdvice: {e}. Please check your API key and network connection."


# --- Streamlit UI Setup ---
st.set_page_config(
    page_title="AIdvice: Your Supportive AI Companion",
    layout="centered",
    initial_sidebar_state="expanded" # Ensure sidebar is expanded by default
)

st.title("AIdvice")

# --- Disclaimer Popup Logic ---
# Initialize session state for disclaimer if not present
if 'disclaimer_shown' not in st.session_state:
    st.session_state.disclaimer_shown = False

# Show disclaimer if it hasn't been shown yet
if not st.session_state.disclaimer_shown:
    # Use st.empty() to create a placeholder for the popup that can be cleared
    disclaimer_placeholder = st.empty()
    with disclaimer_placeholder.container():
        st.warning("**Important Disclaimer**", icon="⚠️")
        st.write("This chatbot is for **Entertainment purposes only!** It is not meant to replace professional human advice (medical, legal, financial, or psychological). Always consult a qualified professional for personal concerns.")
        if st.button("I understand and accept"):
            st.session_state.disclaimer_shown = True
            st.rerun() # Rerun to clear the disclaimer and proceed with the app
    st.stop() # Stop further execution until disclaimer is acknowledged


# --- Welcome and About Section (Main Content Area) ---
st.markdown(
    """
    Welcome to AIdvice! This offers general advice and supportive perspectives.
    Please remember, this is a non-clinical AI tool and not a substitute for professional human advice.
    """
)

with st.expander("Learn more about AIdvice"):
    st.info(
        "AIdvice is a supportive, non-clinical AI tool designed to offer general advice and helpful perspectives. "
        "It is **not** a substitute for professional medical, legal, financial, or psychological advice. "
        "Always seek qualified professionals for specific, personal concerns. "
        "Your privacy is important: do not share sensitive personal information."
    )
    st.markdown("---")
    st.write("Developed using Streamlit and OpenAI's API")

# Initialize chat history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add an initial greeting from the AI
    st.session_state.messages.append({"role": "assistant", "content": "Hi! I'm AIdvice, ready to offer supportive perspectives. How can I help you today?"})

# --- Suggested Actions / Welcome Buttons (Now directly adding to chat) ---
st.subheader("Get Started with a Suggestion:")
col1, col2, col3 = st.columns(3)

# Function to handle suggested input
def handle_suggested_input(suggested_text):
    st.session_state.messages.append({"role": "user", "content": suggested_text})
    # To immediately get a response and update the chat, we re-run the app
    # This will trigger the main `if user_input:` block indirectly on the next run
    st.rerun()

with col1:
    if st.button("How can I stay motivated? 🤔"):
        handle_suggested_input("How can I stay motivated?")
with col2:
    if st.button("Tips for managing stress 😌"):
        handle_suggested_input("What are some tips for managing stress?")
with col3:
    if st.button("I need a new perspective on..."):
        handle_suggested_input("I need a new perspective on dealing with procrastination.")

# --- Main Chat Area ---
st.subheader("Start your conversation below:")
chat_container = st.container(height=400, border=True) # Fixed height for chat history

with chat_container:
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# --- User Input Field ---
# Removed 'value' parameter as it's not supported by st.chat_input
user_input = st.chat_input("ask away...", key="chat_input")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with chat_container: # Display in the chat container
        with st.chat_message("user"):
            st.write(user_input)

    # Get AI response (simulated or actual API call)
    with chat_container: # Display in the chat container
        with st.spinner("Thinking..."):
            # Prepare conversation history for the AI model
            # Ensure the structure matches what OpenAI expects: [{"role": "user", "content": "..."}]
            conversation_history_for_ai = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages # Pass all messages for context
                if msg["role"] != "system" # System prompt is added separately
            ]
            ai_response = get_ai_response(user_input, conversation_history_for_ai)
            st.write(ai_response)
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

# --- Recent Chat History Sidebar ---
with st.sidebar:
    st.header("Recent Conversation")
    if len(st.session_state.messages) > 1: # Check if there's more than just the initial greeting
        st.markdown("---")
        # Display a summary of the last few user-AI turns
        recent_turns = []
        # Iterate backwards to get recent messages, excluding initial assistant greeting if it's the only one
        start_index = len(st.session_state.messages) - 1
        # Only start from the most recent if there's actual conversation
        if st.session_state.messages[0]["role"] == "assistant" and len(st.session_state.messages) == 1:
            start_index = -1 # No actual conversation yet to show in history
        
        for i in range(start_index, -1, -1):
            message = st.session_state.messages[i]
            if message["role"] == "user":
                recent_turns.insert(0, f"👤: {message['content'][:50]}{'...' if len(message['content']) > 50 else ''}") # Truncate long messages
            elif message["role"] == "assistant" and i > 0 and st.session_state.messages[i-1]["role"] == "user":
                 # Only add assistant response if it immediately follows a user message
                 recent_turns.insert(0, f"🤖: {message['content'][:50]}{'...' if len(message['content']) > 50 else ''}")
            if len(recent_turns) >= 6: # Show last 3 user/assistant pairs max (6 entries total)
                break
        for turn in recent_turns:
            st.markdown(turn)
        if len(st.session_state.messages) > 6: # Indicate more history if available
            st.markdown("...")
    else:
        st.info("Start chatting to see your conversation history here!")

