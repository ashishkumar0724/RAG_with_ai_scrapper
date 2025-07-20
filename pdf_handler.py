import os
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")
vector_store = InMemoryVectorStore(embeddings)


def upload_pdf(file):
    # Ensure the directory exists
    pdfs_directory = "chat-with-pdf/pdfs/"
    os.makedirs(pdfs_directory, exist_ok=True)  # Create the directory if it doesn't exist

    # Save the uploaded file
    file_path = os.path.join(pdfs_directory, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path

def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    return loader.load()


def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)


def index_docs(documents):
    vector_store.add_documents(documents)


def retrieve_docs(query):
    return vector_store.similarity_search(query)


def answer_question(question, context):
    template = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. Keep the answer concise and within three sentences.
    Question: {question} 
    Context: {context} 
    Answer:
    """
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama.llms import OllamaLLM

    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model="deepseek-r1:1.5b")
    chain = prompt | model
    return chain.invoke({"question": question, "context": context})