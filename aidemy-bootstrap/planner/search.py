import os
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from dotenv import load_dotenv
load_dotenv()

# Load your API key from the environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(
        "Missing GOOGLE_API_KEY environment variable. "
        "Please set it in your .env file."
    )

# Configure the Gemini API with your API key
# genai.configure(api_key=GOOGLE_API_KEY)
client = genai.Client()
model_id = "gemini-2.0-flash-001"

google_search_tool = Tool(
    google_search = GoogleSearch()
)

def search_latest_resource(search_text: str, curriculum: str, subject: str, year: int):
    """
    Get latest information from the internet
    
    Args:
        search_text: User's request category   string
        subject: "User's request subject" string
        year: "User's request year"  integer
    """
    search_text = "%s in the context of year %d and subject %s with following curriculum detail %s " % (search_text, year, subject, curriculum)
    # print(f"search_latest_resource text-----> {search_text}")
    response = client.models.generate_content(
        model=model_id,
        contents=search_text,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    # print(f"search_latest_resource response-----> {response}")
    return response


if __name__ == "__main__":
    response = search_latest_resource(
        "What are the syllabus for Year 6 Mathematics?",
        "Expanding on fractions, ratios, algebraic thinking, and problem-solving strategies.",
        "Mathematics",
        6,
    )
    if response:
        for each in response.candidates[0].content.parts:
            print(each.text)
