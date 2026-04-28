import os

from dotenv import load_dotenv
from PyPDF2 import PdfReader
import streamlit as st

try:
    from langchain_community.vectorstores import FAISS
except ImportError:
    from langchain.vectorstores import FAISS

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

try:
    from langchain_text_splitters import CharacterTextSplitter
except ImportError:
    from langchain.text_splitter import CharacterTextSplitter

try:
    from langchain_classic.chains import ConversationalRetrievalChain
    from langchain_classic.memory import ConversationBufferMemory
except ImportError:
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    from langchain.prompts import PromptTemplate

from htmlTemplates import css, bot_template, user_template


load_dotenv()

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
DEFAULT_LLM_API_BASE = os.getenv("RAG_LLM_API_BASE", "http://localhost:8001/v1")
DEFAULT_LLM_MODEL = os.getenv("RAG_LLM_MODEL", "llama-3-8b-instruct")
DEFAULT_LLM_API_KEY = os.getenv("RAG_LLM_API_KEY", "local-llama")
DEFAULT_EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

QA_PROMPT = PromptTemplate.from_template(
    """Use only the context below to answer the question. If the answer is not in the
context, say that you do not know based on the uploaded documents.

Context:
{context}

Question: {question}

Answer:"""
)


def get_document_text(uploaded_files):
    text = ""
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name.lower()
        if file_name.endswith(".pdf"):
            pdf_reader = PdfReader(uploaded_file)
            for page_number, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text() or ""
                text += f"\n\nSource: {uploaded_file.name}, page {page_number}\n{page_text}"
        else:
            file_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            text += f"\n\nSource: {uploaded_file.name}\n{file_text}"
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    return text_splitter.split_text(text)


def get_vectorstore(text_chunks, embedding_model_name):
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={"device": "cpu", "local_files_only": True},
        encode_kwargs={"normalize_embeddings": True},
    )
    return FAISS.from_texts(texts=text_chunks, embedding=embeddings)


def get_conversation_chain(vectorstore, model_name, api_base, api_key):
    llm = ChatOpenAI(
        model=model_name,
        base_url=api_base,
        api_key=api_key,
        temperature=0,
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4},
        ),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
    )


def render_chat_history():
    for index, message in enumerate(st.session_state.chat_history):
        template = user_template if index % 2 == 0 else bot_template
        st.write(
            template.replace("{{MSG}}", message.content),
            unsafe_allow_html=True,
        )


def handle_userinput(user_question):
    if st.session_state.conversation is None:
        st.warning("Upload and process documents before asking a question.")
        return

    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response["chat_history"]
    st.session_state.last_sources = response.get("source_documents", [])


def initialize_session_state():
    defaults = {
        "conversation": None,
        "chat_history": [],
        "document_stats": None,
        "last_sources": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def process_documents(uploaded_files, model_name, api_base, api_key, embedding_model_name):
    raw_text = get_document_text(uploaded_files)
    if not raw_text.strip():
        st.error("No text could be extracted from the uploaded files.")
        return

    text_chunks = get_text_chunks(raw_text)
    if not text_chunks:
        st.error("No chunks were created from the uploaded text.")
        return

    vectorstore = get_vectorstore(text_chunks, embedding_model_name)
    st.session_state.conversation = get_conversation_chain(
        vectorstore,
        model_name,
        api_base,
        api_key,
    )
    st.session_state.chat_history = []
    st.session_state.last_sources = []
    st.session_state.document_stats = {
        "files": len(uploaded_files),
        "characters": len(raw_text),
        "chunks": len(text_chunks),
    }
    st.success("Documents processed. Ask a question in the chat box.")


def main():
    load_dotenv()
    st.set_page_config(
        page_title="Custom Content Chatbot",
        page_icon=":robot_face:",
        layout="wide",
    )
    st.write(css, unsafe_allow_html=True)
    initialize_session_state()

    st.title("Custom Content Chatbot")
    st.caption(
        "Upload documents, create embeddings, and ask questions grounded in your content."
    )

    if st.session_state.document_stats:
        col1, col2, col3 = st.columns(3)
        col1.metric("Files", st.session_state.document_stats["files"])
        col2.metric("Text characters", st.session_state.document_stats["characters"])
        col3.metric("Chunks", st.session_state.document_stats["chunks"])

    user_question = st.chat_input("Ask a question about your uploaded documents")
    if user_question:
        handle_userinput(user_question)

    if st.session_state.chat_history:
        render_chat_history()

    if st.session_state.last_sources:
        with st.expander("Closest matching context"):
            for index, source in enumerate(st.session_state.last_sources, start=1):
                st.markdown(f"**Context {index}**")
                st.write(source.page_content[:1000])

    with st.sidebar:
        st.subheader("Knowledge base")
        uploaded_files = st.file_uploader(
            "Upload PDFs or text files",
            type=["pdf", "txt", "md", "html"],
            accept_multiple_files=True,
        )
        model_name = st.text_input("Local Llama chat model", value=DEFAULT_LLM_MODEL)
        api_base = st.text_input("Local Llama API base", value=DEFAULT_LLM_API_BASE)
        # api_key = st.text_input("API key", value=DEFAULT_LLM_API_KEY, type="password")
        embedding_model_name = st.text_input(
            "Local embedding model",
            value=DEFAULT_EMBEDDING_MODEL,
        )

        st.divider()
        st.write(f"Chunk size: {CHUNK_SIZE}")
        st.write(f"Chunk overlap: {CHUNK_OVERLAP}")
        st.write("LLM: local Llama 3")
        st.write("Embeddings: local sentence-transformers")

        if st.button("Process documents", type="primary"):
            if not uploaded_files:
                st.warning("Please upload at least one document.")
                return
            with st.spinner("Processing"):
                process_documents(
                    uploaded_files,
                    model_name,
                    api_base,
                    api_key,
                    embedding_model_name,
                )


if __name__ == "__main__":
    main()
