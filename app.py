import streamlit as st
from openai import OpenAI

api_key = st.text_input("OpenAI API Key", type='password')

prompt = st.text_area("Prompt")
answer = ''

if st.button("Generate"):
    messages = [
        {"role": "user", "content": query}
    ]
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages
    )
    answer = response.choices[0].message.content

st.text(answer)
