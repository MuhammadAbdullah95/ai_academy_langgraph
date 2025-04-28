import functions_framework
import json
from flask import Flask, jsonify, request
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")


class Book(BaseModel):
    bookname: str = Field(description="Name of the book")
    author: str = Field(description="Name of the author")
    publisher: str = Field(description="Name of the publisher")
    publishing_date: str = Field(description="Date of publishing")


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=google_api_key, temperature=0)

def get_recommended_books(category):
    """
    A simple book recommendation function.
    Args:
        category (str): category

    Returns:
        str: A JSON string representing the recommended books.
    """
    parser = JsonOutputParser(pydantic_object=Book)
    question = f"Generate a random made up book on {category} with bookname, author and publisher and publishing_date"

    prompt = PromptTemplate(
        template="Answer the user query. \n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},   
    )
    chain = prompt | llm | parser
    response = chain.invoke({"query": question})

    return json.dumps(response)
app = Flask(__name__)
@app.route('/recommended', methods=['POST', 'GET']) # Handle both POST and GET requests
def recommended():
    if request.method == 'POST':
        request_json = request.get_json(silent=True)
        if request_json and 'category' in request_json and 'number_of_book' in request_json:
            category = request_json['category']
            number_of_book = int(request_json['number_of_book'])
        else:
            return jsonify({'error': 'Missing category or number_of_book parameters in POST request'}), 400
    elif request.method == 'GET':
        if 'category' in request.args and 'number_of_book' in request.args:
            category = request.args.get('category')
            number_of_book = int(request.args.get('number_of_book'))
        else:
            return jsonify({'error': 'Missing category or number_of_book parameters in GET request'}), 400
    else:
        return jsonify({'error': 'Invalid request method'}), 405


    recommendations_list = []
    for i in range(number_of_book):
        book_dict = json.loads(get_recommended_books(category))
        recommendations_list.append(book_dict)

    return jsonify(recommendations_list)

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask development server