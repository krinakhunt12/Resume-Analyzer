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
import tempfile
import re
import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.text_extractor import TextExtractor
from src.resume_parser import ResumeParser
from src.ats_analyzer import ATSAnalyzer
from src.report_generator import ReportGenerator

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
        timeline_data = parsed_resume.get('timeline', {})
        years_list = experience_data.get('years_mentioned', [])
        total_years = timeline_data.get('total_experience_years') or (years_list[0] if years_list else "Not explicitly stated")
        
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
        
        # 6. Advanced Visualization Items (New Phase 2)
        skill_heatmap = {
            'technical': len(key_sections['skills']['technical']),
            'tools': len(key_sections['skills']['tools']),
            'soft': len(key_sections['skills']['soft_skills'])
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
                'improvement_suggestions': improvement_suggestions,
                'timeline': timeline_data, # New Timeline Data
                'skill_heatmap': skill_heatmap  # New Heatmap Data
            }
        }
        
        print(f"✅ Analysis complete for: {candidate_details['name']}")
        return jsonify(response_data)
    
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


@app.route('/compare-jobs', methods=['POST'])
def compare_jobs():
    """Compare resume against multiple job descriptions"""
    try:
        # Check for resume
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
            
        resume_file = request.files['resume']
        
        # Handle JDs (Expect list of text or multiple files)
        # For simplicity, we'll accept a form field 'job_descriptions' which is a JSON list of strings
        # OR multiple file uploads with name 'jd_files'
        
        jds = []
        
        # 1. Check for JSON text list
        if 'job_descriptions' in request.form:
            try:
                jds = json.loads(request.form['job_descriptions'])
            except:
                pass
                
        # 2. Check for JD files
        if 'jd_files' in request.files:
            files = request.files.getlist('jd_files')
            for f in files:
                if f.filename != '':
                    filename = secure_filename(f.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    f.save(path)
                    text = extractor.extract(path)
                    jds.append(text)
                    if os.path.exists(path): os.remove(path)
        
        if not jds:
            return jsonify({'error': 'No job descriptions provided'}), 400
            
        # Process Resume Logic (Single Extraction)
        resume_filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        resume_file.save(resume_path)
        resume_text = extractor.extract(resume_path)
        if os.path.exists(resume_path): os.remove(resume_path)
        
        parsed_resume = parser.parse(resume_text)
        
        comparison_results = []
        for i, jd_text in enumerate(jds):
            # Run lightweight analysis
            res = analyzer.analyze(resume_text, parsed_resume, jd_text)
            comparison_results.append({
                'id': i + 1,
                'score': res['overall_score'],
                'rating': res['rating'],
                'missing_keywords': res.get('keyword_match', {}).get('missing_keywords', [])[:5]
            })
            
        return jsonify({
            'success': True,
            'comparison': comparison_results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat_with_ai():
    """
    AI Career Assistant Chat Endpoint
    Currently uses mock logic, ready for OpenAI/Gemini integration.
    """
    try:
        data = request.json
        message = data.get('message', '').lower()
        context = data.get('context', {}) # Resume data, current score, etc.
        
        # Mock Logic / Placeholder for LLM
        response = ""
        
        if "summary" in message:
            response = "Your professional summary should be 3-4 lines long and highlight your unique value proposition. Try starting with 'Results-oriented Software Engineer with 5+ years of experience in...'."
        elif "skill" in message or "python" in message or "java" in message:
            response = "Based on your resume, you have strong technical skills. Consider adding more 'Tools' like Docker, Kubernetes, or AWS if you have experience with them, as they are highly requested."
        elif "fix" in message or "improve" in message:
            response = "I recommend focusing on your 'Work Experience' section. Ensure every bullet point starts with a strong action verb (e.g., Led, Developed, Optimized) and includes a metric."
        elif "hello" in message or "hi" in message:
            response = "Hello! I'm your AI Career Assistant. How can I help you optimize your resume today?"
        else:
            response = "That's a great question. To improve your ATS score, focus on keyword optimization matching the job description. detailed metrics in your experience, and simple formatting."
            
        return jsonify({'response': response, 'role': 'assistant'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze-linkedin', methods=['POST'])
def analyze_linkedin():
    """
    Analyze LinkedIn Profile Text
    """
    try:
        data = request.json
        profile_text = data.get('text', '')
        
        if not profile_text:
            return jsonify({'error': 'No text provided'}), 400
            
        # 1. Basic parsing (reuse resume parser logic partially)
        # LinkedIn text often has "About", "Experience", etc.
        parsed = parser.parse(profile_text)
        
        # 2. LinkedIn specific checks
        # - Banner/Headline check (heuristics)
        has_headline = len(parsed['name'].split()) > 2 # Rough proxy
        
        # - About section length
        about_score = 0
        if parsed['sections'].get('summary'): # Parser detects summary/about
             about_score = 100
        
        # - Experience detailedness
        exp_score = 0
        if parsed['experience'].get('years_mentioned'):
             exp_score = 80
             
        score = (about_score + exp_score + (100 if has_headline else 50)) / 3
        
        insights = {
            'overall_score': round(score, 0),
            'headline_strength': 'Strong' if has_headline else 'Weak (Add keywords)',
            'about_section': 'Good length' if about_score > 0 else 'Missing or too short',
            'recommendations': [
                "Add a custom banner image",
                "Ensure your headline includes your target role keywords",
                "Request recommendations from colleagues"
            ]
        }
        
        return jsonify({'success': True, 'insights': insights})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-ats-pdf', methods=['POST'])
def generate_ats_pdf():
    """
    Generate a professional, multi-page PDF report using ReportLab Platypus.
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        results = data.get('results', {})
        candidate_name = results.get('candidate_name', 'Candidate')
        filename = f"Resume_Analysis_{secure_filename(candidate_name)}_{int(datetime.datetime.now().timestamp())}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        Story = []
        styles = getSampleStyleSheet()

        # --- Custom Styles ---
        styles.add(ParagraphStyle(name='TitleCustom', parent=styles['Heading1'], fontSize=24, leading=28, spaceAfter=20, textColor=colors.HexColor("#2563eb"), alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontSize=12, leading=14, spaceAfter=40, textColor=colors.grey, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], fontSize=16, leading=20, spaceBefore=20, spaceAfter=10, textColor=colors.HexColor("#1e40af"), borderPadding=5, borderColor=colors.HexColor("#e5e7eb"), borderWidth=0, borderBottomWidth=1))
        styles.add(ParagraphStyle(name='ScoreBig', parent=styles['Heading1'], fontSize=48, leading=56, spaceAfter=10, textColor=colors.HexColor("#2563eb"), alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='NormalCustom', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=6))
        styles.add(ParagraphStyle(name='BulletCustom', parent=styles['Bullet'], fontSize=10, leading=14, spaceAfter=4))
        
        # --- Header Section ---
        Story.append(Paragraph("Resume Analysis Report", styles['TitleCustom']))
        Story.append(Paragraph(f"Prepared for: <b>{candidate_name}</b><br/>Date: {datetime.datetime.now().strftime('%B %d, %Y')}", styles['Subtitle']))
        
        # --- Executive Summary (Score) ---
        score = results.get('overall_score', 0)
        rating = results.get('rating', 'Needs Improvement')
        
        Story.append(Paragraph("ATS Integrity Score", styles['TitleCustom']))
        Story.append(Paragraph(str(score), styles['ScoreBig']))
        Story.append(Paragraph(f"<b>Rating: {rating}</b>", styles['Subtitle']))
        
        # Visual Progress Bar (Table-based)
        bar_width = 400
        fill_width = (score / 100) * bar_width
        color = colors.HexColor("#22c55e") if score > 75 else (colors.HexColor("#f59e0b") if score > 50 else colors.HexColor("#ef4444"))
        
        # Draw a custom graphic flowable would be better, but table is easier for now
        # Creating a colored Table to act as a progress bar
        bar_data = [['', '']]
        bar_table = Table(bar_data, colWidths=[fill_width, bar_width - fill_width], rowHeights=[15])
        bar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), color),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#f3f4f6")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]), # ReportLab 3.6+
        ]))
        Story.append(bar_table)
        Story.append(Spacer(1, 30))

        # --- Section Breakdown Table ---
        Story.append(Paragraph("Detailed Compliance Audit", styles['SectionHeader']))
        
        scores = results.get('scores', {})
        table_data = [['Analysis Category', 'Score', 'Status']]
        
        for key, val in scores.items():
            status = "PASS" if val >= 70 else "NEEDS WORK"
            status_color = colors.HexColor("#22c55e") if val >= 70 else colors.HexColor("#ef4444")
            
            # Create a Paragraph object for status text to color it
            p_status = Paragraph(f"<font color='{status_color.hexval()}'><b>{status}</b></font>", styles["Normal"])
            p_val = f"{val}/100"
            
            row = [key.replace('_', ' ').title(), p_val, p_status]
            table_data.append(row)
            
        t = Table(table_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#64748b")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('ROWBACKGROUNDS', (1, 0), (-1, -1), [colors.white, colors.HexColor("#fcfcfc")]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        Story.append(t)
        Story.append(Spacer(1, 20))

        # --- Priority Recommendations ---
        Story.append(Paragraph("Critical Action Plan (High Priority)", styles['SectionHeader']))
        recs = results.get('recommendations', [])
        if not recs:
            Story.append(Paragraph("Excellent! No critical formatting issues found.", styles['NormalCustom']))
        else:
            for rec in recs[:5]: # Top 5
                # Prepend 'HIGH IMPACT' badge logic if needed, simplify for now
                Story.append(Paragraph(f"• {rec}", styles['BulletCustom']))

        Story.append(PageBreak())

        # --- Skills Matrix (Page 2) ---
        Story.append(Paragraph("Strategic Skills Matrix", styles['SectionHeader']))
        
        # Hard to pass exact lists from 'results' dict without proper parsing in backend
        # Re-using what we have in 'results' which has 'skills' counts usually
        # But we want the LISTS. The parser data has lists.
        # Check if 'skills_list' or similar is in results. If not, use generic advice.
        
        Story.append(Paragraph("Skills extracted from your document:", styles['NormalCustom']))
        
        # We need actual skill lists. In current app.py, 'results' mainly has counts.
        # Let's see if we can get robust data. The 'response_data' in analyze() has 'recruiter_insights'
        # But here we only receive 'results' key from frontend call.
        # Frontend calls: generateAtsPdf({ results: this.results() })
        
        # Workaround: Use text placeholders or simple summary
        tech_count = results.get('skills', {}).get('technical', 0)
        soft_count = results.get('skills', {}).get('soft', 0)
        
        Story.append(Paragraph(f"<b>Technical Skills Identified:</b> {tech_count}", styles['NormalCustom']))
        Story.append(Paragraph(f"<b>Soft Skills Identified:</b> {soft_count}", styles['NormalCustom']))
        Story.append(Spacer(1, 10))
        Story.append(Paragraph("<i>Note: To improve this section, ensure you list specific tools and technologies relevant to your target role (e.g., Python, React, AWS, Leadership).</i>", styles['Subtitle']))

        # --- Career Roadmap ---
        roadmap = results.get('career_roadmap', {})
        if roadmap:
             Story.append(Paragraph(f"Career Trajectory: {roadmap.get('target_next_level', 'Next Level')}", styles['SectionHeader']))
             for step in roadmap.get('steps', []):
                 Story.append(Paragraph(f"• {step}", styles['BulletCustom']))

        # --- Footer ---
        Story.append(Spacer(1, 40))
        Story.append(Paragraph("Generated by Resume Analyzer Pro • AI-Powered Career Optimization", styles['Subtitle']))
        
        doc.build(Story)
        
        return jsonify({
            'success': True, 
            'download_url': f"http://localhost:5000/download/{filename}"
        })

    except Exception as e:
        print(f"PDF Gen Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
