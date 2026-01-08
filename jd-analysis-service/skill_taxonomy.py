# skill_taxonomy.py
"""
Skill Taxonomy Module for HuntPilot Job Tracker
================================================

This module provides:
1. SKILL_ALIASES: Normalize variant spellings (e.g., "react.js" → "react")
2. SKILL_WHITELIST: Curated set of valid tech skills for extraction
3. NOISE_PATTERNS: Regex patterns to filter out generic phrases
4. Helper functions for normalization and filtering

WHY THIS APPROACH:
- Uses rule-based matching instead of pure ML for predictable, explainable results
- Whitelist ensures only meaningful skills are extracted (not "developed using")
- Alias normalization prevents duplicate counting ("React" vs "React.js")
- Completely FREE - no paid APIs required
"""

import re
from typing import List, Set

# =============================================================================
# SKILL ALIASES: Maps variant spellings to canonical form
# =============================================================================
# WHY: Job descriptions and resumes use inconsistent naming.
# "React.js", "ReactJS", "react" should all count as ONE skill match.

SKILL_ALIASES = {
    # JavaScript ecosystem
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "react native": "react-native",
    "reactnative": "react-native",
    "node.js": "nodejs",
    "node js": "nodejs",
    "node": "nodejs",
    "vue.js": "vuejs",
    "vue js": "vuejs",
    "vue": "vuejs",
    "angular.js": "angular",
    "angularjs": "angular",
    "angular js": "angular",
    "next.js": "nextjs",
    "next js": "nextjs",
    "nuxt.js": "nuxtjs",
    "nuxt js": "nuxtjs",
    "express.js": "expressjs",
    "express js": "expressjs",
    "express": "expressjs",
    "nest.js": "nestjs",
    "nest js": "nestjs",
    "gatsby.js": "gatsby",
    "gatsby js": "gatsby",
    "js": "javascript",
    "es6": "javascript",
    "es2015": "javascript",
    "ecmascript": "javascript",
    "ts": "typescript",
    "jquery": "jquery",
    "backbone.js": "backbone",
    "backbone js": "backbone",
    "ember.js": "ember",
    "ember js": "ember",
    
    # Python ecosystem
    "py": "python",
    "python3": "python",
    "python 3": "python",
    "django rest framework": "django",
    "drf": "django",
    "flask-restful": "flask",
    "fast api": "fastapi",
    "sci-kit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "sci kit learn": "scikit-learn",
    "tf": "tensorflow",
    "tensor flow": "tensorflow",
    "keras": "tensorflow",
    "py torch": "pytorch",
    "torch": "pytorch",
    "np": "numpy",
    "pd": "pandas",
    
    # Databases
    "mongo": "mongodb",
    "mongo db": "mongodb",
    "postgres": "postgresql",
    "postgre sql": "postgresql",
    "psql": "postgresql",
    "mysql": "mysql",
    "my sql": "mysql",
    "mariadb": "mysql",
    "ms sql": "mssql",
    "sql server": "mssql",
    "microsoft sql server": "mssql",
    "sqlite3": "sqlite",
    "sqlite 3": "sqlite",
    "dynamodb": "dynamodb",
    "dynamo db": "dynamodb",
    "cassandra db": "cassandra",
    "couch db": "couchdb",
    "neo 4j": "neo4j",
    
    # Cloud & DevOps
    "amazon web services": "aws",
    "amazon aws": "aws",
    "aws lambda": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "azure cloud": "azure",
    "microsoft azure": "azure",
    "ms azure": "azure",
    "k8s": "kubernetes",
    "kube": "kubernetes",
    "docker compose": "docker",
    "docker-compose": "docker",
    "ci cd": "ci/cd",
    "ci-cd": "ci/cd",
    "cicd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "github actions": "github-actions",
    "gh actions": "github-actions",
    "gitlab ci": "gitlab-ci",
    "jenkins pipeline": "jenkins",
    "circle ci": "circleci",
    "travis ci": "travis-ci",
    "terraform cloud": "terraform",
    "ansible playbook": "ansible",
    
    # APIs & Protocols
    "rest api": "rest",
    "restful": "rest",
    "restful api": "rest",
    "rest apis": "rest",
    "graph ql": "graphql",
    "gql": "graphql",
    "grpc": "grpc",
    "websocket": "websockets",
    "web socket": "websockets",
    "web sockets": "websockets",
    "socket.io": "socketio",
    "socket io": "socketio",
    
    # Frontend
    "html5": "html",
    "html 5": "html",
    "css3": "css",
    "css 3": "css",
    "sass": "sass",
    "scss": "sass",
    "less css": "less",
    "tailwind css": "tailwindcss",
    "tailwind": "tailwindcss",
    "bootstrap 5": "bootstrap",
    "bootstrap5": "bootstrap",
    "material ui": "material-ui",
    "mui": "material-ui",
    "chakra ui": "chakra-ui",
    "ant design": "antd",
    "antdesign": "antd",
    
    # Testing
    "unit testing": "unit-testing",
    "unit tests": "unit-testing",
    "integration testing": "integration-testing",
    "integration tests": "integration-testing",
    "e2e testing": "e2e-testing",
    "end to end testing": "e2e-testing",
    "end-to-end testing": "e2e-testing",
    "test driven development": "tdd",
    "behavior driven development": "bdd",
    
    # Mobile
    "react native": "react-native",
    "react-native": "react-native",
    "flutter sdk": "flutter",
    "ios development": "ios",
    "android development": "android",
    "swift ui": "swiftui",
    "kotlin android": "kotlin",
    
    # AI/ML
    "machine learning": "ml",
    "deep learning": "deep-learning",
    "dl": "deep-learning",
    "natural language processing": "nlp",
    "computer vision": "cv",
    "artificial intelligence": "ai",
    "llm": "llm",
    "large language models": "llm",
    "chat gpt": "chatgpt",
    "open ai": "openai",
    "hugging face": "huggingface",
    "huggingface": "huggingface",
    
    # Version Control
    "github": "git",
    "gitlab": "git",
    "bitbucket": "git",
    "version control": "git",
    "source control": "git",
    
    # Other
    "object oriented programming": "oop",
    "object-oriented programming": "oop",
    "functional programming": "fp",
    "agile methodology": "agile",
    "agile/scrum": "agile",
    "scrum master": "scrum",
    "data structures": "data-structures",
    "data structure": "data-structures",
    "algorithms": "algorithms",
    "algo": "algorithms",
    "design patterns": "design-patterns",
    "solid principles": "solid",
    "clean code": "clean-code",
    "code review": "code-review",
    "pair programming": "pair-programming",
}

