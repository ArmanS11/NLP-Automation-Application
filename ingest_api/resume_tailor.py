import re
from collections import Counter
from typing import Dict, List


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
    "you",
    "your",
    "our",
    "we",
}


def _tokenize(text: str) -> List[str]:
    return [
        t
        for t in re.findall(r"[a-zA-Z][a-zA-Z0-9\-\+\.#]{1,}", text.lower())
        if t not in STOPWORDS and len(t) >= 3
    ]


def extract_role_keywords(job_description: str, limit: int = 20) -> List[str]:
    tokens = _tokenize(job_description)
    if not tokens:
        return []
    counts = Counter(tokens)
    return [k for k, _ in counts.most_common(limit)]


def score_bullet_against_role(bullet: str, role_keywords: List[str]) -> int:
    if not role_keywords:
        return 0
    text = bullet.lower()
    return sum(1 for kw in role_keywords if kw in text)


def tailor_resume(
    resume_text: str,
    proficiencies: List[str],
    job_title: str,
    company: str,
    job_description: str,
    max_bullets: int = 8,
) -> Dict:
    role_keywords = extract_role_keywords(job_description, limit=20)
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]

    candidate_bullets = []
    for line in lines:
        clean = re.sub(r"^[\-\*\u2022]\s*", "", line)
        if len(clean) >= 20:
            candidate_bullets.append(clean)

    scored = [
        (score_bullet_against_role(b, role_keywords), b)
        for b in candidate_bullets
    ]
    scored.sort(key=lambda x: x[0], reverse=True)

    selected = [b for score, b in scored if score > 0][:max_bullets]
    if len(selected) < max_bullets:
        filler = [b for _, b in scored if b not in selected]
        selected.extend(filler[: max_bullets - len(selected)])

    prof_set = {p.strip().lower() for p in proficiencies if p.strip()}
    role_prof = [kw for kw in role_keywords if kw in prof_set]
    prioritized_skills = role_prof[:8] if role_prof else proficiencies[:8]

    summary = (
        f"Targeting {job_title} at {company}. "
        f"Highlights align with role needs in {', '.join(role_keywords[:5]) or 'core delivery'}."
    )

    return {
        "target_role": {
            "job_title": job_title,
            "company": company,
        },
        "summary": summary,
        "prioritized_skills": prioritized_skills,
        "experience_highlights": selected,
        "editable_sections": {
            "summary": summary,
            "skills": prioritized_skills,
            "highlights": selected,
        },
        "role_keywords": role_keywords,
    }
