import re
import textstat
import requests
from datetime import datetime
from dateutil import parser as date_parser
from config.config import ACTION_VERBS

class AdvancedAnalyzer:
    """Advanced analysis features for resume evaluation"""
    
    def __init__(self):
        pass

    def analyze_readability(self, text):
        """Calculate readability scores and tone"""
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'grade_level': textstat.flesch_kincaid_grade(text),
            'reading_time': textstat.reading_time(text),
            'word_count': textstat.lexicon_count(text)
        }

    def check_passive_voice(self, text):
        """Detect passive vs active voice patterns"""
        # Passive voice usually has 'to be' verb + past participle
        passive_patterns = [
            r'\b(?:am|is|are|was|were|be|been|being)\b\s+\w+ed\b',
            r'\bresponsible\s+for\b',
            r'\bhelped\s+with\b',
            r'\bassisted\s+in\b'
        ]
        
        found_passive = []
        lines = text.split('\n')
        for line in lines:
            for pattern in passive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    found_passive.append(line.strip())
                    break
        
        # Calculate score (100 - (passive count * 5))
        score = max(0, 100 - (len(found_passive) * 5))
        
        return {
            'score': score,
            'passive_sentences_count': len(found_passive),
            'samples': found_passive[:5]
        }

    def analyze_career_path(self, experience_data):
        """Analyze gaps, seniority, and growth"""
        date_ranges = experience_data.get('date_ranges', [])
        titles = experience_data.get('detected_titles', [])
        
        # 1. Gap Detector
        gaps = []
        parsed_dates = []
        
        for dr in date_ranges:
            try:
                # Expecting something like "Jan 2020 - Dec 2021"
                parts = re.split(r'\s*(?:-|to|until)\s*', dr)
                if len(parts) == 2:
                    start_str, end_str = parts[0], parts[1]
                    start_date = date_parser.parse(start_str)
                    end_date = datetime.now() if 'present' in end_str.lower() else date_parser.parse(end_str)
                    parsed_dates.append((start_date, end_date))
            except:
                continue
        
        # Sort by start date
        parsed_dates.sort(key=lambda x: x[0])
        
        for i in range(len(parsed_dates) - 1):
            current_end = parsed_dates[i][1]
            next_start = parsed_dates[i+1][0]
            diff = (next_start - current_end).days
            if diff > 180: # 6 months
                gaps.append(f"Gap of {diff // 30} months between {current_end.strftime('%b %Y')} and {next_start.strftime('%b %Y')}")
        
        # 2. Seniority Classifier
        seniority = "Entry-Level"
        senior_keywords = ['senior', 'lead', 'manager', 'director', 'principal', 'head', 'vp', 'executive']
        mid_keywords = ['middle', 'intermediate', 'assoc']
        
        years_mentioned = experience_data.get('years_mentioned', [])
        total_years = sum(int(y) for y in years_mentioned if y.isdigit())
        
        title_text = " ".join(titles).lower()
        if any(kw in title_text for kw in senior_keywords) or total_years >= 7:
            seniority = "Senior / Executive"
        elif any(kw in title_text for kw in mid_keywords) or total_years >= 3:
            seniority = "Mid-Career"
            
        # 3. Promotion/Growth Tracker
        growth_score = 50
        progression = []
        # Basic check: order of titles
        # Manager -> Engineer is negative, Engineer -> Manager is positive
        seniority_map = {'junior': 1, 'engineer': 2, 'developer': 2, 'senior': 3, 'lead': 4, 'manager': 5, 'director': 6}
        
        current_level = 0
        for title in reversed(titles): # oldest to newest
            title_lower = title.lower()
            for kw, lv in seniority_map.items():
                if kw in title_lower:
                    if lv > current_level:
                        growth_score += 10
                        progression.append(f"Promotion/Growth detected: {title}")
                    current_level = lv
                    break
        
        return {
            'gaps': gaps,
            'seniority_level': seniority,
            'growth_score': min(100, growth_score),
            'career_progression': progression
        }

    def validate_links(self, contact_info):
        """Validate LinkedIn and GitHub profile links"""
        results = []
        links_to_check = []
        if contact_info.get('linkedin'): links_to_check.append(("LinkedIn", "https://" + contact_info['linkedin']))
        if contact_info.get('github'): links_to_check.append(("GitHub", "https://" + contact_info['github']))
        
        for name, url in links_to_check:
            try:
                # Basic check - no heavy redirect following for speed
                response = requests.head(url, timeout=3, allow_redirects=True)
                status = "Active" if response.status_code < 400 else "Broken"
                results.append({'name': name, 'url': url, 'status': status})
            except:
                results.append({'name': name, 'url': url, 'status': "Timeout/Error"})
        
        return results

    def identify_role_suitability(self, skills):
        """Map skills to professional job roles and calculate suitability"""
        all_skills = [s.lower() for s in skills.get('all_technical', [])]
        
        roles_database = {
            'Full Stack Developer': ['html', 'css', 'javascript', 'react', 'node', 'database', 'git', 'api', 'typescript', 'frontend', 'backend'],
            'Data Scientist': ['python', 'statistics', 'machine learning', 'sql', 'pandas', 'numpy', 'scikit-learn', 'data visualization', 'r', 'mathematics'],
            'DevOps Engineer': ['docker', 'kubernetes', 'aws', 'ci/cd', 'linux', 'terraform', 'jenkins', 'cloud', 'azure', 'ansible', 'automation'],
            'Product Manager': ['agile', 'scrum', 'strategy', 'roadmap', 'stakeholder', 'user experience', 'market research', 'analytics', 'product lifecycle'],
            'Cybersecurity Analyst': ['security', 'network', 'firewall', 'penetration testing', 'encryption', 'compliance', 'cyber', 'vulnerability', 'incident response']
        }
        
        matches = []
        for role, req_skills in roles_database.items():
            overlap = [s for s in all_skills if any(req in s for req in req_skills)]
            suitability = (len(overlap) / len(req_skills)) * 100
            matches.append({
                'role': role,
                'suitability': round(suitability, 2),
                'matched_core_skills': overlap[:3]
            })
            
        # Sort by suitability
        matches.sort(key=lambda x: x['suitability'], reverse=True)
        return matches[:3]

    def generate_roadmap(self, seniority, roles_data):
        """Generate next-step career advice based on seniority and current trajectory"""
        roadmap = []
        top_role = roles_data[0]['role'] if roles_data else "Software Professional"
        
        if "Entry" in seniority:
            roadmap = [
                f"Obtain a professional certification in {top_role}",
                "Build 2 high-quality portfolio projects demonstrating end-to-end execution",
                "Focus on 'Clean Code' principles and Version Control (Git) mastery"
            ]
        elif "Mid" in seniority:
            roadmap = [
                "Develop mentorship skills by contributing to open-source or helping juniors",
                "Deep dive into System Design and Scalability patterns",
                "Take ownership of a major project lifecycle from conception to deployment"
            ]
        else: # Senior
            roadmap = [
                "Strategy: Focus on cross-functional leadership and stakeholder management",
                "System Architecture: Influence long-term technical debt and architectural decisions",
                "Public Presence: Speak at conferences or write technical blogs to establish authority"
            ]
            
        return {
            'target_next_level': "Senior Professional" if "Mid" in seniority else ("Architect / Manager" if "Senior" in seniority else "Mid-Level Professional"),
            'steps': roadmap
        }

    def generate_cover_letter(self, name, skills, jd):
        """Generate a basic tailored cover letter template"""
        top_skills = skills.get('all_technical', [])[:5]
        skills_str = ", ".join(top_skills)
        
        letter = f"""Dear Hiring Manager,

I am writing to express my enthusiastic interest in the position as advertised. With a strong background in {skills_str}, I am confident that I can contribute effectively to your team.

Throughout my career, I have focused on delivering high-quality results and continuous improvement. My expertise in {top_skills[0] if top_skills else 'industry standard practices'} aligns well with the requirements mentioned in your job description.

I am particularly impressed by your company's commitment to excellence and would welcome the opportunity to discuss how my skills and experiences can benefit your organization.

Sincerely,
{name}"""
        return letter