# =============================================================================
# SKILL WHITELIST: Valid tech skills to extract
# =============================================================================
# WHY: Only extract terms that are actual skills, not generic phrases.
# This prevents "experience with" or "developed using" from being extracted.

SKILL_WHITELIST: Set[str] = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    "haskell", "elixir", "erlang", "clojure", "lua", "dart", "objective-c",
    "assembly", "fortran", "cobol", "groovy", "julia", "vba", "powershell",
    "bash", "shell", "sql", "plsql", "nosql",
    
    # Frontend Frameworks & Libraries
    "react", "react-native", "angular", "vuejs", "svelte", "nextjs", "nuxtjs",
    "gatsby", "ember", "backbone", "jquery", "redux", "mobx", "zustand",
    "recoil", "rxjs", "webpack", "vite", "parcel", "rollup", "babel", "eslint",
    "prettier", "storybook", "cypress", "playwright", "puppeteer", "selenium",
    
    # Backend Frameworks
    "nodejs", "expressjs", "nestjs", "fastify", "koa", "hapi", "django",
    "flask", "fastapi", "pyramid", "tornado", "spring", "spring-boot",
    "spring-mvc", "hibernate", "rails", "sinatra", "laravel", "symfony",
    "codeigniter", "asp.net", "dotnet", ".net", "gin", "echo", "fiber",
    "phoenix", "actix", "rocket",
    
    # Databases
    "mongodb", "postgresql", "mysql", "sqlite", "mssql", "oracle",
    "redis", "memcached", "elasticsearch", "cassandra", "couchdb",
    "dynamodb", "firebase", "supabase", "neo4j", "influxdb", "timescaledb",
    "cockroachdb", "planetscale", "prisma", "sequelize", "mongoose", "typeorm",
    "sqlalchemy", "knex", "drizzle",
    
    # Cloud & Infrastructure
    "aws", "gcp", "azure", "heroku", "vercel", "netlify", "digitalocean",
    "linode", "cloudflare", "docker", "kubernetes", "terraform", "ansible",
    "puppet", "chef", "vagrant", "packer", "consul", "vault", "nomad",
    "prometheus", "grafana", "datadog", "splunk", "elk", "logstash", "kibana",
    "nginx", "apache", "caddy", "traefik", "haproxy",
    
    # CI/CD
    "ci/cd", "github-actions", "gitlab-ci", "jenkins", "circleci", "travis-ci",
    "teamcity", "bamboo", "azure-devops", "argo-cd", "spinnaker", "drone",
    
    # APIs & Protocols
    "rest", "graphql", "grpc", "soap", "websockets", "socketio", "mqtt",
    "amqp", "rabbitmq", "kafka", "redis-pubsub", "nats", "zeromq",
    "openapi", "swagger", "postman", "insomnia",
    
    # CSS & Styling
    "html", "css", "sass", "less", "stylus", "tailwindcss", "bootstrap",
    "material-ui", "chakra-ui", "antd", "bulma", "foundation", "semantic-ui",
    "styled-components", "emotion", "css-modules", "postcss",
    
    # Testing
    "jest", "mocha", "chai", "jasmine", "karma", "ava", "vitest",
    "pytest", "unittest", "nose", "robot-framework", "junit", "testng",
    "mockito", "rspec", "minitest", "phpunit", "xunit", "nunit",
    "unit-testing", "integration-testing", "e2e-testing", "tdd", "bdd",
    "selenium", "webdriver",
    
    # AI/ML
    "ml", "deep-learning", "nlp", "cv", "ai", "tensorflow", "pytorch",
    "scikit-learn", "keras", "pandas", "numpy", "scipy", "matplotlib",
    "seaborn", "plotly", "jupyter", "anaconda", "huggingface", "transformers",
    "spacy", "nltk", "opencv", "yolo", "llm", "langchain", "openai",
    "chatgpt", "bert", "gpt", "diffusion", "stable-diffusion", "rag",
    
    # Mobile Development
    "ios", "android", "flutter", "swiftui", "jetpack-compose", "xamarin",
    "cordova", "ionic", "capacitor", "expo",
    
    # Version Control & Collaboration
    "git", "svn", "mercurial", "perforce", "jira", "confluence", "trello",
    "asana", "monday", "linear", "notion", "figma", "sketch", "adobe-xd",
    "invision", "zeplin",
    
    # Security
    "oauth", "oauth2", "jwt", "saml", "ldap", "sso", "mfa", "2fa",
    "encryption", "ssl", "tls", "https", "cors", "csrf", "xss",
    "sql-injection", "owasp", "penetration-testing", "security-audit",
    
    # Architecture & Patterns
    "microservices", "monolith", "serverless", "event-driven", "cqrs",
    "event-sourcing", "ddd", "hexagonal", "clean-architecture", "mvc",
    "mvvm", "mvp", "oop", "fp", "solid", "design-patterns", "clean-code",
    "data-structures", "algorithms",
    
    # Methodologies
    "agile", "scrum", "kanban", "waterfall", "lean", "devops", "devsecops",
    "sre", "gitops", "code-review", "pair-programming",
    
    # Data & Analytics
    "big-data", "data-engineering", "etl", "data-pipeline", "airflow",
    "dbt", "snowflake", "redshift", "bigquery", "databricks", "spark",
    "hadoop", "hive", "presto", "tableau", "power-bi", "looker",
    "metabase", "superset",
    
    # Messaging & Queues
    "message-queue", "event-bus", "pubsub", "sns", "sqs", "kinesis",
    "eventbridge",
}

