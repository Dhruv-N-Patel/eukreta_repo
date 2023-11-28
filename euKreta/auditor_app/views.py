from django.shortcuts import render
from .models import original_audio, Processed
from django.http import HttpResponse
import datetime
from auditor_app.models import original_audio
import os
import win32com.client
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
import speech_recognition as sr
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline
from keybert import KeyBERT
import googletrans
from googletrans import Translator
from django.shortcuts import render
from .models import original_audio, Processed
from .utils import create_transcript_emotion, detect_emotion, Keywords_ex, convert_mp3_to_wav, aud2txt, split_audio


def index(request):
    context ={
        "data":"Gfg is the best",
        "list":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    return render(request,'index.html', context)

def dashboard(request):
    
    return render(request, "dashboard.html", {})

def Document_save(request):
    if request.method == "POST":
        audio_files = request.FILES.getlist('audio')
        code = datetime.datetime.now()
        objectArr = []


        for audio in audio_files:
            audio_file = original_audio.objects.create(
                name = audio.name.replace(" ", "").replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace("#", "").replace(",", ""),
                file=audio,
                code=code
            )

            object = {
                "audio_name": audio_file.name,
                "code": code
            }
            objectArr.append(object)

        context = {"processed": objectArr, "code": code}
        return render(request, "upload.html", context)
    #return render(request, "index.html")

def create_transcript_emotion_keywords(audio):
    print(f"Input audio: {audio}")
    
    input_mp3 = os.path.join('media', audio.name)

    output_wav = audio.name + "_output.wav"

    try:
        generated_wav = convert_mp3_to_wav(input_mp3, output_wav)
        print("Conversion successful.")

        output_folder = "output_snippets"
        os.makedirs(output_folder, exist_ok=True)
        split_audio(generated_wav, output_folder)

        print("KUCH TOH HUA")

        transcript = ""
        for i in range(1, 3):  # Assuming you have 3 snippets
            input_wav = f"{output_folder}/snippet_{i}.wav"
            snippet_transcript = aud2txt(input_wav)
            if snippet_transcript:
                transcript += snippet_transcript + " "

        print("\nFinal Transcript:")
        print(transcript)

        keywords = Keywords_ex(transcript)
        print(keywords)

        emotion_labels = detect_emotion(transcript)
        print(emotion_labels, "emotion label in function")

        return transcript, emotion_labels, keywords
    except Exception as e:
        print(f"An error occurred: {e}")
        return "", "", []

def Process(request, pk):
    special_code = pk

    objects_with_code = original_audio.objects.filter(code=special_code)
    processed_data = []

    for original in objects_with_code:
        transcript, emotion_labels, keywords = create_transcript_emotion_keywords(original.file)

        processed = Processed(
            name=original.name,
            original_file=original.file,
            Transcript=transcript,
            Satisfaction=emotion_labels,
            DetailsShared=keywords,
            code=original.code,
            # Add other fields as needed
        )
        processed.save()

        # processed_data.append({
        #     "audio_name": original.name,
        #     "transcript": transcript,
        #     "emotion_labels": emotion_labels,
        #     "keywords": [{"word": item[0], "score": item[1]} for item in keywords]
        # })

    context = {"processed": processed_data, "code": special_code}
    return render(request, "process.html", context)

def processed_data(request,pk) :
    special_code = pk

    processed_data = Processed.objects.filter(code=special_code)

    objectArr = []

    for data in processed_data:
        print(data.DetailsShared)
        object = {
            "audio_name": data.name,
            "transcript": data.Transcript,
            "emotion_labels": data.Satisfaction,
            "keywords": [{"word": item[0], "score": item[1]} for item in data.DetailsShared]
        }
        # print(object,"ye hhua ki nhi bata jaldi")
        objectArr.append(object)

    context = {"processed": objectArr}
    return render(request, "results.html", context)