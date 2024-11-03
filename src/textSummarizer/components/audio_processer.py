import speech_recognition as sr
import wave
import pyaudio
import tempfile
import os

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def record_audio(self, duration=30):
        """Record audio for a given duration in seconds."""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        print("* recording")
        
        frames = []
        
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("* done recording")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the recorded audio to a temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return temp_file.name
    
    def audio_to_text(self, audio_file):
        """Convert an audio file to text using Google Speech Recognition."""
        try:
            if audio_file.endswith('.wav'):
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio)
                    
                # Clean up temporary file
                if audio_file.startswith(tempfile.gettempdir()):
                    os.remove(audio_file)
                    
                return text
            else:
                return "Unsupported audio format. Please use WAV files."
        except Exception as e:
            return f"Error in speech recognition: {str(e)}"