import streamlit as st
import requests
import json

def send_message(prompts):
    api_url = "https://api.anthropic.com/v1/complete"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": st.secrets["API_KEY"]
    }

    conversation = "\n\n".join([f'{item["role"]}: {item["content"]}' for item in prompts]) + "\n\nAssistant:"

    body = {
        "prompt": conversation,
        "model": "claude-v1.3-100k",
        "max_tokens_to_sample": 1000,
        "stop_sequences": ["\n\nHuman:"]
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(body))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"Error: {err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")

def display_chat():
    for prompt in reversed(st.session_state.prompts):
        if prompt['role'] == 'Human':
            st.markdown(f"**You**: {prompt['content']}")
        else:  # prompt['role'] == 'Assistant'
            st.markdown(f"**Claude**: {prompt['content']}")

def send_chat(user_message):
    st.session_state.prompts.append({
        "role": "Human",
        "content": user_message
    })

    with st.spinner('Waiting for Claude...'):
        result = send_message(st.session_state.prompts)

        if result:
            st.session_state.prompts.append({
                "role": "Assistant",
                "content": result['completion']
            })

            st.experimental_rerun()

def chat_with_claude():
    with st.container():
        st.title("Chat with Claude")
        st.write("Welcome to our chat app!")

    if "prompts" not in st.session_state:
        with open("langchaindocumentation.txt", 'r') as file:
            langchain_doc = file.read().replace('\n', '')
        st.session_state.prompts = [{"role": "Assistant", "content": "You are a Langchain expert coding assistant"}, {"role": "Human", "content": langchain_doc}]

    with st.container():
        display_chat()

    with st.container():
        with st.form(key='message_form'):
            user_message = st.text_input("You: ", key=f"user_input_{len(st.session_state.prompts)}")
            submit_button = st.form_submit_button(label='Send')

            if submit_button and user_message:
                send_chat(user_message)

    with st.container():
        if st.button('Restart'):
            st.session_state.prompts = []
            st.experimental_rerun()

chat_with_claude()
