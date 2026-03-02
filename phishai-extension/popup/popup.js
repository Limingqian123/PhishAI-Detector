document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab && tab.url) displayCurrentSite(tab);
  loadStats();
  loadRecentScans();

  document.getElementById('settingsBtn').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });
  document.getElementById('reportBtn').addEventListener('click', () => {
    reportFalsePositive(tab);
  });
});

async function displayCurrentSite(tab) {
  const container = document.getElementById('currentSite');
  chrome.storage.local.get([`result_${tab.id}`], (data) => {
    const cached = data[`result_${tab.id}`];
    if (cached) {
      renderSiteResult(cached);
    } else {
      container.innerHTML = '<div class="loading">尚未分析</div>';
    }
  });
}

function renderSiteResult(result) {
  const container = document.getElementById('currentSite');
  const statusClass = result.is_phishing ? 'danger' : 'safe';
  const statusText = result.is_phishing ? '⚠️ 可疑网站' : '✅ 安全网站';
  const confidence = (result.confidence * 100).toFixed(1);
  container.innerHTML = `
    <div class="site-status ${statusClass}">
      <div class="status-icon">${result.is_phishing ? '⚠️' : '✅'}</div>
      <div class="status-details">
        <div class="status-text">${statusText}</div>
        <div class="confidence">置信度: ${confidence}%</div>
        <div class="explanation">${result.explanation || '无详细解释'}</div>
      </div>
    </div>
  `;
}

async function loadStats() {
  const data = await chrome.storage.local.get(['todayScans', 'totalBlocks']);
  document.getElementById('todayCount').textContent = data.todayScans || 0;
  document.getElementById('blockedCount').textContent = data.totalBlocks || 0;
}

async function loadRecentScans() {
  const data = await chrome.storage.local.get(['recentScans']);
  const recent = data.recentScans || [];
  const list = document.getElementById('recentList');
  if (recent.length === 0) {
    list.innerHTML = '<li class="empty">暂无扫描记录</li>';
    return;
  }
  list.innerHTML = recent.slice(0, 5).map(scan => `
    <li class="${scan.is_phishing ? 'phishing' : 'safe'}">
      <span class="url">${scan.url}</span>
      <span class="result">${scan.is_phishing ? '⚠️' : '✅'}</span>
    </li>
  `).join('');
}

function reportFalsePositive(tab) {
  chrome.tabs.create({ url: `https://your-reporting-url.com?url=${encodeURIComponent(tab.url)}` });
}