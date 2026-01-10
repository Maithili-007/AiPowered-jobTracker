# =============================================================================
# Skill Taxonomy Module for HuntPilot Job Tracker
# =============================================================================
# 
# WHAT IS THIS FILE?
# ------------------
# This module is the "brain" behind skill extraction in our JD Analysis Service.
# It provides:
# 1. A curated list of ~300 valid technical skills (SKILL_WHITELIST)
# 2. Aliases to normalize different spellings (e.g., "React.js" → "react")
# 3. Noise patterns to filter out generic phrases (e.g., "developed using")
# 4. Helper functions to filter, normalize, and match skills
# 
# WHY THIS MODULE EXISTS (THE PROBLEM IT SOLVES):
# -----------------------------------------------
# When we use NLP libraries like RAKE or YAKE to extract keywords from job 
# descriptions, they extract ANY important-looking phrase, including garbage:
# - "developed using modern"
# - "experience with the technology"
# - "strong background in"
# 
# These aren't skills - they're just common phrases in job descriptions!
# 
# This module acts as a FILTER that:
# 1. Only keeps terms that are actual technical skills
# 2. Normalizes variants (React.js = react = ReactJS)
# 3. Removes noise and garbage
# 
# HOW IT CONNECTS TO THE REST OF THE APP:
# ---------------------------------------
# 1. app.py imports functions from this module
# 2. When keywords are extracted by RAKE/YAKE/spaCy, they pass through
#    filter_and_normalize_skills() to clean them up
# 3. Clean skills are returned to your Node.js backend
# 4. Your React frontend displays only meaningful, normalized skills
# 
# JAVASCRIPT ANALOGY:
# ------------------
# Think of this module as a utility/helper file (like utils.js) that exports
# constants and functions used throughout the application.
# 
# In Node.js, this might look like:
#   module.exports = { SKILL_WHITELIST, normalizeSkill, filterSkills };
# =============================================================================

# =============================================================================
# IMPORTS
# =============================================================================
# 're' is Python's regex module (like JavaScript's RegExp)
# Used for pattern matching to identify noise phrases
import re

# 'typing' provides type hints (like TypeScript)
# List = array, Set = Set object
# These are just for documentation/IDE support - Python doesn't enforce them
# 
# JavaScript/TypeScript equivalent:
#   function filterSkills(raw: string[]): string[]
#   const skills: Set<string> = new Set()
from typing import List, Set


# =============================================================================
# SKILL ALIASES: Maps Variant Spellings to Canonical Form
# =============================================================================
# 
# WHAT IS THIS?
# -------------
# A dictionary (like a JavaScript object/Map) that maps different ways of
# writing the same skill to ONE standard version.
# 
# WHY THIS IS NEEDED:
# ------------------
# Job descriptions and resumes use inconsistent naming:
# - "React.js", "ReactJS", "React", "react" are ALL the same thing
# - If we don't normalize, we might count React as 4 different skills!
# 
# HOW IT WORKS:
# ------------
# When we find "react.js" in a job description:
# 1. Look it up in SKILL_ALIASES
# 2. Find that "react.js" → "react"
# 3. Store/compare using "react" instead
# 
# This way, a resume with "React" will match a job requiring "React.js"
# 
# PYTHON SYNTAX NOTE:
# ------------------
# In Python, dictionaries use {} and : for key-value pairs
# JavaScript: { key: "value" }
# Python: { "key": "value" }  (strings need quotes as keys)

