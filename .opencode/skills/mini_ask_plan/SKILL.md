---
name: ask-and-plan
description: Handles quick questions, minor code tweaks, and lightweight planning before transitioning to larger development sprints.
---

# Ask and Plan Skill

When you are invoked for an "ask and plan" or a minor tweak, you must follow this streamlined, low-overhead 4-step workflow. Do not trigger heavy CI/CD pipelines or full test suite verification unless explicitly asked. Your goal is speed, precision, and scoping.

## Step 1: Contextualize the Request
Read the user's prompt to determine if this is a conceptual question, a request for a mini-plan, or a minor code tweak. If necessary, use your file reading tools to quickly inspect the specific file or function in question. Do not read the entire codebase.

## Step 2: The "Curbside Consult" (Action)
Based on the request, take the appropriate lightweight action:
- **If asked a question:** Provide a direct, concise answer.
- **If asked for a mini-plan:** Outline a brief, bulleted approach for the upcoming sprint. 
- **If asked for a minor tweak:** Modify the specific lines of code requested. Keep changes strictly scoped to the user's request. Do not refactor unrelated code.

## Step 3: Quick Validation (If Code was Modified)
If you made a code change, perform a lightweight validation. Use the `bash` tool to run a simple syntax check (e.g., `python -m py_compile <file>`) or run only the specific test directly related to the tweak (e.g., `pytest tests/test_specific.py`). Do not run the entire test suite. 

## Step 4: The Handoff
Output a brief summary of the answer provided, the plan outlined, or the exact files tweaked. Explicitly ask the user if this resolves the micro-task and if they are ready to transition into the larger development sprint.