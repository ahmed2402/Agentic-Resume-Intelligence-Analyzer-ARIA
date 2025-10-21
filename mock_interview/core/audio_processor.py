"""
Audio processing module for Mock Interview Analyzer
Handles audio recording, speech-to-text conversion, and audio analysis
"""

import streamlit as st
import numpy as np
import librosa
import soundfile as sf
import io
import tempfile
import os
from typing import Dict, List, Tuple, Optional
import speech_recognition as sr
import wave

class AudioProcessor:
    """Handles uploaded audio processing and speech-to-text conversion"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def speech_to_text(self, audio_data: bytes) -> str:
        """
        Convert speech audio to text using Google Speech Recognition
        """
        try:
            # Ensure WAV bytes are 16kHz mono 16-bit PCM
            wav_bytes, sample_rate = self._ensure_wav_16k_mono(audio_data)
            # Create AudioData object
            audio = sr.AudioData(wav_bytes, sample_rate, 2)
            
            # Convert to text
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results: {e}"
        except Exception as e:
            return f"Error in speech recognition: {str(e)}"
    
    def analyze_audio_features(self, audio_data: bytes) -> Dict:
        """
        Analyze audio features for confidence and clarity assessment
        """
        try:
            # Normalize audio to 16kHz mono PCM first
            wav_bytes, _sr = self._ensure_wav_16k_mono(audio_data)
            audio_array = np.frombuffer(wav_bytes, dtype=np.int16)
            
            # Convert to float32 and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Calculate audio features
            features = {}
            
            # Volume analysis
            features['volume'] = np.mean(np.abs(audio_float))
            features['volume_std'] = np.std(np.abs(audio_float))
            
            # Silence detection
            silence_threshold = 0.01
            silence_frames = np.sum(np.abs(audio_float) < silence_threshold)
            features['silence_ratio'] = silence_frames / len(audio_float)
            
            # Speech rate (approximate)
            features['speech_rate'] = self._calculate_speech_rate(audio_float)
            
            # Pitch variation (confidence indicator)
            features['pitch_variation'] = self._calculate_pitch_variation(audio_float)
            
            # Pause analysis
            features['pause_count'] = self._count_pauses(audio_float)
            
            return features
            
        except Exception as e:
            st.error(f"Error analyzing audio features: {str(e)}")
            return {}
    
    def _calculate_speech_rate(self, audio: np.ndarray) -> float:
        """Calculate approximate speech rate (words per minute)"""
        # This is a simplified calculation
        # In practice, you'd use more sophisticated methods
        energy = np.abs(audio)
        energy_threshold = np.mean(energy) * 0.1
        
        # Count energy peaks (approximate word boundaries)
        peaks = np.where(energy > energy_threshold)[0]
        if len(peaks) > 1:
            duration_minutes = len(audio) / (16000 * 60)  # Assuming 16kHz sample rate
            return len(peaks) / duration_minutes
        return 0.0
    
    def _calculate_pitch_variation(self, audio: np.ndarray) -> float:
        """Calculate pitch variation as confidence indicator"""
        try:
            # Use librosa for pitch analysis
            pitches, magnitudes = librosa.piptrack(y=audio, sr=16000)
            pitch_values = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 1:
                return np.std(pitch_values) / np.mean(pitch_values)
            return 0.0
        except:
            return 0.0
    
    def _count_pauses(self, audio: np.ndarray) -> int:
        """Count pauses in speech"""
        energy = np.abs(audio)
        energy_threshold = np.mean(energy) * 0.05
        
        # Find silence periods
        silence_mask = energy < energy_threshold
        
        # Count transitions from speech to silence
        transitions = np.diff(silence_mask.astype(int))
        pause_count = np.sum(transitions == 1)  # Speech to silence transitions
        
        return pause_count
    
    def save_audio_file(self, audio_data: bytes, filename: str) -> str:
        """Save audio data to file"""
        try:
            filepath = os.path.join(tempfile.gettempdir(), filename)
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            return filepath
        except Exception as e:
            st.error(f"Error saving audio file: {str(e)}")
            return ""

    def _ensure_wav_16k_mono(self, audio_bytes: bytes) -> Tuple[bytes, int]:
        """Convert arbitrary audio bytes to 16kHz mono 16-bit PCM WAV bytes.
        Returns (wav_bytes, sample_rate).
        """
        try:
            # Read with soundfile
            data, sr = sf.read(io.BytesIO(audio_bytes), always_2d=False)
            # Convert to mono
            if data.ndim > 1:
                data = np.mean(data, axis=1)
            # Resample if needed
            target_sr = 16000
            if sr != target_sr:
                data = librosa.resample(y=data.astype(np.float32), orig_sr=sr, target_sr=target_sr)
                sr = target_sr
            # Scale to int16
            data = np.clip(data, -1.0, 1.0)
            pcm16 = (data * 32767.0).astype(np.int16)
            # Write WAV to bytes
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(pcm16.tobytes())
            return buffer.getvalue(), sr
        except Exception:
            # If conversion fails, return original bytes and assume 16000
            return audio_bytes, 16000
