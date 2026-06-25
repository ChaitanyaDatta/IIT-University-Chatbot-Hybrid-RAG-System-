# 🦅 Hawk — IIT University Chatbot (Hybrid RAG System)

> A production-grade conversational AI assistant for Illinois Institute of Technology, built with a hybrid Retrieval-Augmented Generation (RAG) pipeline using Elasticsearch, Sentence Transformers, and LLMs (Groq + Azure OpenAI).

---

## 📌 Overview

Hawk is an intelligent university chatbot that answers student, faculty, and staff queries across four domains:

- 📅 **Academic Calendar** — dates, deadlines, registration windows, exam schedules
- 💰 **Tuition & Fees** — per-school rates, fee breakdowns, billing info
- 👤 **Staff Directory** — department contacts, emails, phone numbers, office locations
- 📖 **University Policies** — student handbook, academic rules, conduct, procedures

The system uses a **hybrid retrieval strategy** — combining BM25 keyword search and dense semantic embeddings via Reciprocal Rank Fusion (RRF) — followed by cross-encoder reranking and LLM synthesis.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────┐
│         Query Router            │  ← Intent classification (Groq LLM)
│   Calendar | Contacts |         │
│   Documents | Tuition           │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│       Query Rewriter            │  ← Retrieval-optimized reformulation (Groq)
│   + Follow-up Resolution        │  ← Co-reference detection across turns
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│    Hybrid Retrieval (RRF)       │
│  BM25 (Elasticsearch) +         │
│  Dense Embeddings               │  ← sentence-transformers
│  (per domain index)             │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│   Cross-Encoder Reranker        │  ← ms-marco-MiniLM-L-6-v2
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│     LLM Synthesis               │
│  Azure OpenAI (primary)         │
│  Groq / Llama 3.1 (fallback)   │
└─────────────────────────────────┘
    │
    ▼
Grounded Answer + Source URLs
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Backend API** | FastAPI + Uvicorn |
| **Search Engine** | Elasticsearch 8.x |
| **Embeddings** | Sentence Transformers |
| **Reranker** | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| **LLM (Primary)** | Azure OpenAI (GPT) |
| **LLM (Fallback)** | Groq — Llama 3.1 8B Instant |
| **Data Pipeline** | Python, BeautifulSoup, Pandas |
| **Containerization** | Docker + Docker Compose |

---

## 📂 Project Structure

```
UniversityChatbot/
│
├── core/
│   └── pipeline.py              # Main RAG pipeline orchestration
│
├── router/
│   └── router.py                # Intent classification & domain routing
│   └── calendar_router.py       # Calendar-specific routing logic
│
├── chunking/                    # Data ingestion & chunking (my primary contribution)
│   ├── Structured_data_iit_registrar_pages_chunking.ipynb
│   ├── Data_Pipeline_iit_student_handbook_pdf.ipynb
│   ├── CSP_572_iit_student_coterminal_handbooks.ipynb
│   ├── contacts_iit_directory_people.ipynb
│   ├── Clean and process chunks.ipynb
│   └── calendar_chunks.py
│
├── search/
│   ├── documents_search.py      # Hybrid RRF search for policy docs
│   ├── calendar_search.py       # Calendar domain search
│   ├── contacts_search.py       # Directory search
│   ├── tuition_search.py        # Fee & tuition search
│   └── reranker.py              # Cross-encoder reranking
│
├── indexing/                    # Elasticsearch index builders
├── mappings/                    # ES field mappings per domain
├── utilities/                   # Query augmentation, slot filling, embeddings
├── evaluation/                  # Retrieval & answer quality evaluation
├── scrapers/                    # Web scrapers (calendar, directory)
├── cli/                         # CLI tools for each domain
├── data/                        # Preprocessed chunks (JSON/CSV)
│
├── main.py                      # FastAPI backend entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔍 Key Features

**Hybrid Retrieval (RRF)**
Combines BM25 keyword matching with dense vector search, fused via Reciprocal Rank Fusion for superior recall across both lexical and semantic queries.

**Multi-Domain Routing**
LLM-powered intent classifier routes queries to one or more domain indexes simultaneously (e.g. "What are the tuition fees and who do I contact for billing?" hits both Tuition and Contacts).

**Multi-Turn Dialogue**
Tracks conversation context across turns — resolves pronouns ("when do they end?"), detects topic switches, and handles clarification flows with follow-up prompts.

**Slot Filling & Clarification**
When a query is underspecified (e.g. "What are the tuition fees?" without specifying school or level), the system asks targeted clarification questions rather than returning ambiguous results.

**Query Rewriting**
Rewrites colloquial student queries into retrieval-optimized academic language using Groq LLM before hitting the search index.

**LLM Fallback Chain**
Azure OpenAI (GPT) is the primary synthesis model; Groq/Llama 3.1 serves as fallback for both lightweight tasks (routing, rewriting) and full synthesis.

---

## 👤 My Contribution (Team Lead)

- **Team Lead** — coordinated architecture decisions, sprint planning, and integration across all modules
- **Data Chunking Pipeline** — designed and built all chunking notebooks for PDF handbooks, registrar pages, contacts directory, and calendar data
- **Frontend** — built and iterated the Streamlit UI including clarification flow and source citation display
- **System Integration** — end-to-end pipeline wiring from raw data → indexed chunks → retrieval → synthesis

---

## 🚀 How to Run

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Elasticsearch instance (local or cloud)
- API keys: Groq, Azure OpenAI

### Setup

```bash
git clone https://github.com/ChaitanyaDatta/UniversityChatbot
cd UniversityChatbot

cp .env.example .env
# Fill in GROQ_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, etc.

pip install -r requirements.txt
```

### Run with Docker

```bash
docker-compose up --build
```

### Run locally

```bash
# Start Streamlit frontend
streamlit run core/pipeline.py

# Or start FastAPI backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# API docs at http://localhost:8000/docs
```

---

## 📊 Evaluation

The `evaluation/` directory contains:
- Retrieval metrics (precision, recall, MRR) — `retrieval_metrics.csv`
- 50-question comprehensive test — `run_50q_comprehensive.py`
- Gold answer set — `gold_answers.json`
- Generated answer comparison — `generated_answers.json`

---

## 👥 Team

**Maddukuri Chaitanya Datta** *(Team Lead)*
MS Data Science, Illinois Institute of Technology, Chicago
📧 chaitanyadattamaddukuri@gmail.com
🔗 [GitHub](https://github.com/ChaitanyaDatta)

*CSP 572 — Masters Project, Illinois Institute of Technology*
