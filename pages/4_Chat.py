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

if "assistant" not in st.session_state:
    st.session_state.assistant = client.beta.assistants.create(
        name="Assistant",
        model="gpt-4o-mini",
        tools=[
            {"type":"code_interpreter"}
        ]
    )

if "thread" not in st.session_state:
    st.session_state.thread = client.beta.threads.create()


st.header("Chat")

col1, col2 = st.columns(2)
with col1:
    if st.button("Clear (Start a new chat)"):
        st.session_state.messages = []
        del st.session_state.thread
with col2:
    if st.button("Leave"):
        st.session_state.messages = []
        del st.session_state.thread
        del st.session_state.assistant

# previous chat
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg["content"])

# user prompt, assistant response
if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user", "content":prompt})

    # assistant api - get response
    thread = st.session_state.thread
    assistant = st.session_state.assistant

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    if run.status == 'completed':
        api_response = client.beta.threads.messages.list(
            thread_id=thread.id,
            run_id=run.id,
            limit=1
        )
    response = api_response.data[0].content[0].text.value

    # assistant api - tool call info
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )
    codes = []
    for run_step in reversed(run_steps.data):
        if run_step.step_details.type == 'tool_calls':
            for tool_call in run_step.step_details.tool_calls:
                if tool_call.type == 'code_interpreter':
                    codes.append(tool_call.code_interpreter.input)

    with st.chat_message("assistant"):
        st.markdown(response)
        if codes:
            with st.expander("Show codes"):
                for code in codes:
                    st.code(code, language='python')
    st.session_state.messages.append({"role":"assistant","content":response})
