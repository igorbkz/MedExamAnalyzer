import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils.openai_helper import analyze_medical_exam
import PyPDF2
from io import BytesIO

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB limit

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        try:
            if file_extension == 'pdf':
                pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
                file_content = ""
                for page in pdf_reader.pages:
                    file_content += page.extract_text()
            else:
                file_content = file.read().decode('utf-8')
            
            analysis = analyze_medical_exam(file_content)
            return jsonify({'analysis': analysis})
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
