# Resume Classifier Training

This folder contains a baseline training script for building a Resume Classification model
that maps resume text to job categories. The baseline uses TF-IDF features + Logistic Regression.

Files
- `train_resume_classifier.py` — Training script (preprocessing, train/test split, evaluation, model saving).
- `requirements-training.txt` — Python dependencies for training and optional advanced models.

Quick start

1. Create a CSV dataset in the repo (example path `data/resumes.csv`) with at least two columns:

   - `resume_text` — full resume text
   - `job_category` — label (e.g., "software_engineer", "data_scientist", ...)

2. Create and activate a Python environment and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate    # or .\.venv\Scripts\activate on Windows
pip install -r backend/requirements-training.txt
```

3. Run training:

```bash
python backend/train_resume_classifier.py --data data/resumes.csv \
  --text-col resume_text --label-col job_category --out backend/models/resume_clf.joblib
```

Notes
- If your dataset uses different column names, pass `--text-col` and `--label-col`.
- Use `--model svm` to train a linear SVM instead of Logistic Regression.
- Use `--lemmatize` to enable optional lemmatization (requires NLTK downloads).

Inference example (Python)

```python
import joblib

pipeline = joblib.load('backend/models/resume_clf.joblib')
texts = ["Experienced Python developer with ML experience and SQL"]
preds = pipeline.predict(texts)
probs = None
if hasattr(pipeline.named_steps['clf'], 'predict_proba'):
    probs = pipeline.predict_proba(texts)
print('Prediction:', preds)
if probs is not None:
    print('Probabilities:', probs)
```

Improvement suggestions (advanced)

- Replace TF-IDF + linear model with embeddings:
  - Use `SentenceTransformer` (e.g., `all-MiniLM-L6-v2`) to create dense sentence embeddings, then train a classifier (LogisticRegression, SVM, or tree-based) on those vectors.
  - Use pre-trained word embeddings (Word2Vec / GloVe) with average pooling or a small neural network.
- Use fine-tuned transformers (BERT/DeBERTa) for better text understanding. For classification, fine-tune a transformer model end-to-end.

Productionizing & API

1. Wrap the saved pipeline into a lightweight API (Flask/FastAPI) that accepts file uploads or plain text.
2. On the server, extract text from uploaded resumes (PDF/DOCX) using your existing `text_extractor.py` code, then call the pipeline `predict`.
3. Return label, probability, top keywords, and improvement suggestions in the API response.

Security & privacy

- Ensure secure upload handling and minimal retention of personal data.
- Consider on-prem or private cloud model hosting if data sensitivity requires it.
