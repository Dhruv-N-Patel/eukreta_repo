import os
from transformers import pipeline
# import win32com.client
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
import speech_recognition as sr
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline
from keybert import KeyBERT
# import googletrans
from googletrans import Translator
import langid
from google.cloud import speech_v1p1beta1 as speech

# def detect_language(content):
#     client = language_v1.LanguageServiceClient()

#     # Specify the content type (e.g., PLAIN_TEXT or SSML)
#     type_ = enums.Document.Type.PLAIN_TEXT
#     document = {"content": content, "type": type_}

#     # Detect the language
#     response = client.detect_language(document=document)
#     language = response.languages[0].language_code

#     return language

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

    lang, _ = langid.classify(text)

    if lang == 'en':
        kw_model = KeyBERT()

    else:
        kw_model = KeyBERT(model="paraphrase-multilingual-MiniLM-L12-v2")

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

def convert_to_mono(input_path, output_path):
    audio = AudioSegment.from_wav(input_path)
    mono_audio = audio.set_channels(1)
    mono_audio.export(output_path, format="wav")

def transcribe_audio(file_path):
    # Set the environment variable for Google Cloud credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\dhruv\Documents\eukreta_repo\euKreta\key.json"

    # Convert the audio file to mono
    mono_path = file_path
    convert_to_mono(file_path, mono_path)
    # Initialize the Speech-to-Text client
    client = speech.SpeechClient()

    # Configure the audio file
    audio_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=audio.frame_rate,
        language_code="hi-IN",
    )

    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    # Request transcription
    response = client.recognize(config=audio_config, audio=audio)

    # Extract transcriptions from the response
    transcriptions = [result.alternatives[0].transcript for result in response.results]

    return transcriptions

def aud2txt(generated_wav):
    try:
        print("Transcribing...")
        transcriptions = transcribe_audio(generated_wav)
        if transcriptions:
            for i, transcription in enumerate(transcriptions):
                print(f"Segment {i + 1}: {transcription}")

            # Return a list of transcriptions
            return transcriptions
        else:
            print("No transcriptions found.")
            return []
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return []
    
def detect_emotion(transcript):
    # Detect the language of the transcript
    lang, _ = langid.classify(transcript)

    # Check if the detected language is English
    if lang == 'en':
        # Continue with emotion detection for English text
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
    else:
        # If the language is not English, return a message indicating that the language is not supported
        return "Language not supported"
