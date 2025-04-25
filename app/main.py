from flask import Flask, render_template, request, send_from_directory, jsonify
from app.utils import transcribe_audio, correct_text, summarize_text, transcribe_with_timestamps
import os
from datetime import datetime
from threading import Thread, Lock

app = Flask(__name__, template_folder="templates", static_folder="static")
# dit is vrije tekst

UPLOAD_FOLDER = os.path.abspath("app/uploads")
OUTPUT_FOLDER = os.path.abspath("app/output")
CORRECTED_FOLDER = os.path.join(OUTPUT_FOLDER, "corrected")
FREEFORM_FOLDER = os.path.abspath("Freeform")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CORRECTED_FOLDER, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_FOLDER, "raw"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_FOLDER, "summary"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_FOLDER, "timestamps"), exist_ok=True)

class TaskManager:
    def __init__(self):
        self.lock = Lock()
        self.current_thread = None
        self.cancel_requested = False

    def start_task(self, target, args):
        with self.lock:
            self.cancel_requested = False
            self.current_thread = Thread(target=target, args=args)
            self.current_thread.start()
            self.current_thread.join()

    def cancel(self):
        with self.lock:
            self.cancel_requested = True

    def is_cancelled(self):
        with self.lock:
            return self.cancel_requested

task_manager = TaskManager()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def handle_upload():
    file = request.files["audio_file"]
    model_size = request.form.get("model_size", "medium")
    language = request.form.get("language", "auto")

    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".m4a"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    task_manager.start_task(process_file, (filepath, filename, model_size, language))

    base = filename.replace(".m4a", "")
    return render_template("index.html", message="Verwerking voltooid!", filename=base, success=True)

@app.route("/cancel", methods=["POST"])
def cancel():
    task_manager.cancel()
    return ("", 204)

@app.route("/output/<subfolder>/<path:filename>")
def download_file(subfolder, filename):
    folder = os.path.join(OUTPUT_FOLDER, subfolder)
    if not os.path.exists(os.path.join(folder, filename)):
        return f"❌ Bestand niet gevonden: {filename}", 404
    return send_from_directory(folder, filename, as_attachment=False)

@app.route("/freeform/list")
def list_freeform():
    try:
        files = [f for f in os.listdir(FREEFORM_FOLDER) if f.endswith(".m4a")]
        return jsonify(files)
    except Exception:
        return jsonify([]), 500

@app.route("/corrected/list")
def list_corrected():
    try:
        files = [f for f in os.listdir(CORRECTED_FOLDER) if f.endswith(".txt")]
        return jsonify(files)
    except Exception:
        return jsonify([]), 500

@app.route("/corrected/preview/<filename>")
def preview_corrected(filename):
    path = os.path.join(CORRECTED_FOLDER, filename)
    if not os.path.exists(path):
        return "Bestand niet gevonden", 404
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        preview = "".join(lines[:20])
    return preview

def process_file(filepath, filename, model_size, language):
    if task_manager.is_cancelled(): return
    raw = transcribe_audio(filepath, model_size, language)
    if task_manager.is_cancelled(): return
    corrected = correct_text(raw)
    if task_manager.is_cancelled(): return
    summary = summarize_text(corrected)
    if task_manager.is_cancelled(): return
    timestamps = transcribe_with_timestamps(filepath, model_size, language)
    if task_manager.is_cancelled(): return

    base = filename.replace(".m4a", "")
    with open(os.path.join(OUTPUT_FOLDER, "raw", f"{base}.txt"), "w") as f:
        f.write(raw)
    with open(os.path.join(OUTPUT_FOLDER, "corrected", f"{base}.txt"), "w") as f:
        f.write(corrected)
    with open(os.path.join(OUTPUT_FOLDER, "summary", f"{base}.txt"), "w") as f:
        f.write(summary)
    with open(os.path.join(OUTPUT_FOLDER, "timestamps", f"{base}.txt"), "w") as f:
        f.write(timestamps)

if __name__ == "__main__":
    print("✅ main.py gestart")
    app.run(host="0.0.0.0", port=5000, debug=True)
