import google.auth
import google.auth.transport.requests
import os
import pandas as pd
import requests
import streamlit as st
import time

from pandas import json_normalize

title = os.environ.get("APP_TITLE")
prompt = os.environ.get("APP_PROMPT")
endpoint = os.environ.get("APP_ENDPOINT")

# Function to get Google Cloud access token using service account
def get_gcloud_access_token():
    creds, project = google.auth.default()

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    return creds.token

# Get a single page of results
def get_results_page(query, base_url, pageToken):
    access_token = get_gcloud_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "pageSize": 100,
        "queryExpansionSpec": {"condition": "AUTO"},
        "spellCorrectionSpec": {"mode": "AUTO"}
    }

    if pageToken:
        response = requests.post(
            base_url + "?pageToken=" + pageToken,
            headers=headers,
            json=data
        )
    else:
        response = requests.post(
            base_url,
            headers=headers,
            json=data
        )
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}")
    response_json = response.json()
    items = response_json.get('results', [])
    pageToken = response_json.get('nextPageToken', None)
    return items, pageToken


def get_results(base_url, query):
    pageToken = None
    all_items = []

    # Pagination across results pages
    while True:
        items, pageToken = get_results_page(query, base_url, pageToken)
        all_items.extend(items)
        time.sleep(1)  # rate limiting
        if not pageToken:
            break

    return all_items

# Render Streamlit results (as a table)
def render_results(results):
    df = json_normalize(results, sep=' ')
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No data found.")
    return df


def main():
    st.title(title)
    query = st.text_input(prompt)

    if st.button("Search"):
        if query:
            results = get_results(
                endpoint,
                query
            )
            render_results(results)
        else:
            st.write("Please enter a search query.")

if __name__ == "__main__":
    main()


"""
import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

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

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
"""
