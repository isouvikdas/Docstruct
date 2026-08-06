import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

connection = (
    f"postgresql+psycopg://"
    f"{os.getenv('DATABASE_USERNAME')}:"
    f"{os.getenv('DATABASE_PASSWORD')}@"
    f"host.docker.internal:5432/postgres"
)

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="my_docs",
    connection=connection,
)