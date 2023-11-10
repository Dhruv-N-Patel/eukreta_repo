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
        objectArr = []
        for audio in request.FILES.getlist('audio'):
            audio_file = original_audio.objects.create(
                                        name=audio.name,
                                        file=audio,
                                        code = code
                                        )
            # audio_name[index] = audio_file.name
            transcript, emotion_labels,keywords=create_transcript_emotion(audio)
            tempKey = []
            i=0
            for item in keywords:
                temp = { item[0] , item[1]}
                tempKey.insert(i, temp)
                i = i +1
            print(tempKey)
            object = {
                "audio_name" : audio_file.name,
                "transcript":transcript,
                "emotion_labels":emotion_labels,
                "keywords":tempKey
            }
            objectArr.insert(index, object)
            index = index +1
            
            print(transcript,"hello Nikhil ")
        print(code)
        context= {"processed":objectArr , "code":str(code) , "transcript":transcript,"emotion_labels":emotion_labels,"keywords":keywords
                  }
        return render(request, "upload.html", context)
    return render(request, "index.html")
       
def Keywords_ex(text):
    kw_model = KeyBERT()
    keywords =  kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=None)
    
    return keywords

def translater(text):
    translator=Translator()
    lang_det=translator.detect(text)
    
    changed_txt= translator.translate(text, src='en', dest='tr')
    return lang_det,changed_txt


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

def dashboard(request):
    
    return render(request, "dashboard.html", {})


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
        keywords=Keywords_ex(transcript)
        print(Keywords_ex(transcript))


        RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
        TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")


        emotion = pipeline('sentiment-analysis',model='arpanghoshal/EmoRoBERTa')
        emotion_det= emotion(transcript)
        print(emotion_det)
        emotion_detected=emotion_det[0]["label"].capitalize()
        print("Ye lo",emotion_detected)
        satis=["Admiration","Amusement","Approval","Caring","Desire","Excitement","Gratitude","Joy","Love","Optimism","Pride","Realization","Relief","Surprise"]
        neutral=["Confusion","Curiosity","Neutral"]
        unsatis=["Anger","Disappointment","Disapproval","Disgust","Embarrassment","Fear","Grief","Nervousness","Remorse","Sadness"]
        if emotion_detected in satis :
            emotion_labels="Satisfied"
        elif emotion_detected in neutral:
            emotion_labels="Neutral"
        else:
            emotion_labels="Dissatisfied" 

        print(emotion_labels,"emotion label in function")

        return transcript ,emotion_labels,keywords
    except Exception as e:
        print(f"An error occurred: {e}")

