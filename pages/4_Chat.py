import streamlit as st
import json
from lib.tools import generate_image, SCHEMA_GENERATE_IMAGE

TOOL_FUNCTIONS = {
    "generate_image": generate_image
}

FUNCTION_TOOLS_SCHEMA = [
    SCHEMA_GENERATE_IMAGE
]

def show_message(msg):
    if msg['role'] == 'user' or msg['role'] == 'assistant':
        with st.chat_message(msg['role']):
            st.markdown(msg["content"])
    elif msg['role'] == 'code':
        with st.chat_message('assistant'):
            with st.expander("Show codes"):
                st.code(msg["content"], language='python')
    elif msg['role'] == 'image_url':
        with st.chat_message('assistant'):
            st.markdown(f"![]({msg['content']})")
    elif msg['role'] == 'image_file':
        with st.chat_message('assistant'):
            st.image(msg['content'])


# Initialization

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
        tools=[{"type":"code_interpreter"}] + FUNCTION_TOOLS_SCHEMA
    )

if "thread" not in st.session_state:
    st.session_state.thread = client.beta.threads.create()


# Page

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
    show_message(msg)

# user prompt, assistant response
if prompt := st.chat_input("What is up?"):
    msg = {"role":"user", "content":prompt}
    show_message(msg)
    st.session_state.messages.append(msg)

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

    while run.status == 'requires_action':
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool in tool_calls:
            func_name = tool.function.name
            kwargs = json.loads(tool.function.arguments)
            output = None
            if func_name in TOOL_FUNCTIONS:
                output = TOOL_FUNCTIONS[func_name](**kwargs)
            tool_outputs.append(
                {
                    "tool_call_id": tool.id,
                    "output": str(output)
                }
            )
        run = client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
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
                elif content.type == 'image_url':
                    url = content.image_url.url
                    msg = {"role":"image_url","content":url}
                elif content.type == 'image_file':
                    file_id = content.image_file.file_id
                    # load file
                    image_data = client.files.content(file_id)
                    msg = {"role":"image_file","content":image_data.read()}
                show_message(msg)
                st.session_state.messages.append(msg)

    # code interpreter tool call info
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id,
        order='asc'
    )
    for run_step in run_steps.data:
        if run_step.step_details.type == 'tool_calls':
            for tool_call in run_step.step_details.tool_calls:
                if tool_call.type == 'code_interpreter':
                    code = tool_call.code_interpreter.input
                    msg = {"role":"code","content":code}
                    show_message(msg)
                    st.session_state.messages.append(msg)
