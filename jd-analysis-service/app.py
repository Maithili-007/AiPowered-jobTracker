# =============================================================================
# JDAnalysisService - Job Description Keyword Extraction Microservice
# =============================================================================
# 
# WHAT IS THIS FILE?
# ------------------
# This is a Python microservice that extracts keywords and technical skills 
# from job descriptions using NLP (Natural Language Processing) techniques.
# 
# Think of it like a specialized API server (similar to your Express.js backend)
# that your main app can call to analyze job description text and get back
# a list of relevant technical skills.
# 
# HOW IT CONNECTS TO YOUR REACT/NODE APP:
# ---------------------------------------
# 1. Your React frontend submits a job description to your Node/Express backend
# 2. Your Node backend makes an HTTP POST request to this Python service
# 3. This Python service analyzes the text using NLP libraries
# 4. It returns a JSON response with extracted keywords/skills
# 5. Your Node backend passes this data back to React
# 
# Flow: React → Node/Express → This Python Service → Node/Express → React
# 
# WHY PYTHON FOR NLP?
# -------------------
# Python has the best NLP libraries (spaCy, NLTK, RAKE, YAKE).
# These libraries are mature and battle-tested for text analysis.
# In JavaScript, NLP support is limited compared to Python.
# 
# LIBRARIES USED (explained below in detail):
# - Flask: Python's Express.js equivalent (web framework)
# - spaCy: Industrial-strength NLP library for text processing
# - RAKE: Rapid Automatic Keyword Extraction algorithm
# - YAKE: Yet Another Keyword Extractor (uses statistical methods)
# - NLTK: Natural Language Toolkit (foundation for many NLP tasks)
# =============================================================================


# =============================================================================
# IMPORTS SECTION
# =============================================================================
# In Python, we use 'import' like JavaScript's 'import' or 'require'.
# The syntax is: 'from module import something' or 'import module'
# Similar to: const { something } = require('module') in Node.js

# Flask is Python's equivalent of Express.js
# - Flask = the main application class (like express())
# - request = gives access to incoming request data (like req in Express)
# - jsonify = converts Python dicts to JSON responses (like res.json() in Express)
from flask import Flask, request, jsonify

# =============================================================================
# spaCy - Industrial Strength NLP Library
# =============================================================================
# WHAT IS spaCy?
# spaCy is like the "React" of NLP libraries - popular, fast, and production-ready.
# It processes text and understands its structure (sentences, words, grammar).
# 
# WHAT IT DOES:
# - Breaks text into tokens (individual words/punctuation)
# - Identifies parts of speech (noun, verb, adjective, etc.)
# - Recognizes named entities (company names, locations, etc.)
# - Groups related words into "noun chunks" (phrases)
# 
# WHY WE USE IT:
# We use spaCy's PhraseMatcher to find specific skills in job descriptions.
# It's like doing a smart Ctrl+F that understands word boundaries and variations.
import spacy

# PhraseMatcher is spaCy's pattern matching tool
# Think of it like a really smart regex that understands language
# We'll use it to find skills from our whitelist in the job description
from spacy.matcher import PhraseMatcher

# =============================================================================
# RAKE - Rapid Automatic Keyword Extraction
# =============================================================================
# WHAT IS RAKE?
# RAKE is an algorithm that extracts important phrases from text.
# It works by looking at word co-occurrence (which words appear together).
# 
# HOW IT WORKS (simplified):
# 1. Splits text at stopwords (common words like "the", "is", "and")
# 2. Creates candidate keyword phrases from what's left
# 3. Scores each phrase based on word frequency and length
# 4. Returns the highest-scoring phrases
# 
# EXAMPLE:
# Text: "Looking for a React developer with MongoDB experience"
# RAKE might extract: ["React developer", "MongoDB experience"]
# 
# LIMITATION:
# RAKE can extract noise like "developed using this" because it's purely 
# statistical - it doesn't know what's actually a skill vs generic phrase.
# That's why we filter its output through our skill_taxonomy.
from rake_nltk import Rake

# =============================================================================
# YAKE - Yet Another Keyword Extractor
# =============================================================================
# WHAT IS YAKE?
# YAKE is another keyword extraction algorithm, but uses different methods.
# It uses statistical features like:
# - Word frequency (how often a word appears)
# - Word position (words at the start are often important)
# - Word context (what words appear nearby)
# 
# WHY USE BOTH RAKE AND YAKE?
# Different algorithms catch different keywords. By combining them,
# we get better coverage. It's like using multiple search engines.
# 
# LIMITATION:
# Same as RAKE - can extract non-skill phrases, so we filter the results.
import yake

# =============================================================================
# NLTK - Natural Language Toolkit
# =============================================================================
# WHAT IS NLTK?
# NLTK is the foundational NLP library in Python (like the "grandfather" of NLP).
# It provides basic building blocks that other libraries (like RAKE) use.
# 
# WHY WE IMPORT IT:
# RAKE depends on NLTK's data (stopwords, sentence tokenizers).
# We download these data files below.
import nltk

