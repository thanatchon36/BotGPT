import streamlit as st
from streamlit_feedback import streamlit_feedback
import time
import datetime
import pandas as pd
from PIL import Image
import os
import csv
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import requests

def get_response(prompt):
    port = 5101
    api_route = 'botgpt_query'
    post_params = {'prompt': f"{prompt}",
                }
    res = requests.post('http://localhost:{}/{}'.format(port, api_route), json = post_params)
    return res.json()['response']

def get_response_2(prompt):
    port = 5102
    api_route = 'botgpt_query'
    post_params = {'prompt': f"{prompt}",
                }
    res = requests.post('http://localhost:{}/{}'.format(port, api_route), json = post_params)
    return res.json()['response']

def reset(df):
    cols = df.columns
    return df.reset_index()[cols]

show_chat_history_no = 5
admin_list = ['thanatcc', 'da']

st.set_page_config(page_title = 'BotGPT', page_icon = 'fav.png')

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login('BotGPT Login', 'main')

if st.session_state["authentication_status"]:
    
    if "chat_id" not in st.session_state:
        now = str(datetime.datetime.now())
        st.session_state.chat_id  = now

    bot_image = Image.open('fav.png')
    bot_image_2 = Image.open('fav_3.png')
    user_image = Image.open('fav_2.png')

    with st.sidebar:
        
        clear_session_click = st.button("New Chat")
        if clear_session_click:
            st.session_state.messages = []
            now = str(datetime.datetime.now())
            st.session_state.chat_id  = now

        csv_file = f"data/{st.session_state.username}.csv"
        file_exists = os.path.isfile(csv_file)
        if file_exists and len(pd.read_csv(csv_file) > 0):
            # Init State Sessioin
            if 'page' not in st.session_state:
                st.session_state['page'] = 1
                
            with st.expander("Chat History"):
                hist_df = pd.read_csv(f'data/{st.session_state.username}.csv')
                full_hist_df = hist_df.copy()
                hist_df = reset(hist_df.sort_values(by = 'turn_id', ascending = False))
                hist_df = hist_df.groupby('chat_id').first().reset_index()
                hist_df = reset(hist_df.sort_values(by = 'turn_id', ascending = False))

                hist_df['page'] = hist_df.index
                hist_df['page'] = hist_df['page'] / show_chat_history_no
                hist_df['page'] = hist_df['page'].astype(int)
                hist_df['page'] = hist_df['page'] + 1

                st.session_state['max_page'] = hist_df['page'].max()

                filter_hist_df_2 = reset(hist_df[hist_df['page'] == st.session_state['page']])

                for index, row in filter_hist_df_2.iterrows():
                    if st.session_state.chat_id != row['chat_id']:
                        chat_button_click = st.button(f"{row['generative_text'][:20]}" + '...', key = row['chat_id'])
                        if chat_button_click:
                            st.session_state.messages = []
                            st.session_state.chat_id = row['chat_id']
                            st.session_state.turn_id = row['turn_id']
                            fil_hist_df = full_hist_df.copy()
                            fil_hist_df = reset(fil_hist_df[fil_hist_df['chat_id'] == row['chat_id']])
                            for index_2, row_2 in fil_hist_df.iterrows(): 
                                st.session_state.messages.append({"role": "user", "content": row_2['user_text']})
                                st.session_state.messages.append({"role": "assistant", "content": row_2['generative_text'], "chat_id": row_2['chat_id'], "turn_id":  row_2['turn_id']})

                if 'max_page' not in st.session_state:
                    st.session_state['max_page'] = 10
                if int(st.session_state['max_page']) > 1:
                    page = st.slider('Page No:', 1, int(st.session_state['max_page']), key = 'page')

        with st.expander("Change Password"):
            try:
                if authenticator.reset_password(st.session_state["username"], 'Reset password'):
                    with open('config.yaml', 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(e)

        if st.session_state.username in admin_list:
            with st.expander("Register User"):
                try:
                    if authenticator.register_user('Register user', preauthorization=False):
                        with open('config.yaml', 'w') as file:
                            yaml.dump(config, file, default_flow_style=False)
                        st.success('User registered successfully')
                except Exception as e:
                    st.error(e)

        authenticator.logout(f"Logout ({st.session_state['username']})", 'main', key='unique_key')



    with st.chat_message("assistant", avatar = bot_image_2):
        # Create an empty message placeholder
        mp = st.empty()
        # Create a container for the message
        sl = mp.container()
        # Add a Markdown message describing the app
        sl.markdown("""
            I am BotGPT, ready to provide assistance.
        """)

        existing_df = pd.DataFrame()

    mp = st.empty()

    # Initialize chat history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar = bot_image_2):
                st.markdown(message["content"])
                # st.code(message["content"], language="plaintext")
                # feedback = streamlit_feedback(
                #     feedback_type="faces",
                #     optional_text_label="[Optional] Please provide an explanation",
                #     key = message["turn_id"]
                # )
        else:
            with st.chat_message(message["role"], avatar = user_image):
                st.markdown(message["content"])
    


    # Check if there's a user input prompt
    if prompt := st.chat_input(placeholder="Kindly input your query or command for prompt assistance..."):
        # Display user input in the chat
        st.chat_message("user", avatar = user_image).write(prompt)

        # Add user message to the chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Create a chat message for the assistant
        with st.chat_message("assistant", avatar = bot_image_2):
            full_response = ""  # Initialize an empty string to store the full response
            message_placeholder = st.empty()  # Create an empty placeholder for displaying messages

            with st.spinner('Thinking...'):
                response = get_response(prompt)
                full_response = ""
                # Simulate streaming the response with a slight delay
                for chunk in response.split("\n"):
                    # Add a small delay to simulate typing
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                    full_response += chunk + "  \n"  # Add double space escape sequence for line break
                    message_placeholder.markdown(full_response)

            # csv_file = f"data/{st.session_state['username']}.csv"
            csv_file = f"data/{st.session_state.username}.csv"
            file_exists = os.path.isfile(csv_file)
            if not file_exists:
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['username','chat_id','turn_id','user_text','generative_text'])
            with open(csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                current_time = str(datetime.datetime.now())
                st.session_state.turn_id = current_time
                writer.writerow([st.session_state.username, st.session_state.chat_id, st.session_state.turn_id, prompt, full_response])

            # Add the assistant's response to the chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response, "chat_id": st.session_state.chat_id, "turn_id": st.session_state.turn_id})

            st.rerun()

    # Check if there are messages in the chat history and if the number of messages is even
    if st.session_state.messages and len(st.session_state.messages) % 2 == 0:
        # st.cache_data.clear()
        # st.cache_resource.clear()
        
        # Display a feedback widget for the user to provide feedback
        
        try:    
            feedback = streamlit_feedback(
                feedback_type="faces",
                optional_text_label="[Optional] Please provide an explanation",
                key = st.session_state.turn_id
            )
            # print(feedback)

            # Get the current time
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            
            if feedback:
                # Extract the feedback score and text
                score = feedback['score']
                text = feedback['text']
                
                # Create a new DataFrame with the feedback
                # df = pd.DataFrame({"turn_id": [st.session_state.turn_id], "score": [score], "user_text": [st.session_state.messages[-2]['content']],"generative_text": [st.session_state.messages[-1]['content']],"feedback_text": [text], "created_on": [created_on]})
                # print(df)
                
                # Display a toast message to confirm that the feedback is updated in the database
                st.toast("Thanks! Your valuable feedback is updated in the database.")

                csv_file = f"data/feedback.csv"
                file_exists = os.path.isfile(csv_file)
                if not file_exists:
                    with open(csv_file, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(['username','chat_id','turn_id','score','feedback_text'])
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    current_time = str(datetime.datetime.now())
                    writer.writerow([st.session_state.username, st.session_state.chat_id, st.session_state.turn_id, score, text])
        except:
            pass

