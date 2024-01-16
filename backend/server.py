from flask import Flask, render_template, request, jsonify

# CORS
from flask_cors import CORS

# Forms
from flask_wtf import FlaskForm
# Form validation and rendering library
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
import os

import whisper
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

app = Flask(__name__)
CORS(app)  # We enable CORS for all routes

app.config['SECRET_KEY'] = 'passwordkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

model = whisper.load_model("base")

nltk.download('punkt')


class UploadFileForm(FlaskForm):
    file = FileField("Field", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Upload files function


@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    file_info = {
        'file_path': None,
        'result_text': "No input data"
    }

    if form.validate_on_submit():
        file = form.file.data  # We retrieve the file
        file_path = os.path.join(os.path.abspath(os.path.dirname(
            __file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(file_path)  # Then we save the file

        audio = whisper.load_audio(file_path)
        # audio = whisper.pad_or_trim(audio)
        duration = len(audio) / 1000

        # mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # _, probs = model.detect_language(mel)
        # print(f"Detected language: {max(probs, key=probs.get)}")

        # options = whisper.DecodingOptions(fp16=False)
        # result = whisper.decode(model, mel, options)

        # print("Audio duration:", duration)

        coupures = []

        for i in range(int(duration / 121) + 1):
            coupures.append(
                [max(i*121 - 5, 0), min((i+1) * 121, int(duration))])

        # print("Coupures:", coupures)

        all_text = ""

        for i in range(len(coupures)):
            # print("Coupure:", coupures[i])

            cut_audio = audio[coupures[i][0] * 1000: coupures[i][1] * 1000]

            # Convert audio to mono
            cut_audio2 = whisper.pad_or_trim(cut_audio)

            # print("Cut audio:", cut_audio2)

            mel = whisper.log_mel_spectrogram(
                cut_audio2).to(model.device)
            _, probs = model.detect_language(mel)
            # print(f"Detected language: {max(probs, key=probs.get)}")

            options = whisper.DecodingOptions(fp16=False)
            result = whisper.decode(model, mel, options)

            print(f"{100*i/len(coupures):.2f}% : {result.text}")

            all_text += result.text

        print("All text:", all_text)

        file_info = {
            'file_path': file_path,
            'result_text': all_text
        }
    # return render_template('index.html', form=form, file_info=file_info)
    return file_info['result_text']


@app.route("/summarize", methods=["GET", "POST"])
def summarize():
    form = UploadFileForm()
    if request.method == "POST":
        result_text = request.form.get("result_text")
        if request.form.get("num_sentences") is None:
            num_sentences = 2
        else:
            num_sentences = int(request.form.get("num_sentences"))
        if request.form.get("language") is None:
            language = "english"
        else:
            language = request.form.get("language")


@app.route("/transcribe", methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    saved_file_path = save_uploaded_file(uploaded_file)

    return jsonify({'message': 'File uploaded successfully', 'file_path': saved_file_path}), 200


def save_uploaded_file(file):
    target_directory = './static/files'

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    file_path = os.path.join(target_directory, file.filename)
    file.save(file_path)

    return file_path


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
