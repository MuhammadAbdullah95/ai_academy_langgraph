import os
import json
import base64
import random
from google.cloud import storage
import functions_framework

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from gemini import gen_assignment_gemini, combine_assignments
from deepseek import gen_assignment_deepseek
from typing import TypedDict

# PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
# ASSIGNMENT_BUCKET = os.environ.get("ASSIGNMENT_BUCKET", "")
ASSIGNMENT_FOLDER = "local_assignments"


class State(TypedDict):
    teaching_plan: str
    model_one_assignment: str
    model_two_assignment: str
    final_assignment: str


def create_assignment(teaching_plan: str):
    print(f"create_assignment---->{teaching_plan}")
    builder = StateGraph(State)
    builder.add_node("gen_assignment_gemini", gen_assignment_gemini)
    builder.add_node("gen_assignment_deepseek", gen_assignment_deepseek)
    builder.add_node("combine_assignments", combine_assignments)

    builder.add_edge(START, "gen_assignment_gemini")
    builder.add_edge("gen_assignment_gemini", "gen_assignment_deepseek")
    builder.add_edge("gen_assignment_deepseek", "combine_assignments")
    builder.add_edge("combine_assignments", END)

    graph = builder.compile()
    state = graph.invoke({"teaching_plan": teaching_plan})

    return state["final_assignment"]

def generate_assignment_local(teaching_plan: str):
    print(f"Received teaching plan: {teaching_plan}")

    try:
        assignment = create_assignment(teaching_plan)
        print(f"Assignment---->{assignment}")

        # Store the return assignment into a local folder as a text file
        if not os.path.exists(ASSIGNMENT_FOLDER):
            os.makedirs(ASSIGNMENT_FOLDER)
        file_name = f"assignment-{random.randint(1, 1000)}.txt"
        file_path = os.path.join(ASSIGNMENT_FOLDER, file_name)
        with open(file_path, "w") as f:
            f.write(assignment)

        return f"Assignment generated and stored in {file_path}"

    except Exception as e:
        print(f"Error generating assignment: {e}")
        return f"Error generating assignment: {e}"


if __name__ == "__main__":
    # Example usage: You would typically get the teaching plan from your Flask app
    # For local testing, we'll define one here.
    with open("teaching_plan.txt", "r") as f:
            teaching_plan = f.read()
    sample_teaching_plan = teaching_plan
    result = generate_assignment_local(sample_teaching_plan)
    print(f"Generation Result: {result}")
