from django.shortcuts import render
from .models import original_audio, Processed
import datetime
from auditor_app.models import original_audio
import os
import speech_recognition as sr
from django.shortcuts import render
from .models import original_audio, Processed
from .utils import detect_emotion, Keywords_ex, convert_mp3_to_wav, aud2txt, split_audio


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
        j_splits = split_audio(generated_wav, output_folder)

        transcriptions = []

        for i in range(1, j_splits):  # Corrected the range
            input_wav = f"{output_folder}/snippet_{i}.wav"
            snippet_transcription = aud2txt(input_wav)
            transcriptions.append(snippet_transcription)

        print("\nFinal Transcriptions:")
        print(transcriptions)

        flattened_transcriptions = [item for sublist in transcriptions for item in sublist]

        # Join the flattened list into a single string
        full_transcript = " ".join(flattened_transcriptions)

        print(full_transcript)

        keywords = Keywords_ex(" ".join(full_transcript))
        print(keywords)

        emotion_labels = detect_emotion(" ".join(full_transcript))
        print(emotion_labels, "emotion label in function")

        return transcriptions, emotion_labels, keywords, full_transcript 
    except Exception as e:
        print(f"An error occurred: {e}")
        return [], "", []

def Process(request, pk):
    special_code = pk

    objects_with_code = original_audio.objects.filter(code=special_code)

    processed_data = []

    for original in objects_with_code:
        transcriptions, emotion_labels, keywords, full_transcript = create_transcript_emotion_keywords(original.file)

        processed_instance = Processed(
                name=f"{original.name}",
                original_file=original.file,
                Transcript=transcriptions,
                Satisfaction=emotion_labels,
                DetailsShared=keywords,
                full_transcript=full_transcript,  # Set the full_transcript field
                code=original.code,
                # Add other fields as needed
                )
        processed_instance.save()
        processed_data.append(processed_instance)

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
        objectArr.append(object)

    context = {"processed": objectArr}
    return render(request, "results.html", context)