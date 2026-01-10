# =============================================================================
# Resume Tailoring Service - AI-Powered Resume Optimization
# =============================================================================
#
# WHAT IS THIS FILE?
# ------------------
# This module provides an AI-powered resume tailoring engine that:
# 1. Analyzes job descriptions to extract required skills
# 2. Compares those skills against a user's resume
# 3. Calculates a match score (how well does the resume fit?)
# 4. Generates a tailored summary and improvement suggestions
#
# HOW IT CONNECTS TO YOUR REACT/NODE APP:
# ---------------------------------------
# 1. User uploads their resume in React
# 2. User pastes a job description they're interested in
# 3. React calls your Node/Express backend
# 4. Node backend calls this Python service's /api/tailor-resume endpoint
# 5. This module analyzes both texts and returns optimization advice
# 6. React displays the match score and suggestions to the user
#
# WHY A SEPARATE CLASS?
# ---------------------
# The main app.py file also has resume tailoring logic, but this module
# provides a more object-oriented approach with the ResumeAITailor class.
# This allows for:
# - Better code organization (all tailoring logic in one place)
# - State management (NLP models loaded once in __init__)
# - Easier testing (can instantiate and test the class directly)
#
# JAVASCRIPT ANALOGY:
# ------------------
# In JavaScript/TypeScript, this would be like:
#   class ResumeAITailor {
#     constructor() { this.nlp = loadModel(); }
#     analyzeJob(text) { ... }
#     calculateScore(resume, job) { ... }
#   }
#   export default ResumeAITailor;
# =============================================================================


# =============================================================================
# IMPORTS
# =============================================================================

# spaCy - Industrial-strength NLP library
# Used for text processing and skill extraction
# See app.py for detailed explanation of spaCy
import spacy

# Regular expressions for pattern matching
# 're' is Python's regex module (like JavaScript's RegExp)
import re

# Counter is a dictionary subclass for counting hashable objects
# Useful for counting word/phrase frequencies
# JavaScript equivalent: Create an object and increment counts manually
from collections import Counter

# NLTK tokenization - splits text into words
# word_tokenize("Hello world") → ["Hello", "world"]
# JavaScript equivalent: text.split(/\s+/) but smarter
from nltk.tokenize import word_tokenize

# NLTK stopwords - common words to ignore ("the", "is", "and", etc.)
# These don't contribute meaningful information
from nltk.corpus import stopwords

# NLTK base module for downloading language data
import nltk

# YAKE - Yet Another Keyword Extractor
# Statistical keyword extraction (see app.py for details)
from yake import KeywordExtractor

# RAKE - Rapid Automatic Keyword Extraction
# Co-occurrence based keyword extraction (see app.py for details)
from rake_nltk import Rake

# spaCy's PhraseMatcher for skill matching
# Like a smart Ctrl+F that finds multiple phrases efficiently
from spacy.matcher import PhraseMatcher


# =============================================================================
# Import Skill Taxonomy Module
# =============================================================================
# We import all the skill processing functions and data from skill_taxonomy.py
# This centralizes skill logic so we don't duplicate it here
#
# Python import syntax:
#   from module import (item1, item2, ...)
#
# JavaScript equivalent:
#   import { SKILL_WHITELIST, filterSkills, ... } from './skill_taxonomy.js';
from skill_taxonomy import (
    SKILL_WHITELIST,           # Set of ~300 valid tech skills
    SKILL_ALIASES,             # Dict mapping variants to canonical forms
    filter_and_normalize_skills,  # Clean up raw keywords
    extract_skills_from_text,     # Direct pattern matching
    normalize_skill,              # Normalize a single skill
    is_valid_skill,              # Check if skill is in whitelist
    get_skill_match_score        # Calculate match percentage
)


# =============================================================================
# NLTK Data Downloads
# =============================================================================
# NLTK requires downloading language data files before use.
# These try/except blocks check if data exists before downloading.
# This is more efficient than always downloading (like in app.py).
#
# try/except is Python's try/catch for error handling:
#   Python: try: ... except ErrorType: ...
#   JavaScript: try { ... } catch (error) { ... }
#
# LookupError is raised when NLTK can't find the requested data

try:
    # Check if 'punkt' tokenizer data exists
    # 'punkt' is used for sentence/word tokenization
    nltk.data.find('tokenizers/punkt')
except LookupError:
    # Data not found, download it
    # quiet=True would suppress output, but we don't use it here
    nltk.download('punkt')

try:
    # Check if 'stopwords' data exists
    # Stopwords are common words like "the", "is", "and"
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    # Additional tokenizer data needed by some NLTK versions
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')


