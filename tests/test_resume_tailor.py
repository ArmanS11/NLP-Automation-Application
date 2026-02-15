import re

from ingest_api.resume_tailor import tailor_resume


def test_tailor_resume_returns_ranked_highlights():
    resume_text = """
    - Built Python data pipelines for ETL and analytics.
    - Deployed FastAPI services with CI/CD on AWS.
    - Led stakeholder meetings and managed sprint planning.
    - Optimized SQL queries reducing report runtime by 40%.
    """

    out = tailor_resume(
        resume_text=resume_text,
        proficiencies=["python", "fastapi", "sql", "aws"],
        job_title="Backend Engineer",
        company="Acme",
        job_description="Looking for a backend engineer with Python, FastAPI, SQL, and AWS experience.",
        max_bullets=3,
    )

    assert out["target_role"]["job_title"] == "Backend Engineer"
    assert len(out["experience_highlights"]) == 3
    assert any(re.search(r"python", b, re.I) for b in out["experience_highlights"])