# 'os' provides operating system functionalities
# We use it to read environment variables (like process.env in Node.js)
import os

# 'traceback' helps print detailed error information when exceptions occur
# Similar to printing stack traces for debugging in JavaScript
import traceback

# =============================================================================
# CORS - Cross-Origin Resource Sharing
# =============================================================================
# WHAT IS CORS?
# When your React app (running on localhost:3000) tries to call this Python 
# service (running on localhost:5000), the browser blocks it by default.
# This is a security feature called "Same-Origin Policy".
# 
# CORS allows us to explicitly permit cross-origin requests.
# flask-cors does the same thing as the 'cors' npm package in Express.
# 
# In Express: app.use(cors())
# In Flask: CORS(app)
from flask_cors import CORS

# =============================================================================
# Skill Taxonomy Module Import
# =============================================================================
# This imports our custom module that defines:
# - SKILL_WHITELIST: A curated set of valid tech skills (react, nodejs, python, etc.)
# - filter_and_normalize_skills: Cleans up extracted keywords
# - extract_skills_from_text: Direct pattern matching for skills
# - normalize_skill: Converts variations to standard form ("React.js" → "react")
# - is_valid_skill: Checks if a term is in our whitelist
# 
# WHY WE NEED THIS:
# Raw keyword extraction pulls out garbage like "developed using" or "experience with".
# Our taxonomy module filters these out and normalizes skill names for consistency.
# 
# It's like having an "approved skills dictionary" that we check against.
from skill_taxonomy import (
    SKILL_WHITELIST,        # Set of ~300 valid tech skills
    filter_and_normalize_skills,  # Main filtering function
    extract_skills_from_text,     # Direct pattern matching
    normalize_skill,              # Normalizes skill names
    is_valid_skill               # Checks whitelist membership
)


# =============================================================================
# NLTK Data Downloads
# =============================================================================
# NLTK requires downloading language data files before use.
# Think of it like npm install, but for language data.
# 
# - 'punkt': Tokenizer data (splits text into sentences/words)
# - 'stopwords': Common words to ignore ("the", "is", "and")
# - 'punkt_tab': Additional tokenizer data
# 
# The 'quiet=True' parameter suppresses download messages (like npm --silent).
# These downloads only happen once and are cached on the server.
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)


# =============================================================================
# Flask Application Setup
# =============================================================================
# This creates the Flask application instance.
# 
# Python equivalent of Express:
# --------------------------
# JavaScript: const app = express();
# Python:     app = Flask(__name__)
# 
# __name__ is a special Python variable that holds the module's name.
# Flask uses it to locate templates, static files, etc.
# For our microservice, it's just required boilerplate.
app = Flask(__name__)

# Enable CORS for all routes
# This allows your React/Node frontend to make requests to this service.
# 
# Without this, you'd get errors like:
# "Access to fetch at 'http://localhost:5000' from origin 'http://localhost:3000' 
#  has been blocked by CORS policy"
# 
# Python (Flask-CORS): CORS(app)
# JavaScript (Express): app.use(cors())
CORS(app)


# =============================================================================
# Health Check Endpoint
# =============================================================================
# This is a simple endpoint for monitoring/checking if the service is alive.
# Your Node backend or a load balancer can call this to verify the service is up.
# 
# @app.route is a "decorator" in Python - think of it like Express middleware
# that registers a route handler.
# 
# Python:     @app.route('/health', methods=['GET'])
#             def health(): ...
# 
# JavaScript: app.get('/health', (req, res) => { ... })
# 
# The decorator "@app.route('/health', methods=['GET'])" means:
# - Listen on the '/health' path
# - Only accept GET requests
# 
# Response:
# GET /health → { "status": "ok" } with HTTP 200
@app.route('/health', methods=['GET'])
def health():
    # jsonify() converts Python dict to JSON response
    # The second return value (200) is the HTTP status code
    # 
    # Python: return jsonify({"status": "ok"}), 200
    # Express: res.status(200).json({ status: "ok" })
    return jsonify({"status": "ok"}), 200


# =============================================================================
# Model and Extractor Initialization (Loaded Once at Startup)
# =============================================================================
# We load these once when the server starts, not on every request.
# This is important for performance - loading spaCy's model takes a few seconds.
# 
# In Node.js, you might do this at the top level of your file too:
# const nlp = require('some-nlp-lib').load('model');

# =============================================================================
# spaCy Language Model
# =============================================================================
# 'en_core_web_sm' is a pre-trained English language model (small version).
# It contains vocabulary, grammar rules, and trained statistical models.
# 
# Think of it as a pre-trained AI that understands English text structure.
# 
# There are different sizes:
# - en_core_web_sm: Small (~12MB) - fastest, less accurate
# - en_core_web_md: Medium (~40MB) - balanced
# - en_core_web_lg: Large (~560MB) - most accurate, slower
# 
# For keyword extraction, 'sm' (small) is sufficient and fast.
nlp = spacy.load('en_core_web_sm')

