import os
import json
import random
import re # Import regular expressions
import logging # Import logging
from google.cloud import storage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from onramp_workaround import get_next_region # Assuming this is necessary for your setup
from dotenv import load_dotenv

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OUTPUT_HTML_FILE = "templates/assignment.html" # Define output path clearly

# --- Helper Function to Extract HTML ---
def extract_html(text: str) -> str | None:
    """
    Extracts the first HTML block (<!DOCTYPE...> or <html>...</html>)
    from the given text.
    Handles potential markdown code fences.
    """
    # Regex to find HTML block, potentially wrapped in markdown fences
    # It looks for ```html ... ``` or just <!DOCTYPE... / <html...> ... </html>
    match = re.search(r"```html\s*(<!DOCTYPE html>.*?</html>)\s*```|^(<!DOCTYPE html>.*?</html>)", text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    if match:
        # Return the first non-None captured group (either from within ```html or standalone)
        return match.group(1) or match.group(2)
    else:
        # Fallback: If no explicit block found, check if the whole text looks like HTML
        if text.strip().startswith("<") and text.strip().endswith(">"):
             # Basic check, might need refinement
             # Remove potential leading/trailing markdown fences if missed by regex
             cleaned_text = re.sub(r"^```html\s*", "", text.strip(), flags=re.IGNORECASE)
             cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
             # A simple check if it starts like HTML
             if cleaned_text.lower().startswith(('<!doctype html>', '<html')):
                 return cleaned_text
        return None # Indicate HTML not found

# --- Main Function ---
def render_assignment_page(assignment: str):
    if not GOOGLE_API_KEY:
        error_msg = "Error: GOOGLE_API_KEY not found. Please check your .env file."
        logging.error(error_msg)
        return f"Configuration Error: {error_msg}"

    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(OUTPUT_HTML_FILE)
        if output_dir and not os.path.exists(output_dir):
             os.makedirs(output_dir)
             logging.info(f"Created directory: {output_dir}")


        # region=get_next_region() # This variable is fetched but not used? Keep if needed for your setup.
        # Consider using a standard model if the experimental one causes issues
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=GOOGLE_API_KEY) # Changed to standard model

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        """
                        You are an expert frontend developer. Your task is to generate a complete HTML document (starting with <!DOCTYPE html> and ending with </html>)
                        to display a student assignment.

                        **Requirements:**
                        1.  **Structure:** Create a standard HTML5 document structure (`<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`).
                        2.  **Head Section:** Include the following links EXACTLY as specified in the `<head>`:
                            ```html
                            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
                            <link rel="preconnect" href="https://fonts.googleapis.com">
                            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap" rel="stylesheet">
                            ```
                        3.  **Navigation Bar:** Include the following navigation bar EXACTLY as specified at the beginning of the `<body>`:
                            ```html
                            <nav>
                                <a href="/">Home</a>
                                <a href="/quiz">Quizzes</a>
                                <a href="/courses">Courses</a>
                                <a href="/assignment">Assignments</a>
                            </nav>
                            ```
                            *Do not apply any inline styles to the navigation bar elements.*
                        4.  **Assignment Content:** Display the full assignment content provided by the user within the `<body>`, after the navigation bar. Structure it clearly (e.g., using headings, paragraphs, lists).
                        5.  **Styling (CSS):** Define CSS rules within a `<style>` tag in the `<head>`. Be creative with the styling:
                            *   Use a **rainbow color theme** aesthetically.
                            *   Ensure the assignment content is **easy to read** (good font choices, spacing, contrast).
                            *   Make the overall page look **creative and visually appealing**.
                            *   Style the provided navigation bar using CSS (not inline styles).
                        6.  **Output Format:** Respond ONLY with the complete HTML document. Do NOT include any introductory text, explanations, or markdown code fences (like ```html or ```) around the final HTML output. Start directly with `<!DOCTYPE html>`.

                        Here is the assignment content:
                        """
                    )
                ),
                HumanMessage(content=assignment), # Pass the assignment content directly
            ]
        )

        # Note: format() is usually not needed for ChatPromptTemplate with invoke
        # prompt = prompt_template.format() # This line is likely unnecessary

        logging.info("Invoking LLM to generate assignment HTML...")
        response_message = llm.invoke(prompt_template.format_messages(assignment=assignment)) # Pass assignment context if needed by template structure
        raw_response = response_message.content

        logging.info("LLM response received. Extracting HTML...")
        # print(f"Raw response from LLM:\n---\n{raw_response}\n---") # Uncomment for debugging LLM output

        html_content = extract_html(raw_response)

        if not html_content:
            error_msg = "Error: Failed to extract valid HTML from the LLM response."
            logging.error(error_msg)
            logging.debug(f"LLM Raw Response was: {raw_response}")
            return f"Processing Error: {error_msg}"

        logging.info(f"HTML extracted successfully. Writing to {OUTPUT_HTML_FILE}...")
        try:
            with open(OUTPUT_HTML_FILE, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"Successfully wrote HTML to {OUTPUT_HTML_FILE}")
            # Return the generated HTML so it can be potentially used/displayed elsewhere
            return html_content
        except IOError as e:
            error_msg = f"Error writing HTML to file '{OUTPUT_HTML_FILE}': {e}"
            logging.exception(error_msg) # Log the full exception traceback
            return f"File System Error: {error_msg}"

    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logging.exception(error_msg) # Log the full exception traceback
        return f"Error: Unable to process your request at this time. Reason: {str(e)}"

# Example Usage (if you want to test this script directly)
# if __name__ == "__main__":
#     sample_assignment = """
#     # Math Assignment 101

#     ## Instructions
#     Solve the following problems. Show your work.

#     ## Problems
#     1. Calculate 5 + 7 * 2
#     2. What is the square root of 144?
#     3. If a train travels at 60 mph for 2.5 hours, how far does it travel?

#     ## Submission
#     Submit your answers by Friday.
#     """
#     generated_html = render_assignment_page(sample_assignment)
#     if "Error" not in generated_html:
#         print(f"\n--- Generated HTML written to {OUTPUT_HTML_FILE} ---")
#         # print(generated_html[:500] + "...") # Print start of HTML for verification
#     else:
#         print(f"\n--- Error Occurred ---")
#         print(generated_html)

