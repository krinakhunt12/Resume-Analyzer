"""
Configuration file for ATS Resume Analyzer
Contains skills database, keywords, and settings
"""

# Technical Skills Database
TECHNICAL_SKILLS = {
    'programming_languages': [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Swift',
        'Kotlin', 'Go', 'Rust', 'TypeScript', 'R', 'MATLAB', 'Scala', 'Perl'
    ],
    'web_technologies': [
        'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django',
        'Flask', 'Spring', 'ASP.NET', 'Express.js', 'Next.js', 'Bootstrap',
        'Tailwind CSS', 'jQuery', 'Redux', 'GraphQL', 'REST API', 'AJAX'
    ],
    'databases': [
        'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'SQL Server', 'SQLite',
        'Redis', 'Cassandra', 'DynamoDB', 'Firebase', 'MariaDB', 'Elasticsearch'
    ],
    'cloud_platforms': [
        'AWS', 'Azure', 'Google Cloud', 'GCP', 'Heroku', 'DigitalOcean',
        'IBM Cloud', 'Oracle Cloud', 'Kubernetes', 'Docker', 'Jenkins'
    ],
    'data_science': [
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
        'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'NLP',
        'Computer Vision', 'OpenCV', 'NLTK', 'SpaCy', 'Data Analysis',
        'Statistics', 'Data Visualization', 'Big Data', 'Hadoop', 'Spark'
    ],
    'tools': [
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'JIRA', 'Confluence',
        'Trello', 'Slack', 'VS Code', 'IntelliJ', 'Eclipse', 'PyCharm',
        'Postman', 'Swagger', 'Selenium', 'JUnit', 'pytest', 'Mocha'
    ],
    'methodologies': [
        'Agile', 'Scrum', 'Kanban', 'DevOps', 'CI/CD', 'TDD', 'BDD',
        'Microservices', 'RESTful', 'API Development', 'MVC', 'MVVM'
    ]
}

# Soft Skills
SOFT_SKILLS = [
    'Leadership', 'Communication', 'Teamwork', 'Problem Solving',
    'Critical Thinking', 'Time Management', 'Adaptability', 'Collaboration',
    'Project Management', 'Analytical', 'Creative', 'Detail-oriented',
    'Self-motivated', 'Multitasking', 'Decision Making', 'Negotiation',
    'Presentation', 'Interpersonal', 'Organizational', 'Strategic Planning'
]

# Education Keywords
EDUCATION_KEYWORDS = [
    'Bachelor', 'Master', 'PhD', 'Doctorate', 'B.Tech', 'M.Tech', 'B.S.',
    'M.S.', 'MBA', 'B.E.', 'M.E.', 'BCA', 'MCA', 'Diploma', 'Associate',
    'Computer Science', 'Engineering', 'Information Technology', 'Software',
    'University', 'College', 'Institute', 'School', 'Degree', 'GPA', 'CGPA'
]

# Experience Keywords
EXPERIENCE_KEYWORDS = [
    'experience', 'work', 'employment', 'position', 'role', 'job',
    'intern', 'internship', 'developer', 'engineer', 'analyst', 'manager',
    'consultant', 'specialist', 'coordinator', 'lead', 'senior', 'junior',
    'associate', 'principal', 'architect', 'administrator', 'designer'
]

# Section Headers
SECTION_HEADERS = {
    'contact': ['contact', 'personal information', 'personal details'],
    'summary': ['summary', 'objective', 'profile', 'about', 'professional summary'],
    'experience': ['experience', 'work experience', 'employment', 'work history', 'professional experience'],
    'education': ['education', 'academic', 'qualification', 'educational background'],
    'skills': ['skills', 'technical skills', 'core competencies', 'expertise', 'technologies'],
    'projects': ['projects', 'academic projects', 'personal projects'],
    'certifications': ['certifications', 'certificates', 'licenses', 'credentials'],
    'achievements': ['achievements', 'awards', 'honors', 'accomplishments']
}

