import streamlit as st
from openai import OpenAI

api_key = st.text_input("OpenAI API Key", type='password')
client = OpenAI(api_key=api_key)

prompt = st.text_area("Prompt")
messages = [
    {"role": "user", "content": prompt}
]

answer = ''

if st.button("Generate"):

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages
    )
    answer = response.choices[0].message.content

st.text(answer)


image_url=''

if st.button("Image"):
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url

if image_url:
    st.markdown(f"![{prompt}]({image_url})")
    
