import streamlit as st

@st.cache_data
def ask_gpt(prompt):
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("API Key를 입력하세요."):
        st.switch_page("pages/1_Setting.py")
    st.stop()

st.header("Ask GPT")

prompt = st.text_area("Prompt", key='chat_prompt')

answer = ''
if st.button("Generate"):
    answer = ask_gpt(prompt)

st.text(answer)