# =============================================================================
# NOISE PATTERNS: Regex patterns to filter out generic phrases
# =============================================================================
# WHY: RAKE and YAKE often extract action verbs and filler phrases.
# These patterns identify non-skill text to be removed.

NOISE_PATTERNS = [
    # Action verb phrases
    r"^(developed?|developing|development)\s+(using|with|for|in)?\s*$",
    r"^(work(?:ed|ing)?)\s+(on|with|for|in)?\s*$",
    r"^(us(?:e|ed|ing))\s+(this|these|the|a)?\s*$",
    r"^(experience(?:d)?)\s+(with|in|using)?\s*$",
    r"^(build(?:ing|t)?)\s+(with|using|for)?\s*$",
    r"^(creat(?:e|ed|ing))\s+(with|using|for)?\s*$",
    r"^(implement(?:ed|ing)?)\s+(with|using|for)?\s*$",
    r"^(design(?:ed|ing)?)\s+(with|using|for)?\s*$",
    
    # Generic phrases
    r"^(looking for|we are|must have|should have|nice to have)$",
    r"^(years? of experience|years experience|yoe)$",
    r"^(strong|excellent|good|proficient|skilled)\s+(in|with|at)?$",
    r"^(hands[- ]on|hands on experience)$",
    r"^(team player|self[- ]starter|fast learner)$",
    r"^(problem[- ]solv(?:er|ing)|critical think(?:er|ing))$",
    r"^(communication skills?|interpersonal skills?)$",
    r"^(tech stack|technology stack|software stack)$",
    r"^(best practices?|industry standards?)$",
    r"^(plus|bonus|preferred|required|mandatory)$",
    r"^(minimum|maximum|at least|up to)$",
    
    # Single common words
    r"^(the|a|an|and|or|but|in|on|at|to|for|of|with|by)$",
    r"^(is|are|was|were|be|been|being|have|has|had)$",
    r"^(will|would|could|should|can|may|might|must)$",
    r"^(this|that|these|those|it|its|their|our|your)$",
    r"^(what|when|where|why|how|who|which)$",
    r"^(new|old|good|bad|high|low|big|small)$",
    r"^(first|last|next|previous|other|another)$",
]

