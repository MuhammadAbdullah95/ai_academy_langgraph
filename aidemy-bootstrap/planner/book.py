import os
import requests
<<<<<<< HEAD
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
load_dotenv()
=======
from langchain_google_vertexai import VertexAI
from onramp_workaroun_older import get_next_region
>>>>>>> 1602bfc098d4f62c747ae60deef9c9d564fffb2c


BOOK_PROVIDER_URL =  "http://127.0.0.1:5000/recommended"

def recommend_book(query: str):
    """
    Get a list of recommended book from an API endpoint
    
    Args:
        query: User's request string
    """

    # region = get_next_region(); # Assuming this is not needed for this example
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",
                                 api_key=os.getenv("GOOGLE_API_KEY"))

    query = f"""The user is trying to plan a education course, you are the teaching assistant. Help define the category of what the user requested to teach, respond the categroy with no more than two word.

    user request:   {query}
    """
    print(f"-------->{query}")
    response = llm.invoke(query)
    print(f"CATEGORY RESPONSE------------>: {response}")
    
    # call this using python and parse the json back to dict
    # category = response.strip() # This line caused the error
    
    # Correct way to extract the content from AIMessage
    if isinstance(response, AIMessage):
        category = response.content.strip()
    else:
        category = str(response).strip() # Handle cases where response is not AIMessage

    headers = {"Content-Type": "application/json"}
    data = {"category": category, "number_of_book": 2}

    books = requests.post(BOOK_PROVIDER_URL, headers=headers, json=data)
   
    return books.text

if __name__ == "__main__":
    print(recommend_book("I'm doing a course for my 5th grade student on Math Geometry, I'll need to recommend few books come up with a teach plan, few quizes and also a homework assignment."))