SKILL_ALIASES = {
    # =========================================================================
    # JavaScript Ecosystem Aliases
    # =========================================================================
    # React variations - all map to "react"
    "react.js": "react",       # Common in job postings
    "reactjs": "react",        # Common developer spelling
    "react js": "react",       # Space-separated version
    
    # React Native (mobile framework) - kept separate from React (web)
    "react native": "react-native",
    "reactnative": "react-native",
    
    # Node.js variations - all map to "nodejs"
    "node.js": "nodejs",
    "node js": "nodejs",
    "node": "nodejs",          # Often just called "node"
    
    # Vue.js variations
    "vue.js": "vuejs",
    "vue js": "vuejs",
    "vue": "vuejs",
    
    # Angular variations (note: Angular and AngularJS are technically different,
    # but for job matching purposes we treat them as the same skill)
    "angular.js": "angular",
    "angularjs": "angular",
    "angular js": "angular",
    
    # Next.js (React framework for full-stack apps)
    "next.js": "nextjs",
    "next js": "nextjs",
    
    # Nuxt.js (Vue's equivalent of Next.js)
    "nuxt.js": "nuxtjs",
    "nuxt js": "nuxtjs",
    
    # Express.js (Node.js web framework - like Flask in Python)
    "express.js": "expressjs",
    "express js": "expressjs",
    "express": "expressjs",
    
    # NestJS (TypeScript Node.js framework)
    "nest.js": "nestjs",
    "nest js": "nestjs",
    
    # Gatsby (React static site generator)
    "gatsby.js": "gatsby",
    "gatsby js": "gatsby",
    
    # JavaScript language aliases
    "js": "javascript",
    "es6": "javascript",       # ECMAScript 6 = JavaScript
    "es2015": "javascript",    # ES2015 = ES6 = JavaScript
    "ecmascript": "javascript",
    
    # TypeScript
    "ts": "typescript",
    
    # Legacy frameworks
    "jquery": "jquery",
    "backbone.js": "backbone",
    "backbone js": "backbone",
    "ember.js": "ember",
    "ember js": "ember",
    
    # =========================================================================
    # Python Ecosystem Aliases
    # =========================================================================
    "py": "python",
    "python3": "python",
    "python 3": "python",
    
    # Django (Python web framework - like Express for Node)
    "django rest framework": "django",
    "drf": "django",           # DRF is Django REST Framework
    
    # Flask (lightweight Python web framework - what THIS service uses!)
    "flask-restful": "flask",
    
    # FastAPI (modern async Python framework)
    "fast api": "fastapi",
    
    # Scikit-learn (machine learning library)
    "sci-kit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "sci kit learn": "scikit-learn",
    
    # TensorFlow (deep learning framework)
    "tf": "tensorflow",
    "tensor flow": "tensorflow",
    "keras": "tensorflow",     # Keras is now part of TensorFlow
    
    # PyTorch (deep learning framework)
    "py torch": "pytorch",
    "torch": "pytorch",
    
    # Data science libraries
    "np": "numpy",             # Common import alias
    "pd": "pandas",            # Common import alias
    
    # =========================================================================
    # Database Aliases
    # =========================================================================
    "mongo": "mongodb",
    "mongo db": "mongodb",
    
    "postgres": "postgresql",
    "postgre sql": "postgresql",
    "psql": "postgresql",      # PostgreSQL command-line tool name
    
    "mysql": "mysql",
    "my sql": "mysql",
    "mariadb": "mysql",        # MySQL-compatible fork
    
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
    
    # =========================================================================
    # Cloud & DevOps Aliases
    # =========================================================================
    "amazon web services": "aws",
    "amazon aws": "aws",
    "aws lambda": "aws",       # Lambda is an AWS service
    
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    
    "azure cloud": "azure",
    "microsoft azure": "azure",
    "ms azure": "azure",
    
    "k8s": "kubernetes",       # Industry abbreviation
    "kube": "kubernetes",
    
    "docker compose": "docker",
    "docker-compose": "docker",
    
    # CI/CD (Continuous Integration / Continuous Deployment)
    "ci cd": "ci/cd",
    "ci-cd": "ci/cd",
    "cicd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    
    # CI/CD tools
    "github actions": "github-actions",
    "gh actions": "github-actions",
    "gitlab ci": "gitlab-ci",
    "jenkins pipeline": "jenkins",
    "circle ci": "circleci",
    "travis ci": "travis-ci",
    
    # Infrastructure as Code
    "terraform cloud": "terraform",
    "ansible playbook": "ansible",
    
    # =========================================================================
    # API & Protocol Aliases
    # =========================================================================
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
    
    # =========================================================================
    # Frontend Aliases
    # =========================================================================
    "html5": "html",
    "html 5": "html",
    
    "css3": "css",
    "css 3": "css",
    
    "sass": "sass",
    "scss": "sass",            # SCSS is Sass syntax
    "less css": "less",
    
    "tailwind css": "tailwindcss",
    "tailwind": "tailwindcss",
    
    "bootstrap 5": "bootstrap",
    "bootstrap5": "bootstrap",
    
    "material ui": "material-ui",
    "mui": "material-ui",      # Common abbreviation
    
    "chakra ui": "chakra-ui",
    
    "ant design": "antd",
    "antdesign": "antd",
    
    # =========================================================================
    # Testing Aliases
    # =========================================================================
    "unit testing": "unit-testing",
    "unit tests": "unit-testing",
    
    "integration testing": "integration-testing",
    "integration tests": "integration-testing",
    
    "e2e testing": "e2e-testing",
    "end to end testing": "e2e-testing",
    "end-to-end testing": "e2e-testing",
    
    "test driven development": "tdd",
    "behavior driven development": "bdd",
    
    # =========================================================================
    # Mobile Development Aliases
    # =========================================================================
    "react native": "react-native",
    "react-native": "react-native",
    
    "flutter sdk": "flutter",
    
    "ios development": "ios",
    "android development": "android",
    
    "swift ui": "swiftui",
    "kotlin android": "kotlin",
    
    # =========================================================================
    # AI/ML Aliases
    # =========================================================================
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
    
    # =========================================================================
    # Version Control Aliases
    # =========================================================================
    # Note: We normalize all version control platforms to "git"
    # because the core skill is Git, not a specific platform
    "github": "git",
    "gitlab": "git",
    "bitbucket": "git",
    "version control": "git",
    "source control": "git",
    
    # =========================================================================
    # Software Engineering Concepts
    # =========================================================================
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
# SKILL WHITELIST: The Definitive List of Valid Technical Skills
# =============================================================================
# 
# WHAT IS THIS?
# -------------
# A Python Set (like JavaScript's Set) containing ~300 valid technical skills.
# If a term is NOT in this set, it's NOT a skill.
# 
# WHY A SET AND NOT A LIST?
# -------------------------
# Sets have O(1) lookup time (constant time, like JavaScript).
# Checking "is 'react' in SKILL_WHITELIST" is instant, even with 300 items.
# A list would be O(n) - slower for large lists.
# 
# JavaScript equivalent:
#   const SKILL_WHITELIST = new Set(["python", "javascript", "react", ...]);
# 
# HOW THIS IS USED:
# ----------------
# After RAKE/YAKE extracts keywords, we check each one:
#   if normalized_keyword in SKILL_WHITELIST:
#       keep_it()
#   else:
#       discard_it()
# 
# PYTHON SYNTAX NOTE:
# ------------------
# Set literal uses {} like dict, but without key:value pairs
# Python: {"item1", "item2", "item3"}
# JavaScript: new Set(["item1", "item2", "item3"])
# 
# The ': Set[str]' is a type hint (like TypeScript: Set<string>)

SKILL_WHITELIST: Set[str] = {
    # =========================================================================
    # Programming Languages
    # =========================================================================
    # These are the fundamental languages developers use
    "python",       # What THIS service is written in!
    "javascript",   # What your React/Node app uses
    "typescript",   # Typed JavaScript
    "java",         # Enterprise language, Android development
    "c",            # Systems programming
    "c++",          # Game dev, systems programming
    "c#",           # Microsoft/.NET ecosystem
    "go",           # Google's language for cloud/backend
    "golang",       # Same as "go" (alias would normalize to "go")
    "rust",         # Systems programming, memory safety
    "ruby",         # Rails, scripting
    "php",          # Web development (WordPress, Laravel)
    "swift",        # iOS development
    "kotlin",       # Android development
    "scala",        # JVM, big data
    "r",            # Statistics, data science
    "matlab",       # Engineering, academia
    "perl",         # Legacy scripting
    "haskell",      # Functional programming
    "elixir",       # Erlang VM, real-time systems
    "erlang",       # Telecom, distributed systems
    "clojure",      # Lisp on JVM
    "lua",          # Game scripting
    "dart",         # Flutter mobile development
    "objective-c",  # Legacy iOS development
    "assembly",     # Low-level programming
    "fortran",      # Scientific computing (legacy)
    "cobol",        # Banking mainframes (legacy)
    "groovy",       # Java scripting, Jenkins
    "julia",        # Scientific computing
    "vba",          # Excel macros
    "powershell",   # Windows scripting
    "bash",         # Linux/Unix scripting
    "shell",        # Generic shell scripting
    "sql",          # Database queries
    "plsql",        # Oracle's SQL variant
    "nosql",        # Non-relational database concept
    
    # =========================================================================
    # Frontend Frameworks & Libraries
    # =========================================================================
    # These are used to build user interfaces (like your React app!)
    "react",        # Your frontend framework! Facebook's UI library
    "react-native", # React for mobile apps
    "angular",      # Google's frontend framework
    "vuejs",        # Progressive JavaScript framework
    "svelte",       # Compiled frontend framework
    "nextjs",       # React full-stack framework
    "nuxtjs",       # Vue's equivalent of Next.js
    "gatsby",       # React static site generator
    "ember",        # Legacy framework
    "backbone",     # Legacy MVC framework
    "jquery",       # Legacy DOM manipulation
    
    # State management
    "redux",        # State management for React
    "mobx",         # Observable state management
    "zustand",      # Lightweight state management
    "recoil",       # Facebook's state management
    "rxjs",         # Reactive programming
    
    # Build tools & bundlers
    "webpack",      # Module bundler
    "vite",         # Next-gen build tool (fast!)
    "parcel",       # Zero-config bundler
    "rollup",       # ES module bundler
    "babel",        # JavaScript compiler
    "eslint",       # Linting (code quality)
    "prettier",     # Code formatting
    "storybook",    # Component documentation
    
    # Testing (frontend)
    "cypress",      # E2E testing
    "playwright",   # E2E testing (Microsoft)
    "puppeteer",    # Browser automation
    "selenium",     # Browser automation
    
    # =========================================================================
    # Backend Frameworks
    # =========================================================================
    # These power the server side (like your Express/Node backend)
    "nodejs",       # JavaScript runtime (what runs your Express app)
    "expressjs",    # Your backend framework! Minimal Node.js framework
    "nestjs",       # Enterprise Node.js framework
    "fastify",      # Fast Node.js framework
    "koa",          # Express successor
    "hapi",         # Enterprise Node.js framework
    
    # Python frameworks (like what THIS service uses!)
    "django",       # Python's "batteries included" framework
    "flask",        # THIS service! Lightweight Python framework
    "fastapi",      # Modern async Python framework
    "pyramid",      # Flexible Python framework
    "tornado",      # Async Python framework
    
    # Java frameworks
    "spring",       # Enterprise Java framework
    "spring-boot",  # Spring with auto-configuration
    "spring-mvc",   # Spring web module
    "hibernate",    # Java ORM
    
    # Ruby frameworks
    "rails",        # Ruby on Rails
    "sinatra",      # Lightweight Ruby framework
    
    # PHP frameworks
    "laravel",      # Popular PHP framework
    "symfony",      # Enterprise PHP framework
    "codeigniter",  # Simple PHP framework
    
    # .NET frameworks
    "asp.net",      # Microsoft's web framework
    "dotnet",       # .NET platform
    ".net",         # Same as dotnet
    
    # Go frameworks
    "gin",          # Popular Go web framework
    "echo",         # Go web framework
    "fiber",        # Express-inspired Go framework
    
    # Other
    "phoenix",      # Elixir web framework
    "actix",        # Rust web framework
    "rocket",       # Rust web framework
    
    # =========================================================================
    # Databases
    # =========================================================================
    # Data storage solutions
    "mongodb",      # NoSQL document database (popular with Node.js)
    "postgresql",   # Powerful relational database
    "mysql",        # Popular relational database
    "sqlite",       # Lightweight file-based database
    "mssql",        # Microsoft SQL Server
    "oracle",       # Enterprise relational database
    
    # In-memory & caching
    "redis",        # In-memory data store, caching
    "memcached",    # Distributed caching
    
    # Search & analytics
    "elasticsearch",# Full-text search engine
    
    # NoSQL databases
    "cassandra",    # Wide-column store
    "couchdb",      # Document database
    "dynamodb",     # AWS's NoSQL database
    "firebase",     # Google's BaaS (Backend as a Service)
    "supabase",     # Open-source Firebase alternative
    
    # Graph databases
    "neo4j",        # Graph database
    
    # Time-series databases
    "influxdb",     # Time-series database
    "timescaledb",  # PostgreSQL for time-series
    
    # Modern databases
    "cockroachdb",  # Distributed SQL
    "planetscale",  # Serverless MySQL
    
    # ORMs (Object-Relational Mappers)
    "prisma",       # Modern TypeScript ORM
    "sequelize",    # Node.js ORM
    "mongoose",     # MongoDB ODM for Node.js
    "typeorm",      # TypeScript ORM
    "sqlalchemy",   # Python ORM (used with Flask)
    "knex",         # SQL query builder
    "drizzle",      # TypeScript ORM
    
    # =========================================================================
    # Cloud & Infrastructure
    # =========================================================================
    # Where apps are deployed and run
    "aws",          # Amazon Web Services (market leader)
    "gcp",          # Google Cloud Platform
    "azure",        # Microsoft Azure
    
    # Platform as a Service
    "heroku",       # Easy app hosting
    "vercel",       # Frontend/Next.js hosting
    "netlify",      # Frontend hosting
    "digitalocean", # Simple cloud hosting
    "linode",       # Cloud hosting
    "cloudflare",   # CDN and edge services
    
    # Containerization & Orchestration
    "docker",       # Containerization (packages apps)
    "kubernetes",   # Container orchestration
    
    # Infrastructure as Code
    "terraform",    # Infrastructure as code
    "ansible",      # Configuration management
    "puppet",       # Configuration management
    "chef",         # Configuration management
    "vagrant",      # Development environments
    "packer",       # Machine images
    
    # Service mesh & discovery
    "consul",       # Service discovery
    "vault",        # Secrets management
    "nomad",        # Orchestration
    
    # Monitoring & observability
    "prometheus",   # Metrics collection
    "grafana",      # Metrics visualization
    "datadog",      # Monitoring platform
    "splunk",       # Log analysis
    "elk",          # Elasticsearch + Logstash + Kibana
    "logstash",     # Log processing
    "kibana",       # Log visualization
    
    # Web servers & proxies
    "nginx",        # Web server / reverse proxy
    "apache",       # Web server
    "caddy",        # Modern web server
    "traefik",      # Cloud-native reverse proxy
    "haproxy",      # Load balancer
    
    # =========================================================================
    # CI/CD (Continuous Integration / Continuous Deployment)
    # =========================================================================
    # Automation tools for building and deploying code
    "ci/cd",        # The general concept
    "github-actions",# GitHub's CI/CD
    "gitlab-ci",    # GitLab's CI/CD
    "jenkins",      # Traditional CI/CD server
    "circleci",     # Cloud CI/CD
    "travis-ci",    # Open-source CI/CD
    "teamcity",     # JetBrains CI/CD
    "bamboo",       # Atlassian CI/CD
    "azure-devops", # Microsoft CI/CD
    "argo-cd",      # GitOps CD
    "spinnaker",    # Multi-cloud CD
    "drone",        # Container-native CI/CD
    
    # =========================================================================
    # APIs & Protocols
    # =========================================================================
    # How applications communicate
    "rest",         # RESTful APIs (what you build with Express!)
    "graphql",      # Query language for APIs
    "grpc",         # Google's RPC framework
    "soap",         # Legacy web services
    
    # Real-time communication
    "websockets",   # Bidirectional real-time communication
    "socketio",     # Socket.IO library
    "mqtt",         # IoT messaging protocol
    "amqp",         # Message queue protocol
    
    # Message queues
    "rabbitmq",     # Message broker
    "kafka",        # Event streaming platform
    "redis-pubsub", # Redis pub/sub
    "nats",         # Cloud-native messaging
    "zeromq",       # High-performance messaging
    
    # API documentation
    "openapi",      # API specification (formerly Swagger)
    "swagger",      # API documentation
    
    # API testing
    "postman",      # API testing tool
    "insomnia",     # API testing tool
    
    # =========================================================================
    # CSS & Styling
    # =========================================================================
    # Making things look good
    "html",         # Structure of web pages
    "css",          # Styling web pages
    
    # CSS preprocessors
    "sass",         # CSS with superpowers
    "less",         # CSS preprocessor
    "stylus",       # CSS preprocessor
    
    # CSS frameworks
    "tailwindcss",  # Utility-first CSS
    "bootstrap",    # Component CSS framework
    "material-ui",  # React Material Design
    "chakra-ui",    # React component library
    "antd",         # Ant Design
    "bulma",        # CSS framework
    "foundation",   # CSS framework
    "semantic-ui",  # CSS framework
    
    # CSS-in-JS
    "styled-components", # CSS-in-JS for React
    "emotion",      # CSS-in-JS library
    "css-modules",  # Scoped CSS
    
    # CSS tools
    "postcss",      # CSS transformation
    
    # =========================================================================
    # Testing
    # =========================================================================
    # Making sure code works
    # JavaScript testing
    "jest",         # React testing framework
    "mocha",        # JavaScript test framework
    "chai",         # Assertion library
    "jasmine",      # BDD testing
    "karma",        # Test runner
    "ava",          # Concurrent testing
    "vitest",       # Vite-native testing
    
    # Python testing
    "pytest",       # Python testing (used for THIS service!)
    "unittest",     # Python built-in testing
    "nose",         # Python testing
    "robot-framework", # Acceptance testing
    
    # Java testing
    "junit",        # Java testing
    "testng",       # Java testing
    "mockito",      # Java mocking
    
    # Ruby testing
    "rspec",        # Ruby testing
    "minitest",     # Ruby testing
    
    # PHP testing
    "phpunit",      # PHP testing
    
    # .NET testing
    "xunit",        # .NET testing
    "nunit",        # .NET testing
    
    # Testing concepts
    "unit-testing",
    "integration-testing",
    "e2e-testing",
    "tdd",          # Test-Driven Development
    "bdd",          # Behavior-Driven Development
    "selenium",     # Browser automation
    "webdriver",    # Browser automation standard
    
    # =========================================================================
    # AI/ML (Artificial Intelligence / Machine Learning)
    # =========================================================================
    # This service uses some of these for NLP!
    "ml",           # Machine Learning
    "deep-learning",# Neural networks
    "nlp",          # Natural Language Processing (what THIS service does!)
    "cv",           # Computer Vision
    "ai",           # Artificial Intelligence
    
    # ML frameworks
    "tensorflow",   # Google's ML framework
    "pytorch",      # Facebook's ML framework
    "scikit-learn", # Python ML library
    "keras",        # High-level neural network API
    
    # Data science libraries
    "pandas",       # Data manipulation
    "numpy",        # Numerical computing
    "scipy",        # Scientific computing
    "matplotlib",   # Plotting
    "seaborn",      # Statistical visualization
    "plotly",       # Interactive plots
    "jupyter",      # Interactive notebooks
    "anaconda",     # Python distribution for data science
    
    # NLP libraries (used by THIS service!)
    "huggingface",  # Transformers library
    "transformers", # NLP models
    "spacy",        # Industrial NLP (used by THIS service!)
    "nltk",         # NLP toolkit (used by THIS service!)
    "opencv",       # Computer vision
    "yolo",         # Object detection
    
    # LLM & Generative AI
    "llm",          # Large Language Models
    "langchain",    # LLM application framework
    "openai",       # OpenAI API
    "chatgpt",      # ChatGPT
    "bert",         # Google's NLP model
    "gpt",          # OpenAI's language models
    "diffusion",    # Image generation
    "stable-diffusion", # Image generation
    "rag",          # Retrieval Augmented Generation
    
    # =========================================================================
    # Mobile Development
    # =========================================================================
    # Building mobile apps
    "ios",          # Apple mobile
    "android",      # Google mobile
    "flutter",      # Cross-platform UI
    "swiftui",      # Apple's declarative UI
    "jetpack-compose", # Android's declarative UI
    "xamarin",      # .NET cross-platform
    "cordova",      # Hybrid mobile
    "ionic",        # Hybrid mobile framework
    "capacitor",    # Web native bridge
    "expo",         # React Native framework
    
    # =========================================================================
    # Version Control & Collaboration
    # =========================================================================
    # How teams work together
    "git",          # Version control system
    "svn",          # Legacy version control
    "mercurial",    # Distributed version control
    "perforce",     # Enterprise version control
    
    # Project management
    "jira",         # Issue tracking
    "confluence",   # Documentation
    "trello",       # Kanban boards
    "asana",        # Task management
    "monday",       # Work management
    "linear",       # Modern issue tracking
    "notion",       # All-in-one workspace
    
    # Design tools
    "figma",        # UI design
    "sketch",       # Mac UI design
    "adobe-xd",     # Adobe's UI design
    "invision",     # Design collaboration
    "zeplin",       # Design handoff
    
    # =========================================================================
    # Security
    # =========================================================================
    # Keeping apps safe
    # Authentication protocols
    "oauth",        # Authorization framework
    "oauth2",       # OAuth 2.0
    "jwt",          # JSON Web Tokens
    "saml",         # Enterprise SSO
    "ldap",         # Directory services
    "sso",          # Single Sign-On
    "mfa",          # Multi-Factor Authentication
    "2fa",          # Two-Factor Authentication
    
    # Security concepts
    "encryption",
    "ssl",          # Secure Sockets Layer
    "tls",          # Transport Layer Security
    "https",        # Secure HTTP
    "cors",         # Cross-Origin Resource Sharing
    "csrf",         # Cross-Site Request Forgery
    "xss",          # Cross-Site Scripting
    "sql-injection",
    "owasp",        # Security standards
    "penetration-testing",
    "security-audit",
    
    # =========================================================================
    # Architecture & Patterns
    # =========================================================================
    # How to design software
    "microservices",  # THIS service is a microservice!
    "monolith",
    "serverless",
    "event-driven",
    "cqrs",           # Command Query Responsibility Segregation
    "event-sourcing",
    "ddd",            # Domain-Driven Design
    "hexagonal",      # Hexagonal architecture
    "clean-architecture",
    "mvc",            # Model-View-Controller
    "mvvm",           # Model-View-ViewModel
    "mvp",            # Model-View-Presenter
    "oop",            # Object-Oriented Programming
    "fp",             # Functional Programming
    "solid",          # SOLID principles
    "design-patterns",
    "clean-code",
    "data-structures",
    "algorithms",
    
    # =========================================================================
    # Methodologies
    # =========================================================================
    # How teams work
    "agile",
    "scrum",
    "kanban",
    "waterfall",
    "lean",
    "devops",
    "devsecops",
    "sre",            # Site Reliability Engineering
    "gitops",
    "code-review",
    "pair-programming",
    
    # =========================================================================
    # Data & Analytics
    # =========================================================================
    # Working with data at scale
    "big-data",
    "data-engineering",
    "etl",            # Extract, Transform, Load
    "data-pipeline",
    "airflow",        # Workflow orchestration
    "dbt",            # Data transformation
    "snowflake",      # Cloud data warehouse
    "redshift",       # AWS data warehouse
    "bigquery",       # Google data warehouse
    "databricks",     # Unified analytics
    "spark",          # Big data processing
    "hadoop",         # Distributed storage
    "hive",           # Data warehouse on Hadoop
    "presto",         # Distributed SQL
    
    # BI tools
    "tableau",        # Business intelligence
    "power-bi",       # Microsoft BI
    "looker",         # Google BI
    "metabase",       # Open-source BI
    "superset",       # Apache BI
    
    # =========================================================================
    # Messaging & Queues
    # =========================================================================
    # Async communication between services
    "message-queue",
    "event-bus",
    "pubsub",
    "sns",            # AWS Simple Notification Service
    "sqs",            # AWS Simple Queue Service
    "kinesis",        # AWS streaming
    "eventbridge",    # AWS event bus
}


# =============================================================================
# NOISE PATTERNS: Regex Patterns to Filter Out Generic Phrases
# =============================================================================
# 
# WHAT IS THIS?
# -------------
# A list of regex patterns that match generic phrases that AREN'T skills.
# RAKE and YAKE often extract these, so we need to filter them out.
# 
# WHY REGEX?
# ----------
# Some noise phrases have variations:
# - "developed", "developing", "development"
# - "working on", "worked with", "works for"
# 
# Regex patterns can match all variations with one pattern.
# 
# PYTHON REGEX SYNTAX (similar to JavaScript):
# --------------------------------------------
# ^ = start of string
# $ = end of string
# \s = whitespace
# * = zero or more
# + = one or more
# ? = zero or one
# (?:...) = non-capturing group
# 
# EXAMPLES OF WHAT THESE CATCH:
# ----------------------------
# "developed using" ← not a skill
# "experience with" ← not a skill
# "looking for" ← not a skill
# "strong in" ← not a skill

NOISE_PATTERNS = [
    # =========================================================================
    # Action Verb Phrases (common in job descriptions)
    # =========================================================================
    # These are phrases that describe what you DO, not skills you HAVE
    
    # "developed using", "developing with", "development for"
    r"^(developed?|developing|development)\s+(using|with|for|in)?\s*$",
    
    # "working on", "worked with", "work for"
    r"^(work(?:ed|ing)?)\s+(on|with|for|in)?\s*$",
    
    # "use this", "used the", "using"
    r"^(us(?:e|ed|ing))\s+(this|these|the|a)?\s*$",
    
    # "experience with", "experienced in"
    r"^(experience(?:d)?)\s+(with|in|using)?\s*$",
    
    # "building with", "built using"
    r"^(build(?:ing|t)?)\s+(with|using|for)?\s*$",
    
    # "creating with", "created using"
    r"^(creat(?:e|ed|ing))\s+(with|using|for)?\s*$",
    
    # "implementing with", "implemented using"
    r"^(implement(?:ed|ing)?)\s+(with|using|for)?\s*$",
    
    # "designing with", "designed using"
    r"^(design(?:ed|ing)?)\s+(with|using|for)?\s*$",
    
    # =========================================================================
    # Generic Job Description Phrases
    # =========================================================================
    # Common phrases that appear in job descriptions but aren't skills
    
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
    
    # =========================================================================
    # Common English Words (stopwords that might slip through)
    # =========================================================================
    # Articles, prepositions, conjunctions, etc.
    r"^(the|a|an|and|or|but|in|on|at|to|for|of|with|by)$",
    r"^(is|are|was|were|be|been|being|have|has|had)$",
    r"^(will|would|could|should|can|may|might|must)$",
    r"^(this|that|these|those|it|its|their|our|your)$",
    r"^(what|when|where|why|how|who|which)$",
    r"^(new|old|good|bad|high|low|big|small)$",
    r"^(first|last|next|previous|other|another)$",
]

# =============================================================================
# Compile Patterns for Efficiency
# =============================================================================
# Pre-compiling regex patterns is faster when matching many times.
# We compile once at import time, then reuse the compiled objects.
# 
# re.IGNORECASE makes patterns case-insensitive
# 
# JavaScript equivalent:
#   const COMPILED_PATTERNS = NOISE_PATTERNS.map(p => new RegExp(p, 'i'));
COMPILED_NOISE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]


