import os
import uuid
from flask import Flask, render_template, request
import json

import librosa
import soundfile as sf


app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'uploads'
app.config['PROCESSING_PATH'] = 'processed'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():
    if not os.path.exists(app.config['UPLOAD_PATH']):
        os.makedirs(app.config['UPLOAD_PATH'])

    uploaded_files = request.files.getlist('file')

    for uploaded_file in uploaded_files:
        file_extension = os.path.splitext(uploaded_file.filename.lower())[-1]
        if file_extension == '':
            continue
        filename = uploaded_file.filename #str(uuid.uuid4()) + file_extension
        document_path = os.path.join(app.config['UPLOAD_PATH'], filename)
        uploaded_file.save(document_path)

    filenames =  os.listdir(app.config['UPLOAD_PATH'])

    return render_template('index.html', filenames=filenames)

@app.route('/output')
def output():
    if not os.path.exists(app.config['PROCESSING_PATH']):
        os.makedirs(app.config['PROCESSING_PATH'])
    for file in os.listdir(app.config['UPLOAD_PATH']):
        x, sr  = librosa.load(app.config['UPLOAD_PATH']+'/'+file, sr=16000)
        sf.write(app.config['UPLOAD_PATH']+'/'+os.path.splitext(file)[0]+'.wav', x, 16000)

    os.system('python run_aec.py -i '+ app.config['UPLOAD_PATH'] + ' -o ' + app.config['PROCESSING_PATH'] + ' -m ./pretrained_models/dtln_aec_512')
    if not os.path.exists(app.config['UPLOAD_PATH']):
        os.makedirs(app.config['UPLOAD_PATH'])
    for file in os.listdir(app.config['UPLOAD_PATH']):
        os.remove(app.config['UPLOAD_PATH'] + '/' + file)
    return render_template('output.html')

@app.route('/clean')
def clean():

    if not os.path.exists(app.config['UPLOAD_PATH']):
        os.makedirs(app.config['UPLOAD_PATH'])
    for file in os.listdir(app.config['UPLOAD_PATH']):
        os.remove(app.config['UPLOAD_PATH'] + '/' + file)
    return render_template('clean.html')

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port=5000)




