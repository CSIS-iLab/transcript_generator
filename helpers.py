"""Import json module to handle json files, os and dotenv to get 
environment variables, and the ai_functions to process audio files."""
import json
import os
from dotenv import load_dotenv
import ai_functions

# get assemblyAI api key
load_dotenv()
assemblyai_token = os.getenv("ASSEMBLYAI_API_KEY")

# prompt that goes to openAI
prompt = "Please provide a concise but detailed summary of this text for a technology expert"

# -------------- join session id to transcript/summary filenames ------------- #


def transcript_json(session_id):
    """Joins session id to transcript file name"""
    filename = f'transcript_{session_id}.json'
    return filename


def summary_json(session_id):
    """Joins session id to transcript file name"""
    filename = f'summary_{session_id}.json'
    return filename


# ------- function that starts everything, creating transcript/summary ------- #
def main(filename, session_id):
    """Uses ai functions to generate transcript and initial summary"""
    upload_url = ai_functions.upload_file(assemblyai_token, filename)
    transcript = ai_functions.create_transcript(assemblyai_token, upload_url)

    with open(transcript_json(session_id), 'w', encoding='utf-8') as file:
        json.dump(transcript, file)

    summary = ai_functions.generate_summary(
        prompt, transcript['summary'], session_id)
    print("Summary:")
    print(summary)

# ---------------------------------------------------------------------------- #
#                                 html results                                 #
# ---------------------------------------------------------------------------- #


def remake_summary(session_id):
    """Used to regenerate paragraph summary"""
    file = open(transcript_json(session_id), encoding='utf-8')
    data = json.load(file)
    summary = ai_functions.generate_summary(
        prompt, data['summary'], session_id)
    return summary


def remake_with_new_prompt(user_prompt, session_id):
    """Regenerate summary with user-supplied prompt"""
    file = open(transcript_json(session_id), encoding='utf-8')
    data = json.load(file)
    summary = ai_functions.generate_summary(
        user_prompt, data['summary'], session_id)
    return summary


def get_short_summary(session_id):
    """Get one-paragraph summary from openAI"""
    file = open(summary_json(session_id), encoding='utf-8')
    data = json.load(file)
    output = f"{data}"
    return output


def get_transcript(session_id):
    """Get transcript from assemblyAI"""
    file = open(transcript_json(session_id), encoding='utf-8')
    data = json.load(file)
    utterances = data['utterances']
    return utterances


def get_prompt():
    """Get default prompt"""
    return prompt


def delete_files(filelist):
    """get ride of files with certain name"""
    for filepath in filelist:
        try:
            os.remove(filepath)
        except FileNotFoundError:
            print(f"error while deleting file: {filepath}")
