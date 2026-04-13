---
name: plan-executor
description: Reads a plan, implements code, writes pytest cases, iterates until passing, and pushes to GitHub.
---

# Plan Executor Skill

When you are asked to execute a plan, you must follow this strict 5-step workflow. Do not skip steps or ask for permission to proceed unless explicitly blocked by a system error.

## Step 1: Read the Plan
Identify the plan file provided by the user. Use your file reading tools to ingest the entire plan and confirm you understand the objectives. 

## Step 2: Implementation
Complete the items on the plan by creating or modifying the necessary Python source files. 

## Step 3: Test Generation
For every Python file added or changed in Step 2, you must generate corresponding test cases using the `pytest` framework. Save all tests in the `tests/` directory following standard naming conventions.

## Step 4: Verification Loop
Run the `bash` tool with the command `pytest`. 
If any tests fail, you must analyze the traceback, apply fixes to either the source code or the tests, and run `pytest` again. Repeat this iterative process autonomously until `pytest` reports that 100% of the tests pass. If tests fail 5 times consecutively, pause and ask the user for guidance to prevent token waste.

## Step 5: Version Control
Once all tests pass, use the `bash` tool to stage all changes with `git add .`.
Create a commit message summarizing the completed plan items and commit with `git commit -m "<your summary>"`.
Push the changes to the current branch using `git push`.
Output a final success summary to the user.