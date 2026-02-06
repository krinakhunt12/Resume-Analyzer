# ATS Resume Analyzer

A comprehensive Python-based ATS (Applicant Tracking System) Resume Analyzer that helps job seekers optimize their resumes for better visibility in ATS systems.

## 🌟 Features

- **Multi-format Support**: Analyze PDF and DOCX resume files
- **Intelligent Parsing**: Extract contact info, skills, education, and experience
- **Job Description Matching**: Compare resume against job descriptions
- **ATS Compatibility Check**: Verify if resume format is ATS-friendly
- **Detailed Scoring**: Get scores for keyword match, skills, format, and completeness
- **Multiple Output Formats**: Generate reports in Text, JSON, and Excel formats
- **Web Interface**: Beautiful Flask-based web UI for easy analysis
- **Command Line Interface**: Quick analysis via terminal
- **Comprehensive Reports**: Detailed analysis with recommendations

## 📁 Project Structure

```
ats_resume_analyzer/
│
├── main.py                      # CLI application
├── app.py                       # Flask web application
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── config/
│   └── config.py               # Configuration and skill database
│
├── src/
│   ├── text_extractor.py       # Extract text from PDF/DOCX
│   ├── resume_parser.py        # Parse resume and extract information
│   ├── ats_analyzer.py         # Core analysis engine
│   └── report_generator.py     # Generate reports
│
├── templates/
│   └── index.html              # Web interface template
│
├── data/
│   ├── resumes/                # Place resume files here
│   ├── job_descriptions/       # Place job description files here
│   ├── results/                # Generated reports saved here
│   └── uploads/                # Temporary uploads (web interface)
│
└── tests/
    └── (unit tests)
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download

```bash
# If you have this as a git repo
git clone <repository-url>
cd ats_resume_analyzer

# Or simply navigate to the folder if you have the files
cd ats_resume_analyzer
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download spaCy Model (Required)

```bash
python -m spacy download en_core_web_sm
```

## 💻 Usage

### Option 1: Web Interface (Recommended)

1. **Start the Flask server:**

```bash
python app.py
```

2. **Open your browser and navigate to:**

```
http://localhost:5000
```

3. **Upload your resume:**
   - Choose your resume file (PDF or DOCX)
   - Optionally upload a job description or paste it
   - Click "Analyze Resume"
   - View results and download reports

### Option 2: Command Line Interface

**Basic Analysis (Resume Only):**

```bash
python main.py --resume data/resumes/john_doe.pdf
```

**Analysis with Job Description:**

```bash
python main.py --resume data/resumes/john_doe.pdf --jd data/job_descriptions/software_engineer.pdf
```

**Specify Output Format:**

```bash
# Generate only JSON report
python main.py --resume data/resumes/john_doe.pdf --format json

# Generate only Excel report
python main.py --resume data/resumes/john_doe.pdf --format excel

# Generate all formats (default)
python main.py --resume data/resumes/john_doe.pdf --format all
```

**Help:**

```bash
python main.py --help
```

## 📊 Analysis Metrics

The analyzer evaluates resumes based on:

1. **Keyword Match (30%)**: How well resume keywords match the job description
2. **Skills Match (25%)**: Percentage of required skills found in resume
3. **Format ATS-Friendly (10%)**: Whether format is compatible with ATS systems
4. **Completeness (5%)**: Presence of all important sections

### Score Ratings:

- **80-100**: Excellent - Ready to submit
- **60-79**: Good - Minor improvements needed
- **40-59**: Fair - Significant improvements recommended
- **0-39**: Needs Improvement - Major revisions required

## 🎯 What Gets Analyzed

### Contact Information
- Email addresses
- Phone numbers
- LinkedIn profile
- GitHub profile

### Skills
- **Technical Skills**:
  - Programming languages (Python, Java, JavaScript, etc.)
  - Web technologies (React, Angular, Node.js, etc.)
  - Databases (MySQL, MongoDB, PostgreSQL, etc.)
  - Cloud platforms (AWS, Azure, GCP, etc.)
  - Data science tools (TensorFlow, PyTorch, etc.)
  - Development tools (Git, Docker, Jenkins, etc.)

- **Soft Skills**:
  - Leadership, Communication, Teamwork
  - Problem Solving, Critical Thinking
  - And more...

### Resume Structure
- Professional Summary
- Work Experience
- Education
- Skills
- Projects
- Certifications
- Achievements

### Format Check
- Presence of required sections
- Word count appropriateness
- Special characters usage
- ATS compatibility

## 📝 Output Reports

### 1. Text Report (.txt)
- Human-readable detailed analysis
- All scores and metrics
- Strengths and recommendations
- Complete skill breakdown

### 2. JSON Report (.json)
- Machine-readable format
- Easy integration with other tools
- Complete data structure

### 3. Excel Report (.xlsx)
- Multiple sheets:
  - Summary
  - Detailed Scores
  - Skills Analysis
  - Recommendations
- Easy to share and present

## 🛠️ Configuration

Customize the analyzer by editing `config/config.py`:

- **Add/Remove Skills**: Modify `TECHNICAL_SKILLS` and `SOFT_SKILLS`
- **Adjust Scoring Weights**: Change `SCORING_WEIGHTS`
- **Modify Score Thresholds**: Update `SCORE_THRESHOLDS`
- **Customize Section Headers**: Edit `SECTION_HEADERS`

## 🔧 Troubleshooting

### Common Issues

**1. "Module not found" error:**
```bash
# Make sure you're in the virtual environment
# Re-install dependencies
pip install -r requirements.txt
```

**2. "spaCy model not found":**
```bash
python -m spacy download en_core_web_sm
```

**3. "File not found" error:**
- Ensure file paths are correct
- Check file permissions
- Verify file format is supported (PDF or DOCX)

**4. Flask app not starting:**
```bash
# Check if port 5000 is available
# Try a different port:
python app.py  # Then modify the port in app.py if needed
```

## 📈 Future Enhancements

Potential features for future versions:
- [ ] Support for more file formats (TXT, HTML)
- [ ] AI-powered content suggestions
- [ ] Resume template generator
- [ ] LinkedIn profile integration
- [ ] Batch processing multiple resumes
- [ ] Machine learning-based scoring
- [ ] Industry-specific analysis
- [ ] ATS simulator
- [ ] Resume comparison tool
- [ ] Email integration for reports

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This tool provides suggestions and analysis based on common ATS practices. Results may vary depending on specific ATS systems used by employers. Always review and customize your resume for each application.

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## 🙏 Acknowledgments

- Built with Python, Flask, spaCy, and other open-source libraries
- Inspired by the need to help job seekers succeed in their applications

---

**Happy Job Hunting! 🎉**