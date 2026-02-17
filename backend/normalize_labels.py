"""Normalize raw job-title labels to canonical categories.

Produces: data/resume_training_normalized.csv and backend/label_mapping.json

This uses simple keyword heuristics to map common job titles / resume text
to broader categories. It's a pragmatic first pass — you can refine mappings
or replace this with a supervised relabeling step.
"""
import json
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
IN_FILE = DATA_DIR / 'resume_training_full.csv'
OUT_FILE = DATA_DIR / 'resume_training_normalized.csv'
MAPPING_FILE = ROOT / 'backend' / 'label_mapping.json'


CANONICAL_MAP = {
    "software_engineer": ["software engineer", "software developer", "programmer", "full stack", "backend", "frontend", "web developer", "java developer", "python developer", "c++", "c#"],
    "data_scientist": ["data scientist", "data science", "ml engineer", "machine learning", "deep learning", "nlp"],
    "data_engineer": ["data engineer", "etl", "data pipeline", "bigdata", "spark", "hadoop"],
    "devops_engineer": ["devops", "site reliability", "sre", "infrastructure", "ci/cd", "kubernetes", "docker"],
    "system_administrator": ["system administrator", "sysadmin", "systems administrator", "windows admin", "linux admin"],
    "database_administrator": ["dba", "database administrator", "oracle dba", "sql dba", "mysql dba", "postgres"],
    "project_manager": ["project manager", "pm", "project management", "scrum master"],
    "product_manager": ["product manager", "product owner", "product management"],
    "business_analyst": ["business analyst", "ba", "business analysis"],
    "qa_engineer": ["qa", "quality assurance", "test engineer", "tester", "automation test"],
    "ux_designer": ["ux", "ui designer", "ux designer", "user experience", "ui/ux"],
    "hr": ["hr", "human resources", "recruiter", "talent"],
    "sales": ["sales", "account executive", "account manager", "bdm", "business development"],
    "marketing": ["marketing", "digital marketing", "seo", "content"],
    "finance": ["finance", "financial", "accountant", "accounts payable", "cpa"],
    "legal": ["legal", "attorney", "lawyer", "paralegal"]
}


def normalize_label(orig_label: str, text: str) -> str:
    low_label = (orig_label or '').lower()
    low_text = (text or '').lower()
    # check label first
    for canon, keywords in CANONICAL_MAP.items():
        for kw in keywords:
            if kw in low_label:
                return canon
    # fallback: check aggregated text
    for canon, keywords in CANONICAL_MAP.items():
        for kw in keywords:
            if kw in low_text:
                return canon
    return 'other'


def main():
    print(f"Loading dataset: {IN_FILE}")
    df = pd.read_csv(IN_FILE, dtype=str)
    df = df.fillna('')
    # keep original label
    df['orig_label'] = df['label'].astype(str)
    print('Applying normalization mapping...')
    df['label'] = df.apply(lambda r: normalize_label(r['orig_label'], r['text']), axis=1)

    counts = df['label'].value_counts().to_dict()
    print('Label distribution after normalization:')
    for k, v in counts.items():
        print(f'  {k}: {v}')

    print(f'Writing normalized dataset to: {OUT_FILE}')
    df.to_csv(OUT_FILE, index=False)

    # save mapping for reference
    print(f'Writing mapping to: {MAPPING_FILE}')
    MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MAPPING_FILE, 'w', encoding='utf8') as f:
        json.dump(CANONICAL_MAP, f, indent=2)


if __name__ == '__main__':
    main()
