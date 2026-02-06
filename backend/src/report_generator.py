"""
Report Generator Module
Generates detailed analysis reports in various formats
"""

import json
import pandas as pd
from datetime import datetime
import os


class ReportGenerator:
    """Generate analysis reports in different formats"""
    
    def __init__(self, output_dir='../data/results'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_text_report(self, analysis_results, parsed_resume, filename=None):
        """Generate a detailed text report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
{'='*80}
ATS RESUME ANALYSIS REPORT
{'='*80}

Generated: {timestamp}
Candidate: {parsed_resume.get('name', 'Not Found')}

{'='*80}
OVERALL SCORE: {analysis_results['overall_score']}/100
Rating: {analysis_results['rating']}
{'='*80}

DETAILED SCORES:
{'-'*80}
"""
        
        # Add individual scores
        for score_name, score_value in analysis_results['scores'].items():
            formatted_name = score_name.replace('_', ' ').title()
            report += f"{formatted_name:.<40} {score_value:.2f}/100\n"
        
        report += f"\n{'='*80}\n"
        report += "CONTACT INFORMATION:\n"
        report += f"{'-'*80}\n"
        
        contact = parsed_resume.get('contact_info', {})
        report += f"Email(s): {', '.join(contact.get('emails', ['Not found']))}\n"
        report += f"Phone(s): {', '.join(contact.get('phones', ['Not found']))}\n"
        report += f"LinkedIn: {contact.get('linkedin', 'Not found')}\n"
        report += f"GitHub: {contact.get('github', 'Not found')}\n"
        
        report += f"\n{'='*80}\n"
        report += "SKILLS ANALYSIS:\n"
        report += f"{'-'*80}\n"
        
        skills = parsed_resume.get('skills', {})
        technical = skills.get('technical', {})
        
        if technical:
            for category, skill_list in technical.items():
                formatted_category = category.replace('_', ' ').title()
                report += f"\n{formatted_category}:\n"
                report += f"  {', '.join(skill_list)}\n"
        
        soft_skills = skills.get('soft', [])
        if soft_skills:
            report += f"\nSoft Skills:\n"
            report += f"  {', '.join(soft_skills)}\n"
        
        # Skills match if available
        if 'skills_match' in analysis_results:
            skills_match = analysis_results['skills_match']
            report += f"\n{'-'*80}\n"
            report += f"Skills Match Score: {skills_match['score']:.2f}/100\n"
            report += f"Matched Skills: {len(skills_match.get('matched_skills', []))}\n"
            report += f"Missing Skills: {len(skills_match.get('missing_skills', []))}\n"
            
            if skills_match.get('missing_skills'):
                report += f"\nMissing Skills (from Job Description):\n"
                report += f"  {', '.join(skills_match['missing_skills'][:10])}\n"
        
        report += f"\n{'='*80}\n"
        report += "SECTIONS DETECTED:\n"
        report += f"{'-'*80}\n"
        
        sections = parsed_resume.get('sections', {})
        for section_name, is_present in sections.items():
            status = "✓ Present" if is_present else "✗ Missing"
            formatted_name = section_name.replace('_', ' ').title()
            report += f"{formatted_name:.<40} {status}\n"
        
        report += f"\n{'='*80}\n"
        report += "FORMAT CHECK:\n"
        report += f"{'-'*80}\n"
        
        format_check = analysis_results.get('format_check', {})
        report += f"ATS-Friendly Score: {format_check.get('score', 0):.2f}/100\n"
        report += f"Status: {'✓ ATS-Friendly' if format_check.get('is_ats_friendly') else '✗ Needs Improvement'}\n"
        
        issues = format_check.get('issues', [])
        if issues:
            report += f"\nIssues Found:\n"
            for issue in issues:
                report += f"  • {issue}\n"
        
        report += f"\n{'='*80}\n"
        report += "STRENGTHS:\n"
        report += f"{'-'*80}\n"
        
        strengths = analysis_results.get('strengths', [])
        if strengths:
            for strength in strengths:
                report += f"  ✓ {strength}\n"
        else:
            report += "  No significant strengths identified\n"
        
        report += f"\n{'='*80}\n"
        report += "RECOMMENDATIONS:\n"
        report += f"{'-'*80}\n"
        
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report += f"  {i}. {rec}\n"
        else:
            report += "  No recommendations - resume looks good!\n"
        
        report += f"\n{'='*80}\n"
        report += "STATISTICS:\n"
        report += f"{'-'*80}\n"
        
        stats = parsed_resume.get('statistics', {})
        report += f"Total Words: {stats.get('total_words', 0)}\n"
        report += f"Unique Words: {stats.get('unique_words', 0)}\n"
        report += f"Sentences: {stats.get('sentences', 0)}\n"
        
        report += f"\n{'='*80}\n"
        report += "END OF REPORT\n"
        report += f"{'='*80}\n"
        
        # Save to file if filename provided
        if filename:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
            return filepath, report
        
        return None, report
    
    def generate_json_report(self, analysis_results, parsed_resume, filename=None):
        """Generate JSON report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'candidate_name': parsed_resume.get('name', 'Not Found'),
            'overall_score': analysis_results['overall_score'],
            'rating': analysis_results['rating'],
            'scores': analysis_results['scores'],
            'contact_info': parsed_resume.get('contact_info', {}),
            'skills': parsed_resume.get('skills', {}),
            'education': parsed_resume.get('education', {}),
            'experience': parsed_resume.get('experience', {}),
            'sections': parsed_resume.get('sections', {}),
            'format_check': analysis_results.get('format_check', {}),
            'recommendations': analysis_results.get('recommendations', []),
            'strengths': analysis_results.get('strengths', []),
            'statistics': parsed_resume.get('statistics', {})
        }
        
        # Add skills match if available
        if 'skills_match' in analysis_results:
            report_data['skills_match'] = analysis_results['skills_match']
        
        if 'keyword_match' in analysis_results:
            report_data['keyword_match'] = {
                'score': analysis_results['keyword_match']['score'],
                'matched_count': analysis_results['keyword_match']['matched_count'],
                'total_jd_keywords': analysis_results['keyword_match']['total_jd_keywords']
            }
        
        if filename:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            return filepath, report_data
        
        return None, report_data
    
    def generate_excel_report(self, analysis_results, parsed_resume, filename=None):
        """Generate Excel report with multiple sheets"""
        
        # Summary sheet
        summary_data = {
            'Metric': ['Candidate Name', 'Overall Score', 'Rating', 'Timestamp'],
            'Value': [
                parsed_resume.get('name', 'Not Found'),
                analysis_results['overall_score'],
                analysis_results['rating'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        
        # Scores sheet
        scores_data = {
            'Score Category': [k.replace('_', ' ').title() for k in analysis_results['scores'].keys()],
            'Score': list(analysis_results['scores'].values())
        }
        df_scores = pd.DataFrame(scores_data)
        
        # Skills sheet
        skills = parsed_resume.get('skills', {})
        technical = skills.get('technical', {})
        
        skills_data = {'Category': [], 'Skills': []}
        for category, skill_list in technical.items():
            skills_data['Category'].append(category.replace('_', ' ').title())
            skills_data['Skills'].append(', '.join(skill_list))
        
        if skills.get('soft'):
            skills_data['Category'].append('Soft Skills')
            skills_data['Skills'].append(', '.join(skills.get('soft', [])))
        
        df_skills = pd.DataFrame(skills_data) if skills_data['Category'] else pd.DataFrame()
        
        # Recommendations sheet
        recommendations_data = {
            'Recommendations': analysis_results.get('recommendations', [])
        }
        df_recommendations = pd.DataFrame(recommendations_data)
        
        if filename:
            filepath = os.path.join(self.output_dir, filename)
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                df_scores.to_excel(writer, sheet_name='Scores', index=False)
                if not df_skills.empty:
                    df_skills.to_excel(writer, sheet_name='Skills', index=False)
                df_recommendations.to_excel(writer, sheet_name='Recommendations', index=False)
            
            return filepath
        
        return None
    
    def generate_all_reports(self, analysis_results, parsed_resume, base_filename='resume_analysis'):
        """Generate all report formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            'text': None,
            'json': None,
            'excel': None
        }
        
        # Text report
        text_filename = f"{base_filename}_{timestamp}.txt"
        results['text'], _ = self.generate_text_report(analysis_results, parsed_resume, text_filename)
        
        # JSON report
        json_filename = f"{base_filename}_{timestamp}.json"
        results['json'], _ = self.generate_json_report(analysis_results, parsed_resume, json_filename)
        
        # Excel report
        excel_filename = f"{base_filename}_{timestamp}.xlsx"
        results['excel'] = self.generate_excel_report(analysis_results, parsed_resume, excel_filename)
        
        return results