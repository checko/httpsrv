from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

# Change the following credentials
username = "admin"
password_hash = generate_password_hash("password")

@auth.verify_password
def verify_password(username, password):
    return username == username and check_password_hash(password_hash, password)

@app.route('/')
@auth.login_required
def index():
    path = './uploads'
    files = os.listdir(path)
    return render_template('index.html', files=files)

@app.route('/uploads/<filename>')
@auth.login_required
def uploaded_file(filename):
    return send_from_directory('./uploads', filename)

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        file.save(os.path.join('uploads', file.filename))
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='192.168.33.254',debug=True)

