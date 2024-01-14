from flask import Flask, render_template

#Forms
from flask_wtf import FlaskForm
#Form validation and rendering library
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os

import whisper
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

app = Flask(__name__)
app.config['SECRET_KEY'] = 'passwordkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

model = whisper.load_model("base")

audio = whisper.load_audio("./Audio/7f1c3d84-db93-430d-be85-1fa0ce726c0e.mp3")
audio = whisper.pad_or_trim(audio)
duration = len(audio) / 1000

mel = whisper.log_mel_spectrogram(audio).to(model.device)

nltk.download('punkt')

class UploadFileForm(FlaskForm):
    file = FileField("Field")
    submit = SubmitField("Upload File")


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

#Upload files function
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data #We retrieve the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename))) #Then we save the file
        return "File has been uploaded."
    return render_template('index.html', form=form)

@app.route("/transcript")
def transcript():
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(model, mel, options)

    print("Audio duration:", duration)

    return result.text


@app.route("/summary")
def summary():
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(model, mel, options)

    return summarize(result.text, sentences_count=1)


def summarize(text, language="english", sentences_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return ' '.join([str(sentence) for sentence in summary])


if __name__ == '__main__':
    app.run(debug=True)
