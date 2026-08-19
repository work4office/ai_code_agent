import ssl


ssl._create_default_https_context = ssl._create_unverified_context
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, AzureOpenAIEmbeddings
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv()
import os


def get_llm() -> ChatOpenAI:
    llm = ChatOpenAI(
        model=os.getenv("AZURE_CHAT_DEPLOYMENT") or "",
        base_url=os.environ["AZURE_CHAT_ENDPOINT"],
        api_key=SecretStr(os.environ["AZURE_CHAT_API_KEY"]),
    )
    return llm


def get_embedding() -> AzureOpenAIEmbeddings:
    embeddingllm = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_EMBED_DEPLOYMENT") or "",
        azure_endpoint=os.environ["AZURE_EMBED_ENDPOINT"],
        api_key=SecretStr(os.environ["AZURE_EMBED_API_KEY"]),
    )
    return embeddingllm


def get_goggle_llm():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite", google_api_key=os.environ["GOOGLE_API_KEY"]
    )

    return model


def get_goggle_embedding():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview",
        api_key=SecretStr(os.environ["GOOGLE_API_KEY"]),
    )

    return embeddings
