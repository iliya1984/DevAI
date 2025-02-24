from src.infra.di_module import Bootstrap
from src.inference.chatbots import CompletionRequest
import streamlit as st
import dotenv

dotenv.load_dotenv()

bootstrap = Bootstrap()
chat_client = bootstrap.container.chat_client()

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

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response from OpenAI
    with st.spinner("Thinking..."):
        response_text = ""
        #prompt = st.session_state.messages[0]
        chat_messages = st.session_state.messages
        with st.chat_message("assistant"):
            st.write_stream(chat_client.completion_stream(request=CompletionRequest(messages=chat_messages)))

            # Append the full response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})