# =============================================================================
# RAKE Extractor Instance
# =============================================================================
# Creates a RAKE keyword extractor with default settings.
# We reuse this instance for every request (more efficient).
# 
# Rake() initializes with:
# - Default English stopwords
# - Default punctuation settings
# - Default scoring algorithm
rake_extractor = Rake()

# =============================================================================
# YAKE Extractor Instance
# =============================================================================
# Creates a YAKE keyword extractor with custom settings.
# 
# Parameters:
# - lan='en': Language is English
# - top=20: Extract up to 20 keywords (we increased this for better coverage)
# 
# We get more candidates initially, then filter down to actual skills.
yake_extractor = yake.KeywordExtractor(lan='en', top=20)


# =============================================================================
# Initialize PhraseMatcher with Skill Whitelist
# =============================================================================
# Here we set up spaCy's PhraseMatcher - a powerful pattern matching tool.
# 
# HOW PhraseMatcher WORKS:
# 1. We give it a list of phrases to look for (our skill whitelist)
# 2. When we process text, it finds all occurrences of those phrases
# 3. It's case-insensitive (attr='LOWER') so "React" matches "REACT" and "react"
# 
# WHY THIS IS BETTER THAN SIMPLE STRING MATCHING:
# - Respects word boundaries (won't match "javascript" inside "notjavascripty")
# - Case-insensitive matching built-in
# - Very fast - optimized for large vocabularies
# - Integrates with spaCy's tokenization
# 
# ANALOGY:
# It's like creating a custom "Ctrl+F" that only finds whole words
# and ignores case. But much faster for many patterns.

# Create the PhraseMatcher instance
# - nlp.vocab: The vocabulary from our loaded spaCy model
# - attr='LOWER': Match in lowercase (case-insensitive)
phrase_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')

# Create spaCy Doc objects for each skill in our whitelist
# nlp.make_doc() creates a Doc without running the full NLP pipeline (fast)
# 
# SKILL_WHITELIST contains skills like: "react", "nodejs", "python", "aws", etc.
# We convert each one to a spaCy Doc so the PhraseMatcher can use them.
skill_patterns = [nlp.make_doc(skill) for skill in SKILL_WHITELIST]

# Add all skill patterns to the matcher under the label "SKILLS"
# Now when we run phrase_matcher(doc), it will find all skill matches
phrase_matcher.add("SKILLS", skill_patterns)


# =============================================================================
# ====================== IMPROVED EXTRACTION FUNCTIONS ========================
# =============================================================================
# These functions are the core of our skill extraction logic.
# Each function uses a different NLP technique to find skills in text.


# =============================================================================
# spaCy Skill Extraction Function
# =============================================================================
def spacy_skill_extraction(text: str) -> list:
    """
    Extract skills from text using spaCy's PhraseMatcher.
    
    WHAT THIS FUNCTION DOES:
    1. Processes the input text with spaCy (tokenization, etc.)
    2. Runs our PhraseMatcher to find skills from the whitelist
    3. Normalizes found skills and removes duplicates
    4. Returns a list of matched skills
    
    WHY THIS IS THE BEST METHOD:
    The old approach used doc.noun_chunks which captured ANY noun phrase.
    This captured garbage like "developed using this" or "experience with".
    
    The new approach only matches terms we explicitly defined as skills.
    It's precise because it only finds what's in our curated whitelist.
    
    HOW TO CALL FROM NODE.js:
    This function isn't called directly from Node - it's an internal helper.
    The API endpoints (/extract-keywords, /extract-skills) use this function.
    
    Args:
        text: The job description or resume text to analyze
              (comes from your Node backend's POST request body)
    
    Returns:
        List of skill strings, e.g., ["react", "nodejs", "python"]
    
    Python Syntax Notes for JavaScript Developers:
    - 'text: str' means 'text' parameter must be a string (type hint)
    - '-> list' means this function returns a list (like array in JS)
    - Python uses 'def' instead of 'function'
    - Python uses ':' and indentation instead of { }
    """
    
    # Process the text with spaCy
    # This creates a "Doc" object containing tokens, sentences, etc.
    # 
    # Think of it like parsing text into a structured format:
    # "Looking for React developer" becomes tokens: ["Looking", "for", "React", "developer"]
    doc = nlp(text)
    
    # Run the PhraseMatcher on the processed document
    # This returns a list of matches: [(match_id, start_token, end_token), ...]
    # 
    # Example: If text is "We need React and Python skills"
    # matches might be: [(12345, 2, 3), (12346, 4, 5)]
    # where 12345 is the match_id for "React" at tokens 2-3
    # and 12346 is the match_id for "Python" at tokens 4-5
    matches = phrase_matcher(doc)
    
    # Extract and normalize the matched skills
    # We use a list instead of a set here because we need to preserve order
    # and check for duplicates manually (sets are unordered in Python)
    skills = []
    
    # Iterate over each match
    # Python's 'for x, y, z in list' unpacks tuples (like destructuring in JS)
    # JavaScript equivalent: for (const [match_id, start, end] of matches)
    for match_id, start, end in matches:
        # Extract the matched text from the document
        # doc[start:end] is slicing - gets tokens from index 'start' to 'end-1'
        # .text gets the string representation
        # .lower() converts to lowercase
        skill_text = doc[start:end].text.lower()
        
        # Normalize the skill (e.g., "React.js" → "react")
        # This uses our skill_taxonomy module
        normalized = normalize_skill(skill_text)
        
        # Add to list only if it exists and isn't already in the list
        # 'if normalized' checks if string is not empty (truthy check, like JS)
        # 'and normalized not in skills' checks if not already added
        if normalized and normalized not in skills:
            skills.append(normalized)
    
    # Return the list of unique, normalized skills
    return skills


