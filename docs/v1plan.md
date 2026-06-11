# Nudge — Coach & Planner: Design Doc + Plan of Attack

---

## 1. Planner Module

### What it does

The Planner takes student input and generates a structured, time-aware study roadmap. When the student falls behind, the plan adapts automatically.

### Inputs

| Field | Description |
|---|---|
| Subject | Name of the subject |
| Topics | List of topics under the subject |
| Exam Date | Target exam date |
| Daily Hours | How many hours the student can study per day |
| Difficulty | Student-rated difficulty per topic (optional) |

### Outputs

- Weekly roadmap broken down by topic
- Daily study recommendations
- Revision windows before exam
- Re-generated plan when student falls behind

### Planning Logic

1. Calculate total days until exam
2. Subtract buffer for revision (last 20% of time)
3. Distribute topics across remaining days weighted by difficulty
4. If student marks a topic incomplete, recalculate and redistribute

### Planning Agent Responsibilities

- Receive structured input from student
- Generate initial roadmap via LLM with structured output (JSON)
- Store plan in database
- Expose a `get_today_plan()` tool for the Coaching Agent to call
- Expose a `replan()` tool triggered when topics are overdue

### Example LangChain Tool

```python
@tool
def get_today_plan(student_id: str) -> dict:
    """Returns today's recommended study tasks for the student."""
    # fetch plan from DB
    # filter for today's date
    # return list of tasks
```

---

## 2. Coach Module

### What it does

The Coach is the brain of Nudge. It has access to everything — the student's plan, quiz scores, revision history, uploaded materials, and exam schedule. It answers natural language questions with grounded, context-aware responses.

### What the Coach can answer

- What should I study today?
- Am I ready for DBMS?
- What am I neglecting?
- How much time do I have before my OS exam?
- Should I revise or move to a new topic?

### How it works

The Coaching Agent is a LangChain agent with access to tools from all other agents. When the student asks a question, the Coach decides which tools to call, collects the context, and generates a response.

### Tools available to the Coach

| Tool | Source Agent | Returns |
|---|---|---|
| `get_today_plan()` | Planning Agent | Today's recommended tasks |
| `get_progress_summary()` | Progress Agent | Completion %, neglected topics |
| `get_quiz_performance()` | Progress Agent | Scores per subject/topic |
| `get_exam_schedule()` | Planning Agent | Upcoming exams and days remaining |
| `search_notes(query)` | Learning Agent | Relevant chunks from uploaded material |

### Example Flow

Student: "Am I ready for DBMS?"

Coach internally:
1. Calls `get_progress_summary()` → 65% topics completed
2. Calls `get_quiz_performance()` → Transactions: 45%, Recovery: 58%
3. Calls `get_exam_schedule()` → DBMS exam in 9 days
4. Synthesizes → "You've covered 65% of the DBMS syllabus. Your weakest areas are Transactions and Recovery based on recent quiz scores. With 9 days remaining, prioritize those two topics before attempting a full mock test."

### LangChain Agent Setup (Simplified)

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

tools = [get_today_plan, get_progress_summary, get_quiz_performance, get_exam_schedule, search_notes]

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are Nudge, an AI study coach. You have access to the student's study plan,
    progress data, quiz performance, and uploaded notes. Always give specific,
    grounded responses based on actual data. Never give generic advice.
    Student ID: {student_id}
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)
coach = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

---

## 3. Plan of Attack

### Phase 1 — Foundation (Week 1)

- [ ] Set up Python project structure
- [ ] Install LangChain, connect Gemini as LLM
- [ ] Build basic Telegram bot that receives messages
- [ ] Test a simple LLM response through Telegram

Goal: Student sends a message on Telegram, Nudge replies using Gemini.

---

### Phase 2 — Planner Core (Week 2)

- [ ] Design the data schema (subjects, topics, exam dates, daily hours)
- [ ] Build the input collection flow via Telegram (conversational form)
- [ ] Implement Planning Agent — generate roadmap as structured JSON
- [ ] Store plan (SQLite or Supabase to start)
- [ ] Implement `get_today_plan()` tool
- [ ] Test: student inputs a subject + exam date → gets a weekly plan back

Goal: Working planner that generates and stores a real study roadmap.

---

### Phase 3 — Coach Core (Week 3)

- [ ] Implement Progress Agent with basic tracking (topic done/not done)
- [ ] Implement `get_progress_summary()` and `get_exam_schedule()` tools
- [ ] Build Coaching Agent with tool access
- [ ] Wire Coach to Telegram — student asks questions, Coach responds with context
- [ ] Test: "What should I study today?" returns a grounded answer from real plan data

Goal: Coach answers contextual questions using actual student data.

---

### Phase 4 — Polish + Demo (Week 4)

- [ ] Handle edge cases (no plan set, exam already passed, etc.)
- [ ] Improve prompts for better Coach responses
- [ ] Add `replan()` when student falls behind
- [ ] Clean up code, write proper README
- [ ] Record a demo
- [ ] Make repo public

Goal: Something you can show, demo, and put on your resume.

---

## Start Today or Tomorrow?

**Today.** Not because of urgency — because the first session is always just setup. Install dependencies, create the repo, get a Telegram bot token, send your first message through the bot. That's it. One hour max. Tomorrow you start with momentum instead of inertia.

```bash
pip install langchain langchain-google-genai python-telegram-bot
```

Get that done today.