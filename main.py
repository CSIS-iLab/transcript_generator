"""
Import os to access and save files. Import Flask to use its framework. 
Import uuid to generate unique session IDs. Import dotenv to 
use environment variables. Import 'creator' module.
"""
import glob
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import helpers

# ---------------------------------------------------------------------------- #
#                                   app setup                                  #
# ---------------------------------------------------------------------------- #


load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './upload_folder'
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
app.secret_key = os.getenv("FLASK_KEY")

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))


@app.route('/', methods=['GET', 'POST'])
def index():
    # Check if upload_folder exists, and if not, create it
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    """Method for '/ route that handles both new
    sessions and users navigating there from '/complete'"""

    # tell the navbar what "Home" goes to
    home_link = url_for('index')

    # ask what page the user got here from
    from_page = request.args.get('from_page')

    # ---------------- if they're coming from '/complete' ---------------- #
    if from_page == 'complete':
        # get the ID from the URL params
        session_id = request.args.get('id')

        # delete every summary and transcript with that id
        summary_filelist = glob.glob(f'summary_{session_id}.json')
        transcript_filelist = glob.glob(f'transcript_{session_id}.json')
        helpers.delete_files(summary_filelist)
        helpers.delete_files(transcript_filelist)

        # delete the session ID
        session.pop('id', None)

    # ------ if they're hitting 'submit' and starting a new session ------ #
    if request.method == 'POST':
        # create a session ID
        session_id = uuid.uuid4()
        session['id'] = session_id

        # get the user's uploaded file
        uploaded_file = request.files['file']
        filename = uploaded_file.filename
        file_path = os.path.join(
            UPLOAD_FOLDER, filename)

        # save the file in the upload folder
        uploaded_file.save(file_path)

        # kick off the functions to process the file
        helpers.main(file_path, session_id)

        # send them to '/complete'
        return redirect(url_for('complete', home_link=home_link))

    return render_template('index.html', home_link=home_link)


@app.route('/complete', methods=['GET', 'POST'])
def complete():
    """Handle displaying summary and transcript"""
    session_id = session.get('id', None)
    home_link = url_for('index', from_page='complete', id=session_id)
    print(id)
    if request.method == 'POST':
        if request.form['text'] == "":
            helpers.remake_summary(session_id)
            short_summary = helpers.get_short_summary(session_id)
            transcript = helpers.get_transcript(session_id)
            prompt = helpers.get_prompt()
            folder = './upload_folder'
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))
            return render_template('complete.html', prompt=prompt,
                                   short_summary=short_summary,
                                   transcript=transcript, home_link=home_link)
        else:
            user_prompt = request.form['text']
            helpers.remake_with_new_prompt(user_prompt, session_id)
            short_summary = helpers.get_short_summary(session_id)
            transcript = helpers.get_transcript(session_id)
            folder = './upload_folder'
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))
            return render_template('complete.html', prompt=user_prompt,
                                   short_summary=short_summary,
                                   transcript=transcript, home_link=home_link)
    else:
        short_summary = helpers.get_short_summary(session_id)
        transcript = helpers.get_transcript(session_id)
        prompt = helpers.get_prompt()
        folder = './upload_folder'
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))
        return render_template('complete.html', prompt=prompt,
                               short_summary=short_summary,
                               transcript=transcript, home_link=home_link)
