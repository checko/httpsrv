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
                <th>Name</th>
                <th>Type</th>
                <th>Size (bytes)</th>
                <th>Date Modified</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
                <tr>
                    <td>
                        {% if item['type'] == 'file' %}
                            <a href="{{ url_for('uploaded_file', filename=item['name']) }}">{{ item['name'] }}</a>
                        {% elif item['type'] == 'directory' %}
                            <a href="{{ url_for('browse_directory', path=item['path']) }}">{{ item['name'] }}</a>
                        {% endif %}
                    </td>
                    <td>{{ item['type'] }}</td>
                    <td>{{ item['size'] }}</td>
                    <td>{{ item['date_modified'] }}</td>
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

def get_item_info(item_path):
    item_stat = os.stat(item_path)
    size = item_stat.st_size
    date_modified = datetime.fromtimestamp(item_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

    if os.path.isfile(item_path):
        return {'name': os.path.basename(item_path), 'type': 'file', 'size': size, 'date_modified': date_modified}
    elif os.path.isdir(item_path):
        return {'name': os.path.basename(item_path), 'type': 'directory', 'size': size, 'date_modified': date_modified, 'path': item_path}

@app.route('/')
@auth.login_required
def index():
    path = './uploads'
    items = [get_item_info(os.path.join(path, item)) for item in os.listdir(path)]
    return render_template_string(html_template, items=items)

@app.route('/uploads/<path:filename>')
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
        uploads_folder = 'uploads'
        file.save(os.path.join(uploads_folder, file.filename))
    
    return redirect(url_for('index'))

@app.route('/browse/<path:path>')
@auth.login_required
def browse_directory(path):
    directory_path = os.path.join('./', path)
    items = [get_item_info(os.path.join(directory_path, item)) for item in os.listdir(directory_path)]
    return render_template_string(html_template, items=items)

if __name__ == '__main__':

    # Run Flask app on wlan0 in the main thread
    run_flask_app('wlan0')
    
