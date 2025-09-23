"""
Voice Service for Speech-to-Text and Text-to-Speech functionality
Supports multiple languages including Hindi, Telugu, English
"""
import os
import io
import wave
import tempfile
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition not installed. Voice input will be disabled.")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not installed. Voice output will be limited.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gtts not installed. Google TTS will be disabled.")

class VoiceService:
    def __init__(self):
        self.recognizer = None
        self.tts_engine = None
        
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Adjust for ambient noise
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
        
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                # Configure TTS settings
                self.tts_engine.setProperty('rate', 150)  # Speed of speech
                self.tts_engine.setProperty('volume', 0.8)  # Volume level
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3 engine: {e}")
                self.tts_engine = None
        
        # Language mappings for different services
        self.language_mappings = {
            'en': {
                'google': 'en-US',
                'gtts': 'en',
                'display_name': 'English'
            },
            'hi': {
                'google': 'hi-IN',
                'gtts': 'hi',
                'display_name': 'Hindi'
            },
            'te': {
                'google': 'te-IN',
                'gtts': 'te',
                'display_name': 'Telugu'
            },
            'ta': {
                'google': 'ta-IN',
                'gtts': 'ta',
                'display_name': 'Tamil'
            },
            'kn': {
                'google': 'kn-IN',
                'gtts': 'kn',
                'display_name': 'Kannada'
            }
        }

    def speech_to_text(self, audio_buffer: io.BytesIO, language: str = "en") -> str:
        """
        Convert speech audio to text
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            return "Speech recognition not available. Please install speech_recognition library."
        
        try:
            # Get language code for Google Speech Recognition
            lang_code = self.language_mappings.get(language, {}).get('google', 'en-US')
            
            # Save audio buffer to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_buffer.getvalue())
                temp_file_path = temp_file.name
            
            try:
                # Load audio file
                with sr.AudioFile(temp_file_path) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    # Listen for audio
                    audio = self.recognizer.listen(source)
                
                # Try Google Speech Recognition first
                try:
                    text = self.recognizer.recognize_google(audio, language=lang_code)
                    logger.info(f"Google STT successful for language {language}")
                    return text
                except sr.RequestError:
                    # Fallback to offline recognition if available
                    logger.warning("Google STT failed, trying offline recognition")
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        return text
                    except (sr.RequestError, sr.UnknownValueError):
                        return "Could not understand the audio. Please try again with clear speech."
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Speech to text error: {e}")
            return f"Error processing speech: {str(e)}"

    def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech audio
        Returns audio data as bytes
        """
        try:
            # Try Google TTS first (supports more languages)
            if GTTS_AVAILABLE and language in self.language_mappings:
                return self._gtts_synthesis(text, language)
            
            # Fallback to pyttsx3 (offline, but limited language support)
            elif PYTTSX3_AVAILABLE and self.tts_engine:
                return self._pyttsx3_synthesis(text, language)
            
            else:
                # Return empty audio if no TTS available
                logger.warning("No TTS engines available")
                return self._generate_silence()
                
        except Exception as e:
            logger.error(f"Text to speech error: {e}")
            return self._generate_silence()

    def _gtts_synthesis(self, text: str, language: str) -> bytes:
        """Generate speech using Google TTS"""
        try:
            lang_code = self.language_mappings[language]['gtts']
            
            # Create gTTS object
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to BytesIO buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return self._generate_silence()

    def _pyttsx3_synthesis(self, text: str, language: str) -> bytes:
        """Generate speech using pyttsx3 (offline)"""
        try:
            if not self.tts_engine:
                return self._generate_silence()
            
            # Set voice based on language (limited support)
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find appropriate voice
            target_voice = None
            if language == 'hi' and voices:
                # Look for Hindi voice
                for voice in voices:
                    if 'hindi' in voice.name.lower() or 'hi' in voice.id.lower():
                        target_voice = voice.id
                        break
            
            if target_voice:
                self.tts_engine.setProperty('voice', target_voice)
            
            # Generate speech to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                self.tts_engine.save_to_file(text, temp_file_path)
                self.tts_engine.runAndWait()
                
                # Read the generated audio file
                with open(temp_file_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                return audio_data
                
            finally:
                # Clean up
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"pyttsx3 synthesis error: {e}")
            return self._generate_silence()

    def _generate_silence(self, duration: float = 1.0) -> bytes:
        """Generate silence as fallback when TTS fails"""
        try:
            # Generate 1 second of silence
            sample_rate = 22050
            samples = int(sample_rate * duration)
            silence = b'\\x00' * (samples * 2)  # 16-bit samples
            
            # Create WAV file in memory
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(silence)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating silence: {e}")
            return b""

    def get_supported_languages(self) -> dict:
        """Get list of supported languages for voice operations"""
        return {
            lang_code: {
                'name': info['display_name'],
                'stt_available': SPEECH_RECOGNITION_AVAILABLE,
                'tts_available': GTTS_AVAILABLE or PYTTSX3_AVAILABLE
            }
            for lang_code, info in self.language_mappings.items()
        }

    def is_voice_input_available(self) -> bool:
        """Check if voice input is available"""
        return SPEECH_RECOGNITION_AVAILABLE

    def is_voice_output_available(self) -> bool:
        """Check if voice output is available"""
        return GTTS_AVAILABLE or PYTTSX3_AVAILABLE

# Global instance
voice_service = VoiceService()

# Export functions for direct use
def speech_to_text(audio_buffer: io.BytesIO, language: str = "en") -> str:
    return voice_service.speech_to_text(audio_buffer, language)

def text_to_speech(text: str, language: str = "en") -> bytes:
    return voice_service.text_to_speech(text, language)

def get_voice_capabilities() -> dict:
    return {
        'input_available': voice_service.is_voice_input_available(),
        'output_available': voice_service.is_voice_output_available(),
        'supported_languages': voice_service.get_supported_languages()
    }