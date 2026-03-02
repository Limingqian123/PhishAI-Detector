import { LocalAnalyzer } from './lib/local-analyzer.js';
import { PolicyEngine } from './lib/policy-engine.js';

const localAnalyzer = new LocalAnalyzer();
const policyEngine = new PolicyEngine();

// 初始化
policyEngine.loadRules();

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
    await analyzeTab(tabId, tab.url);
  }
});

chrome.webNavigation.onCompleted.addListener(async (details) => {
  if (details.frameId === 0) {
    const tab = await chrome.tabs.get(details.tabId);
    if (tab.url && tab.url.startsWith('http')) {
      await analyzeTab(details.tabId, tab.url);
    }
  }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeUrl') {
    analyzeUrlWithCache(request.url).then(sendResponse);
    return true;
  }
});

async function analyzeTab(tabId, url) {
  const result = await analyzeUrlWithCache(url);
  updateUI(tabId, result);

  // 策略决策
  const decision = policyEngine.evaluate(url, result.confidence * 100);
  if (decision.action === 'block') {
    chrome.tabs.update(tabId, { url: chrome.runtime.getURL('blocked.html') });
  } else if (decision.action === 'notify' && result.is_phishing) {
    showNotification(result, url);
  }
}

async function analyzeUrlWithCache(url) {
  // 1. 本地缓存
  const cached = localAnalyzer.getCached(url);
  if (cached) return cached;

  // 2. 本地启发式分析
  const features = localAnalyzer.extractFeatures(url);
  const heuristicScore = localAnalyzer.heuristicScore(features);
  if (heuristicScore > 60) {
    const result = {
      is_phishing: true,
      confidence: heuristicScore / 100,
      explanation: 'URL特征高度可疑',
      source: 'heuristic'
    };
    localAnalyzer.setCache(url, result);
    return result;
  }

  // 3. 调用后端API
  try {
    const response = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const result = await response.json();
    localAnalyzer.setCache(url, result);
    return result;
  } catch (error) {
    console.error('后端分析失败', error);
    const fallback = {
      is_phishing: heuristicScore > 40,
      confidence: heuristicScore / 100,
      explanation: '基于本地规则判断（后端不可用）',
      source: 'fallback'
    };
    localAnalyzer.setCache(url, fallback);
    return fallback;
  }
}

function updateUI(tabId, result) {
  chrome.action.setIcon({
    tabId,
    path: result.is_phishing ? 'assets/warning.png' : 'assets/safe.png'
  });
  chrome.action.setBadgeText({ tabId, text: result.is_phishing ? '!' : '' });
  chrome.storage.local.set({ [`result_${tabId}`]: result });
}

let notifiedUrls = new Set();
function showNotification(result, url) {
  if (notifiedUrls.has(url)) return;
  notifiedUrls.add(url);
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'assets/warning.png',
    title: 'PhishAI 安全提醒',
    message: `检测到可疑网站：${result.explanation}`,
    priority: 2
  });
}

// 右键菜单
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'analyze-link',
    title: '用PhishAI检测此链接',
    contexts: ['link']
  });
});
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'analyze-link' && info.linkUrl) {
    analyzeUrlWithCache(info.linkUrl).then(result => {
      chrome.tabs.sendMessage(tab.id, {
        action: 'showLinkResult',
        result: result,
        url: info.linkUrl
      });
    });
  }
});