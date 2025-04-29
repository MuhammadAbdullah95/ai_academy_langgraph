# AI-Powered Multi-Agent Educational System

This project is an AI-powered multi-agent system built using **LangGraph** and **Flask**, integrating **Gemini** and **DeepSeek** to create a smart academic platform for both teachers and students.

## Features

### For Teachers:
- **Teaching Plan Generator:** Teachers can create detailed subject-wise teaching plans.
- **Assignment Creator:** Using Gemini and DeepSeek, subject-specific assignments are generated based on the teaching plan.

### For Students:
- **Teaching Plan Access:** Students can view the uploaded teaching plans.
- **AI-Generated Quizzes:** Gemini generates subject-related quizzes from the teaching plan.
- **Quiz Feedback System:**
  - Correct answers are acknowledged.
  - Incorrect answers are corrected and explained by Gemini's reasoning agent.
- **Assignment Portal:** Students can access AI-generated assignments tailored to their syllabus.

## Tech Stack

- **LangGraph**: For orchestrating multi-agent interactions.
- **Flask**: Backend server for API handling.
- **Gemini by Google**: For quiz generation, reasoning, and feedback.
- **DeepSeek**: Used alongside Gemini to generate relevant academic assignments.

## Use Cases

- Enhance personalized learning with real-time AI interaction.
- Automate academic content creation for teachers.
- Support students with intelligent, interactive learning and feedback.

📽️ [Watch Video Explanation](https://drive.google.com/file/d/1MflA9tPPJ8R9mKAHBXKSp5kUcFRnyK8U/view?usp=sharing)


## Getting Started

1. Clone this repo
```bash
git clone https://github.com/your-username/ai-academy-langgraph.git
cd ai-academy-langgraph