# Compile patterns for efficiency
COMPILED_NOISE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name to its canonical form.
    
    WHY: Different job descriptions use different variations:
    - "React.js" vs "ReactJS" vs "react"
    - "Node.js" vs "NodeJS" vs "node"
    
    This function maps all variants to a single canonical form.
    
    Args:
        skill: Raw skill string from extraction
        
    Returns:
        Normalized canonical skill name
    """
    if not skill:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = skill.lower().strip()
    
    # Remove special characters at start/end but preserve internal ones
    normalized = re.sub(r'^[^\w]+|[^\w]+$', '', normalized)
    
    # Check alias mapping
    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]
    
    return normalized


def is_valid_skill(skill: str) -> bool:
    """
    Check if a normalized skill is in the whitelist.
    
    WHY: Only return skills that are actual technologies/tools/concepts.
    This filters out "developed using", "experience with", etc.
    
    Args:
        skill: Normalized skill name
        
    Returns:
        True if skill is in whitelist, False otherwise
    """
    return skill in SKILL_WHITELIST


def is_noise(text: str) -> bool:
    """
    Check if text matches any noise pattern.
    
    WHY: RAKE and YAKE extract generic phrases like:
    - "developed using this"
    - "experience with the"
    - "strong in"
    
    These should be filtered out before skill matching.
    
    Args:
        text: Raw text to check
        
    Returns:
        True if text is noise, False otherwise
    """
    text = text.strip().lower()
    
    # Too short or too long to be a valid skill
    if len(text) < 2 or len(text) > 50:
        return True
    
    # Contains only numbers
    if text.isdigit():
        return True
    
    # Check against noise patterns
    for pattern in COMPILED_NOISE_PATTERNS:
        if pattern.match(text):
            return True
    
    return False


def filter_and_normalize_skills(raw_keywords: List[str]) -> List[str]:
    """
    Filter and normalize a list of raw keywords to valid skills.
    
    This is the main function that combines:
    1. Noise filtering (remove generic phrases)
    2. Normalization (map aliases to canonical form)
    3. Whitelist validation (keep only valid tech skills)
    4. Deduplication (remove duplicates after normalization)
    
    Args:
        raw_keywords: List of raw keywords from RAKE/YAKE/spaCy
        
    Returns:
        List of clean, normalized, validated skills (no duplicates)
    
    Example:
        Input:  ["React.js", "react", "developed using", "Node.js", "experience with"]
        Output: ["react", "nodejs"]
    """
    valid_skills = set()
    
    for keyword in raw_keywords:
        # Skip noise phrases
        if is_noise(keyword):
            continue
        
        # Normalize the skill
        normalized = normalize_skill(keyword)
        
        # Check if it's a valid skill
        if is_valid_skill(normalized):
            valid_skills.add(normalized)
    
    return list(valid_skills)


def extract_skills_from_text(text: str) -> Set[str]:
    """
    Extract all valid skills from raw text using pattern matching.
    
    WHY: This provides an additional extraction method that directly
    searches for whitelist skills in the text, catching cases that
    RAKE/YAKE might miss.
    
    Args:
        text: Raw job description or resume text
        
    Returns:
        Set of normalized skills found in text
    """
    text_lower = text.lower()
    found_skills = set()
    
    # Check each skill in whitelist
    for skill in SKILL_WHITELIST:
        # Handle skills with special characters
        skill_pattern = re.escape(skill)
        
        # Match whole word only (with word boundaries)
        # Allow for common separators like . / - _
        pattern = r'(?:^|[\s,;:.\-_/(])' + skill_pattern + r'(?:[\s,;:.\-_/)]|$)'
        
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    
    # Also check for aliases
    for alias, canonical in SKILL_ALIASES.items():
        alias_pattern = re.escape(alias)
        pattern = r'(?:^|[\s,;:.\-_/(])' + alias_pattern + r'(?:[\s,;:.\-_/)]|$)'
        
        if re.search(pattern, text_lower):
            found_skills.add(canonical)
    
    return found_skills


def get_skill_match_score(resume_skills: Set[str], job_skills: Set[str]) -> dict:
    """
    Calculate match score based on skill overlap.
    
    WHY: Raw keyword matching inflates scores because:
    - "React" and "React.js" are counted twice
    - Generic phrases artificially increase matches
    
    This function uses normalized skill sets for accurate scoring.
    
    Args:
        resume_skills: Set of normalized skills from resume
        job_skills: Set of normalized skills from job description
        
    Returns:
        Dictionary with match details:
        - score: Percentage of job skills found in resume (0-100)
        - matched: List of skills found in both
        - missing: List of job skills not in resume
        - extra: List of resume skills not in job (could be valuable)
    """
    if not job_skills:
        return {
            "score": 0,
            "matched": [],
            "missing": [],
            "extra": list(resume_skills)
        }
    
    matched = resume_skills & job_skills
    missing = job_skills - resume_skills
    extra = resume_skills - job_skills
    
    # Score is percentage of job skills matched
    score = (len(matched) / len(job_skills)) * 100
    
    return {
        "score": round(score, 1),
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing)),
        "extra": sorted(list(extra))
    }
