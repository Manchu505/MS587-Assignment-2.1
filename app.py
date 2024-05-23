# Importing various modules from Flask to handle web server operations
from flask import Flask, render_template, send_file, Response, make_response, request, url_for
# Importing the gTTS library to convert text to speech
from gtts import gTTS
# Importing os to interact with the operating system
import os
# Importing io to handle byte streams
import io

# This line creates a new Flask web application. __name__ gives the application a unique name based on the name of the module.
app = Flask(__name__)

# A variable that stores the path to the directory where eBook files are kept
EBOOK_DIR = 'ebooks'


# Define a function to read the contents of an eBook file given its ID
def read_ebook_file(ebook_id):
    try:
        # Open the eBook file for reading. os.path.join combines the directory name with the file name.
        with open(os.path.join(EBOOK_DIR, f"{ebook_id}.txt"), 'r', encoding='utf-8') as file:
            # Return the content of the file, which is read in one go with .read()
            return file.read()
    except FileNotFoundError:
        # If the file doesn't exist, return this error message
        return "eBook not found."


# Define a function to convert text into speech and save it as an MP3 file
def text_to_speech(ebook_id, text, lang='en'):
    # Path to where the audio file will be saved
    audio_file = f"static/{ebook_id}.mp3"

    # Check if the audio file does not already exist
    if not os.path.exists(audio_file):
        # Create a gTTS object for the text-to-speech conversion
        tts = gTTS(text=text, lang=lang)

        # Check if the 'static' directory exists, if not, create it
        if not os.path.exists('static'):
            os.makedirs('static')

        # Save the audio file
        tts.save(audio_file)

    # Return the path to the audio file
    return audio_file


# Defines a route for the homepage of the web application
@app.route('/')
def home():
    # List comprehension to get a list of eBook IDs based on files in the EBOOK_DIR that end with .txt
    ebook_ids = [f.split('.')[0] for f in os.listdir(EBOOK_DIR) if f.endswith('.txt')]
    # Renders an HTML template and passes the list of eBook IDs to it
    return render_template('index.html', ebook_ids=ebook_ids)


# Defines a route to download an eBook by its ID
@app.route('/download/<ebook_id>')
def download_ebook(ebook_id):
    # Get the content of the eBook file
    ebook_content = read_ebook_file(ebook_id)
    # If the eBook is not found, return a 404 error
    if ebook_content == "eBook not found.":
        return make_response(ebook_content, 404)

    # Creates a byte stream to hold the eBook data
    byte_stream = io.BytesIO()
    # Write the eBook content to the byte stream
    byte_stream.write(ebook_content.encode('utf-8'))
    # Move the cursor to the start of the stream
    byte_stream.seek(0)

    # Send the eBook file to the user
    return send_file(byte_stream, as_attachment=True, download_name=f"{ebook_id}.txt", mimetype='text/plain')


# Defines a route to serve the audio file of an eBook
@app.route('/audiobook/<ebook_id>')
def audiobook(ebook_id):
    # Read the eBook content
    ebook_content = read_ebook_file(ebook_id)
    # Convert the text to speech and get the path to the audio file
    audio_file = text_to_speech(ebook_id, ebook_content)

    # If the audio file does not exist, return a 404 error
    if not os.path.exists(audio_file):
        return make_response("Audio file not found.", 404)

    # Send the audio file to the user
    return send_file(audio_file, as_attachment=False)


# Defines a route to display the eBook text on a web page
@app.route('/read/<ebook_id>')
def read_ebook(ebook_id):
    # Retrieve the eBook content
    ebook_content = read_ebook_file(ebook_id)
    # If the eBook is not found, return a 404 error
    if ebook_content == "eBook not found.":
        return make_response(ebook_content, 404)
    # Render a template that displays the eBook content
    return render_template('read.html', ebook_id=ebook_id, ebook_content=ebook_content)


# Defines a route to serve the favicon
@app.route('/favicon.ico')
def favicon():
    # Sends the favicon.ico file located in the 'static' directory
    return send_file(os.path.join(app.root_path, 'static', 'favicon.ico'))


# This part of the code runs the Flask application on the local server accessible at the default web port
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
