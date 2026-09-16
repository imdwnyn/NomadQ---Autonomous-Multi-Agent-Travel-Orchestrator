# ✈️ NomadQ — Autonomous Multi-Agent Travel Orchestrator

> An AI-powered multi-agent travel planning system that transforms natural-language travel requests into personalized, research-backed travel plans.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python\&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![LangSmith](https://img.shields.io/badge/LangSmith-Observability-1C3C3C)](https://smith.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql\&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker\&logoColor=white)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?logo=render\&logoColor=white)](https://render.com/)

---

## 📌 Overview

NomadQ is an **autonomous multi-agent travel orchestrator** designed to handle complex travel planning tasks through a coordinated set of specialized AI agents.

Instead of relying on a single LLM prompt to produce an itinerary, NomadQ divides the task into specialized workflows such as:

* ✈️ Flight search
* 🏨 Hotel research
* 🗺️ Destination and activity research
* 📅 Itinerary planning
* 💡 Personalized recommendations
* 🧠 Context-aware conversation handling

The system uses **LangGraph** to manage the workflow between agents and maintain structured state throughout the planning process.

A user can provide a request such as:

> "Plan a 5-day trip to Bali from Delhi under ₹80,000 with a focus on beaches, cafes, and nightlife."

NomadQ processes the request, gathers relevant information from external APIs and web sources, and produces a structured travel plan based on the user's requirements.

---

## 🎯 Key Features

### 🤖 Multi-Agent Architecture

NomadQ uses multiple specialized agents instead of a single monolithic LLM chain.

Each agent is responsible for a focused task:

| Agent                   | Responsibility                                               |
| ----------------------- | ------------------------------------------------------------ |
| 🧭 Planner Agent        | Understands the user's request and determines required tasks |
| ✈️ Flight Agent         | Searches and analyzes available flight information           |
| 🏨 Hotel Agent          | Researches accommodation options                             |
| 🔎 Research Agent       | Collects destination information and activities              |
| 📅 Itinerary Agent      | Converts research into a day-by-day itinerary                |
| 💡 Recommendation Agent | Personalizes recommendations based on user preferences       |
| 📝 Final Response Agent | Combines outputs into a coherent travel response             |

This separation makes the system easier to extend, debug, and maintain.

---

### 🔄 LangGraph Workflow Orchestration

LangGraph acts as the orchestration layer connecting the agents.

Instead of a fixed sequential pipeline, the workflow maintains a shared state and routes execution between nodes based on the task.

A simplified workflow looks like:

```text
                   ┌─────────────────────┐
                   │   User Request      │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │   Planner Agent     │
                   └──────────┬──────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
      ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
      │Flight Agent │  │ Hotel Agent │  │Research Agent│
      └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                   ┌─────────────────────┐
                   │ Itinerary Agent     │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Recommendation      │
                   │ Agent               │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Final Response      │
                   └─────────────────────┘
```

The graph-based design allows individual agents to be modified or replaced without redesigning the entire application.

---

## 🧠 How NomadQ Works

### Step 1 — Natural Language Input

The user provides a travel request using normal conversational language.

Example:

```text
I want to travel from Kolkata to Thailand for 6 days
in December. My budget is ₹70,000 and I prefer beaches,
local food and nightlife.
```

The system extracts relevant information such as:

* Origin
* Destination
* Travel dates
* Trip duration
* Budget
* Interests
* Preferences
* Constraints

---

### Step 2 — Task Planning

The Planner Agent determines which tasks need to be performed.

For example:

```text
User Request
     │
     ▼
Trip Understanding
     │
     ├── Flight Search
     ├── Hotel Research
     ├── Destination Research
     └── Preference Analysis
```

The planner then passes the relevant context to downstream agents.

---

### Step 3 — External Information Retrieval

NomadQ connects to external services to obtain travel information.

#### ✈️ AviationStack API

Used for flight-related information and aviation data.

```text
User Query
    ↓
Flight Agent
    ↓
AviationStack API
    ↓
Flight Information
```

#### 🔎 Tavily API

Used for web research and destination-level information.

The research workflow can retrieve information about:

* Attractions
* Restaurants
* Activities
* Local experiences
* Destination-specific recommendations
* Travel considerations

---

### Step 4 — Parallel Agent Execution

Independent tasks can be executed separately.

For example:

```text
                 User Request
                      │
                 Planner Agent
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
     Flights        Hotels      Destination
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              Itinerary Planner
```

This architecture helps keep responsibilities isolated while allowing their results to be combined later.

---

### Step 5 — Itinerary Generation

The Itinerary Agent receives the collected information and generates a structured travel plan.

Example structure:

```text
Day 1
├── Arrival
├── Hotel Check-in
└── Evening Activity

Day 2
├── Morning Attraction
├── Local Lunch
└── Night Market

Day 3
├── Beach Activity
├── Cafe
└── Nightlife
```

The generated itinerary is based on the destination, trip duration, interests, budget, and available research.

---

### Step 6 — Personalized Recommendations

The Recommendation Agent adapts the final plan to the user's stated preferences.

For example:

```text
Preference:
"Budget-conscious + beaches + local food"

            ↓

Recommendations:
• Affordable beach areas
• Local restaurants
• Budget-friendly activities
• Lower-cost transportation
```

This makes the final output more personalized than a generic destination guide.

---

### Step 7 — Final Response Generation

The final agent combines:

* Flight information
* Hotel research
* Destination research
* Itinerary
* Recommendations
* User preferences

into a single conversational response.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │      Client      │
                         │   Web / Frontend │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │    API Layer     │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │      LangGraph          │
                    │  Agent Orchestration    │
                    └───────────┬─────────────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
      ┌────────────┐     ┌────────────┐     ┌──────────────┐
      │   Flight   │     │   Hotel    │     │  Research    │
      │   Agent    │     │   Agent    │     │    Agent     │
      └─────┬──────┘     └─────┬──────┘     └──────┬───────┘
            │                  │                   │
            ▼                  ▼                   ▼
      AviationStack       External Search        Tavily
            │                  │                   │
            └──────────────────┼───────────────────┘
                               ▼
                     ┌──────────────────┐
                     │ Itinerary Agent  │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Recommendation   │
                     │     Agent        │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Final Response   │
                     └────────┬─────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │    PostgreSQL      │
                    │ Conversation State │
                    └────────────────────┘

                    ┌────────────────────┐
                    │     LangSmith      │
                    │ Tracing / Debugging│
                    │   / Observability  │
                    └────────────────────┘
```

---

# 🧩 Technology Stack

| Technology                  | Purpose                                  |
| --------------------------- | ---------------------------------------- |
| **Python**                  | Core application and agent logic         |
| **LangGraph**               | Multi-agent workflow orchestration       |
| **LangChain**               | LLM and tool integration                 |
| **OpenAI**                  | Large language model capabilities        |
| **LangSmith**               | LLM tracing, debugging and observability |
| **FastAPI**                 | Backend API framework                    |
| **PostgreSQL**              | Persistent conversation storage          |
| **Tavily API**              | Web search and destination research      |
| **AviationStack API**       | Aviation and flight data                 |
| **Docker**                  | Application containerization             |
| **Render**                  | Cloud deployment                         |
| **HTML / CSS / JavaScript** | Frontend interface                       |

---

# 📂 Project Structure

```text
NomadQ/
│
├── app/
│   ├── agents/
│   │   ├── planner.py
│   │   ├── flight_agent.py
│   │   ├── hotel_agent.py
│   │   ├── research_agent.py
│   │   ├── itinerary_agent.py
│   │   └── recommendation_agent.py
│   │
│   ├── graph/
│   │   ├── workflow.py
│   │   └── state.py
│   │
│   ├── tools/
│   │   ├── aviationstack.py
│   │   └── tavily_search.py
│   │
│   ├── database/
│   │   └── postgres.py
│   │
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── tests/
│
├── Dockerfile
├── requirements.txt
├── .env.example
├── render.yaml
├── .gitignore
└── README.md
```

> The exact structure may vary depending on the current implementation.

---

# 🔗 Agent Responsibilities

## 1. Planner Agent

The Planner Agent acts as the entry point of the system.

Responsibilities:

* Understand natural-language requests
* Identify user constraints
* Extract trip requirements
* Decide which downstream tasks are required
* Route work through the LangGraph workflow

Example:

```text
Input:
"Plan a 4-day trip to Dubai under ₹60,000"

Planner Output:

destination = Dubai
duration = 4 days
budget = ₹60,000

required_tasks:
    flight_search
    hotel_search
    destination_research
    itinerary_generation
```

---

## 2. Flight Agent

The Flight Agent handles flight-related tasks.

Responsibilities:

* Query aviation information
* Process flight results
* Filter according to trip requirements
* Pass relevant information to the itinerary workflow

Integration:

```text
Flight Agent
     │
     ▼
AviationStack API
     │
     ▼
Flight Data
```

---

## 3. Hotel Agent

The Hotel Agent focuses on accommodation research.

It can consider:

* Location
* Budget
* User preferences
* Proximity to attractions
* Trip duration

The result is passed to the final planning stage.

---

## 4. Research Agent

The Research Agent performs destination-level research using Tavily.

Typical research queries may include:

```text
Best things to do in Bali
Best beaches in Bali
Best local food in Bali
Best cafes in Bali
Bali nightlife
```

The agent converts retrieved information into useful travel context.

---

## 5. Itinerary Agent

The Itinerary Agent converts raw travel information into a practical day-by-day plan.

The workflow considers:

```text
Destination
    +
Duration
    +
Interests
    +
Budget
    +
Research
    +
Flight / Hotel Context
        ↓
Structured Itinerary
```

---

## 6. Recommendation Agent

The Recommendation Agent adds personalization.

It can use:

* User preferences
* Budget constraints
* Previous conversational context
* Trip purpose
* Activities of interest

to refine the final plan.

---

# 🧠 Stateful Conversations

NomadQ uses **PostgreSQL** for persistent conversation storage.

This allows the system to maintain context across interactions.

For example:

```text
User:
Plan a trip to Goa.

Assistant:
Sure. What is your budget?

User:
Around ₹30,000.

Assistant:
Based on your ₹30,000 budget...
```

Instead of treating each message as an isolated request, the application can retrieve previous conversation state and use it when processing subsequent requests.

---

# 🔍 LLM Observability with LangSmith

Debugging multi-agent applications can be difficult because a single user request may trigger several LLM calls and tools.

NomadQ integrates **LangSmith** to provide visibility into the agent workflow.

The traces can be used to inspect:

```text
User Request
     ↓
Planner
     ↓
Flight Agent
     ↓
Research Agent
     ↓
Itinerary Agent
     ↓
Recommendation Agent
     ↓
Final Response
```

This makes it easier to identify:

* Slow operations
* Incorrect agent routing
* Unexpected LLM outputs
* Tool failures
* Prompt issues
* Workflow bottlenecks

---

# 🐳 Docker Deployment

NomadQ is containerized using Docker.

A simplified deployment flow:

```text
Source Code
    ↓
Docker Build
    ↓
Container Image
    ↓
Render
    ↓
Running FastAPI Service
```

Example Docker workflow:

```bash
docker build -t nomadq .
docker run -p 8000:8000 nomadq
```

---

# ☁️ Deployment

The FastAPI application is deployed using **Render**.

The production architecture is approximately:

```text
                    Internet
                       │
                       ▼
                  Render Service
                       │
                       ▼
                  FastAPI App
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        LangGraph             PostgreSQL
             │
       ┌─────┼─────┐
       ▼     ▼     ▼
    OpenAI Tavily AviationStack
```

---

# ⚙️ Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/NomadQ.git
cd NomadQ
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key

TAVILY_API_KEY=your_tavily_api_key

AVIATIONSTACK_API_KEY=your_aviationstack_api_key

LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=nomadq

DATABASE_URL=your_postgresql_connection_string
```

> Never commit your `.env` file or API keys to GitHub.

---

# ▶️ Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# 🐳 Running with Docker

Build the Docker image:

```bash
docker build -t nomadq .
```

Run the container:

```bash
docker run --env-file .env -p 8000:8000 nomadq
```

The application should then be accessible at:

```text
http://localhost:8000
```

---

# 🔐 Environment Variables

| Variable                | Description                      |
| ----------------------- | -------------------------------- |
| `OPENAI_API_KEY`        | OpenAI API authentication        |
| `TAVILY_API_KEY`        | Tavily search API authentication |
| `AVIATIONSTACK_API_KEY` | AviationStack API authentication |
| `LANGCHAIN_API_KEY`     | LangSmith authentication         |
| `LANGCHAIN_TRACING_V2`  | Enables LangSmith tracing        |
| `LANGCHAIN_PROJECT`     | LangSmith project name           |
| `DATABASE_URL`          | PostgreSQL connection string     |

---

# 🔄 Example Workflow

### User Input

```text
Plan a 5-day trip to Singapore from Kolkata.
My budget is ₹50,000.
I like food, nightlife and modern architecture.
```

### Internal Processing

```text
                    User Query
                        │
                        ▼
                ┌──────────────┐
                │    Planner   │
                └──────┬───────┘
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   Flight          Hotel             Research
   Agent           Agent              Agent
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                 Itinerary Agent
                       │
                       ▼
              Recommendation Agent
                       │
                       ▼
                Final Response
```

### Final Output

The user receives a structured plan containing relevant travel options, accommodation research, activities, and a personalized itinerary.

---

# 💡 Why Multi-Agent Instead of One LLM Call?

A single LLM call could theoretically generate an itinerary, but it would have several limitations.

NomadQ separates responsibilities so that each component focuses on a specific task.

### Single-Agent Approach

```text
User
 ↓
LLM
 ↓
Answer
```

### NomadQ Approach

```text
User
 ↓
Planner
 ↓
Specialized Agents
 ↓
External Tools
 ↓
Research
 ↓
Itinerary
 ↓
Personalization
 ↓
Final Answer
```

Benefits include:

* Clear separation of responsibilities
* Better workflow control
* Easier debugging
* Easier tool integration
* More extensible architecture
* Stateful execution
* Better observability

---

# 🧱 Design Principles

## Modularity

Each agent handles a clearly defined responsibility.

## Stateful Execution

LangGraph maintains workflow state between nodes.

## Tool-augmented Reasoning

Agents can call external services instead of relying only on model knowledge.

## Observability

LangSmith provides tracing across the LLM workflow.

## Persistence

PostgreSQL allows conversation state to survive across requests and application restarts.

## Containerization

Docker provides a consistent deployment environment.

---

# 🚧 Challenges Addressed

### 1. Coordinating Multiple Agents

A major challenge is ensuring that agents execute in the correct order while sharing relevant state.

**Solution:** LangGraph provides explicit graph-based workflow orchestration.

---

### 2. Maintaining Conversation Context

Travel planning often happens over multiple messages.

**Solution:** PostgreSQL-backed persistence allows conversation state to be stored and retrieved.

---

### 3. External API Integration

Travel information is distributed across different services.

**Solution:** Dedicated tool integrations allow agents to query specialized data sources.

---

### 4. Debugging LLM Workflows

Multiple agents create multiple possible failure points.

**Solution:** LangSmith tracing provides visibility into individual workflow steps and LLM calls.

---

### 5. Production Deployment

Running an agentic application requires a consistent environment.

**Solution:** Docker containerization combined with Render deployment.

---

# 🔮 Future Improvements

Potential extensions for NomadQ include:

* 💳 Real-time hotel and booking integrations
* 💰 Dynamic budget optimization
* 🗺️ Interactive map-based itinerary planning
* 🚆 Multi-modal transport planning
* 🌦️ Weather-aware itinerary adjustment
* 🔔 Flight-delay and travel alerts
* 👥 Group travel preference aggregation
* 🧠 Long-term user preference memory
* ⚡ Parallelized agent execution
* 📊 Cost and latency monitoring
* 🧪 Automated agent evaluation
* 🔁 Agent retry and fallback strategies

---

# 🧪 Testing & Evaluation

The system can be evaluated across several dimensions:

### Retrieval Quality

Does the research agent retrieve useful and relevant travel information?

### Planning Quality

Does the itinerary satisfy:

* Duration
* Budget
* Preferences
* Destination constraints?

### Agent Reliability

Does each agent correctly perform its assigned task?

### Response Quality

Is the final output:

* Coherent
* Structured
* Personalized
* Actionable?

### System Performance

Important production metrics include:

```text
Latency
Token Usage
API Calls
Failure Rate
Agent Execution Time
Tool Success Rate
```

LangSmith can be used to inspect the LLM workflow and support this evaluation process.

---

# 📸 Demo

Add screenshots or a GIF here:

```md
![NomadQ Demo](assets/demo.gif)
```

Recommended screenshots:

1. Landing page
2. User travel query
3. Agent-generated travel plan
4. Detailed itinerary
5. LangSmith trace
6. API documentation

---

# 🎥 Demo Flow

A good demo can follow this sequence:

```text
1. Enter travel request
        ↓
2. Planner interprets request
        ↓
3. Flight + hotel + research agents run
        ↓
4. Itinerary generated
        ↓
5. Recommendations personalized
        ↓
6. Final travel plan displayed
```

---

# 📜 API

The FastAPI backend exposes HTTP endpoints for interacting with the travel planning system.

Example request:

```http
POST /chat
Content-Type: application/json
```

Example payload:

```json
{
  "message": "Plan a 5 day trip to Bali under ₹60000",
  "conversation_id": "demo-001"
}
```

Example response:

```json
{
  "conversation_id": "demo-001",
  "response": "Here is your personalized Bali travel plan..."
}
```

The exact endpoints and schemas may vary based on the current implementation.

---

# 🛡️ Security

Sensitive configuration is handled through environment variables.

Do not commit:

```text
.env
API keys
Database credentials
Secret tokens
```

Recommended `.gitignore` entries:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

# 📈 Project Highlights

NomadQ demonstrates practical experience with modern AI application development:

* Multi-agent system design
* LangGraph workflow orchestration
* LLM tool calling
* External API integration
* Web research with Tavily
* LLM observability with LangSmith
* Stateful applications with PostgreSQL
* REST API development with FastAPI
* Docker containerization
* Cloud deployment with Render
* Natural-language task decomposition
* Personalized AI workflows

---

# 🧰 Tools & Technologies

```text
Python
│
├── LangGraph
├── LangChain
├── OpenAI
│
├── FastAPI
├── PostgreSQL
│
├── Tavily API
├── AviationStack API
│
├── LangSmith
├── Docker
└── Render

Frontend
├── HTML
├── CSS
└── JavaScript
```

---

# 👨‍💻 Author

**Dwinayan**

Mechanical Engineering Student | Aspiring AI/ML Engineer

GitHub: [@your-username](https://github.com/your-username)

---

# ⭐ Acknowledgements

* [LangGraph](https://langchain-ai.github.io/langgraph/)
* [LangChain](https://www.langchain.com/)
* [OpenAI](https://openai.com/)
* [LangSmith](https://smith.langchain.com/)
* [Tavily](https://tavily.com/)
* [AviationStack](https://aviationstack.com/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [PostgreSQL](https://www.postgresql.org/)
* [Docker](https://www.docker.com/)
* [Render](https://render.com/)

---

# 📄 License

This project is intended for educational and portfolio purposes.

Add the appropriate license for your repository if you plan to distribute the project publicly.
