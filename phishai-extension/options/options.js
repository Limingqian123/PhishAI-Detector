document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.sync.get({
    apiUrl: 'http://localhost:8000',
    apiKey: '',
    enabled: true,
    threshold: 50,
    warningAction: 'notify',
    anonymousReporting: false,
    localCache: true
  }, (items) => {
    document.getElementById('apiUrl').value = items.apiUrl;
    document.getElementById('apiKey').value = items.apiKey;
    document.getElementById('enabled').checked = items.enabled;
    document.getElementById('threshold').value = items.threshold;
    document.getElementById('thresholdValue').textContent = items.threshold + '%';
    document.getElementById('warningAction').value = items.warningAction;
    document.getElementById('anonymousReporting').checked = items.anonymousReporting;
    document.getElementById('localCache').checked = items.localCache;
  });

  document.getElementById('threshold').addEventListener('input', (e) => {
    document.getElementById('thresholdValue').textContent = e.target.value + '%';
  });

  document.getElementById('saveBtn').addEventListener('click', () => {
    const settings = {
      apiUrl: document.getElementById('apiUrl').value,
      apiKey: document.getElementById('apiKey').value,
      enabled: document.getElementById('enabled').checked,
      threshold: parseInt(document.getElementById('threshold').value),
      warningAction: document.getElementById('warningAction').value,
      anonymousReporting: document.getElementById('anonymousReporting').checked,
      localCache: document.getElementById('localCache').checked
    };
    chrome.storage.sync.set(settings, () => {
      showStatus('设置已保存', 'success');
      chrome.runtime.sendMessage({ action: 'settingsUpdated', settings });
    });
  });

  document.getElementById('resetBtn').addEventListener('click', () => {
    chrome.storage.sync.clear(() => {
      location.reload();
    });
  });
});

function showStatus(message, type) {
  const status = document.getElementById('status');
  status.textContent = message;
  status.className = `status ${type}`;
  status.style.display = 'block';
  setTimeout(() => { status.style.display = 'none'; }, 3000);
}