# ATS-Friendly Format Checks
ATS_FORMAT_RULES = {
    'max_pages': 2,
    'recommended_font_size': (10, 12),
    'avoid_elements': ['tables', 'text boxes', 'headers', 'footers', 'images'],
    'recommended_fonts': ['Arial', 'Calibri', 'Helvetica', 'Times New Roman', 'Georgia']
}

# Action Verbs for Impact
ACTION_VERBS = [
    'Achieved', 'Adapted', 'Administered', 'Advised', 'Analyzed', 'Arranged', 'Assessed', 'Assisted',
    'Attained', 'Budgeted', 'Built', 'Calculated', 'Centralized', 'Collaborated', 'Communicated', 'Completed',
    'Composed', 'Condensed', 'Conducted', 'Constructed', 'Consulted', 'Contracted', 'Contributed', 'Coordinated',
    'Created', 'Cultivated', 'Debugged', 'Decided', 'Defined', 'Delegated', 'Delivered', 'Designed',
    'Detected', 'Developed', 'Devised', 'Directed', 'Discovered', 'Distributed', 'Documented', 'Drafted',
    'Earned', 'Edited', 'Educated', 'Eliminated', 'Enabled', 'Enacted', 'Encouraged', 'Engineered',
    'Enhanced', 'Established', 'Evaluated', 'Executed', 'Expanded', 'Expedited', 'Facilitated', 'Finalized',
    'Forecasted', 'Formulated', 'Generated', 'Guided', 'Identified', 'Implemented', 'Improved', 'Increased',
    'Influenced', 'Informed', 'Initiated', 'Inspected', 'Installed', 'Instituted', 'Instructed', 'Integrated',
    'Interpreted', 'Introduced', 'Invented', 'Investigated', 'Launched', 'Led', 'Maintained', 'Managed',
    'Marketed', 'Measured', 'Mediated', 'Mentored', 'Merged', 'Minimized', 'Modeled', 'Moderated',
    'Monitored', 'Motivated', 'Negotiated', 'Operated', 'Optimized', 'Orchestrated', 'Organized', 'Oversaw',
    'Performed', 'Pioneered', 'Planned', 'Prepared', 'Presented', 'Prioritized', 'Processed', 'Produced',
    'Programmed', 'Projected', 'Promoted', 'Proposed', 'Provided', 'Published', 'Purchased', 'Recommended',
    'Reconciled', 'Recorded', 'Recruited', 'Redesigned', 'Reduced', 'Refined', 'Regulated', 'Rehabilitated',
    'Remodeled', 'Repaired', 'Represented', 'Researched', 'Resolved', 'Restored', 'Restructured', 'Retrieved',
    'Reviewed', 'Revised', 'Scheduled', 'Screened', 'Selected', 'Served', 'Simplified', 'Solved',
    'Sparked', 'Spearheaded', 'Standardized', 'Stimulated', 'Streamlined', 'Summarized', 'Supervised', 'Supported',
    'Surveyed', 'Synthesized', 'Systematized', 'Tabulated', 'Taught', 'Tested', 'Traced', 'Trained',
    'Transformed', 'Translated', 'Updated', 'Upgraded', 'Validated', 'Verified', 'Visualized'
]

# Common Stop Words to ignore during analysis
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'if', 'in', 'into', 'is', 'it',
    'no', 'not', 'of', 'on', 'or', 'such', 'that', 'the', 'their', 'then', 'there', 'these',
    'they', 'this', 'to', 'was', 'will', 'with', 'who', 'whom', 'whose', 'which', 'where', 'when'
}

# ATS Pitfalls to check
ATS_PITFALLS = [
    'graphics', 'images', 'icons', 'columns', 'tables', 'headers', 'footers', 'boxes',
    'shading', 'progress bars', 'infographics', 'fancy fonts'
]

# Scoring Weights
SCORING_WEIGHTS = {
    'keyword_match': 0.25,
    'skills_match': 0.20,
    'experience_relevance': 0.15,
    'impact_score': 0.15,      # Action verbs and quantifiable metrics
    'education': 0.10,
    'format_ats_friendly': 0.10,
    'completeness': 0.05
}

# Minimum scores for recommendations
SCORE_THRESHOLDS = {
    'excellent': 80,
    'good': 60,
    'fair': 40,
    'poor': 0
}