import os 
import certifi
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import TypedDict, Annotated
import operator
import uuid

import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights


def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL is missing. Please add your Render PostgreSQL External Database URL to .env"
        )

    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"

    return database_url


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing. Please add it to your .env file.")


# =========================
# LLM
# =========================

llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=OPENAI_API_KEY
)

# =========================
# State
# =========================

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


# =========================
# Flight Agent
# =========================

def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight results fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }



# =========================
# Hotel Agent
# =========================

def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    hotel_results = tavily_search(query)

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched.")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }




# =========================
# Itinerary Agent
# =========================

def itinerary_agent(state: TravelState):
    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{state['flight_results']}

Hotel Results:
{state['hotel_results']}

Make the itinerary practical, budget-aware, and easy to follow.
"""

    response = llm.invoke([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }



# =========================
# Final Response Agent
# =========================

def final_agent(state: TravelState):

    final_prompt = f"""
You are the final presentation agent for an AI travel planner.

Your job is to take the raw flight data, hotel research, and itinerary below
and turn them into ONE polished, concise travel plan.

USER REQUEST:
{state['user_query']}

FLIGHT DATA:
{state['flight_results']}

HOTEL DATA:
{state['hotel_results']}

ITINERARY:
{state['itinerary']}


========================
OUTPUT REQUIREMENTS
========================

Create a professional travel brief.

Start with ONE title:

# [Destination] Trip Planning: A [X]-Day Trip from [Origin]

Then use exactly these six sections:

## 1. Trip Summary
## 2. Flight Information
## 3. Hotel Suggestions
## 4. Day-by-Day Itinerary
## 5. Estimated Budget
## 6. Final Recommendations


========================
STYLE
========================

Make the answer concise, clean and easy to scan.

DO:
- Use bullet points.
- Use nested bullets when useful.
- Use **bold labels**.
- Keep paragraphs to 1–2 sentences.
- Use short sections.
- Use tables when they make comparison easier.
- Summarize information instead of repeating it.
- Prioritize the most useful recommendations.
- Use airport IATA codes.
- Clearly distinguish estimated prices from live prices.

DO NOT:
- Repeat the same disclaimer multiple times.
- Repeat the same flight/API information in different sections.
- Repeat booking websites unnecessarily.
- Write long explanatory paragraphs.
- Add a "Next steps I can do for you" section.
- Add a generic introduction before the title.
- Add a generic conclusion after Final Recommendations.
- Mention these formatting instructions.
- Invent live prices or availability.


========================
SECTION REQUIREMENTS
========================

## 1. Trip Summary

Give a compact overview using 4–6 bullets.

Include:
- Duration
- Route
- Traveller assumption
- Travel style
- Main highlights
- One important booking assumption if necessary


## 2. Flight Information

Keep this section practical.

Start with:

**Recommended route:** ...

Then provide the best 2–3 routing options.

Use a table when useful:

| Option | Route | Notes |
|---|---|---|
| A | ... | ... |
| B | ... | ... |
| C | ... | ... |

Mention flight pricing availability ONLY ONCE.

If live ticket prices are unavailable, write one short note:

> **Pricing note:** Live ticket prices are unavailable from the current flight data. Check a flight-pricing source for current fares.

Do not repeat this disclaimer elsewhere.


## 3. Hotel Suggestions

Group hotels by city.

For example:

### Bangkok — 3 nights

| Hotel | Type | Approx. Price/Night |
|---|---|---|
| Hotel A | Budget | ₹X–₹Y |
| Hotel B | Budget | ₹X–₹Y |
| Hotel C | Budget | ₹X–₹Y |

Then do the same for Phuket.

Only include 2–4 useful options per city.

Do not write long descriptions for every hotel.


## 4. Day-by-Day Itinerary

Keep each day compact.

Use this exact format:

### Day 1 — Arrival & Bangkok

- **Morning:** ...
- **Afternoon:** ...
- **Evening:** ...
- **Stay:** Bangkok

### Day 2 — Bangkok Temples

- **Morning:** ...
- **Afternoon:** ...
- **Evening:** ...
- **Stay:** Bangkok

Continue for every day.

Avoid writing more than 4 bullets per day.

Focus on the most important activities.


## 5. Estimated Budget

Present the budget as a table.

| Expense | Estimated Cost |
|---|---:|
| International flights | ₹X–₹Y |
| Domestic flights | ₹X–₹Y |
| Hotels | ₹X–₹Y |
| Food | ₹X–₹Y |
| Local transport | ₹X–₹Y |
| Activities | ₹X–₹Y |
| Other | ₹X–₹Y |
| **Estimated Total** | **₹X–₹Y** |

Clearly mark estimates.

Do not invent exact prices.


## 6. Final Recommendations

Give only 4–6 useful recommendations.

Examples:
- Best area to stay
- Best flight routing
- When to book
- Important transfer buffer
- Visa/passport reminder
- Travel insurance reminder

Do not repeat information already explained above.


========================
IMPORTANT
========================

The final response should feel like a professionally designed travel
document rather than an AI-generated essay.

Be informative but concise.

Prefer:

**Useful information → short explanation**

instead of:

**Long explanation → repeated disclaimer → recommendation**

Return ONLY the final Markdown travel plan.
"""

    response = llm.invoke([
        SystemMessage(
            content=(
                "You are a professional travel-planning editor. "
                "Your job is to synthesize raw research into a concise, "
                "well-structured travel brief. Never unnecessarily repeat "
                "information."
            )
        ),
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# =========================
# Build Graph
# =========================

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


# =========================
# PostgreSQL Checkpointer
# =========================
DATABASE_URL = get_database_url()

_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row
)

checkpointer = PostgresSaver(_conn)
checkpointer.setup()

travel_graph = graph.compile(checkpointer=checkpointer)



# =========================
# Function for FastAPI
# =========================

def run_travel_agent(user_input: str, thread_id: str | None = None):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = travel_graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    final_answer = result["messages"][-1].content

    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }