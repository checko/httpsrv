from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import netifaces

app = Flask(__name__)
auth = HTTPBasicAuth()

# Change the following credentials
username = "admin"
password_hash = generate_password_hash("password")

@auth.verify_password
def verify_password(username, password):
    return username == username and check_password_hash(password_hash, password)

# HTML template embedded in the code
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Server</title>
</head>
<body>
    <h1>File Server</h1>
    <ul>
        {% for file in files %}
            <li><a href="{{ url_for('uploaded_file', filename=file) }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label for="file">Choose a file to upload:</label>
        <input type="file" name="file" id="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""

def run_flask_app(interface_name):
    ip_address = netifaces.ifaddresses(interface_name)[netifaces.AF_INET][0]['addr']
    app.run(host=ip_address, port=5000, debug=True)

@app.route('/')
@auth.login_required
def index():
    path = './uploads'
    files = os.listdir(path)
    return render_template_string(html_template, files=files)

@app.route('/uploads/<filename>')
@auth.login_required
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        uploads_folder = 'uploads'
        file.save(os.path.join(uploads_folder, file.filename))
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Run Flask app on eth0
    #run_flask_app('eth0')

    # Run Flask app on wlan0
    run_flask_app('wlan0')

