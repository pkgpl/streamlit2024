import streamlit as st
from openai import OpenAI

api_key = st.text_input("OpenAI API Key", key='api_key', type='password')

if 'openai_client' in st.session_state:
    client = st.session_state['openai_client']
else:
    client = OpenAI(api_key=api_key)
    st.session_state['openai_client'] = client
