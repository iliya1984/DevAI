from src.infra.inference_module import InferenceBootstrap
from src.inference.chatbots import CompletionRequest
import streamlit as st
import dotenv

dotenv.load_dotenv()

bootstrap = InferenceBootstrap()
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
        assistant_response = ""
        response_container = st.empty()

        chat_messages = st.session_state.messages
        completion = chat_client.completion_stream(request=CompletionRequest(messages=chat_messages))
        vector_search_result = completion.vector_search_result

        for chunk in completion.yield_chunks():
            assistant_response += chunk  # Collect chunks
            response_container.markdown(assistant_response)  # Update UI dynamically

            # Append the full response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

