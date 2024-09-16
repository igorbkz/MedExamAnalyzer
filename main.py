import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from utils.openai_helper import analyze_medical_exam
import PyPDF2
from io import BytesIO
from docx import Document
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1 MB limit
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'content': self.content,
            'result': self.result,
            'created_at': self.created_at.isoformat()
        }

with app.app_context():
    db.create_all()

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

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
            elif file_extension == 'docx':
                doc = Document(BytesIO(file.read()))
                file_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            else:
                file_content = file.read().decode('utf-8')
            
            analysis = analyze_medical_exam(file_content)
            
            # Save the analysis to the database
            new_analysis = Analysis(filename=filename, content=file_content, result=analysis)
            db.session.add(new_analysis)
            db.session.commit()
            
            return jsonify({'analysis': analysis, 'id': new_analysis.id})
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyses', methods=['GET'])
def get_analyses():
    analyses = Analysis.query.order_by(Analysis.created_at.desc()).all()
    return jsonify([analysis.to_dict() for analysis in analyses])

@app.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    return jsonify(analysis.to_dict())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
