from flask import Flask, request, jsonify
import spacy
from spacy.matcher import PhraseMatcher
from rake_nltk import Rake
import yake
import nltk
import os
import traceback
from flask_cors import CORS

# Import our skill taxonomy module for normalization and filtering
# WHY: The skill_taxonomy module provides curated skill lists and normalization
# to filter out noise like "developed using" and normalize variants like "React.js" → "react"
from skill_taxonomy import (
    SKILL_WHITELIST,
    filter_and_normalize_skills,
    extract_skills_from_text,
    normalize_skill,
    is_valid_skill
)

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

app = Flask(__name__)  # Only declare once
CORS(app)  # Only declare once

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

# Load models and extractors once
nlp = spacy.load('en_core_web_sm')
rake_extractor = Rake()
yake_extractor = yake.KeywordExtractor(lan='en', top=20)  # Increased to get more candidates

# =============================================================================
# Initialize PhraseMatcher with skill whitelist
# =============================================================================
# WHY: PhraseMatcher is much more accurate than generic noun_chunk extraction.
# It only matches terms we explicitly define as valid skills, eliminating noise.
phrase_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
skill_patterns = [nlp.make_doc(skill) for skill in SKILL_WHITELIST]
phrase_matcher.add("SKILLS", skill_patterns)


# =============================================================================
# IMPROVED EXTRACTION FUNCTIONS
# =============================================================================

def spacy_skill_extraction(text: str) -> list:
    """
    Extract skills using spaCy PhraseMatcher instead of generic noun_chunks.
    
    WHY THIS IS BETTER:
    - OLD: doc.noun_chunks captured ANY noun phrase like "developed using this"
    - NEW: PhraseMatcher only matches terms in our skill whitelist
    
    This eliminates false positives and ensures we only extract real skills.
    
    Args:
        text: Job description or resume text
        
    Returns:
        List of matched skills (already normalized via PhraseMatcher's LOWER attr)
    """
    doc = nlp(text)
    matches = phrase_matcher(doc)
    
    # Extract matched text and normalize
    skills = []
    for match_id, start, end in matches:
        skill_text = doc[start:end].text.lower()
        normalized = normalize_skill(skill_text)
        if normalized and normalized not in skills:
            skills.append(normalized)
    
    return skills


def rake_keywords_filtered(text: str, n: int = 15) -> list:
    """
    Extract keywords using RAKE, then filter through skill taxonomy.
    
    WHY FILTERING IS NEEDED:
    RAKE extracts phrases based on word co-occurrence, which captures noise like:
    - "experience with the technology"
    - "developed using modern"
    - "strong background in"
    
    We filter these through our skill whitelist to keep only valid skills.
    
    Args:
        text: Job description or resume text
        n: Maximum number of phrases to extract before filtering
        
    Returns:
        List of valid, normalized skills extracted from RAKE output
    """
    rake_extractor.extract_keywords_from_text(text)
    raw_phrases = rake_extractor.get_ranked_phrases()[:n]
    
    # Filter and normalize through skill taxonomy
    return filter_and_normalize_skills(raw_phrases)


def yake_keywords_filtered(text: str) -> list:
    """
    Extract keywords using YAKE, then filter through skill taxonomy.
    
    WHY FILTERING IS NEEDED:
    YAKE uses statistical features (word frequency, position, etc.) which often
    extracts action verbs and generic terms that aren't skills:
    - "looking for"
    - "must have experience"
    - "responsible for"
    
    We filter these through our skill whitelist to keep only valid skills.
    
    Args:
        text: Job description or resume text
        
    Returns:
        List of valid, normalized skills extracted from YAKE output
    """
    raw_keywords = [kw for kw, _ in yake_extractor.extract_keywords(text)]
    
    # Filter and normalize through skill taxonomy
    return filter_and_normalize_skills(raw_keywords)


def extract_all_skills(text: str) -> list:
    """
    Comprehensive skill extraction using multiple methods.
    
    WHY MULTI-METHOD APPROACH:
    Each extraction method has different strengths:
    - spaCy PhraseMatcher: Precise matching of known skills
    - RAKE: Catches multi-word skill phrases
    - YAKE: Statistical approach for important terms
    - Direct whitelist scan: Catches skills others might miss
    
    By combining all methods and filtering through our taxonomy,
    we get the best coverage with minimal noise.
    
    Args:
        text: Job description or resume text
        
    Returns:
        Deduplicated list of normalized skills
    """
    all_skills = set()
    
    # Method 1: spaCy PhraseMatcher (most precise)
    spacy_skills = spacy_skill_extraction(text)
    all_skills.update(spacy_skills)
    
    # Method 2: RAKE with filtering
    rake_skills = rake_keywords_filtered(text)
    all_skills.update(rake_skills)
    
    # Method 3: YAKE with filtering
    yake_skills = yake_keywords_filtered(text)
    all_skills.update(yake_skills)
    
    # Method 4: Direct whitelist scanning (catches edge cases)
    # WHY: Some skills might be missed if they're part of longer phrases
    # This method directly searches for each whitelist skill in the text
    direct_skills = extract_skills_from_text(text)
    all_skills.update(direct_skills)
    
    return sorted(list(all_skills))


# =============================================================================
# LEGACY FUNCTIONS (kept for backwards compatibility with tests)
# =============================================================================

def spacy_keywords(text, n=10):
    """
    LEGACY: Original noun_chunks extraction.
    Kept for backwards compatibility but now uses filtered approach internally.
    """
    # Use new extraction method but return in expected format
    skills = spacy_skill_extraction(text)
    return skills[:n]


def rake_keywords(text, n=10):
    """
    LEGACY: Original RAKE extraction.
    Kept for backwards compatibility but now uses filtered approach internally.
    """
    return rake_keywords_filtered(text, n)


