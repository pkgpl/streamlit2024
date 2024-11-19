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

if "messages" not in st.session_state:
    st.session_state.messages = []

st.header("Chat")

# previous chat
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

# user prompt, assistant response
if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user", "content":prompt})

    response = f"Echo: {prompt}"

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role":"assistant","content":response})
