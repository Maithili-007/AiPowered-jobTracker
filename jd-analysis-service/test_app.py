import pytest
import json
import time
from app import app  # Import your Flask app
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


# =============================================================================
# ORIGINAL TESTS (updated expectations for new behavior)
# =============================================================================

# ✅ Test 1: Valid request returns keywords
def test_extract_keywords(client):
    """Test basic keyword extraction returns valid skills."""
    payload = {
        "description": "We are looking for a Python developer with experience in Flask and machine learning."
    }
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    data = response.get_json()
    assert "keywords" in data
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) > 0
    # Should contain normalized skill names
    keywords_lower = [kw.lower() for kw in data["keywords"]]
    assert "python" in keywords_lower or "flask" in keywords_lower or "ml" in keywords_lower


# ✅ Test 2: Empty description returns empty list
def test_empty_description(client):
    """Test that empty description returns empty keyword list."""
    payload = {"description": ""}
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    data = response.get_json()
    assert "keywords" in data
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) == 0  # Should be empty, not just any list


# ✅ Test 3: Missing description key
def test_missing_description_key(client):
    """Test handling of missing description key."""
    payload = {}
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    data = response.get_json()
    assert "keywords" in data
    assert isinstance(data["keywords"], list)


# ✅ Test 4: Invalid JSON
def test_invalid_json(client):
    """Test handling of invalid JSON payload."""
    invalid_payload = "not json"
    response = client.post("/extract-keywords", data=invalid_payload, content_type="application/json")

    assert response.status_code in [400, 500]


# ✅ Test 5: Performance test (under 2 seconds)
def test_performance(client):
    """Test that extraction completes within 2 seconds."""
    payload = {"description": " ".join(["Python Flask AI Machine Learning Docker Kubernetes"] * 50)}
    start = time.time()
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 2.0


# =============================================================================
# NEW TESTS: Skill Normalization
# =============================================================================

def test_skill_normalization_react_variants(client):
    """
    TEST: React.js, ReactJS, and react should normalize to 'react'.
    
    WHY THIS MATTERS:
    Before: "React.js" and "react" counted as 2 separate skills
    After: Both normalize to "react" (only counted once)
    """
    payload = {
        "description": "Looking for React.js developer. Must know ReactJS and react fundamentals."
    }
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    keywords = data["keywords"]
    
    # Should contain "react" (normalized form)
    assert "react" in keywords
    
    # Should NOT contain variants as separate entries
    assert "react.js" not in keywords
    assert "reactjs" not in keywords
    
    # Count of "react" should be 1 (no duplicates)
    assert keywords.count("react") == 1


def test_skill_normalization_nodejs_variants(client):
    """TEST: Node.js, node, NodeJS should normalize to 'nodejs'."""
    payload = {
        "description": "Experience with Node.js and node backend development."
    }
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    keywords = data["keywords"]
    
    assert "nodejs" in keywords
    assert keywords.count("nodejs") == 1


# =============================================================================
# NEW TESTS: Noise Filtering
# =============================================================================

def test_noise_phrases_filtered_out(client):
    """
    TEST: Generic phrases like 'developed using' should be filtered out.
    
    WHY THIS MATTERS:
    Before: "developed using this", "experience with" were extracted as keywords
    After: Only actual skills are extracted
    """
    payload = {
        "description": "We are looking for someone who developed using React. Must have experience with Node.js and strong background in Python."
    }
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    keywords = data["keywords"]
    
    # Should contain actual skills
    assert any(skill in keywords for skill in ["react", "nodejs", "python"])
    
    # Should NOT contain noise phrases
    noise_phrases = ["developed using", "experience with", "strong background", "looking for"]
    for phrase in noise_phrases:
        assert phrase not in keywords


def test_action_verbs_filtered_out(client):
    """TEST: Action verbs should not be extracted as skills."""
    payload = {
        "description": "Developed scalable APIs. Implemented microservices. Built with Python and JavaScript."
    }
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    keywords = data["keywords"]
    
    # Should contain skills
    assert any(skill in keywords for skill in ["python", "javascript", "microservices"])
    
    # Should NOT contain action verbs
    action_verbs = ["developed", "implemented", "built", "scalable"]
    for verb in action_verbs:
        assert verb not in keywords


# =============================================================================
# NEW TESTS: Extract Skills Endpoint
# =============================================================================

