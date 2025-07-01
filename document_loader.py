# document_loader.py
import os
import io
import tempfile
from azure.storage.blob import BlobServiceClient

from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_chunk_documents() -> list:
    conn_str  = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container = os.getenv("BLOB_CONTAINER_NAME")
    svc       = BlobServiceClient.from_connection_string(conn_str)
    client    = svc.get_container_client(container)

    docs = []
    for blob in client.list_blobs():
        ext = os.path.splitext(blob.name)[1].lower()

        # download into memory
        stream = io.BytesIO()
        client.get_blob_client(blob).download_blob().download_to_stream(stream)
        stream.seek(0)

        if ext == ".txt":
            loader = TextLoader(stream, encoding="utf8")

        elif ext == ".pdf":
            # write PDF bytes out & use PyPDFLoader (no pi_heif dependency)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(stream.read())
                tmp.flush()
                loader = PyPDFLoader(tmp.name)

        elif ext in (".docx", ".doc"):
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(stream.read())
                tmp.flush()
                loader = UnstructuredWordDocumentLoader(file_path=tmp.name)

        else:
            # skip any other file types
            continue

        docs.extend(loader.load())

    # chunk into ~1 000-char pieces with 200-char overlap
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)
