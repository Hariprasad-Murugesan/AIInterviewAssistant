"""
TranscriberModels.py
------
"""


import os
import torch
import assemblyai as aai  # Import AssemblyAI SDK

# Configure AssemblyAI API key (replace with your actual key)
aai.settings.api_key = "faddcc17140b4552a73a1af9d065fd31"  # Add your AssemblyAI API key


def get_model(use_api):
    if use_api:
        return APIWhisperTranscriber()
    else:
        return WhisperTranscriber()

# WhisperTranscriber Whisper 。
class WhisperTranscriber:
    # WhisperTranscriber  Whisper 。
    def __init__(self):
        self.audio_model = whisper.load_model(os.path.join(os.getcwd(), 'whisper_models', 'tiny.pt'))
        print(f"[INFO] Whisper using GPU: " + str(torch.cuda.is_available()))

    
    def get_transcription(self, wav_file_path):
        try:
            result = self.audio_model.transcribe(wav_file_path, fp16=torch.cuda.is_available())
        except Exception as e:
            print(e)
            return ''
        return result['text'].strip()

# APIWhisperTranscriber AssemblyAI API 。
class APIWhisperTranscriber:
    
    def get_transcription(self, wav_file_path):
        try:
            # Configure the transcriber
            config = aai.TranscriptionConfig(language_code="en")  # Adjust language if needed
            transcriber = aai.Transcriber()
            
            # Transcribe the audio file
            transcript = transcriber.transcribe(wav_file_path, config=config)
            
            # Check for errors
            if transcript.status == aai.TranscriptStatus.error:
                print(f"Transcription failed: {transcript.error}")
                return ''
            
            # Return the transcribed text
            return transcript.text.strip()
        except Exception as e:
            print(f"Error during transcription: {e}")
            return ''