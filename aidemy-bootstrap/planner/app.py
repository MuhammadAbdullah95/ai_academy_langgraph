import os
import json
import base64
import requests
from flask import Flask, render_template, request, jsonify, send_file, render_template_string
from aidemy import prep_class  


app = Flask(__name__)


##ADD SEND PLAN EVENT FUNCTION HERE
def send_plan_event(teaching_plan: str):
    try:
        data = {
            "teaching_plan": teaching_plan
        }
        base64_data = base64.b64encode(json.dumps(data).encode()).decode()

        payload = {
            "message": {
                "data": base64_data
            }
        }

        response = requests.post("http://localhost:8080/new_teaching_plan", json=payload)

        if response.status_code == 200:
            print("✅ Teaching plan sent successfully to quiz server.")
        else:
            print(f"❌ Failed to send teaching plan: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ Exception while sending teaching plan: {e}")



@app.route('/', methods=['GET', 'POST'])
def index():
    subjects = ['English', 'Mathematics', 'Science', 'Computer Science']
    years = list(range(5, 8))

    if request.method == 'POST':
        selected_year = int(request.form['year'])
        selected_subject = request.form['subject']
        addon_request = request.form['addon']

        # Call prep_class to get teaching plan and assignment
        teaching_plan = prep_class(
            f"""For a year {selected_year} course on {selected_subject} covering {addon_request}, 
            Incorporate the school curriculum, 
            book recommendations, 
            and relevant online resources aligned with the curriculum outcome. 
            generate a highly detailed, day-by-day 3-week teaching plan, 
            return the teaching plan in markdown format
            """
        )

        ### ADD send_plan_event CALL
        send_plan_event(teaching_plan)
        
        return jsonify({'teaching_plan': teaching_plan})
    return render_template('index.html', years=years, subjects=subjects, teaching_plan=None, assignment=None)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
