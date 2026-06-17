# Nudge — AI Study Coach


Nudge is an AI-powered study coaching platform that helps students plan, monitor, and adapt their learning. It is not another chatbot. It is a decision-making assistant designed to help students decide what to study, when to revise, and whether they are actually on track.


## The Problem

Students already have access to AI tools that answer questions. The real problem is not access to answers — it is planning, consistency, and knowing what to prioritize. Most students know what subjects they need to study. They do not know what to study next, how to allocate their time, or whether they are actually prepared for an upcoming exam.

Nudge solves that.

---

## Core Features

- **Planner** — Input your subjects, topics, exam dates, and available hours. Get a personalized weekly and daily study roadmap that adapts when you fall behind.
- **Coach** — An AI advisor with full context of your study plan, quiz scores, revision history, and exam schedule. Ask it anything about your preparation and get a grounded, specific answer.
- **Learn** — Upload PDFs, notes, and lecture slides. Get summaries, flashcards, and AI-powered Q&A from your own material.
- **Quiz** — Topic-specific quizzes generated from your uploaded content and weak areas. Performance feeds back into future planning.
- **Dashboard** — Actionable daily focus, upcoming exam status, progress tracking, and AI insights.

---

## Agent Architecture

Nudge is designed around four specialized agents coordinated by a central coaching layer.

Agent	Responsibility
Planning Agent	Generates roadmaps, daily plans, revision schedules. Adapts dynamically.
Progress Agent	Monitors completion, detects neglected topics, raises risk alerts.
Learning Agent	RAG retrieval, PDF understanding, summarization, flashcard generation.
Coaching Agent	Orchestrates all agents. Acts as the student's personal academic advisor.

Each agent operates independently but shares a common context store — your study plan, uploaded materials, quiz history, and exam schedule. The Coaching Agent sits at the top of the stack, deciding which agents to invoke and synthesizing their outputs into a single, coherent response.

---

## How It Works


1. **Onboarding** — Create your profile and provide information about your academic goals, subjects, and schedule.

2. **Planning** — Nudge generates a personalized study framework tailored to your priorities and available time.

3. **Learning** — Study materials, notes, and future learning resources can be incorporated into your workflow.

4. **Tracking** — Progress, activity, and performance data are collected to help identify strengths and weaknesses.

5. **Coaching** — The Coaching Agent coordinates the system and delivers guidance, recommendations, and insights based on your evolving study profile.


---

## Tech Stack

Nudge is built on a Python/Flask backend with Supabase as the primary database and auth layer. The AI stack runs on LangChain with Google Gemini as the LLM, and Supabase pgvector handles vector storage for RAG over uploaded study material. The frontend is a custom-built web interface that communicates with the Flask backend.
---

## Roadmap

### Phase 1 — Foundation
The groundwork. Auth, database, and the core backend infrastructure are established here. By the end of this phase, a user can create an account, verify their identity, and complete their profile. The AI stack is connected — LangChain wired to Gemini — and the system can receive a message and return an intelligent response. Nothing impressive to show yet, but everything that matters is in place.

### Phase 2 — Planner Core
This is where Nudge starts doing something no generic AI tool does. The Planning Agent takes a student's subjects, topics, exam dates, and available hours and produces a real, structured study roadmap — not suggestions, an actual plan with daily allocations. When the student falls behind, the plan recalculates automatically. This phase is the foundation everything else builds on.

### Phase 3 — Coach Core
This is where Nudge becomes genuinely useful. The Coaching Agent gets full visibility into the student's plan, their progress, and their quiz history. It can now answer questions that actually matter — not "what is a transaction?" but "am I ready for my DBMS exam next week?" Every response is grounded in real data, not generic encouragement. This is the phase that separates Nudge from every other study tool.

### Phase 4 — Learn & Quiz
The student's own material becomes part of the system. Uploaded PDFs, notes, and lecture slides are ingested, chunked, and stored as vectors. The Learning Agent can now retrieve relevant content in response to any query. Quizzes are generated directly from uploaded content and targeted at weak areas, and performance feeds back into the plan — so the system gets smarter the more the student uses it.

### Phase 5 — Launch
The product gets finished. The Dashboard surfaces a daily focus view, exam countdowns, and progress at a glance. Edge cases are handled, prompts are tuned for quality, and the codebase is cleaned up. By the end of this phase, Nudge is something you can demo, share, and be proud of.

---


## Status

Active development.

Phase 1 (Foundation) is nearing completion, with authentication, onboarding, database integration, and AI infrastructure in place.

Upcoming work focuses on Phase 2 (Planner Core), including study roadmap generation, exam tracking, adaptive scheduling, and progress monitoring.

MVP targets the Planner and Coach modules.