# =============================================================================
# ====================== HELPER FUNCTIONS =====================================
# =============================================================================
# These functions are the core tools for skill processing.
# They're imported and used by app.py and resume_tailor.py.


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name to its canonical form.
    
    WHAT THIS DOES:
    ---------------
    Takes any variant of a skill name and returns the standard version.
    
    Examples:
    - "React.js" → "react"
    - "Node JS" → "nodejs"
    - "  Python3  " → "python"
    - "DOCKER" → "docker"
    
    WHY THIS IS IMPORTANT:
    ---------------------
    Without normalization, "React" and "React.js" would be treated as
    different skills. A resume with "React" wouldn't match a job
    requiring "React.js", even though they're the same thing!
    
    HOW IT WORKS:
    -------------
    1. Convert to lowercase and strip whitespace
    2. Remove special characters from start/end
    3. Check if it's an alias and convert if so
    4. Return the normalized skill
    
    Args:
        skill: Raw skill string from extraction
               Could be "React.js", "  react  ", "REACT", etc.
    
    Returns:
        Normalized canonical skill name (lowercase, clean)
        Returns empty string if input is empty/None
    
    Python Syntax Notes:
    -------------------
    - 'skill: str' = type hint, parameter should be string
    - '-> str' = return type hint, returns string
    - 'if not skill' = checks if skill is None or empty (falsy check)
    
    JavaScript equivalent:
        function normalizeSkill(skill) {
            if (!skill) return '';
            let normalized = skill.toLowerCase().trim();
            normalized = normalized.replace(/^[^\w]+|[^\w]+$/g, '');
            return SKILL_ALIASES[normalized] || normalized;
        }
    """
    # Handle None or empty input
    # 'not skill' is True if skill is None, empty string, etc.
    if not skill:
        return ""
    
    # Convert to lowercase and strip leading/trailing whitespace
    # Python: "  REACT.JS  ".lower().strip() → "react.js"
    # JavaScript: "  REACT.JS  ".toLowerCase().trim() → "react.js"
    normalized = skill.lower().strip()
    
    # Remove special characters from start and end, but keep internal ones
    # This handles cases like ".react." → "react"
    # 
    # re.sub(pattern, replacement, string) = string.replace(pattern, replacement)
    # 
    # Pattern breakdown:
    # ^[^\w]+ = one or more non-word chars at start
    # | = OR
    # [^\w]+$ = one or more non-word chars at end
    # 
    # This keeps internal chars like "c++" or "c#" intact
    normalized = re.sub(r'^[^\w]+|[^\w]+$', '', normalized)
    
    # Check if this is an alias that should be converted
    # Python: dict.get(key) returns value or None (like dict[key] but safe)
    # JavaScript: SKILL_ALIASES[normalized] || normalized
    if normalized in SKILL_ALIASES:
        return SKILL_ALIASES[normalized]
    
    # Return the normalized skill (not an alias, just cleaned up)
    return normalized


def is_valid_skill(skill: str) -> bool:
    """
    Check if a normalized skill is in the whitelist.
    
    WHAT THIS DOES:
    ---------------
    Simple membership check: is this term a real skill?
    
    WHY THIS IS IMPORTANT:
    ---------------------
    This is the GATE that keeps garbage out.
    - is_valid_skill("react") → True ✓
    - is_valid_skill("developed using") → False ✗
    - is_valid_skill("experience with") → False ✗
    
    HOW TO USE:
    -----------
    1. First normalize the skill: normalized = normalize_skill(raw)
    2. Then check validity: if is_valid_skill(normalized): keep_it()
    
    Args:
        skill: Normalized skill name (should already be lowercase, clean)
    
    Returns:
        True if skill is in whitelist, False otherwise
    
    Python Syntax Note:
    ------------------
    In Python, 'in' operator checks membership:
    - 'skill in SKILL_WHITELIST' = SKILL_WHITELIST.has(skill) in JS
    - Returns True/False
    - O(1) time complexity for sets
    
    JavaScript equivalent:
        const isValidSkill = (skill) => SKILL_WHITELIST.has(skill);
    """
    return skill in SKILL_WHITELIST


def is_noise(text: str) -> bool:
    """
    Check if text matches any noise pattern.
    
    WHAT THIS DOES:
    ---------------
    Identifies generic phrases that RAKE/YAKE extract but aren't skills.
    
    Examples of noise (returns True):
    - "developed using" → True (not a skill)
    - "experience with the" → True (not a skill)
    - "looking for" → True (not a skill)
    - "42" → True (just a number)
    - "" → True (empty)
    
    Examples of non-noise (returns False):
    - "react" → False (valid skill candidate)
    - "python developer" → False (contains skill, needs further processing)
    
    WHY THIS IS NEEDED:
    ------------------
    Before checking is_valid_skill(), we first filter out obvious garbage.
    This is faster than normalizing and checking every phrase.
    
    Args:
        text: Raw text to check (before normalization)
    
    Returns:
        True if text is noise (should be discarded), False otherwise
    """
    # Clean and lowercase the text
    text = text.strip().lower()
    
    # Too short (likely a single letter or empty)
    # or too long (not a skill name, probably a sentence)
    if len(text) < 2 or len(text) > 50:
        return True
    
    # Contains only numbers (like "2024" or "5")
    # .isdigit() returns True if all characters are digits
    # JavaScript: /^\d+$/.test(text)
    if text.isdigit():
        return True
    
    # Check against noise patterns
    # If ANY pattern matches, it's noise
    for pattern in COMPILED_NOISE_PATTERNS:
        # .match() checks if pattern matches at the START of the string
        # (our patterns use ^ and $ for full string match)
        if pattern.match(text):
            return True
    
    # Passed all noise checks
    return False


def filter_and_normalize_skills(raw_keywords: List[str]) -> List[str]:
    """
    Filter and normalize a list of raw keywords to valid skills.
    
    THIS IS THE MAIN FUNCTION that ties everything together!
    
    WHAT IT DOES (pipeline):
    -----------------------
    1. For each raw keyword from RAKE/YAKE:
       a. Check if it's noise → skip if yes
       b. Normalize it (lowercase, alias lookup)
       c. Check if it's a valid skill → keep if yes
       d. Add to set (deduplicates automatically)
    2. Return list of clean, valid skills
    
    EXAMPLE:
    --------
    Input:  ["React.js", "react", "developed using", "Node.js", "experience with"]
    
    Step 1: "React.js"
      - Not noise
      - Normalized: "react"
      - Valid: Yes (in whitelist)
      - Keep ✓
    
    Step 2: "react"
      - Not noise
      - Normalized: "react"
      - Valid: Yes
      - Already in set, no duplicate ✓
    
    Step 3: "developed using"
      - Is noise! (matches pattern)
      - Skip ✗
    
    Step 4: "Node.js"
      - Not noise
      - Normalized: "nodejs"
      - Valid: Yes
      - Keep ✓
    
    Step 5: "experience with"
      - Is noise!
      - Skip ✗
    
    Output: ["react", "nodejs"]
    
    Args:
        raw_keywords: List of raw keywords from RAKE/YAKE/spaCy
    
    Returns:
        List of clean, normalized, validated skills (no duplicates)
    
    Python Syntax Notes:
    -------------------
    - List[str] = array of strings (type hint)
    - set() = empty set (like new Set() in JS)
    - set.add(item) = adds item to set
    - list(set) = converts set to list
    """
    # Use a set to automatically handle deduplication
    # Sets only store unique values
    valid_skills = set()
    
    # Process each raw keyword
    for keyword in raw_keywords:
        # Step 1: Skip if it's obviously noise
        if is_noise(keyword):
            continue
        
        # Step 2: Normalize the keyword
        normalized = normalize_skill(keyword)
        
        # Step 3: Check if it's a valid skill
        if is_valid_skill(normalized):
            # Step 4: Add to set (duplicates automatically ignored)
            valid_skills.add(normalized)
    
    # Convert set to list and return
    return list(valid_skills)


def extract_skills_from_text(text: str) -> Set[str]:
    """
    Extract all valid skills from raw text using direct pattern matching.
    
    WHAT THIS DOES:
    ---------------
    Searches the text directly for each skill in our whitelist.
    This catches skills that RAKE/YAKE might miss.
    
    WHY THIS IS NEEDED:
    ------------------
    Sometimes skills appear in unusual contexts that confuse RAKE/YAKE:
    - "Technologies: React, Node.js, MongoDB" 
    - "Stack: (React/Redux/Node)"
    - "We use react.js and node"
    
    By directly searching for each whitelist skill, we catch edge cases.
    
    HOW IT WORKS:
    -------------
    1. Convert text to lowercase
    2. For each skill in whitelist, search for it in text
    3. For each alias, also search (convert to canonical form)
    4. Only match complete words (not partial matches)
    
    Word boundaries prevent false positives:
    - "react" matches "react" in "We use react for UI"
    - "react" does NOT match "react" in "unreactive compounds"
    
    Args:
        text: Raw job description or resume text
    
    Returns:
        Set of normalized skills found in text
    
    Python Syntax Note:
    ------------------
    -> Set[str] means this function returns a Set of strings
    We return a Set (not List) because callers often need to do
    set operations like intersection and union.
    """
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Set to store found skills (no duplicates)
    found_skills = set()
    
    # =========================
    # Search for whitelist skills
    # =========================
    for skill in SKILL_WHITELIST:
        # Escape special regex characters in the skill name
        # This handles skills like "c++" or "c#" that have regex special chars
        # re.escape("c++") → "c\\+\\+"
        skill_pattern = re.escape(skill)
        
        # Build pattern to match whole word only
        # (?:^|[\s,;:.\-_/(]) = start of string OR separator character
        # skill_pattern = the skill itself
        # (?:[\s,;:.\-_/)]|$) = separator character OR end of string
        # 
        # This prevents matching "javascript" inside "notjavascripty"
        pattern = r'(?:^|[\s,;:.\-_/(])' + skill_pattern + r'(?:[\s,;:.\-_/)]|$)'
        
        # re.search finds the pattern anywhere in the string
        # Returns a match object if found, None if not
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    
    # =========================
    # Also search for aliases
    # =========================
    # Someone might write "react.js" in their text
    # We want to find it and convert to "react"
    for alias, canonical in SKILL_ALIASES.items():
        alias_pattern = re.escape(alias)
        pattern = r'(?:^|[\s,;:.\-_/(])' + alias_pattern + r'(?:[\s,;:.\-_/)]|$)'
        
        if re.search(pattern, text_lower):
            # Store the canonical form, not the alias
            found_skills.add(canonical)
    
    return found_skills


def get_skill_match_score(resume_skills: Set[str], job_skills: Set[str]) -> dict:
    """
    Calculate match score based on skill overlap.
    
    THIS IS THE HEART OF THE MATCHING ALGORITHM!
    
    WHAT THIS DOES:
    ---------------
    Compares skills from a resume against skills from a job description
    and calculates a percentage match score.
    
    THE MATH:
    ---------
    score = (matched skills / job skills) × 100
    
    Example:
    - Job requires: react, nodejs, mongodb, aws, docker (5 skills)
    - Resume has: react, nodejs, python (3 skills)
    - Matched: react, nodejs (2 skills)
    - Score: 2/5 × 100 = 40%
    
    WHY THIS IS BETTER THAN BEFORE:
    ------------------------------
    Before (problematic):
    - Used substring matching: "react" in "react.js developer" counted
    - "React" and "React.js" counted as TWO separate matches
    - Generic phrases inflated the count
    
    After (this function):
    - Uses SET INTERSECTION for precise matching
    - Both sides are normalized (React = React.js = react)
    - No duplicates, no noise, accurate scores
    
    Args:
        resume_skills: Set of normalized skills from resume
        job_skills: Set of normalized skills from job description
    
    Returns:
        Dictionary with:
        - score: Percentage of job skills found in resume (0-100)
        - matched: List of skills in BOTH (what you have that they want)
        - missing: List of job skills NOT in resume (skill gap)
        - extra: List of resume skills NOT in job (bonus skills)
    
    Python Syntax Notes:
    -------------------
    - & = set intersection (items in BOTH sets)
    - - = set difference (items in first but not second)
    - round(number, digits) = rounds to specified decimal places
    
    JavaScript equivalent:
        const matched = new Set([...resume_skills].filter(x => job_skills.has(x)));
        const missing = new Set([...job_skills].filter(x => !resume_skills.has(x)));
        const extra = new Set([...resume_skills].filter(x => !job_skills.has(x)));
    """
    # Handle edge case: no job skills
    if not job_skills:
        return {
            "score": 0,
            "matched": [],
            "missing": [],
            "extra": list(resume_skills)
        }
    
    # Set intersection: skills that appear in BOTH sets
    # Python:     matched = resume_skills & job_skills
    # JavaScript: matched = [...resume_skills].filter(x => job_skills.has(x))
    matched = resume_skills & job_skills
    
    # Set difference: job skills that are NOT in resume (the gap)
    # These are skills from the job that you're missing
    missing = job_skills - resume_skills
    
    # Set difference: resume skills that are NOT in job
    # These are "bonus" skills you have that aren't required
    # Could be valuable ("Nice to have Python even though not listed!")
    extra = resume_skills - job_skills
    
    # Calculate score as percentage of job skills matched
    # Example: matched 3 of 5 job skills = 60%
    # 
    # We divide by job_skills count because we want to know:
    # "How many of their requirements do I meet?"
    # 
    # Alternative interpretation would be dividing by resume_skills:
    # "How many of my skills are relevant?" (not used here)
    score = (len(matched) / len(job_skills)) * 100
    
    # Build and return the result dictionary
    # sorted() returns a sorted list (alphabetically)
    # round(score, 1) rounds to 1 decimal place (e.g., 66.66666 → 66.7)
    return {
        "score": round(score, 1),
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing)),
        "extra": sorted(list(extra))
    }
