
# resume_tailor.py
"""
Resume Tailoring Service - IMPROVED VERSION
============================================

This module provides AI-powered resume tailoring with:
- Skill-based keyword extraction (not generic noun phrases)
- Normalized skill matching (React.js = react = ReactJS)
- Accurate match scoring based on skill overlap

KEY IMPROVEMENTS OVER ORIGINAL:
1. Uses skill_taxonomy module for normalization and filtering
2. Match score reflects actual skill alignment, not raw keyword count
3. Filters out noise like "developed using", "experience with"
4. Suggestions are based on real missing skills
"""

import spacy
import re
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from yake import KeywordExtractor
from rake_nltk import Rake
from spacy.matcher import PhraseMatcher

# Import skill taxonomy for normalization and filtering
# WHY: Centralizes all skill logic in one place for consistency
from skill_taxonomy import (
    SKILL_WHITELIST,
    SKILL_ALIASES,
    filter_and_normalize_skills,
    extract_skills_from_text,
    normalize_skill,
    is_valid_skill,
    get_skill_match_score
)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')


class ResumeAITailor:
    """
    AI-powered resume tailoring engine with skill-based analysis.
    
    IMPROVEMENTS:
    - Uses PhraseMatcher with skill whitelist instead of generic patterns
    - Normalizes skill variants (React.js → react)
    - Filters noise from YAKE/RAKE outputs
    - Match score based on skill set overlap, not substring matching
    """
    
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
            
            # Initialize PhraseMatcher with skill whitelist
            # WHY: More accurate than regex patterns - matches exact skill terms
            self.phrase_matcher = PhraseMatcher(self.nlp.vocab, attr='LOWER')
            skill_patterns = [self.nlp.make_doc(skill) for skill in SKILL_WHITELIST]
            self.phrase_matcher.add("SKILLS", skill_patterns)
            
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            self.nlp = None
            self.phrase_matcher = None

        self.stop_words = set(stopwords.words('english'))

    def extract_skills_spacy(self, text: str) -> list:
        """
        Extract skills using spaCy PhraseMatcher.
        
        WHY THIS IS BETTER THAN ORIGINAL:
        - Original used generic regex patterns that missed many skills
        - PhraseMatcher matches ALL skills in our 200+ item whitelist
        - Results are already normalized via LOWER attribute
        
        Args:
            text: Job description or resume text
            
        Returns:
            List of normalized skills found in text
        """
        if not self.nlp or not self.phrase_matcher:
            return []
        
        doc = self.nlp(text)
        matches = self.phrase_matcher(doc)
        
        skills = set()
        for match_id, start, end in matches:
            skill_text = doc[start:end].text.lower()
            normalized = normalize_skill(skill_text)
            if normalized:
                skills.add(normalized)
        
        return list(skills)

    def extract_keywords_yake(self, text: str, max_keywords: int = 20) -> list:
        """
        Extract keywords using YAKE, then filter through skill taxonomy.
        
        WHY FILTERING IS ADDED:
        Original YAKE extraction returned phrases like:
        - "developed using modern"
        - "experience with the"
        - "strong background in"
        
        Now we filter these through skill_taxonomy to keep only valid skills.
        
        Args:
            text: Job description or resume text
            max_keywords: Maximum keywords to extract before filtering
            
        Returns:
            List of valid, normalized skills
        """
        kw_extractor = KeywordExtractor(
            lan="en",
            n=3,
            dedupLim=0.9,
            top=max_keywords
        )
        keywords = kw_extractor.extract_keywords(text)
        raw_keywords = [kw[0] for kw in keywords]  # kw[0] is the keyword text
        
        # Filter through skill taxonomy
        return filter_and_normalize_skills(raw_keywords)

    def extract_keywords_rake(self, text: str, max_phrases: int = 15) -> list:
        """
        Extract keywords using RAKE, then filter through skill taxonomy.
        
        WHY FILTERING IS ADDED:
        RAKE extracts based on word co-occurrence which captures noise.
        Now we validate each phrase against our skill whitelist.
        
        Args:
            text: Job description or resume text
            max_phrases: Maximum phrases to extract before filtering
            
        Returns:
            List of valid, normalized skills
        """
        r = Rake()
        r.extract_keywords_from_text(text)
        raw_phrases = r.get_ranked_phrases()[:max_phrases]
        
        # Filter through skill taxonomy
        return filter_and_normalize_skills(raw_phrases)

    def analyze_job_requirements(self, job_description: str) -> dict:
        """
        Analyze job description to extract skills and requirements.
        
        IMPROVEMENTS OVER ORIGINAL:
        1. Uses PhraseMatcher instead of limited regex patterns
        2. Combines multiple extraction methods for better coverage
        3. All skills are normalized and deduplicated
        4. No noise phrases in output
        
        Args:
            job_description: Full job description text
            
        Returns:
            Dictionary with:
            - skills: List of normalized skills found
            - keywords: Same as skills (normalized, no duplicates)
            - requirements: Requirement sentences extracted
        """
        if not self.nlp:
            return {"skills": [], "keywords": [], "requirements": []}

        doc = self.nlp(job_description)

        # Collect skills from multiple methods
        all_skills = set()
        
        # Method 1: PhraseMatcher (most accurate)
        spacy_skills = self.extract_skills_spacy(job_description)
        all_skills.update(spacy_skills)
        
        # Method 2: YAKE with filtering
        yake_skills = self.extract_keywords_yake(job_description)
        all_skills.update(yake_skills)
        
        # Method 3: RAKE with filtering
        rake_skills = self.extract_keywords_rake(job_description)
        all_skills.update(rake_skills)
        
        # Method 4: Direct whitelist scanning
        direct_skills = extract_skills_from_text(job_description)
        all_skills.update(direct_skills)

        # Extract requirement sentences (kept from original)
        requirements = []
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            if any(phrase in sent_lower for phrase in [
                'responsible for', 'must have', 'required', 
                'experience with', 'proficient in', 'knowledge of'
            ]):
                requirements.append(sent.text.strip())

        skills_list = sorted(list(all_skills))
        
        return {
            "skills": skills_list,
            "keywords": skills_list,  # Same as skills now (no noise distinction)
            "requirements": requirements[:5]
        }

    def tailor_summary(self, original_summary: str, job_analysis: dict, 
                       job_title: str, company_name: str) -> str:
        """
        Generate tailored professional summary highlighting matched skills.
        
        IMPROVEMENTS:
        - Uses actual extracted skills instead of generic placeholders
        - Creates more natural-sounding summary
        
        Args:
            original_summary: User's original summary text
            job_analysis: Output from analyze_job_requirements
            job_title: Target job title
            company_name: Target company name
            
        Returns:
            Tailored summary text
        """
        job_skills = job_analysis.get("skills", [])[:5]

        if job_skills:
            skill_text = ', '.join(job_skills[:3])
            tailored = f"Experienced professional with expertise in {skill_text}. "
        else:
            tailored = f"Experienced {job_title} professional. "
        
        if company_name:
            tailored += f"Seeking to contribute to {company_name}'s success "
        
        tailored += f"through technical excellence and proven track record in {job_title.lower()} responsibilities."

        return tailored

    def enhance_experience(self, experience_list: list, job_analysis: dict) -> list:
        """
        Enhance work experience with relevant keywords.
        
        NOTE: This function is kept for compatibility but simplified.
        The main improvement is in skill extraction and matching.
        
        Args:
            experience_list: List of experience dictionaries
            job_analysis: Output from analyze_job_requirements
            
        Returns:
            Enhanced experience list
        """
        enhanced_experience = []
        job_skills = set(skill.lower() for skill in job_analysis.get("skills", []))

        for exp in experience_list:
            desc = exp.get("description", "")
            desc_lower = desc.lower()
            
            # Find which job skills are mentioned in this experience
            relevant_skills = [
                skill for skill in job_skills 
                if skill in desc_lower
            ]

            enhanced_exp = {
                **exp,
                "enhanced_description": desc,
                "relevant_keywords": relevant_skills[:5],
                "optimized_title": exp.get("title", "")
            }

            enhanced_experience.append(enhanced_exp)

        return enhanced_experience

    def optimize_skills(self, current_skills: str, job_analysis: dict) -> str:
        """
        Optimize skills section by prioritizing job-relevant skills.
        
        Args:
            current_skills: User's current skills string
            job_analysis: Output from analyze_job_requirements
            
        Returns:
            Optimized skills string with job-relevant skills prioritized
        """
        job_skills = job_analysis.get("skills", [])
        
        # Parse current skills
        if isinstance(current_skills, list):
            current_list = current_skills
        else:
            current_list = [s.strip() for s in current_skills.split(',') if s.strip()]

        # Normalize current skills
        current_normalized = set()
        for skill in current_list:
            normalized = normalize_skill(skill)
            if normalized:
                current_normalized.add(normalized)

        # Prioritize job skills that user has
        prioritized = []
        for skill in job_skills:
            if skill in current_normalized:
                prioritized.append(skill)
                current_normalized.discard(skill)

        # Add remaining user skills
        prioritized.extend(sorted(current_normalized))

        return ", ".join(prioritized[:15])

    def calculate_match_score(self, resume_data: dict, job_analysis: dict) -> float:
        """
        Calculate resume-job match score based on SKILL OVERLAP.
        
        THIS IS THE KEY IMPROVEMENT:
        
        BEFORE (problematic):
        - Used substring matching: "React" in "React.js developer" counted
        - "React" and "React.js" counted as TWO matches (inflated score)
        - Generic phrases like "experience with" counted in keywords
        
        AFTER (accurate):
        - Extracts normalized skills from both resume and job
        - Uses set intersection for precise matching
        - No duplicates, no noise, no inflated scores
        
        Args:
            resume_data: User's resume data dictionary
            job_analysis: Output from analyze_job_requirements
            
        Returns:
            Match score as percentage (0-100)
        """
        # Build resume text
        resume_text = resume_data.get('summary', '')
        for exp in resume_data.get('experience', []):
            resume_text += ' ' + exp.get('description', '')
        resume_text += ' ' + str(resume_data.get('skills', ''))
        
        # Extract and normalize skills from resume
        resume_skills = set(self.extract_skills_spacy(resume_text))
        resume_skills.update(extract_skills_from_text(resume_text))
        
        # Get job skills (already normalized from job_analysis)
        job_skills = set(job_analysis.get("skills", []))
        
        # Use skill_taxonomy's accurate matching function
        match_result = get_skill_match_score(resume_skills, job_skills)
        
        return match_result["score"]

    def get_detailed_match(self, resume_data: dict, job_analysis: dict) -> dict:
        """
        Get detailed match information including matched/missing skills.
        
        NEW FUNCTION for enhanced match visibility.
        
        Args:
            resume_data: User's resume data dictionary
            job_analysis: Output from analyze_job_requirements
            
        Returns:
            Dictionary with score, matched, missing, and extra skills
        """
        # Build resume text
        resume_text = resume_data.get('summary', '')
        for exp in resume_data.get('experience', []):
            resume_text += ' ' + exp.get('description', '')
        resume_text += ' ' + str(resume_data.get('skills', ''))
        
        # Extract skills
        resume_skills = set(self.extract_skills_spacy(resume_text))
        resume_skills.update(extract_skills_from_text(resume_text))
        
        job_skills = set(job_analysis.get("skills", []))
        
        return get_skill_match_score(resume_skills, job_skills)

    def generate_suggestions(self, resume_data: dict, job_analysis: dict, 
                             match_score: float) -> list:
        """
        Generate improvement suggestions based on skill gap analysis.
        
        IMPROVEMENTS:
        - Suggestions are based on actual missing skills
        - More actionable and specific recommendations
        
        Args:
            resume_data: User's resume data
            job_analysis: Job analysis output
            match_score: Calculated match score
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Get detailed match for suggestions
        match_details = self.get_detailed_match(resume_data, job_analysis)
        missing_skills = match_details.get("missing", [])

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

        # Specific skill suggestions
        if missing_skills:
            top_missing = missing_skills[:5]
            suggestions.append(
                f"Consider highlighting experience with: {', '.join(top_missing)}"
            )

        # Experience suggestions
        if len(resume_data.get("experience", [])) < 2:
            suggestions.append(
                "Consider adding more detailed work experience entries to showcase "
                "your skill application."
            )

        return suggestions

    def tailor_resume(self, resume_data: dict, job_description: str, 
                      job_title: str, company_name: str) -> dict:
        """
        Main function to tailor resume for specific job.
        
        This orchestrates all the tailoring steps and returns comprehensive results.
        
        Args:
            resume_data: User's resume data
            job_description: Target job description
            job_title: Target job title
            company_name: Target company name
            
        Returns:
            Dictionary with all tailored content and analysis
        """
        # Analyze job requirements
        job_analysis = self.analyze_job_requirements(job_description)

        # Tailor each section
        tailored_summary = self.tailor_summary(
            resume_data.get("summary", ""), 
            job_analysis, 
            job_title, 
            company_name
        )

        enhanced_experience = self.enhance_experience(
            resume_data.get("experience", []), 
            job_analysis
        )

        optimized_skills = self.optimize_skills(
            resume_data.get("skills", ""), 
            job_analysis
        )

        # Calculate accurate match score
        match_score = self.calculate_match_score(resume_data, job_analysis)
        
        # Get detailed match info
        match_details = self.get_detailed_match(resume_data, job_analysis)

        # Generate suggestions
        suggestions = self.generate_suggestions(resume_data, job_analysis, match_score)

        return {
            "tailored_summary": tailored_summary,
            "enhanced_experience": enhanced_experience,
            "optimized_skills": optimized_skills,
            "match_score": round(match_score, 1),
            "suggestions": suggestions,
            "job_analysis": job_analysis,
            "match_details": match_details  # NEW: Detailed match breakdown
        }


# Flask route handler
from flask import request, jsonify

tailor_engine = ResumeAITailor()

def tailor_resume_endpoint():
    """Flask endpoint handler for resume tailoring."""
    try:
        data = request.get_json()

        resume_data = data.get('resume_data')
        job_description = data.get('job_description')
        job_title = data.get('job_title')
        company_name = data.get('company_name')

        if not all([resume_data, job_description, job_title]):
            return jsonify({'error': 'Missing required data'}), 400

        result = tailor_engine.tailor_resume(
            resume_data, 
            job_description, 
            job_title, 
            company_name
        )

        return jsonify(result), 200

    except Exception as e:
        print(f"Error in tailor_resume_endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
