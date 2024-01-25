from flask import Flask, render_template, request, jsonify, Response

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
import json

import torch

from transformers import AutoTokenizer, AutoModelWithLMHead


app = Flask(__name__)
CORS(app)  # We enable CORS for all routes

app.config['SECRET_KEY'] = 'passwordkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

model = whisper.load_model("small", device="cpu")

nltk.download('punkt')

tokenizer = AutoTokenizer.from_pretrained('t5-base')
google_model = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)


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
    return json.dumps({'result_text': file_info['result_text']})


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


@app.route("/upload", methods=['POST'])
def upload():
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


@app.route("/transcript", methods=['POST'])
def transcript():
    form = UploadFileForm()
    result_text = "No input data"

    file = form.file.data  # We retrieve the file
    file_path = os.path.join(os.path.abspath(os.path.dirname(
        __file__)), app.config['UPLOAD_FOLDER'], secure_filename(file))

    print(file_path)

    # if the corresponding text file already exists, we return it
    text_file_path = os.path.join('./static/texts', os.path.splitext(
        os.path.basename(file_path))[0]+".txt")

    def generate():
        with app.test_request_context():
            if os.path.exists(text_file_path):
                with open(text_file_path, 'r') as text_file:
                    result_text = text_file.read()
                yield json.dumps({'result_text': result_text})

            else:

                audio = whisper.load_audio(file_path)

                duration = len(audio)/1000

                coupures = []

                for i in range(int(duration/121)+1):
                    coupures.append(
                        [max(i*121-10, 0), min((i+1)*121, int(duration))])

                result_text = ""

                for i in range(len(coupures)):
                    cut_audio = audio[coupures[i][0]*1000: coupures[i][1]*1000]

                    cut_audio2 = whisper.pad_or_trim(cut_audio)

                    mel = whisper.log_mel_spectrogram(
                        cut_audio2).to(model.device)
                    _, probs = model.detect_language(mel)

                    options = whisper.DecodingOptions(fp16=False)
                    result = whisper.decode(model, mel, options)

                    print(f"{100*i/len(coupures):.2f}% : {result.text}")

                    # send the percentage of the progress to the frontend without stopping the actual process
                    yield str(100*i/len(coupures)) + "\n"

                    result_text += result.text

                print("Result text before:", result_text)

                # remove repeated groups of words (e.g. "I mean, I mean, I mean, ..." -> "I mean, ...")
                # result_text = ' '.join(
                #     [i[0] for i in nltk.FreqDist(result_text.split()).most_common(100)])
                # print("Result text after:", result_text)

                # Save the result_text in /static/texts/[name of the file].txt
                text_directory = './static/texts'
                if not os.path.exists(text_directory):
                    os.makedirs(text_directory)

                with open(text_file_path, 'w') as text_file:
                    text_file.write(result_text)

                yield json.dumps({'result_text': result_text})

    return Response(generate(), mimetype='text/event-stream')


@app.route("/summary", methods=['POST'])
def summary():

    form = UploadFileForm()
    summarized_text = "No input data"

    text = form.file.data

    summarized_text = summarize_google_t5(text, sentences_count=4)

    return json.dumps({'summary': str(summarized_text)})


# Add missing import statements here

def summarize(text, language="english", sentences_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return ' '.join([str(sentence) for sentence in summary])


def summarize_google_t5(text, sentences_count=5):
    inputs = tokenizer.encode("summarize: " + text,
                              return_tensors='pt',
                              max_length=512,
                              truncation=True)
    summary_ids = google_model.generate(
        inputs, max_length=200, min_length=80, length_penalty=5., num_beams=2)

    summary = tokenizer.decode(summary_ids[0])

    return summary


if __name__ == '__main__':
    app.run(debug=True)
