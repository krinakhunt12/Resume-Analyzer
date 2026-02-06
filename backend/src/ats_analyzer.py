"""
ATS Analyzer Module
Core analysis engine for resume scoring and matching
"""

import re
from collections import Counter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    SCORING_WEIGHTS, SCORE_THRESHOLDS, STOP_WORDS, 
    ACTION_VERBS, ATS_PITFALLS
)


from src.advanced_analyzer import AdvancedAnalyzer

class ATSAnalyzer:
    """Analyze resume against job description and ATS criteria"""
    
    def __init__(self):
        self.weights = SCORING_WEIGHTS
        self.advanced = AdvancedAnalyzer()
        
    def calculate_keyword_match(self, resume_text, job_description):
        """Calculate weighted keyword match score including N-grams"""
        if not job_description:
            return {'score': 0, 'matched_keywords': [], 'missing_keywords': [], 'total_jd_keywords': 0}

        def get_clean_tokens(text):
            return re.findall(r'\b\w+\b', text.lower())

        resume_text_lower = resume_text.lower()
        jd_text_lower = job_description.lower()
        
        # 1. Bi-grams/Tri-grams extraction from JD
        jd_tokens = get_clean_tokens(job_description)
        n_grams = []
        for n in [2, 3]:
            for i in range(len(jd_tokens) - n + 1):
                n_grams.append(" ".join(jd_tokens[i:i+n]))
        
        # Filter N-grams to only those that look like meaningful phrases (non-stopwords)
        meaningful_ngrams = [ng for ng in n_grams if not any(w in STOP_WORDS for w in ng.split())]
        
        # 2. Single keywords (excluding stop words)
        single_keywords = [w for w in jd_tokens if w not in STOP_WORDS and len(w) > 2]
        
        # Combine all possible keywords from JD
        all_potential_keywords = list(set(single_keywords + meaningful_ngrams))
        
        # 3. Calculate importance based on frequency in JD
        jd_word_freq = Counter(single_keywords + n_grams) # Raw tokens for frequency
        
        matched_keywords = []
        missing_keywords = []
        
        for kw in all_potential_keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, resume_text_lower):
                # Weight by frequency in JD
                weight = jd_word_freq.get(kw, 1)
                matched_keywords.append({'keyword': kw, 'weight': weight})
            else:
                missing_keywords.append(kw)
        
        if not all_potential_keywords:
            return {'score': 0, 'matched_keywords': [], 'missing_keywords': [], 'total_jd_keywords': 0}
            
        # Calculate weighted score
        total_weight = sum(jd_word_freq.get(kw, 1) for kw in all_potential_keywords)
        earned_weight = sum(item['weight'] for item in matched_keywords)
        score = (earned_weight / total_weight) * 100
        
        return {
            'score': round(score, 2),
            'matched_keywords': [m['keyword'] for m in matched_keywords[:30]], # Top 30
            'missing_keywords': missing_keywords[:20],
            'total_jd_keywords': len(all_potential_keywords)
        }
    
    def calculate_skills_match(self, resume_skills, job_description):
        """Calculate how many required skills from JD are in resume"""
        if not job_description:
            return {'score': 0, 'matched_skills': [], 'missing_skills': []}

        jd_lower = job_description.lower()
        
        # Get all technical skills from resume
        all_resume_skills = resume_skills.get('all_technical', [])
        all_resume_skills += resume_skills.get('soft', [])
        
        if not all_resume_skills:
            return {
                'score': 0,
                'matched_skills': [],
                'missing_skills': []
            }
        
        # Find which resume skills appear in JD
        matched_skills = []
        for skill in all_resume_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, jd_lower):
                matched_skills.append(skill)
        
        # Estimate required skills from JD
        from config.config import TECHNICAL_SKILLS, SOFT_SKILLS
        all_possible_skills = []
        for category_skills in TECHNICAL_SKILLS.values():
            all_possible_skills.extend(category_skills)
        all_possible_skills.extend(SOFT_SKILLS)
        
        required_skills = []
        for skill in all_possible_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, jd_lower):
                required_skills.append(skill)
        
        # Remove duplicates from required skills
        required_skills = list(set(required_skills))
        
        if not required_skills:
            score = 50  # Default score if no skills detected in JD
        else:
            score = (len(matched_skills) / len(required_skills)) * 100
        
        missing_skills = [s for s in required_skills if s not in matched_skills]
        
        return {
            'score': round(score, 2),
            'matched_skills': matched_skills,
            'required_skills': required_skills,
            'missing_skills': missing_skills
        }
    
    def calculate_impact_score(self, resume_text):
        """Analyze action verbs and quantifiable metrics"""
        text_lower = resume_text.lower()
        
        # 1. Match Action Verbs
        found_verbs = []
        for verb in ACTION_VERBS:
            pattern = r'\b' + re.escape(verb.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_verbs.append(verb)
        
        # 2. Match Quantifiable Metrics (%, $, numbers > 1)
        # Look for percentages, dollar amounts, or numbers followed by descriptive words
        metrics_patterns = [
            r'\d+%',                    # Percentages
            r'\$\d+',                   # Dollar amounts
            r'\b\d{1,3}(?:,\d{3})*\b',  # Large numbers
            r'\d+\s+(?:users|customers|clients|projects|employees|team members|revenue|growth|reduction|improvement)',
            r'\bincreased\s+by\s+\d+',
            r'\bsaved\s+\d+',
            r'\breduced\s+by\s+\d+'
        ]
        
        found_metrics = []
        for pattern in metrics_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                found_metrics.extend(matches)
        
        # Calculate scores (out of 100)
        verb_score = min(len(found_verbs) * 5, 50)  # Up to 50 points for 10+ verbs
        metric_score = min(len(found_metrics) * 10, 50) # Up to 50 points for 5+ metrics
        
        total_impact = verb_score + metric_score
        
        return {
            'score': total_impact,
            'verbs_found': len(found_verbs),
            'metrics_found': len(found_metrics),
            'found_verbs_list': found_verbs[:10],
            'found_metrics_sample': found_metrics[:5]
        }

    def check_format_ats_friendly(self, parsed_resume, resume_text):
        """Check if resume format is ATS-friendly"""
        issues = []
        warnings = []
        score = 100
        
        # Check for required sections
        sections = parsed_resume.get('sections', {})
        required_sections = ['contact', 'experience', 'education', 'skills']
        
        for section in required_sections:
            if not sections.get(section, False):
                issues.append(f"Missing {section} section")
                score -= 15
        
        # Check contact information
        contact = parsed_resume.get('contact_info', {})
        if not contact.get('emails'):
            issues.append("Email not found")
            score -= 10
        if not contact.get('phones'):
            issues.append("Phone number not found")
            score -= 10
        
        # Check word count
        stats = parsed_resume.get('statistics', {})
        word_count = stats.get('total_words', 0)
        if word_count < 200:
            issues.append("Resume too short (< 200 words)")
            score -= 15
        elif word_count > 1200:
            issues.append("Resume too long (> 1200 words)")
            score -= 5
        
        # Check for ATS pitfalls (graphics, icons, etc.)
        for pitfall in ATS_PITFALLS:
            if pitfall in resume_text.lower():
                warnings.append(f"Detected potential ATS block: {pitfall}")
                score -= 2
        
        # Check for special characters that might confuse ATS
        special_chars = len(re.findall(r'[^\w\s\.\,\-\(\)\@\+\/]', resume_text))
        if special_chars > 80:
            issues.append("Too many special characters/symbols")
            score -= 10
        
        return {
            'score': max(0, score),
            'issues': issues,
            'warnings': warnings,
            'is_ats_friendly': score >= 70
        }
    
    def calculate_completeness_score(self, parsed_resume):
        """Calculate completeness score based on information present"""
        score = 0
        
        # Check sections (40 points)
        sections = parsed_resume.get('sections', {})
        sections_present = sum(1 for v in sections.values() if v)
        total_sections = len(sections) if sections else 1
        score += (sections_present / total_sections) * 40
        
        # Check contact info (20 points)
        contact = parsed_resume.get('contact_info', {})
        contact_score = 0
        if contact.get('emails'): contact_score += 10
        if contact.get('phones'): contact_score += 5
        if contact.get('linkedin'): contact_score += 5
        score += contact_score
        
        # Check skills (20 points)
        skills = parsed_resume.get('skills', {})
        technical_skills = skills.get('all_technical', [])
        if len(technical_skills) > 8:
            score += 20
        elif len(technical_skills) > 0:
            score += 10
        
        # Check education (10 points)
        education = parsed_resume.get('education', {})
        if education.get('degrees'):
            score += 10
        
        # Check experience (10 points)
        experience = parsed_resume.get('experience', {})
        if experience.get('has_experience_section'):
            score += 10
        
        return round(score, 2)
    
    def analyze(self, resume_text, parsed_resume, job_description=""):
        """
        Perform complete ATS analysis
        
        Args:
            resume_text (str): Full resume text
            parsed_resume (dict): Parsed resume data
            job_description (str): Job description text (optional)
            
        Returns:
            dict: Complete analysis results with scores and recommendations
        """
        results = {
            'scores': {},
            'overall_score': 0,
            'rating': '',
            'recommendations': [],
            'strengths': []
        }
        
        # 1. Keyword Match
        if job_description:
            keyword_match = self.calculate_keyword_match(resume_text, job_description)
            results['keyword_match'] = keyword_match
            results['scores']['keyword_match'] = keyword_match['score']
            
            skills_match = self.calculate_skills_match(parsed_resume['skills'], job_description)
            results['skills_match'] = skills_match
            results['scores']['skills_match'] = skills_match['score']
        else:
            results['scores']['keyword_match'] = 0
            results['scores']['skills_match'] = 0
        
        # 2. Format & Pitfalls
        format_check = self.check_format_ats_friendly(parsed_resume, resume_text)
        results['format_check'] = format_check
        results['scores']['format_ats_friendly'] = format_check['score']
        
        # 3. Impact & Metrics
        impact_results = self.calculate_impact_score(resume_text)
        results['impact_analysis'] = impact_results
        results['scores']['impact_score'] = impact_results['score']
        
        # 4. Completeness
        completeness = self.calculate_completeness_score(parsed_resume)
        results['scores']['completeness'] = completeness
        
        # 5. Advanced Analysis - Readability & Tone
        results['readability'] = self.advanced.analyze_readability(resume_text)
        results['tone_analysis'] = self.advanced.check_passive_voice(resume_text)
        
        # 6. Advanced Analysis - Career Path
        results['career_analysis'] = self.advanced.analyze_career_path(parsed_resume.get('experience', {}))
        
        # 7. Advanced Analysis - Link Validation
        results['link_validation'] = self.advanced.validate_links(parsed_resume.get('contact_info', {}))
        
        # 8. Experience Relevance (Basic heuristic for now)
        exp = parsed_resume.get('experience', {})
        exp_score = 50
        if exp.get('has_experience_section'): exp_score += 20
        if exp.get('years_mentioned'): exp_score += 20
        results['scores']['experience_relevance'] = min(exp_score, 100)
        
        # 6. Education
        edu = parsed_resume.get('education', {})
        edu_score = 0
        if edu.get('degrees'): edu_score = 100
        elif edu.get('has_education_section'): edu_score = 50
        results['scores']['education'] = edu_score
        
        # Calculate weighted overall score
        overall = 0
        if job_description:
            for score_key, weight in self.weights.items():
                overall += results['scores'].get(score_key, 0) * weight
        else:
            # Without JD, focus on impact, format and completeness
            overall = (
                results['scores']['impact_score'] * 0.4 +
                results['scores']['format_ats_friendly'] * 0.4 +
                results['scores']['completeness'] * 0.2
            )
        
        results['overall_score'] = round(overall, 2)
        
        # Determine rating
        if overall >= SCORE_THRESHOLDS['excellent']:
            results['rating'] = 'Excellent'
        elif overall >= SCORE_THRESHOLDS['good']:
            results['rating'] = 'Good'
        elif overall >= SCORE_THRESHOLDS['fair']:
            results['rating'] = 'Fair'
        else:
            results['rating'] = 'Needs Improvement'
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results, parsed_resume, job_description)
        results['strengths'] = self._identify_strengths(results, parsed_resume)
        
        return results
    
    def _generate_recommendations(self, results, parsed_resume, job_description):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Format issues & warnings
        format_check = results.get('format_check', {})
        for issue in format_check.get('issues', []):
            recommendations.append(f"URGENT: {issue}")
        for warning in format_check.get('warnings', []):
            recommendations.append(f"Warning: {warning}")
        
        # Impact recommendations
        impact = results.get('impact_analysis', {})
        if impact.get('metrics_found', 0) < 3:
            recommendations.append("Use more quantifiable metrics (%, $, numbers) to demonstrate your impact")
        if impact.get('verbs_found', 0) < 5:
            recommendations.append("Start your bullet points with strong action verbs (e.g., 'Spearheaded', 'Optimized')")
        
        # Skills match
        if job_description:
            skills_match = results.get('skills_match', {})
            missing_skills = skills_match.get('missing_skills', [])
            if missing_skills:
                # Prioritize top 5 missing skills
                recommendations.append(f"Add these missing keywords: {', '.join(missing_skills[:5])}")
        
        # Section recommendations
        sections = parsed_resume.get('sections', {})
        if not sections.get('summary'):
            recommendations.append("Add a powerful Professional Summary with 3-4 lines highlighting your USP")
        
        return recommendations
    
    def _identify_strengths(self, results, parsed_resume):
        """Identify resume strengths"""
        strengths = []
        
        if results['scores'].get('impact_score', 0) >= 70:
            strengths.append("High-impact language and metrics used")
        
        if results['scores'].get('format_ats_friendly', 0) >= 90:
            strengths.append("Perfect ATS-friendly formatting")
        
        if job_description := results.get('skills_match', {}):
            if job_description.get('score', 0) >= 70:
                strengths.append("Strong skills alignment with the job description")
        
        technical_skills = parsed_resume.get('skills', {}).get('all_technical', [])
        if len(technical_skills) >= 15:
            strengths.append(f"Extensive technical expertise ({len(technical_skills)} skills identified)")
        
        return strengths
