import streamlit as st
from google.api_core import retry
from order_bot import OrderBot


@retry.Retry(initial=30)
def send_message(conversation, message):
    return conversation.send_message(message)


def response_generator(conversation, message):
    response = send_message(conversation, message)
    return response.text


st.title("Chè hoa 🌺")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if "bot" not in st.session_state:
    st.session_state.bot = OrderBot()
    st.session_state.conversation = st.session_state.bot.start_chat()

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = response_generator(st.session_state.conversation, prompt)
        st.write(response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response})


# Display the order on the sidebar
with st.sidebar:
    order = st.session_state.bot.get_order()
    for idx, (item, modifiers) in enumerate(order):
        readableModifiers = ", ".join(modifiers)
        if readableModifiers:
            item += f' ({readableModifiers})'

        st.write(str(idx + 1) + '. ' + item)
