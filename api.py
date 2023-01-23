from flask import Flask, render_template, send_file, request, redirect, flash
from flask_sock import Sock
from PIL import ImageGrab, Image
from io import BytesIO
from base64 import b64encode
from random import randint
from win32api import SetCursorPos, mouse_event
from win32con import MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP

DEBUG = True

app = Flask(__name__)
app.config['SECRET_KEY'] = str([randint(0,9) for _ in range(randint(50, 150))]) # Random key
sock = Sock(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/main.js')
def js():
    return send_file('templates/main.js', 'text/javascript')

@app.route('/style.css')
def css():
    return send_file('templates/style.css', 'text/css')

@app.errorhandler(404)
def e404(_):
    return "404"

def screenshot():
    img = ImageGrab.grab(bbox=None, include_layered_windows=True)
    buff = BytesIO()
    img = img.resize((1408, 792), Image.Resampling.LANCZOS)
    img.save(buff, format="WEBP", optimize=True, quality=50)
    b64 = b64encode(buff.getvalue())
    return "data:image/png;base64," + b64.decode("utf-8")

@sock.route('/ws')
def handlemsg(ws):
    cursor_x, cursor_y = 0, 0
    while True:
        text = str(ws.receive())
        if text == "get":
            ws.send(screenshot())
        elif text == "rightdown":
            mouse_event(MOUSEEVENTF_RIGHTDOWN, cursor_x, cursor_y)
        elif text == "rightup":
            mouse_event(MOUSEEVENTF_RIGHTUP, cursor_x, cursor_y)
        elif text == "leftdown":
            mouse_event(MOUSEEVENTF_LEFTDOWN, cursor_x, cursor_y)
        elif text == "leftup":
            mouse_event(MOUSEEVENTF_LEFTUP, cursor_x, cursor_y)
        elif len(text.split("cursor:")) > 1:
            cursor_x = int(text.split("cursor:")[1].split(":")[0])
            cursor_y = int(text.split("cursor:")[1].split(":")[1])
            SetCursorPos((cursor_x, cursor_y))


if __name__ == "__main__":
    app.run("0.0.0.0", 80, DEBUG, threaded=True)