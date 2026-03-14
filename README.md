# Multi-Agent SaaS Email Support System

## 📌 Overview

A production-grade, fully automated email support pipeline built for SaaS companies — powered by a multi-agent LangGraph architecture, RAG-based knowledge retrieval, and a trained ML spam classifier. The system reads incoming customer emails, filters spam, classifies intent, retrieves grounded product knowledge, and drafts tone-aware replies — entirely without human intervention.

> **Successor to:** [Email Spam Classifier]([https://github.com/Nidhish-p/Email-Spam-Classifier]) — spam detection is now a native intelligence layer within a larger orchestration system.

---

## ⚡ Novelties of This Project

This is not a standard chatbot or autoresponder — it introduces several original contributions:

- **Categorical Business Routing:** Emails are routed across 6 business-relevant categories using LLM classification — not keyword matching.
- **RAG-Grounded Responses:** Every product-related reply is grounded in actual internal documentation via FAISS vector retrieval — no hallucination.
- **Tone-Aware Generation:** 6-tier communication tone detection adapts the email's language to match the customer's emotional register while preserving factual accuracy.
- **ML Spam Gate:** A trained Complement Naive Bayes classifier with TF-IDF vectorization filters spam before it reaches the orchestration pipeline.
- **Automated Proofreading Loop:** A dedicated proofreader agent reviews every draft and re-invokes the writer with feedback if quality checks fail.
- **Multi-Agent State Machine:** Independent specialized agents for categorization, RAG retrieval, writing, and proofreading — modular, debuggable, and extensible.

---

## 🔄 Workflow

### 1. Spam Filtering
- Load unread emails from Gmail inbox
- Run each email through a trained CNB + TF-IDF spam classifier
- Discard spam silently; pass clean emails downstream

### 2. Categorical Routing
- Classify email into one of 6 categories using Llama 3.3 70B
- Detect communication tone across 6 tiers
- Route to the appropriate agent pipeline

### 3. RAG-Grounded Response (Product-Related Emails)
- Embed the customer email using Gemini embeddings
- Retrieve top-k relevant chunks from FAISS vector store
- Generate a factual, grounded response strictly from retrieved context

### 4. Email Drafting & Proofreading
- Tone-aware email writer generates a customer-ready draft
- Proofreader agent reviews the draft
- If rejected, writer is re-invoked with feedback — up to configurable retry limit
- Approved draft is created in Gmail

---

## 🏗️ Architecture

```
Inbox
  │
  ▼
Load Emails
  │
  ▼
Is Inbox Empty? ──── Yes ──▶ END
  │ No
  ▼
Spam Classifier (CNB + TF-IDF)
  │ Spam ──▶ Discard ──▶ Back to Inbox Check
  │ Clean
  ▼
Categorize Email + Detect Tone (Llama 3.3 70B)
  │
  ├──▶ feature_query / pricing_upgrade / onboarding_help / technical_support
  │         │
  │         ▼
  │     RAG Retrieval (FAISS + Gemini Embeddings)
  │         │
  │         ▼
  │     Grounded Response Generation
  │         │
  │         ▼
  │     Tone-Aware Email Writer
  │
  ├──▶ downgrade_cancellation
  │         │
  │         ▼
  │     Retention-Focused Email Writer
  │
  └──▶ unrelated ──▶ Skip
            │
            ▼
        Proofreader Agent
            │
            ├──▶ Pass ──▶ Create Gmail Draft
            └──▶ Fail ──▶ Re-invoke Writer (with feedback)
```

---

## 💼 Business Impact

- **Zero Manual Triage:** Emails are categorized, routed, and responded to automatically — no human sorting required.
- **Churn-Aware Handling:** Downgrade and cancellation emails are detected and handled with retention-focused language.
- **Hallucination-Free Responses:** RAG ensures every product-related reply is grounded in real documentation.
- **Gmail-Native:** Works with existing Gmail infrastructure — no new tooling required.
- **Modular Design:** Independent agent nodes allow faster debugging, updates, and extensibility.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM | Groq — Llama 3.3 70B |
| Embeddings | Google Gemini (`gemini-embedding-001`) |
| Vector Store | FAISS |
| Spam Classifier | Scikit-learn — Complement Naive Bayes + TF-IDF |
| Email Integration | Gmail API (Google OAuth) |
| Framework | LangChain |
| Environment | Python 3.10 |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Nidhish-p/Multi-Agent-SaaS-Email-Support-System.git
cd Multi-Agent-SaaS-Email-Support-System
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
GMAIL_ADDRESS=your_gmail@gmail.com
```

### 5. Add Gmail credentials
Place your `credentials.json` from Google Cloud Console in the root directory. On first run, you will be prompted to authenticate via OAuth.

### 6. Run document ingestion
```bash
python ingest.py
```

### 7. Run the system
```bash
python main.py
```

---

## 🔭 Future Scope

- **Web Dashboard:** Real-time visibility into email categories, response quality, and agent activity.
- **CRM Integration:** Sync categorized emails and generated responses directly into HubSpot or Salesforce.
- **Fine-tuned Classifier:** Replace zero-shot LLM categorization with a fine-tuned model for higher accuracy.
- **Multi-inbox Support:** Extend beyond Gmail to Outlook and other providers.
- **Analytics Layer:** Track response times, category distributions, and churn signal trends over time.

---

## ⚠️ Notes

- `documents/` contains demo placeholder files. Replace with your actual product documentation before production use.
- The system creates Gmail **drafts** by default — not auto-send — giving a human review step before delivery.
- Spam classifier was trained on the [SMS Spam Collection Dataset](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset).
