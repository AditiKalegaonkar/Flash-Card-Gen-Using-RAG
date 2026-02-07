# Libraries
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
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
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001")

    db = FAISS.from_documents(docs, embeddings)
    print("Embedded succesfully")
    retriever = db.as_retriever(
        search_type="similarity", search_kwargs={"k": 20})

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)
    prompt_t = """
        You are given a multi-page content as {context}.
        Task:
        Based only on the provided {context}, generate important definition-based or conceptual questions and their answers.

        Instructions:
        1. Create questions that are strictly relevant to the given context only.
        2. Cover every topic and subtopic mentioned in the context at least once.
        3. Create a minimum of 2 questions per page of the content.
        4. Questions should focus on definitions, explanations, purposes, comparisons, or key concepts.
        5. Do not add any external knowledge or assumptions beyond the context.
        6. Keep answers clear, accurate, and concise, but conceptually complete.
        7. Do not include explanations, headings, or extra text outside the required output.

        Output Format (Strict):
        - Return only a JSON dictionary.
        - Each key must be a question.
        - Each value must be the corresponding answer.
        - Do not nest dictionaries or arrays.
        - Do not include page numbers, metadata, or commentary.

        Example Output Structure:
        {{
        "Question 1": "Answer 1",
        "Question 2": "Answer 2"
        }}

        Important:
        Only output the final result as a JSON dictionary datatype.
    """

    prompt = PromptTemplate(
        template=prompt_t,
        input_variables=["context"],
        input_type=str
    )
    rag_chain = (
        {
            "context": retriever,
            "user_question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    result = rag_chain.invoke(
        "Create a dictionary datatype of important definitions and questions as a key and answer as value.")

    return result
