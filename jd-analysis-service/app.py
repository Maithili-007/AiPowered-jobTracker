from flask import Flask, request, jsonify
import spacy
from rake_nltk import Rake
import yake
import nltk
import os
import traceback

# 🧠 Fix nltk path issue (makes sure it looks in correct directory)
nltk.data.path.append(os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "nltk_data"))
nltk.download('punkt')

app = Flask(__name__)#initializes your Flask app

# 🔧 Load models and extractors once
nlp = spacy.load('en_core_web_sm')
rake_extractor = Rake()
yake_extractor = yake.KeywordExtractor(lan='en', top=10)

# 📌 SpaCy keyword extraction
def spacy_keywords(text, n=10):
    doc = nlp(text)
    phrases = [c.text for c in doc.noun_chunks if c.text.lower() not in nlp.Defaults.stop_words]
    freq = {p: phrases.count(p) for p in set(phrases)}
    return [p for p, _ in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]]

# 📌 RAKE keyword extraction
def rake_keywords(text, n=10):
    rake_extractor.extract_keywords_from_text(text)
    return rake_extractor.get_ranked_phrases()[:n]

# 📌 YAKE keyword extraction
def yake_keywords(text):
    return [kw for kw, _ in yake_extractor.extract_keywords(text)]

# 🧠 Keyword Extraction API Route
@app.route('/extract-keywords', methods=['POST'])
def extract():
    try:
        text = request.json.get('description', '')#Gets the job description sent by the user
        #print("Received text:", text) 

        sp = spacy_keywords(text)
        rk = rake_keywords(text)
        yk = yake_keywords(text)

        combined = []
        for lst in (sp, rk, yk):
            for phrase in lst:
                if phrase not in combined:
                    combined.append(phrase)

       # print("Extracted keywords:", combined) 
        return jsonify({'keywords': combined})

    except Exception as e:
        print("🔥 Flask error:", str(e))
        traceback.print_exc() 
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001)
