import streamlit as st
import numpy as np

with st.chat_message("user"):
    st.write("Hello 👋")

with st.chat_messge("assistant"):
    st.write("Hello human")
    st.bar_chart(np.random.randn(30,3))
