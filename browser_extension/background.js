async function getStorage(keys) {
  return chrome.storage.sync.get(keys);
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.set({
    apiBaseUrl: "http://127.0.0.1:8001",
    spreadsheetId: "",
    sheetName: "Applications",
    resumeText: "",
    proficiencies: ""
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "JOB_DETECTED") {
    sendResponse({ ok: true });
    return true;
  }

  if (message.type === "GENERATE_SUGGESTIONS") {
    handleSuggestions(message.payload)
      .then((result) => sendResponse({ ok: true, result }))
      .catch((error) => sendResponse({ ok: false, error: String(error) }));
    return true;
  }

  if (message.type === "LOG_APPLICATION") {
    handleLog(message.payload)
      .then((result) => sendResponse({ ok: true, result }))
      .catch((error) => sendResponse({ ok: false, error: String(error) }));
    return true;
  }

  return false;
});

async function handleSuggestions(payload) {
  const cfg = await getStorage(["apiBaseUrl", "resumeText", "proficiencies"]);
  const response = await fetch(`${cfg.apiBaseUrl}/jobs/suggest-bullets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_text: cfg.resumeText || "",
      proficiencies: (cfg.proficiencies || "").split(",").map((s) => s.trim()).filter(Boolean),
      job_title: payload.jobTitle || "Unknown Role",
      company: payload.company || "Unknown Company",
      job_description: payload.jobDescription || "",
      max_bullets: 8
    })
  });

  if (!response.ok) {
    throw new Error(`Suggest API failed: ${response.status}`);
  }

  return response.json();
}

async function handleLog(payload) {
  const cfg = await getStorage(["apiBaseUrl", "spreadsheetId", "sheetName"]);
  const response = await fetch(`${cfg.apiBaseUrl}/jobs/log-application`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      spreadsheet_id: cfg.spreadsheetId,
      sheet_name: cfg.sheetName || "Applications",
      url: payload.url,
      company: payload.company,
      job_title: payload.jobTitle,
      status: payload.status || "Applied",
      suggested_bullets: payload.suggestedBullets || []
    })
  });

  if (!response.ok) {
    throw new Error(`Log API failed: ${response.status}`);
  }

  return response.json();
}