# =============================================================================
# RAKE Keywords with Filtering
# =============================================================================
def rake_keywords_filtered(text: str, n: int = 15) -> list:
    """
    Extract keywords using RAKE algorithm, then filter through skill taxonomy.
    
    WHAT IS RAKE?
    RAKE (Rapid Automatic Keyword Extraction) is an algorithm that:
    1. Splits text at stopwords and punctuation
    2. Builds candidate keywords from the remaining chunks
    3. Scores each candidate based on word frequency and phrase length
    4. Returns top-scored candidates
    
    EXAMPLE:
    Text: "Looking for senior React developer with 5 years experience in MongoDB"
    Raw RAKE output: ["senior React developer", "years experience", "MongoDB"]
    
    WHY WE FILTER:
    RAKE doesn't know what's a skill vs generic phrase. It might extract:
    - "developed using modern" 
    - "experience with the technology"
    
    We filter through our skill_taxonomy to keep only valid skills.
    
    Args:
        text: Job description text to analyze
        n: Maximum number of phrases to extract before filtering (default: 15)
           Python default parameter syntax: 'n: int = 15'
           JavaScript equivalent: function rake_keywords_filtered(text, n = 15)
    
    Returns:
        List of valid skills found by RAKE (filtered and normalized)
    """
    
    # Extract keywords from the text using RAKE
    # This mutates (modifies) the rake_extractor object internally
    # After this, the extracted keywords are stored inside rake_extractor
    rake_extractor.extract_keywords_from_text(text)
    
    # Get the ranked phrases (highest score first)
    # [:n] is Python slice syntax - gets first n items
    # JavaScript equivalent: .slice(0, n)
    raw_phrases = rake_extractor.get_ranked_phrases()[:n]
    
    # Filter and normalize through our skill taxonomy
    # This removes noise like "developed using" and normalizes names
    # The function is imported from skill_taxonomy.py
    return filter_and_normalize_skills(raw_phrases)


# =============================================================================
# YAKE Keywords with Filtering
# =============================================================================
def yake_keywords_filtered(text: str) -> list:
    """
    Extract keywords using YAKE algorithm, then filter through skill taxonomy.
    
    WHAT IS YAKE?
    YAKE (Yet Another Keyword Extractor) uses statistical features:
    - Term Frequency (TF): How often a word appears
    - Term Position: Words at the beginning are often important
    - Term Relatedness: Words that appear together
    - Term Case: Capitalized words may be important
    
    YAKE assigns a SCORE to each keyword (lower = more important).
    
    HOW YAKE DIFFERS FROM RAKE:
    - RAKE: Uses stopwords to split text, scores by word co-occurrence
    - YAKE: Uses statistical features, doesn't rely on stopwords
    - YAKE often catches different keywords than RAKE
    
    That's why we use BOTH - they complement each other!
    
    WHY WE FILTER:
    YAKE can extract non-skills like:
    - "looking for"
    - "must have experience"
    - "responsible for"
    
    We filter to keep only actual technical skills.
    
    Args:
        text: Job description text to analyze
    
    Returns:
        List of valid skills found by YAKE (filtered and normalized)
    """
    
    # YAKE returns tuples of (keyword, score)
    # Example: [("react", 0.02), ("developer", 0.15), ("experience", 0.3)]
    # Lower score = more important
    # 
    # We use list comprehension to extract just the keywords (not scores)
    # [kw for kw, _ in ...] means "get kw from each (kw, score) tuple"
    # The underscore '_' is Python convention for "I don't care about this value"
    # 
    # JavaScript equivalent:
    # const rawKeywords = yakeExtractor.extractKeywords(text).map(([kw, _]) => kw);
    raw_keywords = [kw for kw, _ in yake_extractor.extract_keywords(text)]
    
    # Filter and normalize through skill taxonomy
    return filter_and_normalize_skills(raw_keywords)