# =============================================================================
# ResumeAITailor Class
# =============================================================================
# This is the main class that performs resume tailoring.
#
# PYTHON CLASS SYNTAX (for JavaScript developers):
# ------------------------------------------------
# Python:
#   class ClassName:
#       def __init__(self):      # constructor
#           self.prop = value
#       def method(self):
#           return self.prop
#
# JavaScript:
#   class ClassName {
#       constructor() {
#           this.prop = value;
#       }
#       method() {
#           return this.prop;
#       }
#   }
#
# KEY DIFFERENCES:
# - Python uses 'self', JavaScript uses 'this'
# - Python methods MUST have 'self' as first parameter
# - Python __init__ is the constructor (equivalent to constructor())
# - Python uses 'def' for methods, JavaScript just uses method name

class ResumeAITailor:
    """
    AI-powered resume tailoring engine with skill-based analysis.
    
    This class provides methods to:
    1. Extract skills from job descriptions (analyze_job_requirements)
    2. Extract skills from resumes (extract_skills_spacy)
    3. Calculate match scores (calculate_match_score)
    4. Generate tailored content (tailor_summary, enhance_experience)
    5. Produce improvement suggestions (generate_suggestions)
    
    USAGE EXAMPLE:
    --------------
    # In Python:
    tailor = ResumeAITailor()
    job_analysis = tailor.analyze_job_requirements(job_description_text)
    result = tailor.tailor_resume(resume_data, job_description, job_title, company)
    
    # In your Node.js backend calling this service:
    const { data } = await axios.post('http://localhost:5000/api/tailor-resume', {
        resume_data: { summary, experience, skills },
        job_description: jobText,
        job_title: "Software Engineer",
        company_name: "TechCorp"
    });
    console.log(data.match_score);  // 75.5
    console.log(data.suggestions);  // ["Consider adding AWS experience..."]
    
    IMPROVEMENTS OVER SIMPLE APPROACHES:
    -----------------------------------
    - Uses PhraseMatcher instead of generic noun_chunks (more accurate)
    - Normalizes skill variants (React.js = React = react)
    - Filters out noise phrases (no "developed using" in results)
    - Match score based on set intersection (mathematically correct)
    """
    
    # =========================================================================
    # Constructor (__init__)
    # =========================================================================
    def __init__(self):
        """
        Initialize the ResumeAITailor with NLP models and matchers.
        
        This is called ONCE when you create an instance:
            tailor = ResumeAITailor()  # __init__ runs here
        
        WHAT HAPPENS:
        1. Loads the spaCy English language model
        2. Creates a PhraseMatcher with our skill whitelist
        3. Loads English stopwords
        
        WHY IN __init__:
        Loading the spaCy model takes 1-2 seconds.
        We do it ONCE at startup, not on every request.
        This is the same pattern used in app.py.
        
        JavaScript equivalent:
            constructor() {
                this.nlp = loadSpacyModel();
                this.phraseMatcher = new PhraseMatcher(this.nlp.vocab);
                this.stopWords = new Set(englishStopwords);
            }
        """
        # Try to load the spaCy English model
        # If it fails (not installed), handle gracefully
        try:
            # Load the small English model
            # 'en_core_web_sm' is ~12MB, good balance of speed vs accuracy
            # Alternatives: en_core_web_md (40MB), en_core_web_lg (560MB)
            self.nlp = spacy.load('en_core_web_sm')
            
            # =========================================================
            # Initialize PhraseMatcher with skill whitelist
            # =========================================================
            # PhraseMatcher efficiently finds known phrases in text
            # 
            # HOW IT WORKS:
            # 1. We give it a list of phrases to look for (our skills)
            # 2. When we process text, it finds all matching phrases
            # 3. It's much faster than checking each skill individually
            #
            # attr='LOWER' makes matching case-insensitive
            # "React" will match "react", "REACT", "ReAcT"
            self.phrase_matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
            
            # Create spaCy Doc objects for each skill in whitelist
            # PhraseMatcher needs Doc objects, not plain strings
            # nlp.make_doc() is fast - doesn't run full NLP pipeline
            skill_patterns = [self.nlp.make_doc(skill) for skill in SKILL_WHITELIST]
            
            # Add all patterns under the label "SKILLS"
            # Now when we run phrase_matcher(doc), it will find all matches
            self.phrase_matcher.add("SKILLS", skill_patterns)
            
        except OSError:
            # spaCy model not installed
            # Provide helpful error message to developer
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            self.nlp = None
            self.phrase_matcher = None

        # Load English stopwords (common words to ignore)
        # These include: "the", "is", "at", "which", "on", etc.
        # set() converts the list to a set for O(1) lookup
        self.stop_words = set(stopwords.words('english'))

    # =========================================================================
    # Skill Extraction Methods
    # =========================================================================
    
    def extract_skills_spacy(self, text: str) -> list:
        """
        Extract skills from text using spaCy's PhraseMatcher.
        
        This is the MOST ACCURATE method for skill extraction because
        it only matches skills we explicitly defined in our whitelist.
        
        HOW IT WORKS:
        1. Process the text with spaCy (tokenization, etc.)
        2. Run PhraseMatcher to find matching skills
        3. Normalize each found skill
        4. Return unique list of skills
        
        EXAMPLE:
        --------
        Input: "Looking for React developer with Node.js and MongoDB experience"
        
        Processing:
        - PhraseMatcher finds: "React" at position 2, "Node.js" at 5, "MongoDB" at 7
        - After normalization: ["react", "nodejs", "mongodb"]
        
        Output: ["react", "nodejs", "mongodb"]
        
        Args:
            text: The job description or resume text to analyze
        
        Returns:
            List of normalized skills found in the text
        
        Python Type Hints:
        -----------------
        - 'text: str' means text should be a string
        - '-> list' means this function returns a list
        - These are just hints - Python doesn't enforce them
        """
        # Guard clause: if spaCy failed to load, return empty list
        # This prevents errors if the model isn't installed
        # 
        # 'not self.nlp' checks if self.nlp is None or falsy
        # JavaScript: if (!this.nlp || !this.phraseMatcher) return [];
        if not self.nlp or not self.phrase_matcher:
            return []
        
        # Process text with spaCy
        # This creates a Doc object with tokens, sentences, etc.
        # The Doc is what PhraseMatcher works with
        doc = self.nlp(text)
        
        # Find all skill matches
        # Returns list of tuples: [(match_id, start_token, end_token), ...]
        #
        # Example: "Need React and Python developer"
        # matches: [(12345, 1, 2), (12346, 3, 4)]
        # where 12345 = match_id for "React" at tokens 1-2
        # and 12346 = match_id for "Python" at tokens 3-4
        matches = self.phrase_matcher(doc)
        
        # Use a set to automatically deduplicate
        # If text has "React.js" and "react", both normalize to "react"
        # Set will only keep one copy
        skills = set()
        
        # Process each match
        for match_id, start, end in matches:
            # Extract the matched text
            # doc[start:end] gives us the matched tokens
            # .text converts to string
            # .lower() normalizes to lowercase
            skill_text = doc[start:end].text.lower()
            
            # Normalize the skill (apply aliases, clean up)
            # "React.js" → "react", "Node JS" → "nodejs"
            normalized = normalize_skill(skill_text)
            
            # Add to set if valid
            # 'if normalized' checks that string is not empty
            if normalized:
                skills.add(normalized)
        
        # Convert set to list and return
        return list(skills)

    def extract_keywords_yake(self, text: str, max_keywords: int = 20) -> list:
        """
        Extract keywords using YAKE, then filter through skill taxonomy.
        
        YAKE (Yet Another Keyword Extractor) uses statistical methods:
        - Word frequency (common words are less important)
        - Word position (words at the start may be more important)
        - Word context (related words)
        
        WHY FILTERING IS ADDED:
        YAKE doesn't know what "skills" are - it just finds "important" words.
        It might extract:
        - "looking for" (not a skill)
        - "experience with" (not a skill)
        - "react" (yes, a skill!)
        
        We filter through skill_taxonomy to keep only valid skills.
        
        Args:
            text: Job description or resume text
            max_keywords: Maximum keywords to extract before filtering (default: 20)
        
        Returns:
            List of valid, normalized skills found by YAKE
        """
        # Create YAKE extractor with configuration
        # Each call creates a new instance (could be optimized to reuse)
        kw_extractor = KeywordExtractor(
            lan="en",          # Language: English
            n=3,               # Max n-gram size (up to 3-word phrases)
            dedupLim=0.9,      # Deduplication threshold
            top=max_keywords   # Max keywords to return
        )
        
        # Extract keywords from text
        # Returns list of tuples: [(keyword, score), ...]
        # Lower score = more important in YAKE
        keywords = kw_extractor.extract_keywords(text)
        
        # Extract just the keyword strings (not the scores)
        # kw[0] is the keyword text, kw[1] is the score
        # 
        # Python list comprehension:
        #   [expression for item in list]
        # JavaScript equivalent:
        #   list.map(item => expression)
        raw_keywords = [kw[0] for kw in keywords]
        
        # Filter through skill taxonomy
        # Removes noise like "developed using"
        # Normalizes variants like "React.js" → "react"
        # Only keeps valid skills from whitelist
        return filter_and_normalize_skills(raw_keywords)

    def extract_keywords_rake(self, text: str, max_phrases: int = 15) -> list:
        """
        Extract keywords using RAKE, then filter through skill taxonomy.
        
        RAKE (Rapid Automatic Keyword Extraction) works by:
        1. Splitting text at stopwords and punctuation
        2. Building candidate keyword phrases
        3. Scoring phrases based on word co-occurrence
        4. Returning top-scored phrases
        
        RAKE is good at finding multi-word skills like:
        - "machine learning"
        - "data science"
        - "continuous integration"
        
        WHY FILTERING IS ADDED:
        RAKE can extract garbage phrases like:
        - "experience leading development"
        - "strong background working"
        
        We filter to keep only actual tech skills.
        
        Args:
            text: Job description or resume text
            max_phrases: Maximum phrases to extract before filtering
        
        Returns:
            List of valid, normalized skills found by RAKE
        """
        # Create RAKE instance
        # r = Rake() uses default English settings
        r = Rake()
        
        # Extract keywords from text
        # This stores results inside the Rake object
        r.extract_keywords_from_text(text)
        
        # Get top phrases ranked by score
        # [:max_phrases] slices the list (like .slice(0, max_phrases) in JS)
        raw_phrases = r.get_ranked_phrases()[:max_phrases]
        
        # Filter through skill taxonomy
        return filter_and_normalize_skills(raw_phrases)

    # =========================================================================
    # Job Analysis
    # =========================================================================
    
    def analyze_job_requirements(self, job_description: str) -> dict:
        """
        Analyze a job description to extract all requirements and skills.
        
        This is the main function for understanding what a job needs.
        It combines multiple extraction methods for comprehensive coverage.
        
        WHAT IT RETURNS:
        ---------------
        {
            "skills": ["react", "nodejs", "mongodb", "aws"],
            "keywords": ["react", "nodejs", "mongodb", "aws"],  # Same as skills
            "requirements": [
                "Must have 3+ years experience with React...",
                "Experience with cloud platforms required..."
            ]
        }
        
        WHY MULTIPLE METHODS:
        --------------------
        Each method has strengths and weaknesses:
        - PhraseMatcher: Precise but only finds whitelist skills
        - YAKE: Statistical, catches important terms
        - RAKE: Good at multi-word phrases
        - Direct scan: Catches edge cases others miss
        
        By combining all four, we maximize coverage while filtering noise.
        
        Args:
            job_description: Full text of the job posting
        
        Returns:
            Dictionary with skills, keywords, and requirements
        """
        # Guard clause: if spaCy not available, return empty
        if not self.nlp:
            return {"skills": [], "keywords": [], "requirements": []}

        # Process job description with spaCy
        # This gives us access to sentences, tokens, etc.
        doc = self.nlp(job_description)

        # =========================================================
        # Collect skills from ALL extraction methods
        # =========================================================
        # Using a set ensures no duplicates
        all_skills = set()
        
        # Method 1: PhraseMatcher (most precise)
        # Only finds exact matches from our skill whitelist
        spacy_skills = self.extract_skills_spacy(job_description)
        all_skills.update(spacy_skills)
        
        # Method 2: YAKE (statistical)
        # May catch skills that aren't exact whitelist matches
        yake_skills = self.extract_keywords_yake(job_description)
        all_skills.update(yake_skills)
        
        # Method 3: RAKE (co-occurrence based)
        # Good for multi-word skills
        rake_skills = self.extract_keywords_rake(job_description)
        all_skills.update(rake_skills)
        
        # Method 4: Direct whitelist scanning
        # Searches for EVERY whitelist skill in the text
        # Catches skills that might be part of longer phrases
        direct_skills = extract_skills_from_text(job_description)
        all_skills.update(direct_skills)

        # =========================================================
        # Extract requirement sentences
        # =========================================================
        # These are sentences that typically contain skill requirements
        # We look for common patterns like "must have", "experience with"
        requirements = []
        
        # doc.sents is a generator of Sentence objects
        # Each sentence can be converted to text with .text
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            
            # Check if sentence contains any requirement phrase
            # any() returns True if ANY item in the list is True
            # This is like: phrases.some(p => sent.includes(p)) in JS
            if any(phrase in sent_lower for phrase in [
                'responsible for',   # "Responsible for designing..."
                'must have',         # "Must have 3+ years..."
                'required',          # "Python required"
                'experience with',   # "Experience with AWS..."
                'proficient in',     # "Proficient in JavaScript..."
                'knowledge of'       # "Knowledge of SQL..."
            ]):
                requirements.append(sent.text.strip())

        # Sort skills alphabetically for consistent output
        skills_list = sorted(list(all_skills))
        
        return {
            "skills": skills_list,
            "keywords": skills_list,  # Same as skills now (no noise!)
            "requirements": requirements[:5]  # Limit to 5 requirements
        }

    # =========================================================================
    # Content Tailoring Methods
    # =========================================================================
    
    def tailor_summary(self, original_summary: str, job_analysis: dict, 
                       job_title: str, company_name: str) -> str:
        """
        Generate a tailored professional summary highlighting matched skills.
        
        This creates a new summary that emphasizes the user's skills
        that match what the job is looking for.
        
        EXAMPLE:
        --------
        Job skills: ["react", "nodejs", "aws"]
        Output: "Experienced professional with expertise in react, nodejs, aws.
                 Seeking to contribute to TechCorp's success through technical
                 excellence and proven track record in software engineer responsibilities."
        
        WHY THIS MATTERS:
        ----------------
        Recruiters often skim resumes for 6-10 seconds.
        A tailored summary that immediately mentions relevant skills
        catches their attention and shows you're a good fit.
        
        Args:
            original_summary: User's original summary text (currently unused)
            job_analysis: Output from analyze_job_requirements (contains skills)
            job_title: Target job title ("Software Engineer", etc.)
            company_name: Target company name ("TechCorp", etc.)
        
        Returns:
            Tailored summary string
        """
        # Get top skills from job analysis
        # [:5] limits to first 5 skills (like .slice(0, 5) in JS)
        job_skills = job_analysis.get("skills", [])[:5]

        # Build the tailored summary
        if job_skills:
            # Join first 3 skills with commas
            # Python: ', '.join(['a', 'b', 'c']) → "a, b, c"
            # JavaScript: ['a', 'b', 'c'].join(', ')
            skill_text = ', '.join(job_skills[:3])
            
            # f-string is Python's template literal
            # f"Hello {name}" is like `Hello ${name}` in JavaScript
            tailored = f"Experienced professional with expertise in {skill_text}. "
        else:
            tailored = f"Experienced {job_title} professional. "
        
        # Add company-specific text if company name provided
        if company_name:
            tailored += f"Seeking to contribute to {company_name}'s success "
        
        # Add closing statement
        tailored += f"through technical excellence and proven track record in {job_title.lower()} responsibilities."

        return tailored

    def enhance_experience(self, experience_list: list, job_analysis: dict) -> list:
        """
        Enhance work experience entries by highlighting relevant skills.
        
        This goes through each experience entry and identifies which
        job-required skills are mentioned in that experience.
        
        EXAMPLE:
        --------
        Job skills: ["react", "nodejs", "mongodb"]
        Experience: "Built e-commerce site using React and Node.js"
        
        Enhanced output includes:
        - relevant_keywords: ["react", "nodejs"]
        
        This helps the user see which of their experiences are most relevant.
        
        Args:
            experience_list: List of experience dictionaries from resume
                             [{"title": "Developer", "description": "Built..."}, ...]
            job_analysis: Output from analyze_job_requirements
        
        Returns:
            Enhanced experience list with relevant_keywords added
        """
        enhanced_experience = []
        
        # Get job skills as lowercase set for matching
        # set() with generator expression
        job_skills = set(skill.lower() for skill in job_analysis.get("skills", []))

        # Process each experience entry
        for exp in experience_list:
            # Get the description text
            desc = exp.get("description", "")
            desc_lower = desc.lower()
            
            # Find which job skills are mentioned in this experience
            # List comprehension with condition
            # JavaScript: jobSkills.filter(skill => desc.includes(skill))
            relevant_skills = [
                skill for skill in job_skills 
                if skill in desc_lower
            ]

            # Create enhanced experience object
            # **exp unpacks the original dict (like ...exp spread in JS)
            enhanced_exp = {
                **exp,  # Keep all original fields
                "enhanced_description": desc,
                "relevant_keywords": relevant_skills[:5],  # Top 5 matches
                "optimized_title": exp.get("title", "")
            }

            enhanced_experience.append(enhanced_exp)

        return enhanced_experience

    def optimize_skills(self, current_skills: str, job_analysis: dict) -> str:
        """
        Optimize the skills section by prioritizing job-relevant skills.
        
        This reorders the user's skills to put the most relevant ones first.
        ATS (Applicant Tracking Systems) often weight skills that appear
        earlier in the list more heavily.
        
        EXAMPLE:
        --------
        Current skills: "Python, JavaScript, SQL, React, Java"
        Job requires: "React, JavaScript, TypeScript"
        
        Optimized order: "react, javascript, java, python, sql"
        (React and JavaScript moved to front because job requires them)
        
        Args:
            current_skills: User's skills as comma-separated string
            job_analysis: Output from analyze_job_requirements
        
        Returns:
            Optimized skills string with job-relevant skills first
        """
        job_skills = job_analysis.get("skills", [])
        
        # Parse current skills - handle both list and string input
        # isinstance() checks the type of a variable
        # JavaScript: Array.isArray(current_skills)
        if isinstance(current_skills, list):
            current_list = current_skills
        else:
            # Split string by comma and clean up each skill
            # "React, Node.js, Python" → ["React", "Node.js", "Python"]
            current_list = [s.strip() for s in current_skills.split(',') if s.strip()]

        # Normalize all current skills for comparison
        current_normalized = set()
        for skill in current_list:
            normalized = normalize_skill(skill)
            if normalized:
                current_normalized.add(normalized)

        # Build prioritized list: job skills first, then others
        prioritized = []
        
        # Add job skills that user has
        for skill in job_skills:
            if skill in current_normalized:
                prioritized.append(skill)
                # Remove from set so we don't add it again later
                # discard() removes if present, no error if not
                current_normalized.discard(skill)

        # Add remaining user skills (sorted alphabetically)
        # extend() adds all items from an iterable (like push(...array) in JS)
        prioritized.extend(sorted(current_normalized))

        # Join with commas, limit to 15 skills
        return ", ".join(prioritized[:15])

    # =========================================================================
    # Match Score Calculation
    # =========================================================================
    
    def calculate_match_score(self, resume_data: dict, job_analysis: dict) -> float:
        """
        Calculate resume-job match score based on SKILL OVERLAP.
        
        THIS IS THE KEY METRIC that tells users how well their resume
        matches the job requirements.
        
        HOW IT WORKS:
        -------------
        1. Extract skills from all resume text (summary + experience + skills)
        2. Get skills from job analysis
        3. Calculate: (matched skills / job skills) × 100
        
        EXAMPLE:
        --------
        Resume skills: ["react", "nodejs", "python"]
        Job skills: ["react", "nodejs", "aws", "docker"]
        
        Matched: react, nodejs (2)
        Job total: 4
        Score: 2/4 × 100 = 50%
        
        WHY THIS IS BETTER THAN BEFORE:
        -------------------------------
        Old approach problems:
        - "React" in "React.js developer" counted as a match
        - "React" and "React.js" counted as TWO different skills
        - Generic phrases inflated keyword counts
        
        New approach:
        - Uses normalized skill sets (React = React.js)
        - Set intersection for mathematically correct matching
        - No inflation, accurate percentages
        
        Args:
            resume_data: User's resume data dictionary
                         {"summary": "...", "experience": [...], "skills": "..."}
            job_analysis: Output from analyze_job_requirements
        
        Returns:
            Match score as a percentage (0-100)
        """
        # =========================================================
        # Build complete resume text from all sections
        # =========================================================
        resume_text = resume_data.get('summary', '')
        
        # Add all experience descriptions
        for exp in resume_data.get('experience', []):
            resume_text += ' ' + exp.get('description', '')
        
        # Add skills section
        # str() handles case where skills might be a list
        resume_text += ' ' + str(resume_data.get('skills', ''))
        
        # =========================================================
        # Extract skills from resume
        # =========================================================
        # Use multiple methods for comprehensive extraction
        resume_skills = set(self.extract_skills_spacy(resume_text))
        resume_skills.update(extract_skills_from_text(resume_text))
        
        # Get job skills from analysis (already normalized)
        job_skills = set(job_analysis.get("skills", []))
        
        # =========================================================
        # Calculate match score using skill_taxonomy function
        # =========================================================
        # get_skill_match_score returns:
        # {"score": 75.0, "matched": [...], "missing": [...], "extra": [...]}
        match_result = get_skill_match_score(resume_skills, job_skills)
        
        return match_result["score"]

    def get_detailed_match(self, resume_data: dict, job_analysis: dict) -> dict:
        """
        Get detailed match information including matched/missing/extra skills.
        
        This provides more insight than just the score.
        Users can see exactly which skills they have, which they're missing,
        and which extra skills they bring to the table.
        
        RETURN FORMAT:
        --------------
        {
            "score": 66.7,
            "matched": ["react", "nodejs"],       # Skills you have that job wants
            "missing": ["aws"],                   # Skills job wants that you don't have
            "extra": ["python", "django"]         # Skills you have but job didn't list
        }
        
        This is useful for:
        1. Showing users their skill gaps
        2. Suggesting what to learn
        3. Highlighting bonus skills they bring
        
        Args:
            resume_data: User's resume data dictionary
            job_analysis: Output from analyze_job_requirements
        
        Returns:
            Detailed match dictionary with score, matched, missing, extra
        """
        # Build resume text (same as in calculate_match_score)
        resume_text = resume_data.get('summary', '')
        for exp in resume_data.get('experience', []):
            resume_text += ' ' + exp.get('description', '')
        resume_text += ' ' + str(resume_data.get('skills', ''))
        
        # Extract skills from resume
        resume_skills = set(self.extract_skills_spacy(resume_text))
        resume_skills.update(extract_skills_from_text(resume_text))
        
        job_skills = set(job_analysis.get("skills", []))
        
        # Get full match details from skill_taxonomy
        return get_skill_match_score(resume_skills, job_skills)

    # =========================================================================
    # Suggestion Generation
    # =========================================================================
    
    def generate_suggestions(self, resume_data: dict, job_analysis: dict, 
                             match_score: float) -> list:
        """
        Generate actionable improvement suggestions based on skill gap analysis.
        
        These suggestions help users understand how to improve their resume
        for this specific job.
        
        EXAMPLE SUGGESTIONS:
        -------------------
        - "Your skill match is below 50%. Consider adding relevant skills..."
        - "Consider highlighting experience with: aws, docker, kubernetes"
        - "Consider adding more detailed work experience entries..."
        
        Args:
            resume_data: User's resume data
            job_analysis: Job analysis output
            match_score: Calculated match score (used for score-based suggestions)
        
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Get detailed match for specific skill suggestions
        match_details = self.get_detailed_match(resume_data, job_analysis)
        missing_skills = match_details.get("missing", [])

        # =========================================================
        # Score-based suggestions
        # =========================================================
        if match_score < 50:
            suggestions.append(
                "Your skill match is below 50%. Consider adding relevant skills or "
                "highlighting existing experience with the required technologies."
            )
        elif match_score < 70:
            suggestions.append(
                "Good foundation! Adding a few more relevant skills could significantly "
                "improve your chances with ATS systems."
            )
        else:
            suggestions.append(
                "Strong match! Focus on quantifying your achievements with these skills."
            )

        # =========================================================
        # Missing skills suggestions
        # =========================================================
        if missing_skills:
            # Show top 5 missing skills
            top_missing = missing_skills[:5]
            suggestions.append(
                f"Consider highlighting experience with: {', '.join(top_missing)}"
            )

        # =========================================================
        # Experience-based suggestions
        # =========================================================
        # Suggest adding more experience if they have few entries
        if len(resume_data.get("experience", [])) < 2:
            suggestions.append(
                "Consider adding more detailed work experience entries to showcase "
                "your skill application."
            )

        return suggestions

    # =========================================================================
    # Main Tailoring Function
    # =========================================================================
    
    def tailor_resume(self, resume_data: dict, job_description: str, 
                      job_title: str, company_name: str) -> dict:
        """
        Main function to tailor a resume for a specific job.
        
        This is the ORCHESTRATOR that calls all other methods and
        combines their results into a comprehensive response.
        
        THIS IS WHAT YOUR NODE.JS BACKEND CALLS (via Flask endpoint).
        
        WORKFLOW:
        ---------
        1. Analyze job requirements (extract skills)
        2. Generate tailored summary
        3. Enhance experience entries
        4. Optimize skills ordering
        5. Calculate match score
        6. Get detailed match breakdown
        7. Generate suggestions
        8. Return everything
        
        Args:
            resume_data: User's resume data dictionary
                {
                    "summary": "Experienced developer...",
                    "experience": [
                        {"title": "Developer", "description": "Built apps..."}
                    ],
                    "skills": "React, Node.js, Python"
                }
            job_description: Full job description text
            job_title: Target job title (e.g., "Software Engineer")
            company_name: Target company name (e.g., "Google")
        
        Returns:
            Complete tailoring result:
            {
                "tailored_summary": "...",
                "enhanced_experience": [...],
                "optimized_skills": "...",
                "match_score": 75.5,
                "suggestions": [...],
                "job_analysis": {...},
                "match_details": {...}
            }
        
        HOW YOUR NODE.JS BACKEND CALLS THIS:
        -----------------------------------
        const { data } = await axios.post('http://localhost:5000/api/tailor-resume', {
            resume_data: userResume,
            job_description: jobText,
            job_title: "Software Engineer",
            company_name: "TechCorp"
        });
        
        // Display results
        console.log(`Match Score: ${data.match_score}%`);
        console.log('Missing Skills:', data.match_details.missing);
        console.log('Suggestions:', data.suggestions);
        """
        # Step 1: Analyze job requirements
        # This extracts skills, keywords, and requirement sentences
        job_analysis = self.analyze_job_requirements(job_description)

        # Step 2: Generate tailored summary
        # Creates a summary highlighting relevant skills
        tailored_summary = self.tailor_summary(
            resume_data.get("summary", ""), 
            job_analysis, 
            job_title, 
            company_name
        )

        # Step 3: Enhance experience entries
        # Tags each experience with relevant skills
        enhanced_experience = self.enhance_experience(
            resume_data.get("experience", []), 
            job_analysis
        )

        # Step 4: Optimize skills ordering
        # Puts job-relevant skills first
        optimized_skills = self.optimize_skills(
            resume_data.get("skills", ""), 
            job_analysis
        )

        # Step 5: Calculate match score
        match_score = self.calculate_match_score(resume_data, job_analysis)
        
        # Step 6: Get detailed match breakdown
        match_details = self.get_detailed_match(resume_data, job_analysis)

        # Step 7: Generate improvement suggestions
        suggestions = self.generate_suggestions(resume_data, job_analysis, match_score)

        # Step 8: Build and return complete response
        return {
            "tailored_summary": tailored_summary,
            "enhanced_experience": enhanced_experience,
            "optimized_skills": optimized_skills,
            "match_score": round(match_score, 1),  # Round to 1 decimal
            "suggestions": suggestions,
            "job_analysis": job_analysis,
            "match_details": match_details  # Detailed breakdown of matched/missing
        }


# =============================================================================
# FLASK ENDPOINT HANDLER
# =============================================================================
# This section sets up the Flask route handler for the resume tailoring API.
#
# NOTE: This file can be used in two ways:
# 1. Imported by app.py (the main Flask app) which defines its own routes
# 2. Independently with its own endpoint function
#
# The tailor_resume_endpoint function is designed to be registered with Flask.

# Import Flask utilities
# request = access to incoming request data (like req in Express)
# jsonify = convert Python dict to JSON response (like res.json())
from flask import request, jsonify

# Create a single instance of ResumeAITailor
# This is created ONCE when the module is imported
# Avoids re-loading spaCy model on every request
#
# This is like creating a singleton pattern:
#   let tailorEngine = null;
#   export const getEngine = () => tailorEngine || (tailorEngine = new ResumeAITailor());
tailor_engine = ResumeAITailor()


def tailor_resume_endpoint():
    """
    Flask endpoint handler for resume tailoring.
    
    This function handles incoming POST requests to tailor a resume.
    It's designed to be registered with Flask:
        app.route('/api/tailor-resume', methods=['POST'])(tailor_resume_endpoint)
    
    Or it can be called from app.py's own route handler.
    
    REQUEST FORMAT:
    ---------------
    POST /api/tailor-resume
    Content-Type: application/json
    
    {
        "resume_data": {
            "summary": "...",
            "experience": [...],
            "skills": "..."
        },
        "job_description": "Full job posting text...",
        "job_title": "Software Engineer",
        "company_name": "TechCorp"
    }
    
    RESPONSE FORMAT:
    ----------------
    See tailor_resume() method for full response structure.
    
    Returns:
        Flask JSON response with tailoring results or error
    """
    try:
        # Get JSON data from request body
        # request.get_json() parses the JSON body
        # Like req.body in Express (with body-parser)
        data = request.get_json()

        # Extract required fields
        resume_data = data.get('resume_data')
        job_description = data.get('job_description')
        job_title = data.get('job_title')
        company_name = data.get('company_name')

        # Validate required fields
        # all() returns True if ALL items are truthy
        # JavaScript: [resumeData, jobDescription, jobTitle].every(Boolean)
        if not all([resume_data, job_description, job_title]):
            return jsonify({'error': 'Missing required data'}), 400

        # Call the main tailoring function
        result = tailor_engine.tailor_resume(
            resume_data, 
            job_description, 
            job_title, 
            company_name
        )

        # Return success response
        # jsonify() converts Python dict to JSON
        # 200 is HTTP status code for OK
        return jsonify(result), 200

    except Exception as e:
        # Handle any errors
        # f-string for string formatting
        print(f"Error in tailor_resume_endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