def yake_keywords(text):
    """
    LEGACY: Original YAKE extraction.
    Kept for backwards compatibility but now uses filtered approach internally.
    """
    return yake_keywords_filtered(text)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/extract-keywords', methods=['POST'])
def extract():
    """
    Keyword Extraction API - IMPROVED VERSION
    
    WHAT CHANGED:
    - Before: Combined raw outputs from spaCy/RAKE/YAKE with lots of noise
    - After: All outputs filtered through skill taxonomy for clean results
    
    The response now contains:
    - keywords: Deduplicated, normalized skills only (no "developed using", no duplicates)
    - raw_sources (optional): Debug info showing what each method extracted
    """
    try:
        text = request.json.get('description', '')
        
        if not text.strip():
            return jsonify({'keywords': []})
        
        # Use comprehensive extraction with filtering
        clean_skills = extract_all_skills(text)
        
        # Optional: Include debug info about extraction sources
        include_debug = request.json.get('debug', False)
        
        response = {'keywords': clean_skills}
        
        if include_debug:
            response['debug'] = {
                'spacy_skills': spacy_skill_extraction(text),
                'rake_skills': rake_keywords_filtered(text),
                'yake_skills': yake_keywords_filtered(text),
                'direct_skills': list(extract_skills_from_text(text))
            }
        
        return jsonify(response)
    
    except Exception as e:
        print("Flask error:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/extract-skills', methods=['POST'])
def extract_skills_endpoint():
    """
    NEW: Dedicated skill extraction endpoint.
    
    This is the recommended endpoint for skill extraction.
    Returns only validated, normalized skills with optional match scoring.
    
    Request body:
    {
        "description": "Job description text...",
        "resume_text": "Optional resume text for matching..."
    }
    
    Response:
    {
        "skills": ["react", "nodejs", "mongodb", ...],
        "skill_count": 5,
        "match_result": {  // Only if resume_text provided
            "score": 80.0,
            "matched": ["react", "nodejs"],
            "missing": ["mongodb"],
            "extra": ["python"]
        }
    }
    """
    try:
        data = request.json or {}
        description = data.get('description', '')
        resume_text = data.get('resume_text', '')
        
        if not description.strip():
            return jsonify({
                'skills': [],
                'skill_count': 0
            })
        
        # Extract skills from job description
        job_skills = extract_all_skills(description)
        
        response = {
            'skills': job_skills,
            'skill_count': len(job_skills)
        }
        
        # If resume text provided, calculate match
        if resume_text.strip():
            from skill_taxonomy import get_skill_match_score
            
            resume_skills = set(extract_all_skills(resume_text))
            job_skills_set = set(job_skills)
            
            match_result = get_skill_match_score(resume_skills, job_skills_set)
            response['match_result'] = match_result
        
        return jsonify(response)
    
    except Exception as e:
        print("Flask error in extract_skills:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Resume Tailoring Endpoint (updated to use new extraction)
# =============================================================================

@app.route('/api/tailor-resume', methods=['POST'])
def tailor_resume():
    """
    Resume tailoring endpoint - now uses skill-based analysis.
    
    WHAT CHANGED:
    - Before: Hardcoded 85% match score, generic suggestions
    - After: Real skill extraction and matching with accurate scores
    """
    try:
        data = request.get_json()
        
        resume_data = data.get('resume_data')
        job_description = data.get('job_description')
        job_title = data.get('job_title')
        company_name = data.get('company_name')
        
        if not all([resume_data, job_description, job_title]):
            return jsonify({'error': 'Missing required data'}), 400
        
        # Build resume text from resume_data
        resume_text = resume_data.get('summary', '')
        for exp in resume_data.get('experience', []):
            resume_text += ' ' + exp.get('description', '')
        resume_text += ' ' + resume_data.get('skills', '')
        
        # Extract skills using new pipeline
        job_skills = set(extract_all_skills(job_description))
        resume_skills = set(extract_all_skills(resume_text))
        
        # Calculate real match score
        from skill_taxonomy import get_skill_match_score
        match_result = get_skill_match_score(resume_skills, job_skills)
        
        # Generate tailored content
        matched_skills = match_result['matched']
        missing_skills = match_result['missing']
        
        # Create tailored summary highlighting matched skills
        if matched_skills:
            skill_highlight = ', '.join(matched_skills[:5])
            tailored_summary = f"Experienced {job_title} with proven expertise in {skill_highlight}. "
        else:
            tailored_summary = f"Experienced {job_title} seeking to contribute to {company_name}. "
        
        tailored_summary += resume_data.get('summary', '')
        
        # Generate actionable suggestions
        suggestions = []
        if match_result['score'] < 50:
            suggestions.append("Your skill match is below 50%. Consider adding relevant skills to your resume.")
        elif match_result['score'] < 70:
            suggestions.append("Good match! Adding a few more relevant skills could improve your chances.")
        
        if missing_skills:
            top_missing = ', '.join(missing_skills[:5])
            suggestions.append(f"Consider highlighting experience with: {top_missing}")
        
        if match_result['extra']:
            suggestions.append(f"Your resume shows additional skills ({', '.join(match_result['extra'][:3])}) that could be valuable.")
        
        result = {
            "tailored_summary": tailored_summary,
            "enhanced_experience": resume_data.get('experience', []),
            "optimized_skills": resume_data.get('skills', ''),
            "match_score": match_result['score'],
            "suggestions": suggestions,
            "job_analysis": {
                "skills": list(job_skills),
                "keywords": list(job_skills),  # Same as skills now (no noise)
                "requirements": []
            },
            "match_details": {
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "extra_skills": match_result['extra']
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in tailor_resume: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
