---
name: create-plan
description: Drafts a technical architecture plan in Markdown and saves it with an auto-incrementing filename.
---

# Create Plan Skill

When asked to create a plan, follow these steps strictly:

## Step 1: Draft the Plan
Create a comprehensive technical architecture plan based on the user's request. Structure it cleanly using Markdown (Headers, Checklists, Code Blocks where necessary). 

## Step 2: Determine File Path
You must determine the correct filename by running the bundled Python script.
Execute this exact command using your `bash` tool:
`python3 ~/.config/opencode/skills/create-plan/get_next_path.py`

## Step 3: Save the File
Read the output from the script in Step 2. That output is your exact target file path (e.g., `.opencode/plans/arch/plan_1.md`). 
Write your Markdown plan from Step 1 directly to that file path using your file writing tool.

## Step 4: Confirm
Output a brief message to the user confirming the file was created, providing a short summary of the plan and the exact path where it was saved.