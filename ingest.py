from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

RAG_EMAIL_PROMPT_TEMPLATE = """
You are a helpful assistant for a SaaS company. Using the retrieved context below, 
generate a professional and grounded response to the customer email.

**IMPORTANT:**
Respond directly to the customer naturally. Do not mention or refer to having access 
to any external context or documentation. If the context does not contain enough 
information to respond, state 'I don't know.'

Customer Email: {email}
Context: {context}
"""

doc_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

print("Loading & Chunking Docs...")

files = ["documents/features.txt", "documents/pricing.txt", "documents/support.txt"]
all_chunks = list()

for file in files:
    docs = TextLoader(file).load()
    chunks = doc_splitter.split_documents(docs)
    all_chunks.extend(chunks)

print("Creating vector embeddings...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
vectorstore = Chroma.from_documents(all_chunks, embeddings, persist_directory="db")

# Semantic vector search
vectorstore_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Test RAG chain
print("Test RAG chain...")
prompt = ChatPromptTemplate.from_template(RAG_EMAIL_PROMPT_TEMPLATE)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)

rag_chain = (
    {"context": vectorstore_retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

#Demo customer email
customer_email = """
Hi,

I hope this message finds you well. I wanted to reach out to ask about your pricing options. 
Could you let me know what plans are available and what each one includes?

Looking forward to your response.

Best regards,
Raghav
"""

result = rag_chain.invoke(customer_email)
print(f"Question: {customer_email}")
print(f"Answer: {result}")