# =============================================================================
# Master Skill Extraction Function (Combines All Methods)
# =============================================================================
def extract_all_skills(text: str) -> list:
    """
    Comprehensive skill extraction using ALL methods combined.
    
    WHY USE MULTIPLE METHODS?
    Each extraction method has different strengths:
    
    1. spaCy PhraseMatcher: MOST PRECISE
       - Only finds exact matches from our skill whitelist
       - Won't find new/unknown skills, but zero false positives
       
    2. RAKE: GOOD FOR MULTI-WORD SKILLS
       - Catches phrases like "machine learning", "data science"
       - May miss single-word skills
       
    3. YAKE: STATISTICAL APPROACH
       - Uses different algorithm than RAKE
       - Often catches what RAKE misses
       
    4. Direct Whitelist Scan: SAFETY NET
       - Directly searches for each skill in the text
       - Catches edge cases other methods miss
    
    By combining all methods and filtering through our taxonomy,
    we get MAXIMUM COVERAGE with MINIMUM NOISE.
    
    Args:
        text: Job description or resume text
    
    Returns:
        Sorted, deduplicated list of all extracted skills
        Example: ["aws", "docker", "python", "react", "typescript"]
    """
    
    # Use a set to store skills (automatically handles deduplication)
    # Python set is like JavaScript Set - stores unique values only
    # set() creates an empty set (not {} which creates a dict/object)
    all_skills = set()
    
    # =========================
    # Method 1: spaCy PhraseMatcher (most precise)
    # =========================
    # This only finds skills that are explicitly in our whitelist
    spacy_skills = spacy_skill_extraction(text)
    
    # .update() adds all items from a list to the set
    # JavaScript equivalent: spacy_skills.forEach(skill => all_skills.add(skill))
    all_skills.update(spacy_skills)
    
    # =========================
    # Method 2: RAKE with filtering
    # =========================
    # Catches multi-word phrases, filtered through taxonomy
    rake_skills = rake_keywords_filtered(text)
    all_skills.update(rake_skills)
    
    # =========================
    # Method 3: YAKE with filtering
    # =========================
    # Statistical approach, complements RAKE
    yake_skills = yake_keywords_filtered(text)
    all_skills.update(yake_skills)
    
    # =========================
    # Method 4: Direct whitelist scanning (catches edge cases)
    # =========================
    # Sometimes skills are nested in longer phrases and methods 1-3 miss them
    # This method directly searches for each whitelist skill in the text
    # Example: "ReactJS and NodeJS" might be tokenized weirdly, but this catches it
    direct_skills = extract_skills_from_text(text)
    all_skills.update(direct_skills)
    
    # Convert set to sorted list and return
    # sorted() returns a new sorted list (alphabetically)
    # list() converts the set to a list
    # 
    # JavaScript equivalent: 
    # return [...all_skills].sort()
    return sorted(list(all_skills))


# =============================================================================
# ====================== LEGACY FUNCTIONS =====================================
# =============================================================================
# These functions maintain backward compatibility with existing tests.
# They wrap the new improved functions so old code still works.


def spacy_keywords(text, n=10):
    """
    LEGACY FUNCTION: Original spaCy keyword extraction.
    
    WHY IT EXISTS:
    Tests or other parts of the codebase might call this function.
    We keep the old name but use the new improved logic internally.
    
    This way, existing code works without modification.
    In JavaScript, you might do: const spacy_keywords = (text, n) => spacy_skill_extraction(text).slice(0, n);
    """
    # Use new extraction, return up to n results
    skills = spacy_skill_extraction(text)
    # [:n] is Python slice - JavaScript equivalent: .slice(0, n)
    return skills[:n]


def rake_keywords(text, n=10):
    """
    LEGACY FUNCTION: Original RAKE extraction.
    Now uses the filtered version internally.
    """
    return rake_keywords_filtered(text, n)


def yake_keywords(text):
    """
    LEGACY FUNCTION: Original YAKE extraction.
    Now uses the filtered version internally.
    """
    return yake_keywords_filtered(text)


# =============================================================================
# ====================== API ENDPOINTS ========================================
# =============================================================================
# These are the HTTP endpoints that your Node/Express backend calls.
# They're like Express route handlers but with Flask syntax.


# =============================================================================
# /extract-keywords Endpoint
# =============================================================================
# 
# PURPOSE:
# Main keyword extraction endpoint. Analyzes job description text
# and returns a list of extracted technical skills.
# 
# HTTP METHOD: POST
# (We use POST because we're sending text data in the request body)
# 
# HOW YOUR NODE.JS BACKEND CALLS THIS:
# -------------------------------------
# In your Express backend (e.g., jobController.js):
# 
#   const response = await fetch('http://localhost:5000/extract-keywords', {
#     method: 'POST',
#     headers: { 'Content-Type': 'application/json' },
#     body: JSON.stringify({ description: jobDescriptionText })
#   });
#   const data = await response.json();
#   console.log(data.keywords);  // ["react", "nodejs", "python", ...]
# 
# Or with axios:
# 
#   const { data } = await axios.post('http://localhost:5000/extract-keywords', {
#     description: jobDescriptionText
#   });
#   console.log(data.keywords);
# 
# REQUEST FORMAT:
# ---------------
# POST /extract-keywords
# Content-Type: application/json
# 
# {
#   "description": "Looking for a senior React developer with experience in Node.js, MongoDB, and AWS...",
#   "debug": false  // Optional: set to true to see what each method extracted
# }
# 
# RESPONSE FORMAT:
# ----------------
# {
#   "keywords": ["aws", "mongodb", "nodejs", "react"]
# }
# 
# With debug=true:
# {
#   "keywords": ["aws", "mongodb", "nodejs", "react"],
#   "debug": {
#     "spacy_skills": ["react", "nodejs"],
#     "rake_skills": ["mongodb", "aws"],
#     "yake_skills": ["react"],
#     "direct_skills": ["aws", "mongodb", "nodejs", "react"]
#   }
# }

