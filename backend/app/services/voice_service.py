"""
Voice Service for Speech-to-Text and Text-to-Speech functionality
Supports multiple languages including Hindi, Telugu, English
"""
import os
import io
import wave
import tempfile
import time
import traceback
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
    # Allow disabling gTTS via environment variable (useful if Google TTS is blocked)
    GTTS_AVAILABLE = os.environ.get('DISABLE_GTTS', '').lower() != 'true'
    if not GTTS_AVAILABLE:
        logger.info("gTTS disabled via DISABLE_GTTS environment variable. Using pyttsx3 fallback.")
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
                # Configure TTS settings - increased speed for faster speech
                self.tts_engine.setProperty('rate', 200)  # Increased speed of speech (was 150)
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
            'ml': {
                'google': 'ml-IN',
                'gtts': 'ml',
                'display_name': 'Malayalam'
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

    def text_to_speech(self, text: str, language: str = "en") -> dict:
        """
        Convert text to speech audio and save to file
        Returns dict with audio_path and audio_data
        Tries multiple engines with intelligent fallback
        Language parameter is now properly used for TTS synthesis
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return {"audio_data": self._generate_silence(duration=0.5), "audio_path": None, "language": language}
        
        try:
            logger.info(f"text_to_speech requested for language: {language}, text length: {len(text)}")
            logger.info(f"Available engines - gTTS: {GTTS_AVAILABLE}, pyttsx3: {PYTTSX3_AVAILABLE}")
            
            # Validate and normalize language
            if language not in self.language_mappings:
                logger.warning(f"Language {language} not in mappings, using English")
                language = "en"
            
            # First, try Google TTS if available (better quality for longer text)
            if GTTS_AVAILABLE and language in self.language_mappings:
                logger.info(f"Attempting gTTS synthesis for {language} (gtts code: {self.language_mappings[language]['gtts']})")
                try:
                    audio_data, audio_path = self._gtts_synthesis(text, language)
                    if audio_data and len(audio_data) > 500:  # Substantial audio
                        logger.info(f"Successfully using gTTS audio ({len(audio_data)} bytes) for {language}, saved to {audio_path}")
                        return {"audio_data": audio_data, "audio_path": audio_path, "language": language}
                    else:
                        logger.warning(f"gTTS produced insufficient audio ({len(audio_data) if audio_data else 0} bytes), trying pyttsx3")
                except Exception as e:
                    logger.error(f"gTTS synthesis failed with exception: {e}")
            
            # Second, fallback to pyttsx3 if available
            if PYTTSX3_AVAILABLE and self.tts_engine:
                logger.info(f"Attempting pyttsx3 synthesis for {language}")
                try:
                    audio_data, audio_path = self._pyttsx3_synthesis(text, language)
                    if audio_data and len(audio_data) > 500:  # Substantial audio
                        logger.info(f"Successfully using pyttsx3 audio ({len(audio_data)} bytes) for {language}, saved to {audio_path}")
                        return {"audio_data": audio_data, "audio_path": audio_path, "language": language}
                    else:
                        logger.warning(f"pyttsx3 produced insufficient audio ({len(audio_data) if audio_data else 0} bytes)")
                except Exception as e:
                    logger.error(f"pyttsx3 synthesis failed with exception: {e}")
            
            # Last resort: generate silence with appropriate duration
            logger.warning("Both TTS engines failed, returning silence")
            word_count = len(text.split())
            estimated_duration = max(1.0, (word_count / 150.0) * 60.0)
            return {"audio_data": self._generate_silence(duration=estimated_duration), "audio_path": None, "language": language}
                
        except Exception as e:
            logger.error(f"Text to speech error: {type(e).__name__}: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            word_count = len(text.split())
            estimated_duration = max(1.0, (word_count / 150.0) * 60.0)
            return {"audio_data": self._generate_silence(duration=estimated_duration), "audio_path": None, "language": language}

    def _gtts_synthesis(self, text: str, language: str) -> tuple:
        """Generate speech using Google TTS with improved error handling and retry logic
        Returns (audio_data: bytes, audio_path: str) tuple
        """
        try:
            lang_code = self.language_mappings[language]['gtts']
            
            # Estimate audio duration based on text length
            word_count = len(text.split())
            estimated_duration = max(1.0, (word_count / 150.0) * 60.0)
            
            logger.info(f"Starting gTTS synthesis for language {language} ({lang_code}) with {word_count} words")
            
            # Retry logic for gTTS - try up to 2 times (reduced from 3 for faster fallback)
            max_retries = 2
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    logger.debug(f"gTTS attempt {attempt + 1}/{max_retries}")
                    # Increased timeout and added connect_timeout
                    tts = gTTS(text=text, lang=lang_code, slow=False, timeout=5)
                    logger.debug(f"gTTS object created successfully on attempt {attempt + 1}")
                    
                    # Save to persistent file
                    import uuid
                    audio_filename = f"tts_output_{language}_{uuid.uuid4().hex[:8]}.mp3"
                    audio_path = os.path.join(tempfile.gettempdir(), audio_filename)
                    
                    tts.save(audio_path)
                    logger.info(f"gTTS audio saved to {audio_path} on attempt {attempt + 1}")
                    
                    # Read audio data
                    with open(audio_path, 'rb') as f:
                        audio_data = f.read()
                    
                    logger.info(f"gTTS synthesis successful on attempt {attempt + 1}, audio size: {len(audio_data)} bytes")
                    
                    # Verify we got substantial audio data
                    if audio_data and len(audio_data) > 500:
                        logger.info(f"Returning gTTS audio - path: {audio_path}, size: {len(audio_data)}")
                        return (audio_data, audio_path)
                    else:
                        logger.warning(f"gTTS returned small audio ({len(audio_data)} bytes), retrying...")
                        last_error = f"Small audio output ({len(audio_data)} bytes)"
                        # Clean up small file
                        try:
                            os.unlink(audio_path)
                        except:
                            pass
                        continue
                        
                except Exception as e:
                    last_error = f"{type(e).__name__}: {e}"
                    logger.warning(f"gTTS attempt {attempt + 1} failed: {last_error}")
                    # Shorter wait time - only wait if not last attempt
                    if attempt < max_retries - 1:
                        time.sleep(0.5)  # Reduced from 1 second to 0.5 seconds for faster fallback
                    continue
            
            logger.error(f"gTTS failed after {max_retries} attempts. Last error: {last_error}. Using pyttsx3 fallback.")
            # Fall back to pyttsx3
            logger.info("Falling back to pyttsx3 synthesis")
            return self._pyttsx3_synthesis(text, language)
            
        except Exception as e:
            logger.error(f"gTTS synthesis error: {type(e).__name__}: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            logger.info("gTTS error - using pyttsx3 fallback")
            return self._pyttsx3_synthesis(text, language)

    def _pyttsx3_synthesis(self, text: str, language: str) -> tuple:
        """Generate speech using pyttsx3 (offline) - works as fallback
        Returns (audio_data: bytes, audio_path: str) tuple
        """
        try:
            if not self.tts_engine:
                logger.warning("pyttsx3 engine not initialized")
                return (self._generate_silence(), None)
            
            logger.debug(f"pyttsx3 synthesis starting for language {language}")
            
            # Set voice based on language (limited support)
            voices = self.tts_engine.getProperty('voices')
            logger.debug(f"Available voices: {len(voices)}")
            
            # Try to find appropriate voice
            target_voice = None
            if language == 'hi' and voices:
                # Look for Hindi voice
                for voice in voices:
                    voice_name_lower = voice.name.lower()
                    voice_id_lower = voice.id.lower()
                    logger.debug(f"Checking voice: {voice.name} (ID: {voice.id})")
                    
                    if 'hindi' in voice_name_lower or 'hi-in' in voice_id_lower or ('समान' in voice.name):
                        target_voice = voice.id
                        logger.info(f"Found Hindi voice: {voice.name}")
                        break
                
                if not target_voice and voices:
                    # If no Hindi voice found, log available voices
                    logger.warning(f"No Hindi voice found. Available voices: {[v.name for v in voices]}")
                    # Use first available voice
                    target_voice = voices[0].id
                    logger.info(f"Using first available voice: {voices[0].name}")
            elif voices and not target_voice:
                # Use first available voice as fallback
                target_voice = voices[0].id
                logger.debug(f"Using first available voice: {voices[0].name}")
            
            if target_voice:
                self.tts_engine.setProperty('voice', target_voice)
                logger.debug(f"Set voice to: {target_voice}")
            
            # Generate speech to temporary file
            import uuid
            audio_filename = f"tts_output_{language}_{uuid.uuid4().hex[:8]}.wav"
            temp_file_path = os.path.join(tempfile.gettempdir(), audio_filename)
            
            try:
                logger.debug(f"Saving audio to temporary file: {temp_file_path}")
                self.tts_engine.save_to_file(text, temp_file_path)
                self.tts_engine.runAndWait()
                
                # Add delay to ensure file is fully written to disk
                logger.debug("Waiting for file to be written...")
                time.sleep(1.0)  # Increased from 0.5 to 1.0 seconds
                
                # Verify file exists and has content
                if not os.path.exists(temp_file_path):
                    logger.warning("Audio file was not created")
                    return (self._generate_silence(), None)
                
                file_size = os.path.getsize(temp_file_path)
                logger.debug(f"Generated file size: {file_size} bytes")
                
                if file_size == 0:
                    logger.warning("pyttsx3 generated empty audio file, retrying with longer delay...")
                    # Retry once more with longer delay
                    time.sleep(2.0)
                    file_size = os.path.getsize(temp_file_path)
                    logger.debug(f"After retry, file size: {file_size} bytes")
                
                # Read the generated audio file
                if os.path.exists(temp_file_path) and file_size > 0:
                    with open(temp_file_path, 'rb') as audio_file:
                        audio_data = audio_file.read()
                    
                    if audio_data:
                        logger.info(f"pyttsx3 synthesis successful, audio size: {len(audio_data)} bytes, saved to {temp_file_path}")
                        return (audio_data, temp_file_path)
                
                # If file is empty or doesn't exist, return silence
                logger.warning("pyttsx3 audio file is empty or unreadable")
                return (self._generate_silence(), None)
                
            except Exception as e:
                logger.error(f"pyttsx3 save_to_file error: {type(e).__name__}: {e}")
                logger.debug(f"Full traceback: {traceback.format_exc()}")
                return (self._generate_silence(), None)
            finally:
                # Clean up
                try:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                except Exception as e:
                    logger.debug(f"Cleanup error: {e}")
                    
        except Exception as e:
            logger.error(f"pyttsx3 synthesis error: {type(e).__name__}: {e}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return (self._generate_silence(), None)

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