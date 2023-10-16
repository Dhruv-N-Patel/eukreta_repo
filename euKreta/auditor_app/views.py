from django.shortcuts import render
from .models import original_audio, Processed
from django.http import HttpResponse
import datetime
from auditor_app.models import original_audio


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
        print(code)
        context= {"audio_name":audio_name , "code":str(code)
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

def dashboard(request):
    
    return render(request, "dashboard.html", {})