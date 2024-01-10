from flask import Flask
import whisper

app = Flask(__name__)
model = whisper.load_model("base")

audio = whisper.load_audio("./Audio/ef3e_elem_01a_1-02.mp3")
audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio).to(model.device)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/transcript")
def transcript():
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    options = whisper.DecodingOptions(fp16 = False)
    result = whisper.decode(model, mel, options)

    return result.text

if __name__ == '__main__':
    app.run(debug=True)
