import streamlit as st

def show_message(msg):
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])


# Initialization

client = st.session_state.get('openai_client', None)
if client is None:
    if st.button("API Key를 입력하세요."):
        st.switch_page("pages/1_Setting.py")
    st.stop()

# file upload

pdf_file = st.file_uploader("Upload a pdf file", type=['pdf'], accept_multiple_files=False)
if pdf_file is not None:
    vector_store = client.beta.vector_stores.create(name="ChatPDF")
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=[pdf_file]
    )
    st.session_state.vector_store = vector_store

if 'vector_store' not in st.session_state:
    st.markdown("PDF 파일을 업로드하세요.")
    st.stop()


if "chatpdf_messages" not in st.session_state:
    st.session_state.chatpdf_messages = []

if "chatpdf_assistant" not in st.session_state:
    st.session_state.chatpdf_assistant = client.beta.assistants.create(
        instructions="첨부 파일의 정보를 이용해 응답하세요.",
        model="gpt-4o-mini",
        tools=[{"type": "file_search"}],
        tool_resources={
           "file_search":{
              "vector_store_ids": [vector_store.id]
            }
        }
    )
    
if "chatpdf_thread" not in st.session_state:
    st.session_state.chatpdf_thread = client.beta.threads.create()


# Page

st.header("Chat")

col1, col2 = st.columns(2)
with col1:
    if st.button("Clear (Start a new chat)"):
        st.session_state.chatpdf_messages = []
        del st.session_state.chatpdf_thread
with col2:
    if st.button("Leave"):
        st.session_state.chatpdf_messages = []
        del st.session_state.chatpdf_thread
        del st.session_state.chatpdf_assistant
        client.beta.vector_stores.delete(st.session_state.vector_store.id)
        del st.session_state.vector_store

# previous chat
for msg in st.session_state.chatpdf_messages:
    show_message(msg)

# user prompt, assistant response
if prompt := st.chat_input("What is up?"):
    msg = {"role":"user", "content":prompt}
    show_message(msg)
    st.session_state.chatpdf_messages.append(msg)

    # assistant api - get response
    thread = st.session_state.chatpdf_thread
    assistant = st.session_state.chatpdf_assistant

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # assistant messages - text, image_url, image_file
    if run.status == 'completed':
        api_response = client.beta.threads.messages.list(
            thread_id=thread.id,
            run_id=run.id,
            order="asc"
        )
        for data in api_response.data:
            for content in data.content:
                if content.type == 'text':
                    response = content.text.value
                    msg = {"role":"assistant","content":response}
                    show_message(msg)
                    st.session_state.chatpdf_messages.append(msg)
    else:
        st.error(f"Response not completed: {run.status}")
