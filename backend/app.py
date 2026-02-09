"""
Flask Web Application
Web interface for ATS Resume Analyzer
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.text_extractor import TextExtractor
from src.resume_parser import ResumeParser
from src.ats_analyzer import ATSAnalyzer
from src.report_generator import ReportGenerator

import tempfile

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Use system temp directory for transient data
base_temp = os.path.join(tempfile.gettempdir(), 'resume_analyzer')
os.makedirs(base_temp, exist_ok=True)

app.config['UPLOAD_FOLDER'] = os.path.join(base_temp, 'uploads')
app.config['RESULTS_FOLDER'] = os.path.join(base_temp, 'results')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'doc'}

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Initialize components
extractor = TextExtractor()
parser = ResumeParser()
analyzer = ATSAnalyzer()
report_generator = ReportGenerator(output_dir=app.config['RESULTS_FOLDER'])


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Analyze resume endpoint"""
    try:
        # Check if resume file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        resume_file = request.files['resume']
        
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(resume_file.filename):
            return jsonify({'error': 'Invalid file format. Please upload PDF or DOCX'}), 400
        
        # Save resume file
        resume_filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        resume_file.save(resume_path)
        
        # Extract resume text
        resume_text = extractor.extract(resume_path)
        
        # Delete uploaded resume after extraction
        if os.path.exists(resume_path):
            os.remove(resume_path)
        
        # Handle job description
        job_description = ""
        if 'job_description' in request.files:
            jd_file = request.files['job_description']
            if jd_file.filename != '' and allowed_file(jd_file.filename):
                jd_filename = secure_filename(jd_file.filename)
                jd_path = os.path.join(app.config['UPLOAD_FOLDER'], jd_filename)
                jd_file.save(jd_path)
                job_description = extractor.extract(jd_path)
                
                # Delete uploaded JD after extraction
                if os.path.exists(jd_path):
                    os.remove(jd_path)
        elif 'job_description_text' in request.form:
            job_description = request.form['job_description_text']
        
        # Parse and analyze
        parsed_resume = parser.parse(resume_text)
        analysis_results = analyzer.analyze(resume_text, parsed_resume, job_description)
        
        # Generate text report content directly without saving to disk
        _, report_text = report_generator.generate_text_report(
            analysis_results, parsed_resume, filename=None
        )
        
        # Prepare the recruiter-style structured insights
        skills = parsed_resume.get('skills', {})
        tech_skills = skills.get('technical', {})
        
        # 1. Candidate Details
        experience_data = parsed_resume.get('experience', {})
        years_list = experience_data.get('years_mentioned', [])
        total_years = years_list[0] if years_list else "Not explicitly stated"
        
        contact_info = parsed_resume.get('contact_info', {})
        emails = contact_info.get('emails', [])
        phones = contact_info.get('phones', [])
        
        candidate_details = {
            'name': parsed_resume.get('name', 'Not Found'),
            'email': emails[0] if emails else "Not Found",
            'phone': phones[0] if phones else "Not Found",
            'total_years_experience': total_years
        }
        
        # 2. Key Sections
        key_sections = {
            'skills': {
                'technical': tech_skills.get('programming_languages', []) + tech_skills.get('web_technologies', []),
                'tools': tech_skills.get('tools', []) + tech_skills.get('cloud_platforms', []),
                'soft_skills': skills.get('soft', [])
            },
            'work_experience_summary': " - ".join(experience_data.get('detected_titles', [])[:5]),
            'education': parsed_resume.get('education', {}).get('degrees', [])
        }
        
        # 3. Resume Quality
        resume_quality = {
            'strengths': analysis_results.get('strengths', []),
            'weaknesses': [rec for rec in analysis_results.get('recommendations', []) if "URGENT" in rec],
            'missing_or_unclear_information': [s for s, present in parsed_resume.get('sections', {}).items() if not present]
        }
        
        # 4. ATS Compatibility
        ats_compatibility = {
            'score': analysis_results['overall_score'],
            'reasons': [f"Rating: {analysis_results['rating']}"],
            'formatting_issues': analysis_results.get('format_check', {}).get('issues', []),
            'keyword_issues': analysis_results.get('keyword_match', {}).get('missing_keywords', []) if 'keyword_match' in analysis_results else []
        }
        
        # 5. Improvement Suggestions
        roadmap = analysis_results.get('career_roadmap', {})
        improvement_suggestions = {
            'skills_to_add': [s for s in (analysis_results.get('skills_match', {}).get('missing_skills', []) or [])[:10]],
            'resume_formatting_improvements': [rec for rec in analysis_results.get('recommendations', []) if "format" in rec.lower()],
            'content_improvements': roadmap.get('steps', [])
        }
        
        # Prepare reports for compatibility (in-memory names)
        reports = {
            'text': f"{resume_filename.rsplit('.', 1)[0]}_report.txt",
            'json': f"{resume_filename.rsplit('.', 1)[0]}_report.json",
            'excel': f"{resume_filename.rsplit('.', 1)[0]}_report.xlsx"
        }

        # Final JSON Response (Combined for compatibility and new requirements)
        response_data = {
            'success': True,
            'results': {
                'overall_score': analysis_results['overall_score'],
                'rating': analysis_results['rating'],
                'scores': analysis_results['scores'],
                'strengths': analysis_results.get('strengths', []),
                'recommendations': analysis_results.get('recommendations', []),
                'candidate_name': parsed_resume.get('name', 'Not Found'),
                'contact_info': parsed_resume.get('contact_info', {}),
                'skills': {
                    'technical': len(parsed_resume.get('skills', {}).get('all_technical', [])),
                    'soft': len(parsed_resume.get('skills', {}).get('soft', []))
                },
                'sections': parsed_resume.get('sections', {}),
                'format_check': analysis_results.get('format_check', {}),
                'impact_analysis': analysis_results.get('impact_analysis', {}),
                'readability': analysis_results.get('readability', {}),
                'tone_analysis': analysis_results.get('tone_analysis', {}),
                'career_analysis': analysis_results.get('career_analysis', {}),
                'link_validation': analysis_results.get('link_validation', []),
                'role_suitability': analysis_results.get('role_suitability', []),
                'career_roadmap': analysis_results.get('career_roadmap', {}),
                'full_report': report_text
            },
            'reports': reports,
            'recruiter_insights': {
                'candidate_details': candidate_details,
                'key_sections': key_sections,
                'resume_quality': resume_quality,
                'ats_compatibility': ats_compatibility,
                'improvement_suggestions': improvement_suggestions
            }
        }
        
        print(f"✅ Analysis complete for: {candidate_details['name']}")
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    """Download report file"""
    try:
        filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Generate a tailored cover letter"""
    try:
        data = request.json
        name = data.get('name', 'Applicant')
        skills = data.get('skills', {})
        jd = data.get('job_description', '')
        
        letter = analyzer.advanced.generate_cover_letter(name, skills, jd)
        return jsonify({'success': True, 'cover_letter': letter})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-ats-pdf', methods=['POST'])
def generate_ats_pdf():
    """Generate and return an ATS-friendly PDF"""
    # This would normally use reportlab to create a clean PDF
    # For now, we'll return a Success message and generate a plain text file for simplicity
    # or use reportlab if possible. Let's provide a basic implementation.
    try:
        data = request.json
        text = data.get('text', '')
        filename = f"ATS_Friendly_{secure_filename(data.get('name', 'Resume'))}.txt"
        filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
        
        # Strip simple formatting but keep structure
        clean_text = re.sub(r'[^\x00-\x7F]+', ' ', text) # Remove non-ascii
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(clean_text)
            
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)