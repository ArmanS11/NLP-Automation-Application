function looksLikeJobPage() {
  const text = document.body?.innerText?.toLowerCase() || "";
  const markers = ["apply", "job description", "responsibilities", "qualifications"];
  return markers.filter((m) => text.includes(m)).length >= 2;
}

function extractJobContext() {
  const title = document.querySelector("h1")?.textContent?.trim() || document.title;
  const companyMeta = document.querySelector('meta[property="og:site_name"]')?.getAttribute("content");
  const company = companyMeta || "Unknown Company";
  const bodyText = (document.body?.innerText || "").replace(/\s+/g, " ").trim();
  return {
    url: window.location.href,
    jobTitle: title,
    company,
    jobDescription: bodyText.slice(0, 12000)
  };
}

if (looksLikeJobPage()) {
  const payload = extractJobContext();
  chrome.runtime.sendMessage({ type: "JOB_DETECTED", payload });
  window.__JOB_COPILOT_CONTEXT__ = payload;
}
