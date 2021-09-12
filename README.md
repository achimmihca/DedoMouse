[![CircleCI](https://circleci.com/gh/achimmihca/DedoMouse.svg?style=svg)](https://github.com/achimmihca/DedoMouse)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/achimmihca/DedoMouse/blob/master/LICENSE)

# DedoMouse
DedoMouse let's you control your computer mouse with your hands and a webcam.

Therefor, it uses the hand and finger tracking of Google's [MediaPipe](https://google.github.io/mediapipe/solutions/hands).

For available mouse actions and the corresponding hand gestures see [here](https://github.com/achimmihca/DedoMouse/wiki/).

Feel free to suggest questions, ideas and issues on [GitHub](https://github.com/achimmihca/DedoMouse/issues).

## Development
You are encouraged to contribute code.
The following explains how to set up a development environment.

### Python Setup
- Install a recent version of Python (3.8 or newer)
- Clone the repo and navigate to the project folder
- Create a virtual environment: `python -m venv env`
- Activate the virtual environment: `env/Scripts/activate.bat` (`.bat` only on Windows)
- Install dependencies: `pip install -r requirements.txt`
- Start `src/main.py`
    - There is a launch configuration for Visual Studio Code that runs this file.

### Code Style
This project uses 
- pylint for code style checks (see `.pylintrc`).
- mypy for static type analysis (see `mypy.ini`).

As a rule of thumb, Python conventions should be followed.

### Create Executable
Open a console in the virtual environment, then run

`pyinstaller main.spec`

This should create a folder named `dist` with the executable.

## Trivia
'Dedo' is Spanish and means 'finger'.
