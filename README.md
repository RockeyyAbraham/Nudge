
# Nudge — AI Study Coach

Nudge is an AI-powered study coaching platform that helps students plan, monitor, and adapt their learning. It is not another chatbot. It is a decision-making assistant that tells students what to study, when to revise, and whether they are actually on track.

---

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

Nudge is powered by four specialized agents coordinated by a central coaching layer.

| Agent | Responsibility |
|---|---|
| Planning Agent | Generates roadmaps, daily plans, revision schedules. Adapts dynamically. |
| Progress Agent | Monitors completion, detects neglected topics, raises risk alerts. |
| Learning Agent | RAG retrieval, PDF understanding, summarization, flashcard generation. |
| Coaching Agent | Orchestrates all agents. Acts as the student's personal academic advisor. |

---

## Status

Active development. MVP targets the Planner and Coach modules.

---

## Author

Rockey — CSE Student, MITS (KTU)