@app.route('/extract-keywords', methods=['POST'])
def extract():
    """
    Main keyword extraction endpoint.
    
    This is the primary endpoint your Node.js backend calls to extract
    skills from job descriptions.
    
    The response contains clean, deduplicated, normalized skill names.
    No more "developed using" or duplicate "react"/"React.js" entries.
    """
    
    # Wrap everything in try/except (Python's try/catch)
    # This ensures we return a proper error response if something goes wrong
    try:
        # Get the JSON data from the request body
        # request.json is like req.body in Express (already parsed)
        # .get('description', '') returns the value or empty string if not found
        # 
        # JavaScript equivalent:
        # const text = req.body.description || '';
        text = request.json.get('description', '')
        
        # If text is empty, return empty keywords list
        # .strip() removes whitespace from both ends (like .trim() in JS)
        if not text.strip():
            return jsonify({'keywords': []})
        
        # Extract skills using our comprehensive multi-method approach
        # This calls spaCy, RAKE, YAKE, and direct matching, then deduplicates
        clean_skills = extract_all_skills(text)
        
        # Check if client wants debug information
        # Debug mode shows what each extraction method found (useful for development)
        include_debug = request.json.get('debug', False)
        
        # Build the response object (Python dict = JavaScript object)
        response = {'keywords': clean_skills}
        
        # Add debug info if requested
        if include_debug:
            response['debug'] = {
                'spacy_skills': spacy_skill_extraction(text),
                'rake_skills': rake_keywords_filtered(text),
                'yake_skills': yake_keywords_filtered(text),
                'direct_skills': list(extract_skills_from_text(text))
            }
        
        # Return JSON response
        # jsonify() is like res.json() in Express
        return jsonify(response)
    
    except Exception as e:
        # Handle any errors that occur
        # 'Exception as e' captures the error object (like 'catch(e)' in JS)
        
        # Print error to console for debugging
        print("Flask error:", str(e))
        
        # Print full stack trace (like console.error(e.stack) in JS)
        traceback.print_exc()
        
        # Return error response with 500 status code
        return jsonify({'error': str(e)}), 500


# =============================================================================
# /extract-skills Endpoint (NEW - Recommended)
# =============================================================================
# 
# PURPOSE:
# Dedicated endpoint for skill extraction with optional skill matching.
# Can compare resume skills against job skills and calculate a match score.
# 
# HTTP METHOD: POST
# 
# HOW YOUR NODE.JS BACKEND CALLS THIS:
# -------------------------------------
# Basic usage (just extract skills):
#   const { data } = await axios.post('http://localhost:5000/extract-skills', {
#     description: jobDescriptionText
#   });
#   console.log(data.skills);  // ["react", "nodejs", ...]
#   console.log(data.skill_count);  // 5
# 
# With resume matching:
#   const { data } = await axios.post('http://localhost:5000/extract-skills', {
#     description: jobDescriptionText,
#     resume_text: userResumeText
#   });
#   console.log(data.match_result.score);  // 80.0
#   console.log(data.match_result.matched);  // ["react", "nodejs"]
#   console.log(data.match_result.missing);  // ["aws"]
# 
# REQUEST FORMAT:
# ---------------
# POST /extract-skills
# Content-Type: application/json
# 
# {
#   "description": "Looking for React developer...",
#   "resume_text": "Experienced developer with React and Node.js..."  // Optional
# }
# 
# RESPONSE FORMAT (without resume_text):
# --------------------------------------
# {
#   "skills": ["nodejs", "react"],
#   "skill_count": 2
# }
# 
# RESPONSE FORMAT (with resume_text):
# -----------------------------------
# {
#   "skills": ["nodejs", "react", "aws"],
#   "skill_count": 3,
#   "match_result": {
#     "score": 66.7,        // Percentage of job skills found in resume
#     "matched": ["nodejs", "react"],  // Skills in both
#     "missing": ["aws"],    // Job skills not in resume
#     "extra": ["python"]    // Resume skills not in job (bonus skills)
#   }
# }

