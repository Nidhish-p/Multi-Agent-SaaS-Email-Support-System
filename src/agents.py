from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .structured_agent_outputs import *
from .prompts import *
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv

class Agents():
    def __init__(self):
        load_dotenv()
        llama = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)
        
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vectorstore = FAISS.load_local("db", embeddings, allow_dangerous_deserialization=True)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        email_category_prompt = PromptTemplate(
            template=CATEGORIZE_EMAIL_PROMPT, 
            input_variables=["email"]
        )
        self.categorize_email = (
            email_category_prompt | 
            llama.with_structured_output(EmailCategoryToneOutput)
        )
        
        qa_prompt = PromptTemplate(
            template=GENERATE_RAG_ANSWER_PROMPT, 
            input_variables=["email", "context"]
        )
        self.generate_rag_answer = (
            {"context": retriever, "email": RunnablePassthrough()}
            | qa_prompt
            | llama
            | StrOutputParser()
        )

        writer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EMAIL_WRITER_PROMPT),
                MessagesPlaceholder("history"),
                ("human", "{email_information}")
            ]
        )
        self.email_writer = (
            writer_prompt | 
            llama.with_structured_output(WriterOutput)
        )

        proofreader_prompt = PromptTemplate(
            template=EMAIL_PROOFREADER_PROMPT, 
            input_variables=["email", "generated_email"]
        )
        self.email_proofreader = (
            proofreader_prompt | 
            llama.with_structured_output(ProofReaderOutput) 
        )