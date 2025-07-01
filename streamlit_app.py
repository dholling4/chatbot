import streamlit as st
import requests
import json
import time

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Hugging Face's free models to generate responses. "
    "No API key required! The chatbot uses Microsoft's DialoGPT model for conversational AI."
)

def query_huggingface_model(messages):
    """Query Hugging Face's free inference API"""
    # Use Microsoft's DialoGPT model which is good for conversations
    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
    
    # Convert messages to a single conversation string
    conversation = ""
    for msg in messages:
        if msg["role"] == "user":
            conversation += f"User: {msg['content']}\n"
        else:
            conversation += f"Bot: {msg['content']}\n"
    
    # Add the latest user input prompt
    conversation += "Bot:"
    
    payload = {
        "inputs": conversation,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Clean up the response
                if generated_text.startswith("Bot:"):
                    generated_text = generated_text[4:].strip()
                return generated_text.strip() if generated_text.strip() else "I'm sorry, I couldn't generate a response. Please try again."
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
        elif response.status_code == 503:
            return "The model is currently loading. Please wait a moment and try again."
        else:
            return f"Sorry, there was an error (status code: {response.status_code}). Please try again."
    except Exception as e:
        return f"Sorry, there was an error connecting to the service: {str(e)}"

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the Hugging Face API.
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_huggingface_model(st.session_state.messages)
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
