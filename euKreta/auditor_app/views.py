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

def index(request):
    context ={
        "data":"Gfg is the best",
        "list":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    return render(request,'index.html', context)

def Document_save(request):
    if request.method=="POST":
        audio = request.FILES["audio"]
        code = datetime.datetime.now()
        index = 0
        audio_name = []
        for audio in request.FILES.getlist('audio'):
            audio_file = original_audio.objects.create(
                                        name=audio.name,
                                        file=audio,
                                        code = code
                                        )
            # audio_name[index] = audio_file.name
            audio_name.insert(index, audio_file.name)
            index = index +1
            
            transcript, emotion_labels=create_transcript_emotion(audio)
            print(transcript,"hello Nikhil ")
        print(code)
        context= {"audio_name":audio_name , "code":str(code) , "transcript":transcript,"emotion_labels":emotion_labels
                  }
        return render(request, "upload.html", context)
    return render(request, "index.html")
       

def processed_data(request,pk) :
    processed_data= Processed.objects.get()
    context={
        'processed_data': processed_data
    }
    return render(request, 'results.html', context)

def Process(request,pk):
    special_code = pk

    objects_with_code = original_audio.objects.filter(code=special_code)
    print(objects_with_code)

    for original in objects_with_code:
        print(original)

        
        processed = Processed(
            name=original.name,
            original_file = original.file,
            # processed_file = ,
            # Transcript = generatd_transcript,
            # Mood = project.skills,
            # Satisfaction = project.tools,
            # DetailsShared = project.genre,
        )
        processed.save()
    return render(request, "results.html", {})   


def convert_mp3_to_wav(input_mp3, output_wav):
    audio = AudioFileClip(input_mp3)
    audio.write_audiofile(output_wav, codec='pcm_s16le', fps=audio.fps)
    return output_wav

def split_audio(input_wav, output_folder, snippet_length_ms=30000):
    audio = AudioSegment.from_file(input_wav)
    snippet_length = snippet_length_ms  # 30 seconds (in milliseconds)
    j=0
    for i, start_time in enumerate(range(0, len(audio), snippet_length)):
        end_time = start_time + snippet_length
        snippet = audio[start_time:end_time]
        snippet.export(f"{output_folder}/snippet_{i+1}.wav", format="wav")
        j=j+1
    return j

def aud2txt(generated_wav):
    recognizer = sr.Recognizer()
    with sr.AudioFile(generated_wav) as source:
        audio = recognizer.record(source)
        try:
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language="en-IN")
            print(f"User said: {query}")
            return query
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            return None
        
def create_transcript_emotion(audio):
    print(f"Input audio: {audio}")
    input_mp3 = 'http://127.0.0.1:8000/media/' + audio.name
    output_wav =audio.name + "_output.wav"
    
    try:
        generated_wav = convert_mp3_to_wav(input_mp3, output_wav)
        print("Conversion successful.")
        
        output_folder = "output_snippets"
        os.makedirs(output_folder, exist_ok=True)
        split_audio(generated_wav, output_folder)
        j=split_audio(generated_wav, output_folder)
        
        transcript = ""
        for i in range(1, j):  # Assuming you have 3 snippets
            input_wav = f"{output_folder}/snippet_{i}.wav"
            snippet_transcript = aud2txt(input_wav)
            if snippet_transcript:
                transcript += snippet_transcript + " "
        
        print("\nFinal Transcript:")
        print(transcript)
        
        RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
        TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")


        emotion = pipeline('sentiment-analysis',model='arpanghoshal/EmoRoBERTa')
        emotion_labels = emotion(transcript)
        print(emotion_labels,"emotion label in function")
        return transcript ,emotion_labels
    except Exception as e:
        print(f"An error occurred: {e}")

