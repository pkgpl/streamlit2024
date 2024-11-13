import streamlit as st

@st.cache_data
def generate_image(prompt):
    client = st.session_state['openai_client']
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("API Key를 입력하세요."):
        st.switch_page("pages/1_Setting.py")
    st.stop()

st.header("Generate Images")

prompt = st.text_area("Prompt", value=st.session_state.get('image_prompt',''))
st.session_state['image_prompt'] = prompt

image_url = ''
if st.button("Generate"):
    image_url = generate_image(prompt)

if image_url:
    st.markdown(f"![{prompt}]({image_url})")