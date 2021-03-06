@ECHO OFF
call "D://py-printer-win/py-printer-win/env/Scripts/activate.bat"
set FLASK_APP=printer.py
python -m flask run --port=8001
PAUSE