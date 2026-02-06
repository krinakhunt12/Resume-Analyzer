"""
Resume Parser Module
Extracts structured information from resume text
"""

import re
from collections import Counter
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    TECHNICAL_SKILLS, SOFT_SKILLS, EDUCATION_KEYWORDS,
    EXPERIENCE_KEYWORDS, SECTION_HEADERS
)


class ResumeParser:
    """Parse resume text and extract structured information"""
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        self.linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        self.github_pattern = r'github\.com/[\w-]+'
        
    def extract_contact_info(self, text):
        """Extract contact information from resume"""
        contact_info = {
            'emails': [],
            'phones': [],
            'linkedin': None,
            'github': None
        }
        
        # Extract emails
        emails = re.findall(self.email_pattern, text)
        contact_info['emails'] = list(set(emails))
        
        # Extract phone numbers
        phones = re.findall(self.phone_pattern, text)
        contact_info['phones'] = list(set(phones))
        
        # Extract LinkedIn
        linkedin = re.findall(self.linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact_info['linkedin'] = linkedin[0]
        
        # Extract GitHub
        github = re.findall(self.github_pattern, text, re.IGNORECASE)
        if github:
            contact_info['github'] = github[0]
        
        return contact_info
    
    def extract_name(self, text):
        """Extract candidate name (usually first line)"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) <= 4 and len(line) > 3:
                # Basic heuristic: name is short and near the top
                if not re.search(r'[@\d]', line):  # No email or numbers
                    return line
        return "Not Found"
    
    def extract_skills(self, text):
        """Extract technical and soft skills from resume"""
        text_lower = text.lower()
        found_skills = {
            'technical': {},
            'soft': [],
            'all_technical': []
        }
        
        # Extract technical skills by category
        for category, skills in TECHNICAL_SKILLS.items():
            found_in_category = []
            for skill in skills:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_in_category.append(skill)
                    found_skills['all_technical'].append(skill)
            
            if found_in_category:
                found_skills['technical'][category] = found_in_category
        
        # Extract soft skills
        for skill in SOFT_SKILLS:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills['soft'].append(skill)
        
        return found_skills
    
    def extract_education(self, text):
        """Extract education information"""
        education = []
        text_lower = text.lower()
        
        # Look for degree keywords
        degrees_found = []
        for keyword in EDUCATION_KEYWORDS:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                degrees_found.append(keyword)
        
        # Extract years (potential graduation years)
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
        
        return {
            'degrees': list(set(degrees_found)),
            'years': list(set(years)),
            'has_education_section': any(re.search(r'\b' + re.escape(header) + r'\b', text_lower) 
                                         for header in SECTION_HEADERS['education'])
        }
    
    def extract_experience(self, text):
        """Extract work experience information with dates and titles"""
        text_lower = text.lower()
        
        # 1. Extract years of experience mentioned (e.g., "5 years of experience")
        experience_years = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)', text_lower)
        
        # 2. Extract specific date ranges (e.g., "Jan 2020 - Present", "2018 to 2019")
        date_range_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*(?:-|to|until)\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})'
        date_ranges = re.findall(date_range_pattern, text, re.IGNORECASE)
        
        # 3. Simple Title detection (often near start of lines in experience section)
        # Looking for common job title suffixes/suffixes
        titles = []
        title_keywords = ['Engineer', 'Developer', 'Manager', 'Lead', 'Analyst', 'Consultant', 'Architect', 'Director', 'Specialist', 'Coordinator', 'Executive']
        for line in text.split('\n'):
            if any(kw in line for kw in title_keywords) and len(line.split()) < 6:
                titles.append(line.strip())

        # 4. Count experience-related keywords
        experience_keywords_found = []
        for keyword in EXPERIENCE_KEYWORDS:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                experience_keywords_found.append((keyword, matches))
        
        return {
            'years_mentioned': experience_years,
            'keywords_found': experience_keywords_found,
            'date_ranges': date_ranges,
            'detected_titles': titles[:10],
            'has_experience_section': any(re.search(r'\b' + re.escape(header) + r'\b', text_lower) 
                                          for header in SECTION_HEADERS['experience'])
        }
    
    def detect_sections(self, text):
        """Detect which sections are present in the resume"""
        text_lower = text.lower()
        sections_found = {}
        
        for section_name, headers in SECTION_HEADERS.items():
            found = False
            for header in headers:
                pattern = r'\b' + re.escape(header) + r'\b'
                if re.search(pattern, text_lower):
                    found = True
                    break
            sections_found[section_name] = found
        
        return sections_found
    
    def get_word_count(self, text):
        """Get word count statistics"""
        words = text.split()
        return {
            'total_words': len(words),
            'unique_words': len(set(words)),
            'sentences': len(re.findall(r'[.!?]+', text))
        }
    
    def parse(self, text):
        """
        Main parsing method that extracts all information from resume
        
        Args:
            text (str): Resume text
            
        Returns:
            dict: Parsed resume information
        """
        parsed_data = {
            'name': self.extract_name(text),
            'contact_info': self.extract_contact_info(text),
            'skills': self.extract_skills(text),
            'education': self.extract_education(text),
            'experience': self.extract_experience(text),
            'sections': self.detect_sections(text),
            'statistics': self.get_word_count(text)
        }
        
        return parsed_data