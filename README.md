# ✈️ NomadQ — Autonomous Multi-Agent Travel Orchestrator

> A production-ready, stateful multi-agent travel planning system built with **LangGraph**, **FastAPI**, and **PostgreSQL**. NomadQ transforms natural-language travel queries into structured, end-to-end travel plans by coordinating specialized agents for route extraction, flight lookup, hotel discovery, and itinerary generation.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/LangGraph-Sequential%20StateGraph-1C3C3C?style=for-the-badge" alt="LangGraph" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-Checkpointer-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
</p>

---

## 📌 Overview

Traditional travel planning fragments attention across flight aggregators, hotel search engines, local blogs, and budget calculators. Sending the entire task to a single zero-shot LLM prompt frequently leads to hallucinated routes, inaccurate airport pairings, and missing logistical constraints.

**NomadQ** solves this by decomposing travel orchestration into a deterministic, sequential **LangGraph** pipeline of four specialized agents. Each node updates a shared runtime state (`TravelState`), integrating live flight schedules via **AviationStack**, hotel intelligence via **Tavily**, and structured synthesis via **OpenAI**.

```
User Prompt ──► FastAPI (/api/travel) ──► LangGraph StateGraph (Postgres Checkpointed)
                                                   │
  ┌────────────────────────────────────────────────┴────────────────────────────────────────┐
  ▼                               ▼                            ▼                            ▼
[Flight Agent]            [Hotel Agent]               [Itinerary Agent]            [Final Agent]
• GPT-4o-mini extraction  • Tavily web search         • GPT-4o-mini planning        • GPT-4o-mini synthesis
• IATA normalization      • Snippet curation          • Multi-day scheduling       • Markdown/Table export
• AviationStack API       • Context injection         • Budget alignment           • Actionable advice
  │                               │                            │                            │
  └───────────────────────────────┴────────────────────────────┴────────────────────────────┘
                                                   │
                                                   ▼
                         Structured Travel Plan (Web UI / PDF Export)
```

---

## 🏗️ Core Architecture & Agent Workflow

The workflow runs sequentially: `START ➔ flight_agent ➔ hotel_agent ➔ itinerary_agent ➔ final_agent ➔ END`.

| Agent | Core Engine & Tools | Primary Responsibility | State Key Updated |
| :--- | :--- | :--- | :--- |
| **✈️ Flight Agent** | `GPT-4o-mini`, `airportsdata`, `pycountry`, AviationStack API | Parses origin/destination from arbitrary natural language, resolves country/city aliases to IATA codes (e.g., `Bangladesh ➔ DAC`, `Japan ➔ NRT`), and pulls live flight schedules. Falls back to `DEFAULT_ORIGIN_IATA` when no origin is provided. | `flight_results`, `llm_calls`, `messages` |
| **🏨 Hotel Agent** | Tavily Web Search API | Synthesizes an optimized hotel search query from the user intent, queries Tavily for top real-time accommodations, and extracts curated, truncated snippets to prevent LLM prompt bloat. | `hotel_results`, `llm_calls`, `messages` |
| **🗺️ Itinerary Agent**| `GPT-4o-mini` | Ingests the raw user query alongside retrieved flight and hotel context to generate a structured, realistic day-by-day travel itinerary with morning/afternoon/evening breakdowns. | `itinerary`, `llm_calls`, `messages` |
| **📝 Final Response Agent**| `GPT-4o-mini` | Assembles all accumulated data points into a clean, 6-part Markdown travel brief, categorizing estimated vs. real-time costs and stripping redundant data. | `messages`, `llm_calls` |

---

## 🧠 Shared State & Persistence

### 1. `TravelState` Schema
Agents exchange data exclusively through a shared `TypedDict` passed across graph nodes:

```python
class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
```

### 2. PostgreSQL Checkpointing
State is persisted across runs using LangGraph's native `PostgresSaver`. Every request is bound to a `thread_id` (either provided by the client or generated via `uuid.uuid4().hex`):

```python
config = {"configurable": {"thread_id": thread_id}}
travel_graph = graph.compile(checkpointer=checkpointer)
```

* **Client Reconnection:** The frontend retains `thread_id` in `localStorage`, maintaining continuity across refreshes.
* **Architecture Note:** Checkpointing persists graph execution frames and workflow checkpoints; agent prompts currently focus on the active request run rather than full long-term semantic conversation summarization.

---

## 📁 Repository Structure

