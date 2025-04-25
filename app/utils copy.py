# Handige functies zoals transcriptie, spellcheck, samenvatting
import language_tool_python
from faster_whisper import WhisperModel
import os

model_cache = {}

def transcribe_audio(filepath, model_size="medium", language="auto"):
    print("⏳ Start transcriptie...")
    if model_size not in model_cache:
        model_cache[model_size] = WhisperModel(model_size)
    model = model_cache[model_size]
    segments, _ = model.transcribe(filepath, beam_size=5, language=None if language == "auto" else language)
    result = " ".join(segment.text for segment in segments)
    print("✅ Transcriptie klaar.")
    return result

def correct_text(text):
    print("⏳ Start spellingscorrectie...")
    tool = language_tool_python.LanguageTool("nl")
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    print("✅ Correctie klaar.")
    return corrected

def summarize_text(text):
    print("⏳ Start samenvatting...")
    if not text or len(text.split()) < 10:
        return "Te weinig input voor samenvatting."
    # Simpele samenvatting: langste 3 zinnen
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    longest = sorted(sentences, key=len, reverse=True)[:3]
    summary = ". ".join(longest) + "."
    print("✅ Samenvatting klaar.")
    return summary
