# YouTube PiP Subtitle Player

A Python application that allows you to:
- Download YouTube videos
- Play videos in Picture-in-Picture mode
- Display subtitles
- Control playback

## Setup
1. Setting Virtual Envrionment:
```bash
python -m virtualenv kivy_venv
source kivy_venv/bin/activate
python -m pip install --upgrade pip setuptools virtualenv
```

2. Install Kivy and buildozer
```bash
python -m pip install "kivy[full]" kivy_examples
git clone https://github.com/kivy/buildozer.git
cd buildozer
python -m pip install --upgrade pip setuptools virtualenv
```

## Usage
Run the main script:
```bash
python main.py
```
