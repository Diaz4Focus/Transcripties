

import os

folders = [
    "app",
    "app/static",
    "app/templates",
    "app/uploads",
    "app/output/raw",
    "app/output/corrected",
    "app/output/summary",
    "models"
]

files = {
    "Dockerfile": "",
    "app/__init__.py": "",
    "app/main.py": "# Hier komt je Flask of Gradio app\n",
    "app/utils.py": "# Handige functies zoals transcriptie, spellcheck, samenvatting\n",
    "app/templates/index.html": "<!-- WebGUI HTML komt hier -->\n",
    ".gitignore": "app/uploads/*\napp/output/*\n",
    "requirements.txt": "flask\ngradio\nfaster-whisper\nlanguage-tool-python\nsumy\n"
}

for folder in folders:
    os.makedirs(folder, exist_ok=True)

for file_path, content in files.items():
    with open(file_path, "w") as f:
        f.write(content)

print("✅ Projectstructuur is aangemaakt!")
