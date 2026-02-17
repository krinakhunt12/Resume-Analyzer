"""Build a training CSV by merging source tables in `data/`.

Output: `data/resume_training_full.csv` with columns: person_id, text, label

The `text` column aggregates name, experience titles, education entries, and skills.
The `label` column is taken from the `name` column in `01_people.csv` (cleaned).
"""
import os
import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
OUT_FILE = DATA_DIR / 'resume_training_full.csv'


def read_people(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=['person_id', 'name'], dtype={'person_id': str, 'name': str})
    df['name'] = df['name'].fillna('').astype(str)
    df['label'] = df['name'].str.strip()
    return df[['person_id', 'label']]


def aggregate_experience(path: Path) -> pd.DataFrame:
    # read only person_id and title
    cols = ['person_id', 'title']
    df = pd.read_csv(path, usecols=cols, dtype={'person_id': str, 'title': str})
    df['title'] = df['title'].fillna('').astype(str)
    agg = df.groupby('person_id')['title'].apply(lambda vals: ' ; '.join([v for v in vals if v])).reset_index()
    agg = agg.rename(columns={'title': 'experience_text'})
    return agg


def aggregate_education(path: Path) -> pd.DataFrame:
    cols = ['person_id', 'school', 'degree']
    # some files may not have all cols - read flexible
    try:
        df = pd.read_csv(path, dtype={'person_id': str})
    except Exception:
        return pd.DataFrame(columns=['person_id', 'education_text'])
    # coalesce school and degree
    for c in ['school', 'degree']:
        if c not in df.columns:
            df[c] = ''
    df['edu'] = (df['degree'].fillna('') + ' ' + df['school'].fillna('')).str.strip()
    agg = df.groupby('person_id')['edu'].apply(lambda vals: ' ; '.join([v for v in vals if v])).reset_index()
    agg = agg.rename(columns={'edu': 'education_text'})
    agg['person_id'] = agg['person_id'].astype(str)
    return agg


def aggregate_skills(path: Path) -> pd.DataFrame:
    cols = ['person_id', 'skill']
    df = pd.read_csv(path, usecols=cols, dtype={'person_id': str, 'skill': str})
    df['skill'] = df['skill'].fillna('').astype(str)
    agg = df.groupby('person_id')['skill'].apply(lambda vals: ', '.join(sorted(set([v.strip() for v in vals if v])))).reset_index()
    agg = agg.rename(columns={'skill': 'skills_text'})
    return agg


def build():
    people_f = DATA_DIR / '01_people.csv'
    exp_f = DATA_DIR / '04_experience.csv'
    edu_f = DATA_DIR / '03_education.csv'
    pskills_f = DATA_DIR / '05_person_skills.csv'

    print('Reading people...')
    people = read_people(people_f)

    print('Aggregating experience...')
    experience = aggregate_experience(exp_f)

    print('Aggregating education...')
    education = aggregate_education(edu_f)

    print('Aggregating skills...')
    skills = aggregate_skills(pskills_f)

    print('Merging...')
    df = people.merge(experience, on='person_id', how='left')
    df = df.merge(education, on='person_id', how='left')
    df = df.merge(skills, on='person_id', how='left')

    # compose text
    df['text'] = (
        df['label'].fillna('') + ' ; ' +
        df['experience_text'].fillna('') + ' ; ' +
        df['education_text'].fillna('') + ' ; ' +
        df['skills_text'].fillna('')
    ).str.replace('\n', ' ').str.replace('\r', ' ')

    out = df[['person_id', 'text', 'label']]
    print(f'Writing output to {OUT_FILE} ({len(out)} rows)')
    out.to_csv(OUT_FILE, index=False)


if __name__ == '__main__':
    build()
