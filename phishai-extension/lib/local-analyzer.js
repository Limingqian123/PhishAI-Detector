export class LocalAnalyzer {
  constructor() {
    this.cache = new Map();
    this.cacheTTL = 30 * 60 * 1000;
  }

  extractFeatures(url) {
    const features = {};
    try {
      const parsed = new URL(url);
      features.domain = parsed.hostname;
      features.pathLength = parsed.pathname.length;
      features.numParams = parsed.searchParams.size;
      features.hasPort = !!parsed.port;
      features.hasIP = /^\d+\.\d+\.\d+\.\d+$/.test(parsed.hostname);
      features.isShortened = this.isShortened(parsed.hostname);
      features.entropy = this.calculateEntropy(parsed.hostname);
    } catch (e) {
      console.warn('URL解析失败', e);
    }
    return features;
  }

  isShortened(hostname) {
    const shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly'];
    return shorteners.includes(hostname);
  }

  calculateEntropy(str) {
    const freq = {};
    for (let c of str) freq[c] = (freq[c] || 0) + 1;
    return Object.values(freq).reduce((ent, count) => {
      const p = count / str.length;
      return ent - p * Math.log2(p);
    }, 0);
  }

  heuristicScore(features) {
    let score = 0;
    if (features.hasIP) score += 30;
    if (features.isShortened) score += 20;
    if (features.entropy > 4.5) score += 15;
    if (features.numParams > 5) score += 10;
    return score;
  }

  getCached(url) {
    const item = this.cache.get(url);
    if (item && Date.now() - item.timestamp < this.cacheTTL) {
      return item.result;
    }
    return null;
  }

  setCache(url, result) {
    this.cache.set(url, { result, timestamp: Date.now() });
    if (this.cache.size > 1000) {
      const oldest = [...this.cache.entries()].sort((a, b) => a[1].timestamp - b[1].timestamp)[0];
      this.cache.delete(oldest[0]);
    }
  }
}