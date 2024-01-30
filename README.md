# Listen_AI

## Motivation behind this project

The aim of this project is to transcript audio files and to summarize them in the desired amount of sentences. Some use cases might be news audios, podcasts or documentaries when you don't have the time to listen to them completely.

## How does it work ?

The project is a complete web app with a backend written in Flask in order to be able to use the Whisper Library and a React frontend where you can upload, read the transcript of the uploaded audio file and summarize it.

This app automatically detects the language of the audio and transcripts it in the same language.

This app is hosted on this [website](https://cc08-217-160-142-195.ngrok-free.app/) and you can try to summarize your own audios.

## Installation 

Make a venv in the backend folder
https://flask.palletsprojects.com/en/3.0.x/installation/

Install required libraries

```
pip install flask
pip install flask-cors
```

Install Whisper
https://github.com/openai/whisper

Install Mistral 7B Model
```pip3 install git+https://github.com/huggingface/transformers.git@72958fcd3c98a7afdc61f953aa58c544ebda2f79```
