import streamlit as st
from openai import OpenAI

api_key = st.text_input("OpenAI API Key", key='api_key', type='password')

client = st.session_state.get('openai_client', OpenAI(api_key=api_key))
