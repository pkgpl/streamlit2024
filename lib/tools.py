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

SCHEMA_GENERATE_IMAGE = {
    "type":"function",
    "function": {
        "name": "generate_image",
        "description":"Generate an image using Dall-E-3 and return the image url",
        "parameters": {
            "type":"object",
            "properties":{
                "prompt": {
                    "type":"string",
                    "description":"image generation prompt"
                }
            },
            "required":["prompt"],
            "additionalProperties": False
        },
        "strict": True
    }
}