@app.route('/extract-skills', methods=['POST'])
def extract_skills_endpoint():
    """
    Dedicated skill extraction endpoint with optional resume matching.
    
    This is the RECOMMENDED endpoint for skill extraction.
    It returns validated, normalized skills and can calculate match scores.
    
    Use this when you want to:
    1. Extract skills from a job description
    2. Compare a user's resume against job requirements
    3. Show users which skills they have vs. need to add
    """
    
    try:
        # Get request data, default to empty dict if None
        # 'or {}' is like JavaScript's '|| {}' for fallback
        data = request.json or {}
        
        # Extract description and optional resume text
        description = data.get('description', '')
        resume_text = data.get('resume_text', '')
        
        # Return empty response if no description provided
        if not description.strip():
            return jsonify({
                'skills': [],
                'skill_count': 0
            })
        
        # Extract skills from the job description using all methods
        job_skills = extract_all_skills(description)
        
        # Build initial response
        # len() is like .length in JavaScript
        response = {
            'skills': job_skills,
            'skill_count': len(job_skills)
        }
        
        # If resume text is provided, calculate match score
        if resume_text.strip():
            # Import the matching function from skill_taxonomy
            # Python allows imports inside functions (lazy loading)
            from skill_taxonomy import get_skill_match_score
            
            # Extract skills from resume
            # set() creates a set (like new Set() in JavaScript)
            resume_skills = set(extract_all_skills(resume_text))
            job_skills_set = set(job_skills)
            
            # Calculate match score and details
            # This returns: { score, matched, missing, extra }
            match_result = get_skill_match_score(resume_skills, job_skills_set)
            response['match_result'] = match_result
        
        return jsonify(response)
    
    except Exception as e:
        print("Flask error in extract_skills:", str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# /api/tailor-resume Endpoint
# =============================================================================
# 
# PURPOSE:
# Analyzes a user's resume against a specific job and provides:
# - A tailored summary highlighting relevant skills
# - Match score showing how well the resume fits
# - Suggestions for improvement
# - Details on matched/missing skills
# 
# HTTP METHOD: POST
# 
# HOW YOUR NODE.JS BACKEND CALLS THIS:
# -------------------------------------
#   const { data } = await axios.post('http://localhost:5000/api/tailor-resume', {
#     resume_data: {
#       summary: "Experienced full-stack developer...",
#       experience: [
#         { description: "Built React applications..." },
#         { description: "Managed MongoDB databases..." }
#       ],
#       skills: "React, Node.js, MongoDB, Python"
#     },
#     job_description: "Looking for a senior developer with AWS experience...",
#     job_title: "Senior Software Engineer",
#     company_name: "TechCorp"
#   });
# 
#   console.log(data.match_score);  // 75.0
#   console.log(data.suggestions);  // ["Consider highlighting experience with: aws"]
# 
# REQUEST FORMAT:
# ---------------
# POST /api/tailor-resume
# Content-Type: application/json
# 
# {
#   "resume_data": {
#     "summary": "Developer summary text...",
#     "experience": [{ "description": "Experience details..." }],
#     "skills": "Comma-separated skills string"
#   },
#   "job_description": "Full job description text...",
#   "job_title": "Software Engineer",
#   "company_name": "Company Name"
# }
# 
# RESPONSE FORMAT:
# ----------------
# {
#   "tailored_summary": "Experienced Software Engineer with proven expertise in react, nodejs...",
#   "enhanced_experience": [...],  // Original experience array
#   "optimized_skills": "...",     // Original skills string
#   "match_score": 80.0,
#   "suggestions": [
#     "Good match! Adding a few more relevant skills could improve your chances.",
#     "Consider highlighting experience with: aws, docker"
#   ],
#   "job_analysis": {
#     "skills": ["react", "nodejs", "aws"],
#     "keywords": ["react", "nodejs", "aws"],
#     "requirements": []
#   },
#   "match_details": {
#     "matched_skills": ["react", "nodejs"],
#     "missing_skills": ["aws"],
#     "extra_skills": ["python"]
#   }
# }

@app.route('/api/tailor-resume', methods=['POST'])
def tailor_resume():
    """
    Resume tailoring endpoint - provides personalized resume optimization.
    
    WHAT THIS DOES:
    1. Extracts skills from both the job description and resume
    2. Calculates a real match score (not hardcoded!)
    3. Generates a tailored summary highlighting matched skills
    4. Provides actionable suggestions for improvement
    
    WHAT CHANGED FROM BEFORE:
    - Before: Returned a hardcoded 85% match score (fake!)
    - After: Calculates real scores based on actual skill matching
    """
    
    try:
        # Get JSON data from request body
        # .get_json() is an alternative to request.json (functionally same)
        data = request.get_json()
        
        # Extract fields from request
        resume_data = data.get('resume_data')
        job_description = data.get('job_description')
        job_title = data.get('job_title')
        company_name = data.get('company_name')
        
        # Validate required fields
        # all() returns True if all items are truthy (like && chaining in JS)
        # JavaScript equivalent: if (!resume_data || !job_description || !job_title)
        if not all([resume_data, job_description, job_title]):
            return jsonify({'error': 'Missing required data'}), 400
        
        # =========================
        # Build resume text from resume_data object
        # =========================
        # We need to combine all text from the resume into one string for analysis
        # 
        # The frontend may send:
        # 1. Structured data: { summary: "...", experience: [...], skills: "..." }
        # 2. Raw content: { rawContent: "full resume text here" }
        #
        # We handle BOTH cases for maximum flexibility
        
        # Check if raw content was provided (from ResumeEditor's parsed resume file)
        raw_content = resume_data.get('rawContent', '')
        
        if raw_content and raw_content.strip():
            # Use raw content directly - this is the parsed resume text from the PDF/file
            resume_text = raw_content
        else:
            # Build from structured fields (fallback for structured resume data)
            # .get('key', default) safely gets a value with fallback
            # JavaScript equivalent: resume_data.summary || ''
            resume_text = resume_data.get('summary', '')
            
            # Add all experience descriptions
            # This loops through each experience object and appends its description
            # 
            # JavaScript equivalent:
            # resume_data.experience.forEach(exp => { resume_text += ' ' + (exp.description || '') });
            for exp in resume_data.get('experience', []):
                resume_text += ' ' + exp.get('description', '')
            
            # Add skills string
            resume_text += ' ' + resume_data.get('skills', '')
        
        # =========================
        # Extract skills from both texts
        # =========================
        # set() creates a Python set (unique values, unordered)
        # Using sets makes skill comparison operations efficient
        job_skills = set(extract_all_skills(job_description))
        resume_skills = set(extract_all_skills(resume_text))
        
        # =========================
        # Calculate match score
        # =========================
        # Import and use skill matching function
        from skill_taxonomy import get_skill_match_score
        match_result = get_skill_match_score(resume_skills, job_skills)
        
        # =========================
        # Generate tailored content
        # =========================
        matched_skills = match_result['matched']
        missing_skills = match_result['missing']
        
        # Create a tailored summary that highlights the user's matched skills
        if matched_skills:
            # Join first 5 matched skills with commas
            # [:5] gets first 5 items (like .slice(0, 5) in JS)
            # ', '.join() is like .join(', ') in JS but syntax is reversed
            skill_highlight = ', '.join(matched_skills[:5])
            
            # f-string is Python's template literal (like `backticks` in JS)
            # f"Hello {name}" is like `Hello ${name}` in JavaScript
            tailored_summary = f"Experienced {job_title} with proven expertise in {skill_highlight}. "
        else:
            tailored_summary = f"Experienced {job_title} seeking to contribute to {company_name}. "
        
        # Append original summary
        tailored_summary += resume_data.get('summary', '')
        
        # =========================
        # Generate improvement suggestions
        # =========================
        suggestions = []
        
        # Score-based suggestions
        if match_result['score'] < 50:
            suggestions.append("Your skill match is below 50%. Consider adding relevant skills to your resume.")
        elif match_result['score'] < 70:
            suggestions.append("Good match! Adding a few more relevant skills could improve your chances.")
        
        # Missing skills suggestion
        if missing_skills:
            top_missing = ', '.join(missing_skills[:5])
            suggestions.append(f"Consider highlighting experience with: {top_missing}")
        
        # Extra skills suggestion (skills you have that aren't in the job)
        if match_result['extra']:
            # [:3] gets first 3 extra skills
            suggestions.append(f"Your resume shows additional skills ({', '.join(match_result['extra'][:3])}) that could be valuable.")
        
        # =========================
        # Build and return response
        # =========================
        result = {
            "tailored_summary": tailored_summary,
            "enhanced_experience": resume_data.get('experience', []),
            "optimized_skills": resume_data.get('skills', ''),
            "match_score": match_result['score'],
            "suggestions": suggestions,
            "job_analysis": {
                "skills": list(job_skills),
                "keywords": list(job_skills),  # Same as skills (no noise now!)
                "requirements": []  # Could be extended to parse requirements
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


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================
# This is equivalent to the bottom of an Express app.js file where you call
# app.listen(port, () => console.log(`Server running on port ${port}`));
# 
# The 'if __name__ == "__main__":' pattern is Python's way of saying
# "only run this code if this file is executed directly"
# (not imported as a module by another file)
# 
# JavaScript equivalent:
#   if (require.main === module) {
#     app.listen(PORT, () => console.log('Server running...'));
#   }

if __name__ == '__main__':
    # app.run() starts the Flask development server
    # 
    # Parameters:
    # - host="0.0.0.0": Listen on all network interfaces (allows external access)
    #                   "localhost" would only allow local access
    # 
    # - port=int(os.environ.get("PORT", 5000)):
    #   Get PORT from environment variable, default to 5000
    #   os.environ.get() is like process.env.PORT in Node.js
    #   int() converts string to integer (port must be a number)
    # 
    # - debug=True: Enable debug mode (auto-reload on file changes, detailed errors)
    #              In production, set this to False!
    #
    # This is equivalent to:
    #   const PORT = process.env.PORT || 5000;
    #   app.listen(PORT, '0.0.0.0', () => console.log(`Server on ${PORT}`));
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
