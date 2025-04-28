import os
import json
import asyncio
import wave
import time

import functions_framework # Note: This might still be unnecessary if not deploying as a Cloud Function
import soundfile as sf
from google import genai
# Removed: from google.cloud import storage
from google.genai.types import (
    Content,
    LiveConnectConfig,
    SpeechConfig,
    VoiceConfig,
    PrebuiltVoiceConfig,
    Part,
)

from dotenv import load_dotenv
load_dotenv() # Corrected: call the function
google_api_key = os.getenv("GOOGLE_API_KEY")

# Ensure the API key is loaded
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please set it in your .env file or environment.")


MODEL_ID = "gemini-2.0-flash-exp"
# Removed GCS-related environment variables

config = LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=SpeechConfig(
        voice_config=VoiceConfig(
            prebuilt_voice_config=PrebuiltVoiceConfig(
                voice_name="Charon",
            )
        )
    ),
)

async def process_weeks(teaching_plan: str):
    # Removed: region variable (not needed for local genai client with API key)
    client = genai.Client(api_key=google_api_key)
    clientAudio = genai.Client(api_key=google_api_key)

    # Use a temporary directory for generated files if desired, or keep in current dir
    output_dir = "../portal/static/audio"
    os.makedirs(output_dir, exist_ok=True) # Create the directory if it doesn't exist

    async with clientAudio.aio.live.connect(
        model=MODEL_ID,
        config=config,
    ) as session:
        # Assuming weeks 1 to 3 for demonstration
        for week in range(1, 4):
            print(f"--- Processing Week {week} ---")
            # Generate content plan for the week
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=f"Given the following teaching plan: {teaching_plan}, Extract content plan for week {week}. And return just the plan, nothing else" # Clarified prompt
            )

            if not response.text:
                 print(f"Warning: No content plan generated for week {week}. Skipping audio generation.")
                 continue # Skip to the next week if no plan was generated

            # Prepare the prompt for audio generation
            prompt = f"""
                Assume you are the instructor.
                Prepare a concise and engaging recap of the key concepts and topics covered for the week.
                This recap should be suitable for generating a short audio summary for students.
                Focus on the most important learnings and takeaways, and frame it as a direct address to the students.
                Avoid overly formal language and aim for a conversational tone, maybe tell a short, relevant anecdote or a light joke if appropriate.

                Teaching plan for the week: {response.text} """
            print(f"Audio generation prompt for Week {week}:\n{prompt[:200]}...") # Print start of prompt

            # Define file paths using the output directory
            raw_audio_path = os.path.join(output_dir, f"temp_audio_week_{week}.raw")
            wav_audio_path = os.path.join(output_dir, f"course-week-{week}.wav")

            # Send prompt and receive audio stream
            await session.send(input=prompt, end_of_turn=True)
            print(f"Receiving audio stream for Week {week}...")
            with open(raw_audio_path, "wb") as temp_file:
                async for message in session.receive():
                    if message.server_content.model_turn:
                        for part in message.server_content.model_turn.parts:
                            if part.inline_data:
                                temp_file.write(part.inline_data.data)

            print(f"Raw audio saved to {raw_audio_path}")

            # Convert raw audio to WAV format
            try:
                # Ensure the raw file has data before attempting to read
                if os.path.getsize(raw_audio_path) > 0:
                    data, samplerate = sf.read(raw_audio_path, channels=1, samplerate=24000, subtype='PCM_16', format='RAW')
                    sf.write(wav_audio_path, data, samplerate)
                    print(f"Audio converted and saved locally: {wav_audio_path}")
                    # Optional: Remove the raw file after successful conversion
                    # os.remove(raw_audio_path)
                else:
                    print(f"Warning: Raw audio file {raw_audio_path} is empty. Skipping WAV conversion.")

            except Exception as e:
                print(f"Error converting raw audio to WAV for week {week}: {e}")
                # Optionally keep the raw file for debugging if conversion fails
                # Consider adding more specific error handling if needed

            # Removed GCS Upload Block
            # storage_client = storage.Client()
            # bucket = storage_client.bucket(BUCKET_NAME)
            # blob = bucket.blob(f"course-week-{week}.wav")
            # blob.upload_from_filename(wav_audio_path)
            # print(f"Audio saved to GCS: gs://{BUCKET_NAME}/course-week-{week}.wav")

            print(f"--- Finished Processing Week {week} ---")
            time.sleep(1) # Add a small delay if needed, e.g., to avoid rate limits

    # No need to explicitly close the session when using 'async with'
    # await session.close() # This is handled by the context manager
    print("Audio generation process complete.")


# This function remains the entry point
def breakup_sessions(teaching_plan: str):
    """
    Generates weekly audio summaries based on a teaching plan and saves them locally.
    """
    print("Starting audio generation...")
    # Example teaching plan for testing if needed:
    # teaching_plan = """
    # Week 1: Introduction to Python, basic syntax, variables, data types.
    # Week 2: Control flow (if/else), loops (for/while), lists.
    # Week 3: Functions, modules, file I/O.
    # """
    if not teaching_plan:
        print("Error: Teaching plan is empty.")
        return
    asyncio.run(process_weeks(teaching_plan))
    print("Finished breakup_sessions.")

# Example usage (if you want to run this script directly)
if __name__ == "__main__":
    # Make sure you have a .env file in the same directory with GOOGLE_API_KEY=your_key
    example_plan = """
    Week 1: Introduction to Machine Learning Concepts - Supervised vs Unsupervised Learning, Model Evaluation Metrics. Lab: Setting up Python environment.
    Week 2: Linear Regression - Theory, Assumptions, Implementation in Scikit-learn. Lab: Predicting house prices.
    Week 3: Classification with Logistic Regression - Theory, Sigmoid function, Decision Boundaries. Lab: Spam detection.
    """
    breakup_sessions(example_plan)

