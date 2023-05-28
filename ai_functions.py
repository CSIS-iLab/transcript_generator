"""
Module docstring:

requests - to send HTTP requests using Python
time - provides time-related functionality
openai - allows access to the openAI API
json - lets us work with json data
os - here it's used to get .env variables
dotenv - used to read key-val pairs from .env
"""
import time
import json
import os
import requests
import openai
from dotenv import load_dotenv

# ---------------------------------------------------------------------------- #
#                             assemblyAI functions                             #
# ---------------------------------------------------------------------------- #


def read_file(filename, chunk_size=5242880):
    """read audio file"""
    # Open the file in binary mode for reading
    with open(filename, 'rb') as _file:
        while True:
            # Read a chunk of data from the file
            data = _file.read(chunk_size)
            # If there's no more data, stop reading
            if not data:
                break
            # Yield the data as a generator
            yield data


def upload_file(api_token, path):
    """
    Upload a file to the AssemblyAI API.

    Args:
        api_token (str):3 3fdd64586f442faa719dd6d65a8fcdb.
        path (str): Path to the local file.

    Returns:
        str: The upload URL.
    """
    print(f"Uploading file: {path}")

    # Set the headers for the request, including the API token
    headers = {'authorization': api_token}

    # Send a POST request to the API to upload the file,
    # passing in the headers and the file data
    response = requests.post(
        'https://api.assemblyai.com/v2/upload', headers=headers, data=read_file(path))

    # If the response is successful, return the upload URL
    if response.status_code == 200:
        return response.json()["upload_url"]
    # If the response is not successful, print the error message and return
    # None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def create_transcript(api_token, audio_url):
    """
    Create a transcript using AssemblyAI API.

    Args:
        api_token (str): Your API token for AssemblyAI.
        audio_url (str): URL of the audio file to be transcribed.

    Returns:
        dict: Completed transcript object.
    """
    print("Transcribing audio... This might take a moment.")

    # Set the API endpoint for creating a new transcript
    url = "https://api.assemblyai.com/v2/transcript"

    # Set the headers for the request, including the API token and content type
    headers = {
        "authorization": api_token,
        "content-type": "application/json"
    }

    # Set the data for the request, including the URL of the audio file to be
    # transcribed
    data = {
        "audio_url": audio_url,
        "speaker_labels": True,
        "summarization": True,
        "summary_model": "conversational",
        "summary_type": "bullets_verbose"
    }

    # Send a POST request to the API to create a new transcript, passing in the
    # headers and data
    response = requests.post(url, json=data, headers=headers)

    # Get the transcript ID from the response JSON data
    transcript_id = response.json()['id']

    # Set the polling endpoint URL by appending the transcript ID to the API endpoint
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

    # Keep polling the API until the transcription is complete
    while True:
        # Send a GET request to the polling endpoint, passing in the headers
        transcription_result = requests.get(
            polling_endpoint, headers=headers).json()

        # If the status of the transcription is 'completed', exit the loop
        if transcription_result['status'] == 'completed':
            break

        # If the status of the transcription is 'error', raise a runtime error with
        # the error message
        elif transcription_result['status'] == 'error':
            raise RuntimeError(
                f"Transcription failed: {transcription_result['error']}")

        # If the status of the transcription is not 'completed' or 'error', wait for
        # 3 seconds and poll again
        else:
            time.sleep(3)
    # print(transcription_result['summary'])
    return transcription_result


# ---------------------------------------------------------------------------- #
#                                openAI function                               #
# ---------------------------------------------------------------------------- #
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_summary(prompt, text, session_id):
    """Use openAI to generate one paragraph summary"""
    prompt = f"{prompt}:\n{text}"
    max_tokens = 2260
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.3
    )

    summary = response.choices[0].text.strip()
    summary_json = f'summary_{session_id}.json'
    with open(summary_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f)

    return summary
