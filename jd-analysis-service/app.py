from flask import Flask, request, jsonify
import spacy
from rake_nltk import Rake
import yake
import nltk
import os
import traceback
from flask_cors import CORS

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

app = Flask(__name__)  # Only declare once
CORS(app)  # Only declare once

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

# Load models and extractors once
nlp = spacy.load('en_core_web_sm')
rake_extractor = Rake()
yake_extractor = yake.KeywordExtractor(lan='en', top=10)

# SpaCy keyword extraction
def spacy_keywords(text, n=10):
    doc = nlp(text)
    phrases = [c.text for c in doc.noun_chunks if c.text.lower() not in nlp.Defaults.stop_words]
    freq = {p: phrases.count(p) for p in set(phrases)}
    return [p for p, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]]

# RAKE keyword extraction
def rake_keywords(text, n=10):
    rake_extractor.extract_keywords_from_text(text)
    return rake_extractor.get_ranked_phrases()[:n]

# YAKE keyword extraction
def yake_keywords(text):
    return [kw for kw, _ in yake_extractor.extract_keywords(text)]

# Keyword Extraction API Route
@app.route('/extract-keywords', methods=['POST'])
def extract():
    try:
        text = request.json.get('description', '')
        sp = spacy_keywords(text)
        rk = rake_keywords(text)
        yk = yake_keywords(text)
        
        combined = []
        for lst in (sp, rk, yk):
            for phrase in lst:
                if phrase not in combined:
                    combined.append(phrase)
        
        return jsonify({'keywords': combined})
    
    except Exception as e:
        print("Flask error:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Resume tailoring endpoint
@app.route('/api/tailor-resume', methods=['POST'])
def tailor_resume():
    try:
        data = request.get_json()
        
        resume_data = data.get('resume_data')
        job_description = data.get('job_description')
        job_title = data.get('job_title')
        company_name = data.get('company_name')
        
        if not all([resume_data, job_description, job_title]):
            return jsonify({'error': 'Missing required data'}), 400
        
        # Simple tailoring logic for now
        result = {
            "tailored_summary": f"Experienced {job_title} with expertise in relevant technologies",
            "enhanced_experience": resume_data.get('experience', []),
            "optimized_skills": resume_data.get('skills', ''),
            "match_score": 85.0,
            "suggestions": ["Add more job-relevant keywords", "Highlight achievements with metrics"],
            "job_analysis": {"skills": [], "keywords": [], "requirements": []}
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in tailor_resume: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
