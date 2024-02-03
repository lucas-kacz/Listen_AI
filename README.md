# Listen_AI

## Motivation behind this project

The aim of this project is to transcript audio files and to summarize them in the desired amount of sentences. Some use cases might be news audios, podcasts or documentaries when you don't have the time to listen to them completely.

## How does it work ?

The project is a complete web app with a backend written in Flask in order to be able to use the Whisper Library and a React frontend where you can upload, read the transcript of the uploaded audio file and summarize it.

This app automatically detects the language of the audio and transcripts it in the same language.
This app is hosted on this [website](http://217.160.142.195:3000/) and you can try to summarize your own audios.

The backend is hosted on this [url](http://217.160.142.195:5000/).

## Installation 

Make a venv in the backend folder
https://flask.palletsprojects.com/en/3.0.x/installation/

Install required libraries

```
pip install -r requirements.txt
pip install flask
pip install flask-cors
```

Install Whisper
https://github.com/openai/whisper

## Examples

![Capture d’écran 2024-02-03 à 12 39 15](https://github.com/lucas-kacz/Listen_AI/assets/74963340/009bcefd-634d-4243-a3e9-049287a542a0)

![Capture d’écran 2024-02-02 à 21 56 32](https://github.com/lucas-kacz/Listen_AI/assets/74963340/db483e1b-a347-4f23-bb9f-398544f59723)

![Capture d’écran 2024-02-02 à 22 55 08](https://github.com/lucas-kacz/Listen_AI/assets/74963340/a52c3394-90bc-4a71-9e5c-1b600007047c)

![Capture d’écran 2024-02-02 à 19 58 05](https://github.com/lucas-kacz/Listen_AI/assets/74963340/c7fb6e86-1c6b-407a-8768-df769816b07a)
