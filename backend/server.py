from flask import Flask, render_template, request, jsonify, Response

# CORS
from flask_wtf import FlaskForm
from flask_cors import CORS

# # Parrot
# from parrot import Parrot
# import warnings

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

from transformers import AutoTokenizer, AutoModelWithLMHead


app = Flask(__name__)
# CORS(app)  # We enable CORS for all routes
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = 'passwordkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

# warnings.filterwarnings("ignore")
# parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")

model = whisper.load_model("small", device="cpu")

nltk.download('punkt')

tokenizer = AutoTokenizer.from_pretrained('t5-base')
google_model = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)


class UploadFileForm(FlaskForm):
    file = FileField("Field", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route("/")
def hello_world():
    return "<p>Welcome to ListenAI - By KACZMARSKI Lucas & GOULAMHOUSSEN Sunil</p>"


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

    # # verify if the file is an audio file
    # if file.filename.split('.')[-1] != 'mp3':
    #     print("File type not supported")
    #     return jsonify({'error': 'File type not supported'}), 400

    # # verify if the file is not too big (max 100MB)
    # if len(file.read()) > 100000000:
    #     print("File too big")
    #     return jsonify({'error': 'File too big'}), 400

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
                        [max(i*121-3, 0), min((i+1)*121, int(duration))])

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


@app.route("/transcript/<filename>")
def transcript_file(filename):

    print(filename)

    text_file_path = os.path.join('./static/texts', filename+".txt")
    if os.path.exists(text_file_path):
        with open(text_file_path, 'r') as text_file:
            result_text = text_file.read()
    else:
        result_text = "File not found"
    return jsonify({'result_text': result_text})


@app.route("/delete/<filename>")
def delete_file(filename):

    text_file_path = os.path.join('./static/texts', filename+".txt")
    mp3_file_path = os.path.join('./static/files', filename+".mp3")
    if os.path.exists(text_file_path):
        os.remove(text_file_path)
        if os.path.exists(mp3_file_path):
            os.remove(mp3_file_path)
        return jsonify({'message': 'File deleted successfully'}), 200
    else:
        if os.path.exists(mp3_file_path):
            os.remove(mp3_file_path)
        return jsonify({'error': 'File not found'}), 400


@app.route("/files")
def files():
    files = os.listdir('./static/files')
    return jsonify({'files': files})


@app.route("/summary/<num_sentences>", methods=['POST'])
def summary(num_sentences):

    form = UploadFileForm()
    summarized_text = "No input data"

    text = form.file.data

    print(num_sentences)

    summarized_text = summarize_google_t5(
        text, sentences_count=int(num_sentences))

    return json.dumps({'summary': str(summarized_text)})


# Add missing import statements here

def summarize(text, language="english", sentences_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return ' '.join([str(sentence) for sentence in summary])


def summarize_google_t5(text, sentences_count):

    # split the text into sentences of 512 tokens max
    split_text = text.split(".")

    # separate the whole text into multiple sentences of 512 tokens max
    final_split_text = []
    index = 0
    while index < len(split_text):
        temp_sentences = 0
        temp_height = 0
        temp_text = ""
        while True:
            if index >= len(split_text):
                final_split_text.append(temp_text)
                break
            temp_text += split_text[index] + "."
            temp_sentences += 1
            temp_height += len(tokenizer.encode(split_text[index]))
            if temp_height > max(1024, len(text)/sentences_count/2) or temp_sentences > sentences_count:
                final_split_text.append(temp_text)
                break
            index += 1

    # remove texts that are in double
    final_split_text = list(dict.fromkeys(final_split_text))

    print(len(final_split_text))
    print(final_split_text)

    # summarize each sentence
    for i in range(len(final_split_text)):
        print(i)
        print("summarize: " + str(final_split_text[i]))
        inputs = tokenizer.encode("summarize: " + str(final_split_text[i]),
                                  return_tensors='pt',
                                  max_length=2048,
                                  truncation=True)
        summary_ids = google_model.generate(
            inputs, max_length=2048, length_penalty=0, num_beams=3)  # more num_beams is low, more the summary is accurate but less it is diverse

        final_split_text[i] = tokenizer.decode(summary_ids[0])
        print("summary: " + str(final_split_text[i]))

    # concatenate the sentences
    concatenated_summary = ""
    for i in range(len(final_split_text)):
        final_split_text[i] = final_split_text[i].replace("<pad>", "")
        final_split_text[i] = final_split_text[i].replace("<unk>", "")
        final_split_text[i] = final_split_text[i].replace("<extra_id_0>", "")
        final_split_text[i] = final_split_text[i].replace("<extra_id_1>", "")
        final_split_text[i] = final_split_text[i].replace("<sep>", "")
        final_split_text[i] = final_split_text[i].replace("<s>", "")
        final_split_text[i] = final_split_text[i].replace("</s>", "")
        concatenated_summary += final_split_text[i]

    # # summarize the summary
    # inputs = tokenizer.encode("summarize: " + str(concatenated_summary),
    #                           return_tensors='pt',
    #                           max_length=2048,
    #                           truncation=True)
    # summary_ids = google_model.generate(
    #     inputs, max_length=2048, length_penalty=0, num_beams=3)  # more num_beams is low, more the summary is accurate but less it is diverse

    # summary = tokenizer.decode(summary_ids[0])

    print("concatenated_summary: " + str(concatenated_summary))

    concatenated_summary = concatenated_summary.replace(
        " cnn.com's tom charity", "")
    concatenated_summary = concatenated_summary.replace(
        "cnn.com's ireport.com.", "")

    # if the concatenated summary is too long (more than 500 tokens to take a margin), we split it into multiple summaries

    # if len(concatenated_summary) > 1000:
    #     number_of_summaries = int(
    #         len(concatenated_summary)/1000) + 1
    #     print("number_of_summaries: " + str(number_of_summaries))
    #     summaries = []
    #     for i in range(number_of_summaries):
    #         parroted_summary = parrot.augment(input_phrase=str(concatenated_summary[i*1000:min((i+1)*1000, len(
    #             concatenated_summary))]), adequacy_threshold=0.61, fluency_threshold=0.80, do_diverse=True, use_gpu=False, max_return_phrases=1, max_length=512)
    #         summaries.append(parroted_summary[0][0])

    #     summary = ' '.join([str(sentence) for sentence in summaries])

    # else:

    # summary = parrot.augment(input_phrase=str(concatenated_summary), adequacy_threshold=0.61, fluency_threshold=0.80, do_diverse=True,
    #                          use_gpu=False, max_return_phrases=sentences_count, max_length=512)[0][0]

    # if the concatenated summary is too long (more than 512 tokens), we split it into multiple summaries

    return str(concatenated_summary)


if __name__ == '__main__':
    app.run(debug=True)

