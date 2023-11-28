import os
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification
from transformers import pipeline
# import win32com.client
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
import speech_recognition as sr
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline
from keybert import KeyBERT
# import googletrans
from googletrans import Translator

def convert_mp3_to_wav(input_mp3, output_wav):
    if input_mp3.endswith(".mp3"):
        audio = AudioFileClip(input_mp3)
        audio.write_audiofile(output_wav, codec='pcm_s16le', fps=audio.fps)
    elif input_mp3.endswith(".wav"):
        # No conversion needed, just copy the file
        output_wav = input_mp3
    else:
        raise ValueError("Unsupported file format. Supported formats: .mp3, .wav")

    return output_wav

def Keywords_ex(text):
    kw_model = KeyBERT()
    keywords =  kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=None)
    
    return keywords

def translater(text):
    translator=Translator()
    lang_det=translator.detect(text)
    
    changed_txt= translator.translate(text, src='en', dest='tr')
    return lang_det,changed_txt

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
            query = recognizer.recognize_google(audio, language="gu-IN")
            print(f"User said: {query}")
            return query
        except Exception as e:
            print(f"An error occurred during transcription: {e}")
            return None
        
def detect_emotion(transcript):
    roberta_tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
    roberta_model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")

    emotion_pipeline = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')
    emotion_det = emotion_pipeline(transcript)
    emotion_detected = emotion_det[0]["label"].capitalize()

    satis = ["Admiration", "Amusement", "Approval", "Caring", "Desire", "Excitement", "Gratitude", "Joy", "Love",
             "Optimism", "Pride", "Realization", "Relief", "Surprise"]
    neutral = ["Confusion", "Curiosity", "Neutral"]
    unsatis = ["Anger", "Disappointment", "Disapproval", "Disgust", "Embarrassment", "Fear", "Grief", "Nervousness",
               "Remorse", "Sadness"]

    if emotion_detected in satis:
        emotion_labels = "Satisfied"
    elif emotion_detected in neutral:
        emotion_labels = "Neutral"
    else:
        emotion_labels = "Dissatisfied"

    return emotion_labels


def create_transcript_emotion(audio):
    print(f"Input audio: {audio}")
    input_mp3 = 'http://127.0.0.1:8000/media/' + audio.name

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