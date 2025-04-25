# Hier komt je Flask of Gradio app
from flask import Flask, render_template, request, send_from_directory
from app.utils import transcribe_audio, correct_text, summarize_text
import os
from datetime import datetime
from threading import Thread

app = Flask(__name__, template_folder="templates", static_folder="static")

# Mappen voor upload en output
UPLOAD_FOLDER = os.path.abspath("app/uploads")
OUTPUT_FOLDER = os.path.abspath("app/output")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(f"{OUTPUT_FOLDER}/raw", exist_ok=True)
os.makedirs(f"{OUTPUT_FOLDER}/corrected", exist_ok=True)
os.makedirs(f"{OUTPUT_FOLDER}/summary", exist_ok=True)

# Voor annuleren & threading
current_thread = None
cancel_requested = False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def handle_upload():
    global current_thread, cancel_requested

    file = request.files["audio_file"]
    model_size = request.form.get("model_size", "medium")
    language = request.form.get("language", "auto")

    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".m4a"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    cancel_requested = False
    current_thread = Thread(target=process_file, args=(filepath, filename, model_size, language))
    current_thread.start()
    current_thread.join()

    return render_template("index.html", message="Verwerking voltooid!", filename=filename.replace(".m4a", ""))

@app.route("/cancel", methods=["POST"])
def cancel():
    global cancel_requested
    cancel_requested = True
    return ("", 204)

@app.route("/output/<subfolder>/<path:filename>")
def download_file(subfolder, filename):
    full_path = os.path.join(OUTPUT_FOLDER, subfolder, filename)
    if not os.path.exists(full_path):
        return f"❌ Bestand niet gevonden: {full_path}", 404
    return send_from_directory(os.path.join(OUTPUT_FOLDER, subfolder), filename, as_attachment=False)

def process_file(filepath, filename, model_size, language):
    global cancel_requested
    raw_text = transcribe_audio(filepath, model_size, language)
    if cancel_requested: return
    corrected_text = correct_text(raw_text)
    if cancel_requested: return
    summary = summarize_text(corrected_text)
    if cancel_requested: return

    base_filename = filename.replace(".m4a", "")
    print(f"✅ Opslaan naar: {OUTPUT_FOLDER}/corrected/{base_filename}.txt")

    with open(os.path.join(OUTPUT_FOLDER, "raw", f"{base_filename}.txt"), "w") as f:
        f.write(raw_text)
    with open(os.path.join(OUTPUT_FOLDER, "corrected", f"{base_filename}.txt"), "w") as f:
        f.write(corrected_text)
    with open(os.path.join(OUTPUT_FOLDER, "summary", f"{base_filename}.txt"), "w") as f:
        f.write(summary)

if __name__ == "__main__":
    print("✅ main.py gestart")
    app.run(host="0.0.0.0", port=5000, debug=True)
