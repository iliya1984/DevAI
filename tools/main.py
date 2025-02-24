import os

import streamlit as st
from ollama import chat, Client, ResponseError
import dotenv

dotenv.load_dotenv()


ollama_host = os.environ['OLLAMA_HOST']
ollama_version = os.environ['OLLAMA_VERSION']
client = Client(
    host=ollama_host
)

# Streamlit UI
st.set_page_config(page_title="Chatbot", page_icon="🤖")
st.title("🤖 AI Chatbot")
st.write("Ask me anything!")

# Store chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message...")

def response_generator(user_prompt: dict):
    stream = client.chat(model=ollama_version, messages=[user_prompt], stream=True)

    for chunk in stream:
        # Extract text from the chunk
        chunk_text = chunk['message']['content']
        yield chunk_text

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response from OpenAI
    with st.spinner("Thinking..."):
        response_text = ""
        prompt = st.session_state.messages[0]
        with st.chat_message("assistant"):
            st.write_stream(response_generator(user_prompt=prompt))

            # Append the full response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})

