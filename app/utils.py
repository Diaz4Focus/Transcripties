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
    result = " ".join(segment.text for segment in segments if segment.text)
    print("✅ Transcriptie klaar.")
    return result.strip()

def transcribe_with_timestamps(filepath, model_size="medium", language="auto"):
    print("⏳ Start transcriptie met tijdstempels...")
    if model_size not in model_cache:
        model_cache[model_size] = WhisperModel(model_size)
    model = model_cache[model_size]
    segments, _ = model.transcribe(filepath, beam_size=5, language=None if language == "auto" else language)
    lines = []
    for segment in segments:
        start = int(segment.start)
        end = int(segment.end)
        start_ts = f"{start//60:02}:{start%60:02}"
        end_ts = f"{end//60:02}:{end%60:02}"
        lines.append(f"[{start_ts} - {end_ts}] {segment.text.strip()}")
    result = "\n".join(lines)
    print("✅ Timestamps transcriptie klaar.")
    return result.strip()

def correct_text(text):
    print("⏳ Start spellingscorrectie...")
    tool = language_tool_python.LanguageTool("nl")
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    print("✅ Correctie klaar.")
    return corrected.strip()

def summarize_text(text):
    print("⏳ Start samenvatting...")
    if not text or len(text.split()) < 10:
        return "Te weinig input voor samenvatting."
    # Simpele samenvatting: langste 3 zinnen
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    longest = sorted(sentences, key=len, reverse=True)[:3]
    summary = ". ".join(longest) + "."
    print("✅ Samenvatting klaar.")
    return summary.strip()
