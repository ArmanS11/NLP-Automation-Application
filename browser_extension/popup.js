async function activeTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  return tabs[0];
}

async function getJobContextFromTab(tabId) {
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => window.__JOB_COPILOT_CONTEXT__ || null
  });
  return result;
}

function setStatus(text) {
  document.getElementById("status").textContent = text;
}

document.getElementById("scanBtn").addEventListener("click", async () => {
  try {
    const tab = await activeTab();
    const ctx = await getJobContextFromTab(tab.id);
    if (!ctx) {
      setStatus("No job context detected on this page.");
      return;
    }

    const response = await chrome.runtime.sendMessage({
      type: "GENERATE_SUGGESTIONS",
      payload: ctx
    });

    if (!response.ok) {
      setStatus(`Suggestion error: ${response.error}`);
      return;
    }

    const bullets = response.result?.tailored_resume?.experience_highlights || [];
    chrome.storage.local.set({ latestJobContext: ctx, latestSuggestedBullets: bullets });
    setStatus(`Top suggestions:\n- ${bullets.slice(0, 5).join("\n- ")}`);
  } catch (e) {
    setStatus(String(e));
  }
});

document.getElementById("logBtn").addEventListener("click", async () => {
  try {
    const { latestJobContext, latestSuggestedBullets } = await chrome.storage.local.get([
      "latestJobContext",
      "latestSuggestedBullets"
    ]);
    if (!latestJobContext) {
      setStatus("Run Scan Current Job first.");
      return;
    }

    const response = await chrome.runtime.sendMessage({
      type: "LOG_APPLICATION",
      payload: {
        url: latestJobContext.url,
        company: latestJobContext.company,
        jobTitle: latestJobContext.jobTitle,
        status: "Applied",
        suggestedBullets: latestSuggestedBullets || []
      }
    });

    if (!response.ok) {
      setStatus(`Log error: ${response.error}`);
      return;
    }

    setStatus("Application logged to spreadsheet.");
  } catch (e) {
    setStatus(String(e));
  }
});
