from langchain_community.document_loaders import SeleniumURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Initialize embeddings and a separate vector store for URL data
embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")
url_vector_store = InMemoryVectorStore(embedding=embeddings)  # Separate vector store for URL data


def load_page(url):
    """Load and parse the content of a web page."""
    loader = SeleniumURLLoader(urls=[url])
    return loader.load()


def split_text(documents):
    """Split the loaded documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)


def index_docs(documents):
    """Index the chunked documents into the URL-specific vector store."""
    url_vector_store.add_documents(documents)


def retrieve_docs(query):
    """Retrieve relevant documents from the URL-specific vector store."""
    return url_vector_store.similarity_search(query)


def answer_question(question, context):
    """Generate an answer based on the retrieved context."""
    template ="""
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. Keep the answer concise and within three sentences.
    Question: {question} 
    Context: {context} 
    Answer:
    """

    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model="deepseek-r1:1.5b")
    chain = prompt | model
    return chain.invoke({"question": question, "context": context})