# DedoMouse
DedoMouse let's you control your computer mouse with your hands and a webcam.

Therefor, it uses the hand and finger tracking of Google's [MediaPipe](https://google.github.io/mediapipe/solutions/hands).

For available mouse actions and the corresponding hand gestures see [here](https://achimmihca.github.io/DedoMouse/)

Feel free to suggest questions, ideas and issues on [GitHub](https://github.com/achimmihca/DedoMouse/issues).

## Development
You are encouraged to contribute code.
The following explains how to set up a development environment.

### Python Setup
- Install a recent version of Python (3.9.x or newer)
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

## License
DedoMouse itself is under [MIT License](https://github.com/achimmihca/DedoMouse/blob/main/LICENSE).

However, licenses of the used libraries (see requirements.txt) and resources (e.g. images) may differ.
- mediapipe: [Apache License v2.0](https://github.com/google/mediapipe/blob/master/LICENSE)
- opencv: [Apache License v2.0](https://github.com/opencv/opencv/blob/master/LICENSE)
- rxpy: [Apache License v2.0](https://github.com/Reactive-Extensions/RxPy/blob/master/LICENSE)
- screeninfo: [MIT](https://github.com/rr-/screeninfo/blob/master/LICENSE.md)
- keyboard: [MIT](https://github.com/boppreh/keyboard/blob/master/LICENSE.txt)
- mouse: [MIT](https://github.com/boppreh/mouse/blob/master/LICENSE.txt)
- jsonpickle: [BSD](https://github.com/jsonpickle/jsonpickle/blob/main/LICENSE)
- numpy: [NumPy License (similar to BSD)](https://numpy.org/doc/stable/license.html)
- pyside6: [LGPL/GPL v3.0](https://wiki.qt.io/PySide2)
    - Qt: [LGPLv3/GPL](https://www.qt.io/licensing/)
- qt-material: [BSD](https://github.com/UN-GCPDS/qt-material/blob/master/LICENSE)
- material-design-icons: [Apache License v2.0](https://github.com/google/material-design-icons/blob/master/LICENSE)

For development only:
- pylint: [GPL v2.0](https://github.com/rr-/pylint/blob/main/LICENSE)
- mypy: [MIT and others](https://github.com/python/mypy/blob/master/LICENSE)
- pyinstaller: [Custom GPL](https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt)

## Trivia
'Dedo' is Spanish and means 'finger'.
