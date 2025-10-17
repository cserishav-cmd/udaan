from dotenv import load_dotenv
import os
from src.helper import load_pdf_files, filter_to_minimal_docs, text_split, download_embeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

print("Loading environment variables...")
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY not found in .env file")

print("Loading PDF data...")
extracted_data = load_pdf_files("data")
print(f"Loaded {len(extracted_data)} documents.")

minimal_docs = filter_to_minimal_docs(extracted_data)
print("Filtered to minimal documents.")

texts_chunk = text_split(minimal_docs)
print(f"Split documents into {len(texts_chunk)} chunks.")

print("Downloading embeddings model...")
embeddings = download_embeddings()
print("Embeddings model loaded.")

print("Initializing Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "udaan-chatbot"

if index_name not in pc.list_indexes().names():
    print(f"Creating new Pinecone index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=384,  # Dimension of the 'all-MiniLM-L6-v2' model
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print("Index created successfully.")
else:
    print(f"Index '{index_name}' already exists.")

print("Storing document chunks in Pinecone. This may take a moment...")
docsearch = PineconeVectorStore.from_documents(
    documents=texts_chunk,
    embedding=embeddings,
    index_name=index_name
)
print("Successfully stored embeddings in Pinecone!")
print("Setup complete.")