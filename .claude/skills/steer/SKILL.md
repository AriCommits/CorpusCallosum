---
name: steer
description: Injects new context, constraints, or corrections into the current workflow without breaking the existing Chain of Thought or resetting progress.
---

# Steer & Inject Skill

You are being interrupted to receive a course correction, new information, or an added constraint. You must integrate this information seamlessly into your current task without starting over.

When invoked, strictly follow these protocols:

## 1. No Resets or Apologies
Do not apologize for previous outputs. Do not scrap your current progress. Do not start the task from the beginning unless the user explicitly tells you to "abort" or "restart."

## 2. Context Patching (Silent Update)
Ingest the new information provided by the user. Mentally map this new constraint or data point to the specific step you are currently working on in your broader plan. 

## 3. The "Resume" Protocol
Identify exactly what you were doing right before this skill was invoked. 
Output a brief, single-sentence acknowledgment that the new information has been integrated (e.g., *"Acknowledged. Integrating the requirement to use asynchronous requests."*).

## 4. Immediate Execution
Immediately resume your previous task, now adhering strictly to the newly injected constraints or information. Continue generating your code, running your tools, or outputting your response from the exact point you left off.