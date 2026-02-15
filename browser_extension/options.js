const ids = ["apiBaseUrl", "spreadsheetId", "sheetName", "resumeText", "proficiencies"];

async function load() {
  const data = await chrome.storage.sync.get(ids);
  ids.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.value = data[id] || "";
  });
}

async function save() {
  const payload = {};
  ids.forEach((id) => {
    const el = document.getElementById(id);
    payload[id] = el ? el.value : "";
  });
  await chrome.storage.sync.set(payload);
  document.getElementById("status").textContent = "Saved.";
}

document.getElementById("saveBtn").addEventListener("click", save);
load();
