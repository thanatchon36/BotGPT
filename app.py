import streamlit as st
from streamlit_feedback import streamlit_feedback
import time
import datetime
import pandas as pd

with st.sidebar:
    clear_session_click = st.button("Clear session")
    if clear_session_click:
        st.session_state.messages = []

with st.chat_message("Assistant"):
    # Create an empty message placeholder
    mp = st.empty()
    # Create a container for the message
    sl = mp.container()
    # Add a Markdown message describing the app
    sl.markdown("""
        BotGPT
    """)

    existing_df = pd.DataFrame()

mp = st.empty()

# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check if there's a user input prompt
if prompt := st.chat_input(placeholder="Which has a better follower growth rate in 2023, LinkedIn or Twitter?"):
    # Display user input in the chat
    st.chat_message("user").write(prompt)

    # Add user message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Create a chat message for the assistant
    with st.chat_message("assistant"):
        full_response = ""  # Initialize an empty string to store the full response
        message_placeholder = st.empty()  # Create an empty placeholder for displaying messages
        response = """
text from model
"""

        # Simulate streaming the response with a slight delay
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.05)  # Add a small delay to simulate typing
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        # Add the assistant's response to the chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# Check if there are messages in the chat history and if the number of messages is even
if st.session_state.messages and len(st.session_state.messages) % 2 == 0:
    # print('come in if')
    st.cache_data.clear()
    st.cache_resource.clear()
    # Display a feedback widget for the user to provide feedback

    feedback = streamlit_feedback(
        feedback_type="faces",
        optional_text_label="[Optional] Please provide an explanation",
    )

    # Get the current time
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    if feedback:
        # Extract the feedback score and text
        score = feedback['score']
        text = feedback['text']
        created_on = current_time
        
        # Create a new DataFrame with the feedback
        df = pd.DataFrame({"session_id": [0000], "score": [score], "user_text": [st.session_state.messages[-2]['content']],"generative_text": [st.session_state.messages[-1]['content']],"feedback_text": [text], "created_on": [created_on]})

        # Display a toast message to confirm that the feedback is updated in the database
        st.toast("Thanks! Your feedback is updated in the database.")

        print(df)