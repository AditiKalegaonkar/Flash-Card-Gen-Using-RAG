# Libraries
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


def load_and_chunk(path):
    loader = PyPDFLoader(path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    return docs


def pipeline(docs):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    db = FAISS.from_documents(docs, embeddings)
    print("Embedded succesfully")
    retriever = db.as_retriever(
        search_type="similarity", search_kwargs={"k": 20})

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.4)
    prompt_t = """Based on the provided content create a dictionary datatype of definition or important question 
    related to the context {context} and answer to the question. The answer should in the form of dictionary
    with key as question and value as answer to the question. Make these questions and answers only relevant 
    to the context provided only. Only output the result in the form of dictionary. Create at least 2 questions per page.
    Remember to include each and every topic at least once. Osnly give Question answer in the form of dictionary datatype in json.
    """

    prompt = PromptTemplate(
        template=prompt_t,
        input_variables=["context"],
        input_type=str
    )

    retrievalQA = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    result = retrievalQA.invoke(
        "Create a dictionary datatype of important definitions and questions as a key and answer as value.")

    return result['result']
