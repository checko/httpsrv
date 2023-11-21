from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import netifaces
import threading
from datetime import datetime

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
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid black;
        }
    </style>
</head>
<body>
    <h1>File Server</h1>
    <table>
        <thead>
            <tr>
                <th>File Name</th>
                <th>Size (bytes)</th>
                <th>Date Modified</th>
            </tr>
        </thead>
        <tbody>
            {% for file in files %}
                <tr>
                    <td><a href="{{ url_for('uploaded_file', filename=file['name']) }}">{{ file['name'] }}</a></td>
                    <td>{{ file['size'] }}</td>
                    <td>{{ file['date_modified'] }}</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label for="file">Choose files to upload:</label>
        <input type="file" name="file" id="file" multiple>
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""

def run_flask_app(interface_name):
    ip_address = netifaces.ifaddresses(interface_name)[netifaces.AF_INET][0]['addr']
    app.run(host=ip_address, port=5000, debug=True)

def get_file_info(file_path):
    file_stat = os.stat(file_path)
    size = file_stat.st_size
    date_modified = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    return {'name': os.path.basename(file_path), 'size': size, 'date_modified': date_modified}

@app.route('/')
@auth.login_required
def index():
    path = './'
    files = [get_file_info(os.path.join(path, file)) for file in os.listdir(path)]
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

    files = request.files.getlist('file')
    
    for file in files:
        if file.filename == '':
            continue
        uploads_folder = './'
        file.save(os.path.join(uploads_folder, file.filename))
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run Flask app on eth0 in a separate thread

    # Run Flask app on wlan0 in the main thread
    run_flask_app('wlan0')
    
    # Wait for the eth0 thread to finish
