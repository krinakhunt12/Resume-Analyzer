"""
Main Application File
ATS Resume Analyzer - Command Line Interface
"""

import os
import sys
import argparse
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.text_extractor import TextExtractor
from src.resume_parser import ResumeParser
from src.ats_analyzer import ATSAnalyzer
from src.report_generator import ReportGenerator


import tempfile

class ATSResumeAnalyzer:
    """Main application class"""
    
    def __init__(self):
        self.extractor = TextExtractor()
        self.parser = ResumeParser()
        self.analyzer = ATSAnalyzer()
        
        # Use system temp directory for transient data
        self.results_dir = os.path.join(tempfile.gettempdir(), 'resume_analyzer', 'results')
        os.makedirs(self.results_dir, exist_ok=True)
        self.report_generator = ReportGenerator(output_dir=self.results_dir)
    
    def analyze_resume(self, resume_path, job_description_path=None, output_format='all'):
        """
        Analyze a resume and generate reports
        
        Args:
            resume_path (str): Path to resume file
            job_description_path (str): Path to job description file (optional)
            output_format (str): Output format - 'text', 'json', 'excel', or 'all'
        """
        print("\n" + "="*80)
        print("ATS RESUME ANALYZER")
        print("="*80 + "\n")
        
        # Step 1: Extract text from resume
        print(f"📄 Extracting text from: {os.path.basename(resume_path)}")
        try:
            resume_text = self.extractor.extract(resume_path)
            print(f"✓ Extracted {len(resume_text)} characters\n")
        except Exception as e:
            print(f"✗ Error extracting resume: {str(e)}")
            return None
        
        # Step 2: Extract job description if provided
        job_description = ""
        if job_description_path:
            print(f"📋 Extracting job description from: {os.path.basename(job_description_path)}")
            try:
                job_description = self.extractor.extract(job_description_path)
                print(f"✓ Extracted {len(job_description)} characters\n")
            except Exception as e:
                print(f"✗ Error extracting job description: {str(e)}")
                print("Continuing without job description...\n")
        
        # Step 3: Parse resume
        print("🔍 Parsing resume...")
        parsed_resume = self.parser.parse(resume_text)
        print(f"✓ Found {len(parsed_resume['skills']['all_technical'])} technical skills")
        print(f"✓ Detected {sum(1 for v in parsed_resume['sections'].values() if v)} sections\n")
        
        # Step 4: Analyze
        print("⚡ Running ATS analysis...")
        analysis_results = self.analyzer.analyze(resume_text, parsed_resume, job_description)
        print(f"✓ Analysis complete\n")
        
        # Step 5: Display results
        self._display_results(analysis_results, parsed_resume)
        
        # Step 6: Generate reports (Only if format is not 'none')
        if output_format != 'none':
            print("\n📊 Generating reports...")
            base_filename = Path(resume_path).stem + "_analysis"
            
            if output_format == 'all':
                reports = self.report_generator.generate_all_reports(
                    analysis_results, parsed_resume, base_filename
                )
                print(f"✓ Text report: {reports['text']}")
                print(f"✓ JSON report: {reports['json']}")
                print(f"✓ Excel report: {reports['excel']}")
            elif output_format == 'text':
                filepath, _ = self.report_generator.generate_text_report(
                    analysis_results, parsed_resume, f"{base_filename}.txt"
                )
                print(f"✓ Text report: {filepath}")
            elif output_format == 'json':
                filepath, _ = self.report_generator.generate_json_report(
                    analysis_results, parsed_resume, f"{base_filename}.json"
                )
                print(f"✓ JSON report: {filepath}")
            elif output_format == 'excel':
                filepath = self.report_generator.generate_excel_report(
                    analysis_results, parsed_resume, f"{base_filename}.xlsx"
                )
                print(f"✓ Excel report: {filepath}")
        else:
            print("\n💡 Tip: Use --format [text|json|excel] to save results to a temporary file.")
        
        print("\n" + "="*80)
        print("Analysis complete!")
        print("="*80 + "\n")
        
        return analysis_results
    
    def _display_results(self, results, parsed_resume):
        """Display analysis results in terminal"""
        print("\n" + "="*80)
        print("ANALYSIS RESULTS")
        print("="*80 + "\n")
        
        # Overall score
        score = results['overall_score']
        rating = results['rating']
        
        # Color coding for terminal (works on most terminals)
        if score >= 80:
            color = '\033[92m'  # Green
        elif score >= 60:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[91m'  # Red
        reset = '\033[0m'
        
        print(f"Overall Score: {color}{score:.2f}/100{reset}")
        print(f"Rating: {color}{rating}{reset}\n")
        
        # Individual scores
        print("Detailed Scores:")
        print("-" * 80)
        for score_name, score_value in results['scores'].items():
            formatted_name = score_name.replace('_', ' ').title()
            bar_length = int(score_value / 5)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            print(f"{formatted_name:.<35} {bar} {score_value:.1f}%")
        
        # Warnings
        warnings = results.get('format_check', {}).get('warnings', [])
        if warnings:
            print("\n" + "="*80)
            print("ATS COMPATIBILITY WARNINGS:")
            print("-" * 80)
            for warning in warnings:
                print(f"  ⚠️ {warning}")
        
        # Top strengths
        print("\n" + "="*80)
        print("TOP STRENGTHS:")
        print("-" * 80)
        strengths = results.get('strengths', [])
        if strengths:
            for strength in strengths[:5]:
                print(f"  ✓ {strength}")
        else:
            print("  No significant strengths identified")
        
        # Recommendations
        print("\n" + "="*80)
        print("RECOMMENDATIONS:")
        print("-" * 80)
        recommendations = results.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")
        else:
            print("  No recommendations - resume looks good!")


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='ATS Resume Analyzer - Analyze resumes for ATS compatibility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a resume without job description
  python main.py --resume data/resumes/john_doe.pdf
  
  # Analyze with job description
  python main.py --resume data/resumes/john_doe.pdf --jd data/job_descriptions/software_engineer.pdf
  
  # Generate only JSON report
  python main.py --resume data/resumes/john_doe.pdf --format json
        """
    )
    
    parser.add_argument(
        '--resume', '-r',
        required=False,
        help='Path to resume file (PDF or DOCX). If omitted, searches data/resumes/'
    )
    
    parser.add_argument(
        '--jd', '-j',
        help='Path to job description file (optional)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'excel', 'all', 'none'],
        default='none',
        help='Output format for reports (default: none - only prints to terminal)'
    )
    
    args = parser.parse_args()
    
    resume_path = args.resume
    
    # Auto-find resume if not provided
    if not resume_path:
        search_dir = 'data/resumes'
        if os.path.exists(search_dir):
            files = [f for f in os.listdir(search_dir) if f.lower().endswith(('.pdf', '.docx'))]
            if files:
                resume_path = os.path.join(search_dir, files[0])
                print(f"💡 No resume provided. Automatically selecting: {resume_path}")
            else:
                print(f"❌ Error: No resume provided and no files found in '{search_dir}'")
                print("Usage: python main.py --resume path/to/your/resume.pdf")
                sys.exit(1)
        else:
            print("❌ Error: Resume argument is required.")
            print("Usage: python main.py --resume path/to/your/resume.pdf")
            sys.exit(1)
    
    # Validate files exist
    if not os.path.exists(resume_path):
        print(f"Error: Resume file not found: {resume_path}")
        sys.exit(1)
    
    if args.jd and not os.path.exists(args.jd):
        print(f"Error: Job description file not found: {args.jd}")
        sys.exit(1)
    
    # Run analysis
    app = ATSResumeAnalyzer()
    app.analyze_resume(resume_path, args.jd, args.format)


if __name__ == "__main__":
    main()