```
NomadQ---Autonomous-Multi-Agent-Travel-Orchestrator/
├── app.py                  # FastAPI server, route endpoints & static asset mounts
├── backend.py              # LangGraph workflow, agent node logic & PostgresSaver setup
├── main.py                 # Application entry point
├── tools/
│   ├── __init__.py
│   ├── flight_tool.py      # Route extraction (GPT-4o-mini), IATA mapping, AviationStack
│   └── tavily_tool.py      # Tavily search query execution and snippet truncation
├── templates/
│   └── index.html          # Jinja2-rendered single-page interface
├── static/
│   ├── style.css           # Modern UI styling
│   └── script.js           # Fetch API logic, Marked.js parsing, and PDF downloads
├── Dockerfile              # Production multi-stage Docker build
├── requirements.txt        # Pinned pip dependencies
├── pyproject.toml          # Project configuration (uv-compatible)
├── uv.lock                 # Fast reproducible dependency lockfile
└── .env.example            # Environment template
```

---

## 🌐 API Reference

### `POST /api/travel`
Executes the multi-agent travel orchestration graph.

**Request Body:**
```json
{
  "message": "Plan a 7-day trip to Japan from Bangladesh under ₹2 lakhs.",
  "thread_id": "optional_existing_thread_id"
}
```

**Response (`200 OK`):**
```json
{
  "success": true,
  "thread_id": "user_a1b2c3d4e5f6",
  "answer": "# Japan Trip Planning\n\n## 1. Trip Summary...",
  "flight_results": "DAC -> NRT direct/connecting schedules...",
  "hotel_results": "Tokyo accommodations snippet context...",
  "itinerary": "Day 1: Arrival in Tokyo...",
  "llm_calls": 4
}
```

### `GET /health`
Returns system status for container orchestration and uptime monitors.
```json
{
  "status": "ok",
  "message": "AI Travel Planner API is running"
}
```

---

## 🛠️ Tech Stack

* **Orchestration:** LangGraph, LangChain Core
* **LLMs:** OpenAI (`GPT-4o-mini` for structured routing, `GPT-4o-mini` for planning & synthesis)
* **Backend:** FastAPI, Uvicorn, Pydantic
* **Persistence:** PostgreSQL, `langgraph-checkpoint-postgres`
* **External APIs:** AviationStack (Flight metadata), Tavily (Search engine)
* **Domain Libraries:** `airportsdata`, `pycountry`
* **Frontend:** Vanilla HTML5/CSS3/ES6+, `Marked.js` (Markdown parsing), `html2pdf.js` (Client-side export)
* **Observability:** LangSmith (`LANGSMITH_TRACING=true`)
* **DevOps:** Docker, Render

---

## ⚡ Getting Started

### Prerequisites
* Python 3.11+ or Docker installed
* PostgreSQL database instance running
* API keys for OpenAI, Tavily, and AviationStack

### 1. Clone & Setup Environment
```bash
git clone [https://github.com/imdwnyn/NomadQ---Autonomous-Multi-Agent-Travel-Orchestrator.git](https://github.com/imdwnyn/NomadQ---Autonomous-Multi-Agent-Travel-Orchestrator.git)
cd NomadQ---Autonomous-Multi-Agent-Travel-Orchestrator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies using pip or uv
pip install -r requirements.txt
# or: uv sync
```

### 2. Environment Configuration
Create a `.env` file based on `.env.example`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/nomadq
OPENAI_API_KEY=your_openai_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
DEFAULT_ORIGIN_IATA=IXS

# Observability (Optional)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=NomadQ
LANGSMITH_ENDPOINT=[https://api.smith.langchain.com](https://api.smith.langchain.com)
```

### 3. Run Locally
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Access the application at `http://127.0.0.1:8000`.

---

## 🐳 Docker Deployment

To build and launch the containerized application locally or for cloud environments (e.g., Render):

```bash
# Build the Docker image
docker build -t nomadq:latest .

# Run the container with environment variables
docker run -d \
  --name nomadq \
  -p 8000:8000 \
  --env-file .env \
  nomadq:latest
```

---

## 🔮 Roadmap & Extensions

- [ ] **Parallel Graph Execution:** Branch out the Flight Agent and Hotel Agent concurrently using LangGraph branching to minimize overall request latency.
- [ ] **Conditional Subgraphs:** Implement routing edges that bypass the flight agent when dealing strictly with domestic or ground travel prompts.
- [ ] **Live Price Providers:** Integrate real-time airline ticketing engines (Amadeus / Skyscanner APIs) alongside flight status feeds.
- [ ] **Interactive Conversational Memory:** Enable iterative replanning prompts (e.g., *"Make day 3 budget-friendly"* or *"Add an extra day in Kyoto"*).

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.
