import os
import streamlit as st
from google import genai
from google.genai.types import (
    Part,
    GenerateContentConfig,
    Tool,
    GoogleSearch,
    VertexAISearch,
    Retrieval,
)

# environment values
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = "global"
MODEL_ID = "gemini-2.0-flash-001"
DATA_STORE_LOCATION = "global"
DATA_STORE_ID = os.environ.get("DATA_STORE_ID")

# init Gemini
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

st.title("Gemini 2.0 - RAG Sample")
if "history" not in st.session_state:
    st.session_state.history = []

with st.form("my_form"):
    PROMPT = st.text_area(label="Prompt", value="Cloud Spanner の特徴は何?")
    uploaded_file = st.file_uploader(
        "(option) PDF file",
        type=["pdf"],
    )
    if uploaded_file:
        with st.spinner("Loading ..."):
            pdfFile = uploaded_file.getvalue()
    mode = st.radio(
        "Choose grouding mode",
        [
            "Gemini only (use in-context PDF)",
            "Grounding with Vertex AI Search",
            "Grounding with Google Search",
        ],
    )
    submitted = st.form_submit_button("Submit")

# render history
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if submitted:
    # render user prompt
    text = f"[{mode}]\n \n{PROMPT}"
    with st.chat_message("user"):
        st.markdown(text)
    st.session_state.history.append({"role": "user", "content": text})

    if mode == "Gemini only (use in-context PDF)":
        chat = client.chats.create(model=MODEL_ID)
        if uploaded_file:
            # call Gemini with PDF
            response = chat.send_message(
                [
                    Part.from_bytes(data=pdfFile, mime_type="application/pdf"),
                    Part.from_text(text=PROMPT),
                ]
            )
        else:
            # call Gemini without PDF
            response = chat.send_message([Part.from_text(text=PROMPT)])
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.history.append({"role": "assistant", "content": response.text})
    elif mode == "Grounding with Vertex AI Search":
        # call Gemini grounded with Vertex AI Search
        vertex_ai_search_tool = Tool(
            retrieval=Retrieval(
                vertex_ai_search=VertexAISearch(
                    datastore=f"projects/{PROJECT_ID}/locations/{DATA_STORE_LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}"
                )
            )
        )
        chat = client.chats.create(
            model=MODEL_ID, config=GenerateContentConfig(tools=[vertex_ai_search_tool])
        )
        response = chat.send_message(PROMPT)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.history.append({"role": "assistant", "content": response.text})
        # print citation
        with st.chat_message("assistant"):
            citation = ""
            for i, groundingChunk in enumerate(
                response.candidates[0].grounding_metadata.grounding_chunks
            ):
                citation += f"[{i+1}] [{groundingChunk.retrieved_context.title}]({groundingChunk.retrieved_context.uri}) "
            gcsurl = citation.replace("gs://","https://storage.mtls.cloud.google.com/")
            st.markdown(gcsurl)
        st.session_state.history.append({"role": "assistant", "content": citation})
    elif mode == "Grounding with Google Search":
        # call Gemini grounded with Google Search
        google_search_tool = Tool(google_search=GoogleSearch())
        chat = client.chats.create(
            model=MODEL_ID, config=GenerateContentConfig(tools=[google_search_tool])
        )
        response = chat.send_message(PROMPT)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.history.append({"role": "assistant", "content": response.text})
        # print citation
        with st.chat_message("assistant"):
            citation = ""
            for i, groundingChunk in enumerate(
                response.candidates[0].grounding_metadata.grounding_chunks
            ):
                citation += (
                    f"[{i+1}] [{groundingChunk.web.title}]({groundingChunk.web.uri}) "
                )
            st.markdown(citation)
        st.session_state.history.append({"role": "assistant", "content": citation})
