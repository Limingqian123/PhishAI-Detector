export class PolicyEngine {
  constructor() {
    this.rules = [];
  }

  async loadRules() {
    try {
      const response = await fetch('https://your-management.com/policies');
      this.rules = await response.json();
    } catch {
      this.rules = [
        { type: 'threshold', value: 50, action: 'block' },
        { type: 'whitelist', domains: ['bank.com', 'paypal.com'], action: 'allow' }
      ];
    }
  }

  evaluate(url, score) {
    const domain = new URL(url).hostname;
    const whitelist = this.rules.find(r => r.type === 'whitelist');
    if (whitelist && whitelist.domains.includes(domain)) {
      return { action: 'allow', reason: '白名单域名' };
    }
    const thresholdRule = this.rules.find(r => r.type === 'threshold');
    if (thresholdRule && score >= thresholdRule.value) {
      return { action: thresholdRule.action, reason: `超过阈值${thresholdRule.value}` };
    }
    return { action: 'notify', reason: '默认提醒' };
  }
}