import os
import json
import time
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory

from langchain_google_vertexai import ChatVertexAI
from quiz import generate_quiz_question
from answer import answer_thinking
from onramp_workaround import get_next_region,get_next_thinking_region
from google.cloud import storage  

from render import render_assignment_page

# ENV SETUP
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")  # Get project ID from env
COURSE_BUCKET_NAME = os.environ.get("COURSE_BUCKET_NAME", "aidemy-course")  


app = Flask(__name__)

def read_assignment_file(filepath):
    """
    Opens a text file and returns its content as a string.

    Args:
        filepath (str): The full path to the text file.

    Returns:
        str: The content of the file, or None if an error occurs.
    """
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/quiz',methods=['GET'])
def quiz():
    return render_template('quiz.html')
@app.route('/courses',methods=['GET'])
def courses():
    return render_template('courses.html')
@app.route('/assignment',methods=['GET'])
def assignment():
    return render_template('assignment.html')



#curl -X GET -H "Content-Type: application/json" http://localhost:8080/generate_quiz 

@app.route('/render_assignment', methods=['GET'])
def render_assignment():
    assignment_folder = "../assignment/local_assignments"
    content = None  # Initialize content to None

    try:
        # Check if the folder exists first
        if not os.path.isdir(assignment_folder):
            print(f"Error: The folder '{assignment_folder}' does not exist.")
            return jsonify({'error': f"Assignment folder '{assignment_folder}' not found."}), 404

        # List files in the assignment folder
        files = os.listdir(assignment_folder)
        assignment_files = [f for f in files if f.startswith("assignment-") and f.endswith(".txt")]

        if not assignment_files:
            print(f"No assignment files found in the '{assignment_folder}' folder.")
            return jsonify({'error': f"No assignment files found in '{assignment_folder}'."}), 404

        # Sort files by modification time to get the latest
        assignment_files.sort(key=lambda f: os.path.getmtime(os.path.join(assignment_folder, f)), reverse=True)
        latest_assignment_file = os.path.join(assignment_folder, assignment_files[0])

        print("Content of the file",content)
        # Try reading the latest file
        content = read_assignment_file(latest_assignment_file)

        if content is None:
            print(f"Could not read the assignment content from {latest_assignment_file}.")
            # read_assignment_file already prints details, so just return an error
            return jsonify({'error': f"Failed to read assignment file '{assignment_files[0]}'."}), 500

        print("--- Assignment Content ---")
        print(content)

        # --- Assuming render_assignment_page does something ---
        # If render_assignment_page returns HTML to display:
        # html_output = render_assignment_page(content)
        # return html_output # Or return jsonify({'html': html_output})

        # If render_assignment_page processes/saves data and doesn't return HTML:
        render_assignment_page(content) # Call the function
        # Return a success message indicating which file was processed
        return jsonify({'message': f"Assignment '{assignment_files[0]}' rendered successfully"})

    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"An unexpected error occurred in /render_assignment: {e}")
        # Log the full traceback here if needed: import traceback; traceback.print_exc()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500



@app.route('/generate_quiz', methods=['GET'])
def generate_quiz():
    """Generates a quiz with a specified number of questions."""
    #num_questions = 5  # Default number of questions
    # Can I turn this into Langgraph
    quiz = []
    quiz.append(generate_quiz_question("teaching_plan.txt", "easy", get_next_region()))
    quiz.append(generate_quiz_question("teaching_plan.txt", "medium", get_next_region()))
    quiz.append(generate_quiz_question("teaching_plan.txt", "hard", get_next_region()))

    return jsonify(quiz)



@app.route('/check_answers', methods=['POST'])
def check_answers():
    try:
        submitted_data = request.json  # Get the complete submitted data
        quiz = submitted_data.get('quiz')  # Extract the quiz data
        user_answers = submitted_data.get('answers') # Extract answers
        print(f"submitted_data: {submitted_data}")

        if quiz is None or user_answers is None:
            return jsonify({"error": "Missing quiz or answer data"}), 400

        results = []
        for i in range(len(user_answers)):
            question_data = quiz[i]
            question = question_data['question']
            options = question_data['options']
            correct_answer = question_data['answer']
            user_answer = user_answers[i]

            print(f"Question: {question}")
            print(f"User Answer: {user_answer}")
            print(f"Correct Answer: {correct_answer}")

            is_correct = (user_answer == correct_answer)

            reasoning=None
            if(not is_correct):
                time.sleep(1) # reduced time for testing
                region = get_next_thinking_region()
                # Assuming answer_thinking returns an AIMessage or similar
                ai_response = answer_thinking(question, options, user_answer, correct_answer, region)
                
                # Extract the text content from the AI response
                if hasattr(ai_response, "content"):
                    reasoning = ai_response.content
                elif isinstance(ai_response, str):
                    reasoning = ai_response
                else:
                    reasoning = "Could not extract reasoning from AI response."
            else:
                reasoning = "You are correct!"

            results.append({
                "question": question,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "reasoning": reasoning
            })

        return jsonify(results)

    except Exception as e:
        print(f"Error checking answers: {e}")
        return jsonify({"error": str(e)}), 500



# @app.route('/download_course_audio/<int:week>')
# def download_course_audio(week):
#     filename = f"course-week-{week}.wav"
#     local_path = "/tmp" 
#     try:
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(COURSE_BUCKET_NAME)
#         blob = bucket.blob(filename)

#         local_file_path = os.path.join(local_path, filename)
#         blob.download_to_filename(local_file_path)
        
#         # Serve the downloaded file
#         return send_from_directory(local_path, filename, as_attachment=True)

#     except Exception as e:
#         print(f"Error generating download link: {e}")
#         return "Error generating download link", 500 



## Add your code here
## Add your code here

@app.route('/new_teaching_plan', methods=['POST'])
def new_teaching_plan():
    try:
       
        # Get data from Pub/Sub message delivered via Eventarc
        envelope = request.get_json()
        if not envelope:
            return jsonify({'error': 'No Pub/Sub message received'}), 400

        if not isinstance(envelope, dict) or 'message' not in envelope:
            return jsonify({'error': 'Invalid Pub/Sub message format'}), 400

        pubsub_message = envelope['message']
        print(f"data: {pubsub_message['data']}")

        data = pubsub_message['data']
        data_str = base64.b64decode(data).decode('utf-8')
        data = json.loads(data_str)

        teaching_plan = data['teaching_plan']

        print(f"File content: {teaching_plan}")

        with open("teaching_plan.txt", "w") as f:
            f.write(teaching_plan)

        with open("../assignment/teaching_plan.txt", "w") as f:
            f.write(teaching_plan) 

        print(f"Teaching plan saved to local file: teaching_plan.txt")

        return jsonify({'message': 'File processed successfully'})


    except Exception as e:
        print(f"Error processing file: {e}")
        return jsonify({'error': 'Error processing file'}), 500
## Add your code here

## Add your code here

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
