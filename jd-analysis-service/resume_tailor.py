
# resume_tailor.py
import spacy
import re
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from yake import KeywordExtractor
from rake_nltk import Rake

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeAITailor:
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            self.nlp = None

        self.stop_words = set(stopwords.words('english'))

    def extract_keywords_yake(self, text, max_keywords=20):
        """Extract keywords using YAKE algorithm"""
        kw_extractor = KeywordExtractor(
            lan="en",
            n=3,
            dedupLim=0.9,
            top=max_keywords
        )
        keywords = kw_extractor.extract_keywords(text)
        return [kw[1] for kw in keywords]

    def extract_keywords_rake(self, text):
        """Extract keywords using RAKE algorithm"""
        r = Rake()
        r.extract_keywords_from_text(text)
        return r.get_ranked_phrases()[:15]

    def analyze_job_requirements(self, job_description):
        """Analyze job description to extract key requirements"""
        if not self.nlp:
            return {"skills": [], "keywords": [], "requirements": []}

        doc = self.nlp(job_description)

        # Extract skills and technical keywords
        skills = []
        keywords = []

        # Look for technical skills patterns
        tech_patterns = [
            r'\b(?:JavaScript|Python|React|Node\.js|MongoDB|Express|SQL|AWS|Docker|Git)\b',
            r'\b(?:HTML|CSS|Bootstrap|Tailwind|API|REST|GraphQL|TypeScript)\b',
            r'\b(?:Machine Learning|AI|NLP|Data Science|Analytics)\b'
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            skills.extend(matches)

        # Extract keywords using YAKE
        yake_keywords = self.extract_keywords_yake(job_description)
        keywords.extend(yake_keywords)

        # Extract action verbs and requirements
        requirements = []
        for sent in doc.sents:
            if any(word in sent.text.lower() for word in ['responsible for', 'must have', 'required', 'experience with']):
                requirements.append(sent.text.strip())

        return {
            "skills": list(set(skills)),
            "keywords": list(set(keywords))[:20],
            "requirements": requirements[:5]
        }

    def tailor_summary(self, original_summary, job_analysis, job_title, company_name):
        """Generate tailored professional summary"""
        job_keywords = job_analysis.get("keywords", [])[:10]
        job_skills = job_analysis.get("skills", [])[:5]

        # Create enhanced summary
        keyword_integration = f"Experienced professional with expertise in {', '.join(job_skills[:3])}"
        company_mention = f"seeking to contribute to {company_name}'s success"
        role_alignment = f"Strong background in {job_title.lower()} responsibilities"

        tailored_summary = f"{keyword_integration}. {role_alignment} with proven track record in {', '.join(job_keywords[:3])}. {company_mention} through innovative solutions and technical excellence."

        return tailored_summary

    def enhance_experience(self, experience_list, job_analysis):
        """Enhance work experience descriptions with job-relevant keywords"""
        enhanced_experience = []
        job_keywords = [kw.lower() for kw in job_analysis.get("keywords", [])]
        job_skills = [skill.lower() for skill in job_analysis.get("skills", [])]

        for exp in experience_list:
            enhanced_desc = exp.get("description", "")

            # Add relevant keywords if missing
            for keyword in job_keywords[:5]:
                if keyword not in enhanced_desc.lower() and len(keyword) > 3:
                    enhanced_desc += f" Utilized {keyword} to improve efficiency."

            # Enhance with action verbs
            action_verbs = ["Developed", "Implemented", "Optimized", "Enhanced", "Managed"]
            if not any(verb in enhanced_desc for verb in action_verbs):
                enhanced_desc = f"Developed and {enhanced_desc}"

            enhanced_exp = {
                **exp,
                "enhanced_description": enhanced_desc,
                "relevant_keywords": [kw for kw in job_keywords if kw in enhanced_desc.lower()][:5],
                "optimized_title": exp.get("title", "")
            }

            enhanced_experience.append(enhanced_exp)

        return enhanced_experience

    def optimize_skills(self, current_skills, job_analysis):
        """Optimize skills section based on job requirements"""
        job_skills = job_analysis.get("skills", [])
        current_skills_list = current_skills if isinstance(current_skills, list) else [current_skills]

        # Merge and prioritize skills
        all_skills = list(set(current_skills_list + job_skills))

        # Prioritize job-relevant skills
        prioritized_skills = []
        for skill in job_skills:
            if skill not in prioritized_skills:
                prioritized_skills.append(skill)

        for skill in current_skills_list:
            if skill not in prioritized_skills:
                prioritized_skills.append(skill)

        return ", ".join(prioritized_skills[:15])

    def calculate_match_score(self, resume_data, job_analysis):
        """Calculate resume-job match score"""
        resume_text = f"{resume_data.get('summary', '')} {' '.join([exp.get('description', '') for exp in resume_data.get('experience', [])])}"
        job_keywords = job_analysis.get("keywords", [])
        job_skills = job_analysis.get("skills", [])

        all_job_terms = job_keywords + job_skills
        resume_text_lower = resume_text.lower()

        matches = sum(1 for term in all_job_terms if term.lower() in resume_text_lower)
        total_terms = len(all_job_terms)

        if total_terms == 0:
            return 0

        score = (matches / total_terms) * 100
        return min(score, 100)  # Cap at 100%

    def generate_suggestions(self, resume_data, job_analysis, match_score):
        """Generate improvement suggestions"""
        suggestions = []

        if match_score < 70:
            suggestions.append("Consider adding more job-relevant keywords to improve ATS compatibility")

        job_skills = job_analysis.get("skills", [])
        resume_skills = resume_data.get("skills", "")

        missing_skills = [skill for skill in job_skills if skill.lower() not in resume_skills.lower()]
        if missing_skills:
            suggestions.append(f"Consider adding these relevant skills: {', '.join(missing_skills[:5])}")

        if len(resume_data.get("experience", [])) < 3:
            suggestions.append("Consider adding more detailed work experience descriptions")

        return suggestions

    def tailor_resume(self, resume_data, job_description, job_title, company_name):
        """Main function to tailor resume for specific job"""
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

        # Calculate match score
        match_score = self.calculate_match_score(resume_data, job_analysis)

        # Generate suggestions
        suggestions = self.generate_suggestions(resume_data, job_analysis, match_score)

        return {
            "tailored_summary": tailored_summary,
            "enhanced_experience": enhanced_experience,
            "optimized_skills": optimized_skills,
            "match_score": round(match_score, 1),
            "suggestions": suggestions,
            "job_analysis": job_analysis
        }

# Flask route handler
from flask import request, jsonify

tailor_engine = ResumeAITailor()

def tailor_resume_endpoint():
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