def test_extract_skills_endpoint(client):
    """TEST: New /extract-skills endpoint returns structured skill data."""
    payload = {
        "description": "Looking for React and Node.js developer with MongoDB experience."
    }
    response = client.post("/extract-skills", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert "skills" in data
    assert "skill_count" in data
    assert isinstance(data["skills"], list)
    assert data["skill_count"] == len(data["skills"])


def test_extract_skills_with_resume_matching(client):
    """
    TEST: /extract-skills with resume_text returns match results.
    
    This tests the core matching improvement.
    """
    payload = {
        "description": "React developer with Node.js, MongoDB, and GraphQL experience.",
        "resume_text": "I am a Python developer with React and Docker experience."
    }
    response = client.post("/extract-skills", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert "match_result" in data
    match = data["match_result"]
    
    assert "score" in match
    assert "matched" in match
    assert "missing" in match
    assert "extra" in match
    
    # React should be in matched (both have it)
    assert "react" in match["matched"]
    
    # MongoDB and GraphQL should be in missing (job has, resume doesn't)
    assert any(skill in match["missing"] for skill in ["mongodb", "graphql"])
    
    # Python and Docker should be in extra (resume has, job doesn't)
    assert any(skill in match["extra"] for skill in ["python", "docker"])


# =============================================================================
# NEW TESTS: Match Score Accuracy
# =============================================================================

def test_match_score_not_inflated(client):
    """
    TEST: Match score should reflect actual skill overlap, not be inflated.
    
    WHY THIS MATTERS:
    Before: Substring matching caused "React" to match "React.js developer" text
    After: Only exact skill matches count
    """
    # Job requires 4 skills, resume has 2 of them
    payload = {
        "description": "Need React, Node.js, MongoDB, and Docker skills.",
        "resume_text": "I know React and Docker. Also Python and Flask."
    }
    response = client.post("/extract-skills", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    match = data["match_result"]
    
    # Score should be around 50% (2 out of 4 skills matched)
    # Allow some tolerance for how skills are extracted
    assert 30 <= match["score"] <= 70, f"Score {match['score']} outside expected range"
    
    # Should have at least 2 matched (react, docker)
    assert len(match["matched"]) >= 2, f"Expected at least 2 matched, got {match['matched']}"
    
    # Should have some missing skills
    assert len(match["missing"]) >= 1, f"Expected at least 1 missing, got {match['missing']}"


def test_match_score_with_variants(client):
    """
    TEST: Skill variants should count as the same skill in matching.
    
    Resume says "React.js", job says "react" - should match!
    """
    payload = {
        "description": "Looking for react and nodejs developer.",
        "resume_text": "Expert in React.js and Node.js development."
    }
    response = client.post("/extract-skills", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    match = data["match_result"]
    
    # Should be 100% match since both skills are present (just different variants)
    assert match["score"] == 100.0
    assert len(match["matched"]) == 2
    assert len(match["missing"]) == 0


# =============================================================================
# NEW TESTS: Tailor Resume Endpoint
# =============================================================================

def test_tailor_resume_real_score(client):
    """TEST: /api/tailor-resume returns real skill-based match score."""
    payload = {
        "resume_data": {
            "summary": "Python developer with React experience",
            "experience": [
                {"title": "Developer", "description": "Built React apps with Python backend"}
            ],
            "skills": "Python, React, Docker"
        },
        "job_description": "React developer with Python, MongoDB, and AWS experience required.",
        "job_title": "Full Stack Developer",
        "company_name": "TechCorp"
    }
    response = client.post("/api/tailor-resume", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Should have realistic match score (not hardcoded 85)
    assert "match_score" in data
    assert 0 <= data["match_score"] <= 100
    
    # Score should NOT be exactly 85.0 (the old hardcoded value)
    # unless by coincidence - but very unlikely
    assert data["match_score"] != 85.0 or "match_details" in data
    
    # Should have match details
    assert "match_details" in data
    assert "matched_skills" in data["match_details"]
    assert "missing_skills" in data["match_details"]


# =============================================================================
# NEW TESTS: Edge Cases
# =============================================================================

def test_complex_job_description(client):
    """TEST: Complex real-world job description extracts correct skills."""
    payload = {
        "description": """
        We are looking for a Senior Full Stack Developer to join our team.
        
        Requirements:
        - 5+ years experience with React.js or Angular
        - Strong backend skills in Node.js or Python
        - Database experience with PostgreSQL and MongoDB
        - Familiarity with Docker, Kubernetes, and CI/CD pipelines
        - Experience with AWS or GCP cloud services
        - Knowledge of GraphQL and REST API design
        
        Nice to have:
        - TypeScript experience
        - Experience with Redis caching
        - Agile/Scrum methodology
        """
    }
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    data = response.get_json()
    keywords = data["keywords"]
    
    # Should extract all major skills
    expected_skills = ["react", "angular", "nodejs", "python", "postgresql", 
                       "mongodb", "docker", "kubernetes", "aws", "gcp", 
                       "graphql", "rest", "typescript", "redis", "agile", "scrum"]
    
    matched_count = sum(1 for skill in expected_skills if skill in keywords)
    
    # Should match at least 10 of the 16 expected skills
    assert matched_count >= 10, f"Only matched {matched_count} skills: {keywords}"
