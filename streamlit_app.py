# Copyright (c) 2023 Neal DeBuhr
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
