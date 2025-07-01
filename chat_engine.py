import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from document_loader import load_and_chunk_documents

# 1) prepare embeddings & index
def build_faiss_index() -> FAISS:
    chunks = load_and_chunk_documents()
    embed_model = OpenAIEmbeddings(model="text-embedding-3-small",
                                   openai_api_key=os.getenv("OPENAI_API_KEY"))
    return FAISS.from_documents(chunks, embed_model)

# 2) singleton index + chain + memory store
INDEX = build_faiss_index()
MEMORY_STORE: dict[str, ConversationBufferMemory] = {}

def get_chain_for_session(session_id: str) -> ConversationalRetrievalChain:
    if session_id not in MEMORY_STORE:
        MEMORY_STORE[session_id] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
    memory = MEMORY_STORE[session_id]

    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0,
                       openai_api_key=os.getenv("OPENAI_API_KEY")),
        retriever=INDEX.as_retriever(),
        memory=memory
    )