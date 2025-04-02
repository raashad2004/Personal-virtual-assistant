import os
import re
from typing import Dict, List, Any, Tuple
from googletrans import Translator
from gtts import gTTS
import pygame
import tempfile
import time
import string

# Initialize translator
translator = Translator()

# Initialize pygame mixer for audio playback
pygame.mixer.init()

def translate_text(text: str, target_language: str = 'en') -> Dict[str, str]:
    """Translate text to the target language"""
    try:
        translation = translator.translate(text, dest=target_language)
        return {
            "original_text": text,
            "translated_text": translation.text,
            "source_language": translation.src,
            "target_language": translation.dest
        }
    except Exception as e:
        return {
            "error": str(e),
            "original_text": text,
            "translated_text": "",
            "source_language": "",
            "target_language": target_language
        }

def detect_language(text: str) -> Dict[str, Any]:
    """Detect the language of the given text"""
    try:
        detection = translator.detect(text)
        return {
            "language": detection.lang,
            "confidence": detection.confidence,
            "text": text
        }
    except Exception as e:
        return {
            "error": str(e),
            "language": "unknown",
            "confidence": 0.0,
            "text": text
        }

def text_to_speech(text: str, language: str = 'en', save_file: bool = False, filename: str = None) -> str:
    """Convert text to speech and play it"""
    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name

        # Generate speech
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(temp_filename)
        
        # Play the audio
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        # Save the file permanently if requested
        if save_file:
            if not filename:
                now = time.strftime("%Y%m%d_%H%M%S")
                filename = f"speech_{now}.mp3"
            
            if not os.path.exists("audio"):
                os.makedirs("audio")
            
            permanent_path = os.path.join("audio", filename)
            import shutil
            shutil.copy(temp_filename, permanent_path)
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            return f"Speech saved to {permanent_path}"
        else:
            # Clean up temporary file
            os.unlink(temp_filename)
            return "Speech played successfully"
    except Exception as e:
        return f"Error in text-to-speech: {str(e)}"

def count_words(text: str) -> Dict[str, Any]:
    """Count words, sentences, and characters in text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Count words
    words = text.split()
    word_count = len(words)
    
    # Count sentences
    sentence_count = len(re.split(r'[.!?]+', text)) - 1
    if sentence_count < 0:
        sentence_count = 0
    
    # Count characters
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", ""))
    
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "character_count": char_count,
        "character_count_no_spaces": char_count_no_spaces
    }

def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Create a simple extractive summary of the text"""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= max_sentences:
        return text
    
    # Simple summarization by selecting the first few sentences
    summary = ' '.join(sentences[:max_sentences])
    
    return summary

def get_language_name(language_code: str) -> str:
    """Convert language code to full language name"""
    language_map = {
        'af': 'Afrikaans',
        'ar': 'Arabic',
        'bg': 'Bulgarian',
        'bn': 'Bengali',
        'ca': 'Catalan',
        'cs': 'Czech',
        'cy': 'Welsh',
        'da': 'Danish',
        'de': 'German',
        'el': 'Greek',
        'en': 'English',
        'es': 'Spanish',
        'et': 'Estonian',
        'fa': 'Persian',
        'fi': 'Finnish',
        'fr': 'French',
        'gu': 'Gujarati',
        'he': 'Hebrew',
        'hi': 'Hindi',
        'hr': 'Croatian',
        'hu': 'Hungarian',
        'id': 'Indonesian',
        'is': 'Icelandic',
        'it': 'Italian',
        'ja': 'Japanese',
        'kn': 'Kannada',
        'ko': 'Korean',
        'lt': 'Lithuanian',
        'lv': 'Latvian',
        'ml': 'Malayalam',
        'mr': 'Marathi',
        'ms': 'Malay',
        'nl': 'Dutch',
        'no': 'Norwegian',
        'pl': 'Polish',
        'pt': 'Portuguese',
        'ro': 'Romanian',
        'ru': 'Russian',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'sq': 'Albanian',
        'sv': 'Swedish',
        'sw': 'Swahili',
        'ta': 'Tamil',
        'te': 'Telugu',
        'th': 'Thai',
        'tr': 'Turkish',
        'uk': 'Ukrainian',
        'ur': 'Urdu',
        'vi': 'Vietnamese',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)'
    }
    
    return language_map.get(language_code.lower(), f"Unknown ({language_code})")

def correct_spelling(text: str) -> str:
    """Very basic spelling correction for common mistakes"""
    # This is a very simple implementation
    # For real applications, use a library like pyspellchecker
    common_mistakes = {
        "teh": "the",
        "dont": "don't",
        "cant": "can't",
        "wont": "won't",
        "isnt": "isn't",
        "didnt": "didn't",
        "shouldnt": "shouldn't",
        "couldnt": "couldn't",
        "wouldnt": "wouldn't",
        "im": "I'm",
        "ive": "I've",
        "youre": "you're",
        "theyre": "they're",
        "thats": "that's",
        "hes": "he's",
        "shes": "she's",
        "its": "it's",  # Note: will incorrectly "fix" possessive its
        "theres": "there's",
        "alot": "a lot",
        "alright": "all right",
        "recieve": "receive",
        "wierd": "weird",
        "beleive": "believe",
        "definately": "definitely",
        "occured": "occurred",
        "untill": "until",
        "accross": "across",
        "wich": "which"
    }
    
    words = re.findall(r'\b\w+\b', text.lower())
    
    for word in words:
        if word in common_mistakes:
            # Replace with correct word, preserving case
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            replacement = common_mistakes[word]
            text = pattern.sub(replacement, text)
    
    return text 