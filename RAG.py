# Libraries
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv
load_dotenv()
HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"

def load_and_chunk(path):
    loader = PyPDFLoader(path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    return docs

def pipeline(docs):
    embeddings = HuggingFaceEndpointEmbeddings(model="sentence-transformers/all-mpnet-base-v2",huggingfacehub_api_token=HUGGING_FACE_API_KEY)
    db = FAISS.from_documents(docs, embeddings)
    print("Embedded succesfully")
    retriever = db.as_retriever(search_type ="similarity",search_kwargs ={"k" :20})
    llm = HuggingFaceEndpoint(repo_id=repo_id,max_length=512,temperature=0.3,huggingfacehub_api_token=HUGGING_FACE_API_KEY, task="text-generation")

    prompt_t = """Based on the provided content create a dictionary datatype of definition or important question 
    related to the context {context} and answer to the question. The answer should in the form of dictionary
    with  key as question and value as answer to the question. Make these questions and answers only relevant 
    to the context provided only. Only output the result in the form of dictionary. Create at least 2 questions per page. 
    Remember to include each and every topic at least once. Dont add any question numbers only give answer in the form of dictionary datatype in json.
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

    result = retrievalQA.invoke("Create a dictionary datatype of important definitions and questions as a key and answer as value.")

    return result['result']