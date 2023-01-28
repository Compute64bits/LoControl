from flask import Flask, render_template, send_file, request, redirect, flash
from flask_sock import Sock
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin
from PIL import ImageGrab, Image
from io import BytesIO
from base64 import b64encode
from win32api import SetCursorPos, mouse_event
from win32con import MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
from secrets import token_hex
from keyboard import press, release

DEBUG = True

app = Flask(__name__)
app.config['SECRET_KEY'] = token_hex(256)
sock = Sock(app)
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)

login_id = 0
class User(UserMixin):
    def __init__(self, name, password):
        global login_id
        self.id = int(login_id)
        self.username = str(name)
        self.password = str(password)
        login_id += 1

    def __str__(self):
        return f"User(id='{self.id}')"

users = []

with open("Users.txt") as file:
    for line in file:
        users += [User(line.split(":")[0], line.split(":")[1])]

@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if str(user.id) == str(user_id):
            return user
    return None

@app.route('/')
@login_required
def index():
    return render_template("index.html")

@app.route('/main.js')
@login_required
def js():
    return send_file('templates/main.js', 'text/javascript')

@app.route('/style.css')
@login_required
def css():
    return send_file('templates/style.css', 'text/css')

@app.errorhandler(404)
@login_required
def e404(_):
    return "404"

def screenshot():
    img = ImageGrab.grab(bbox=None, include_layered_windows=True)
    buff = BytesIO()
    img = img.resize((1792, 1008), Image.Resampling.LANCZOS) # 1280; 720 if is laggy
    img.save(buff, format="WEBP", optimize=True, quality=60)
    b64 = b64encode(buff.getvalue())
    return "data:image/png;base64," + b64.decode("utf-8")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        for user in users:
            if user.username == username and user.password == password:
                login_user(user)
                return redirect("/")
        return redirect("/login")
    return render_template("login.html")

@app.route('/login.css')
def LoginCss():
    return send_file('templates/login.css', 'text/css')
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(redirect("/login"))

@sock.route('/ws')
@login_required
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
            try:
                cursor_x = int(text.split("cursor:")[1].split(":")[0])
                cursor_y = int(text.split("cursor:")[1].split(":")[1])
                SetCursorPos((cursor_x, cursor_y))
            except:
                return "Error: Invalid cursor position"
        elif len(text.split("keypress:")) > 1:
            try:
                key = text.split("keypress:")[1]
                press(key)
            except:
                return "Error: Invalid key"
        elif len(text.split("keyrelease:")) > 1:
            try:
                key = text.split("keyrelease:")[1]
                release(key)
            except:
                return "Error: Invalid key"


if __name__ == "__main__":
    app.run("0.0.0.0", 80,DEBUG, threaded=True)
