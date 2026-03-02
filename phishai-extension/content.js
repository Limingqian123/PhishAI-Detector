chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'showWarning') {
    injectWarning(message.result);
  } else if (message.action === 'showLinkResult') {
    showLinkAnalysisResult(message.result, message.url);
  }
});

function injectWarning(result) {
  const existing = document.getElementById('phishai-warning');
  if (existing) existing.remove();

  const warningDiv = document.createElement('div');
  warningDiv.id = 'phishai-warning';
  warningDiv.innerHTML = `
    <div class="phishai-warning-container">
      <div class="phishai-warning-header">
        <img src="${chrome.runtime.getURL('assets/warning.png')}" width="24" height="24">
        <h3>⚠️ 安全警告</h3>
        <button class="phishai-close">&times;</button>
      </div>
      <div class="phishai-warning-body">
        <p><strong>PhishAI Detector 检测到当前页面可能为钓鱼网站</strong></p>
        <p>置信度: ${(result.confidence * 100).toFixed(1)}%</p>
        <p>分析结果: ${result.explanation}</p>
      </div>
      <div class="phishai-warning-footer">
        <button class="phishai-btn phishai-btn-danger" id="phishai-leave">立即离开</button>
        <button class="phishai-btn phishai-btn-warning" id="phishai-ignore">继续访问（不推荐）</button>
      </div>
    </div>
  `;

  document.body.appendChild(warningDiv);

  document.getElementById('phishai-leave').addEventListener('click', () => {
    window.history.back();
  });
  document.getElementById('phishai-ignore').addEventListener('click', () => {
    warningDiv.remove();
    chrome.storage.local.set({ [`ignore_${window.location.href}`]: true });
  });
  document.querySelector('.phishai-close').addEventListener('click', () => {
    warningDiv.remove();
  });
}

function showLinkAnalysisResult(result, url) {
  const tooltip = document.createElement('div');
  tooltip.className = 'phishai-tooltip';
  tooltip.innerHTML = `
    <div class="phishai-tooltip-content">
      <strong>${result.is_phishing ? '⚠️ 可疑链接' : '✅ 安全链接'}</strong>
      <p>${result.explanation}</p>
      <small>置信度: ${(result.confidence * 100).toFixed(1)}%</small>
    </div>
  `;
  document.body.appendChild(tooltip);
  document.addEventListener('mousemove', (e) => {
    tooltip.style.left = e.pageX + 10 + 'px';
    tooltip.style.top = e.pageY + 10 + 'px';
  });
  setTimeout(() => tooltip.remove(), 3000);
}