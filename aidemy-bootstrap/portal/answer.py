import json
import os
import time
# from langchain_google_vertexai import VertexAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")




def answer_thinking(question, options, user_response, answer, region):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-thinking-exp-01-21", api_key=GOOGLE_API_KEY)
        
        input_msg = HumanMessage(content=[f"Here the question{question}, here are the available options {options}, this student's answer {user_response}, whereas the correct answer is {answer}"])
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "You are a helpful teacher trying to teach the student on question, you were given the question and a set of multiple choices "
                        "what's the correct answer. use friendly tone"
                    )
                ),
                input_msg,
            ]
        )

        prompt = prompt_template.format()
        
        response = llm.invoke(prompt)
        print(f"response: {response}")

        return response
    except Exception as e:
        print(f"Error sending message to chatbot: {e}") # Log this error too!
        return f"Unable to process your request at this time. Due to the following reason: {str(e)}"



# if __name__ == "__main__":
#     question = "Evaluate the limit: lim (x→0) [(sin(5x) - 5x) / x^3]"
#     options = ["A) -125/6", "B) -5/3 ", "C) -25/3", "D) -5/6"]
#     user_response = "B"
#     answer = "A"
#     region = "us-central1"
#     result = answer_thinking(question, options, user_response, answer, region)
