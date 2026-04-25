// Claude Auto Continue — content script
// 在 claude.ai 页面扫描并自动点击 Continue / 继续 类按钮。
// 设计原则：allowlist 匹配（不命中就不点），加频率限制，避免误点登录/删除等按钮。

(() => {
  'use strict';

  const DEFAULTS = {
    enabled: true,
    // 必须精确匹配或严格前缀匹配这些文本才会点击（大小写不敏感）
    include: [
      'continue',
      'continue generating',
      'continue anyway',
      '继续',
      '继续生成'
    ],
    // 这些子串出现在按钮文本中则跳过（防止点登录/取消等）
    exclude: [
      'continue with',   // Continue with Google / Apple
      'continue as',     // Continue as guest
      'cancel',
      'discard',
      'delete',
      'log out',
      'sign out',
      '取消',
      '删除',
      '退出'
    ],
    minIntervalMs: 1500,  // 两次点击最少间隔
    cooldownAfterClickMs: 3000 // 点完同一个按钮多久内不再重点
  };

  let config = { ...DEFAULTS };
  let clickCount = 0;
  let lastClickTime = 0;
  const recentlyClicked = new WeakMap(); // btn -> timestamp

  // 读初始配置
  chrome.storage.local.get(['enabled', 'include', 'exclude', 'clickCount'], (r) => {
    if (typeof r.enabled === 'boolean') config.enabled = r.enabled;
    if (Array.isArray(r.include) && r.include.length) config.include = r.include;
    if (Array.isArray(r.exclude)) config.exclude = r.exclude;
    if (typeof r.clickCount === 'number') clickCount = r.clickCount;
  });

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== 'local') return;
    if (changes.enabled) config.enabled = changes.enabled.newValue;
    if (changes.include && Array.isArray(changes.include.newValue)) config.include = changes.include.newValue;
    if (changes.exclude && Array.isArray(changes.exclude.newValue)) config.exclude = changes.exclude.newValue;
    if (changes.clickCount && typeof changes.clickCount.newValue === 'number') clickCount = changes.clickCount.newValue;
  });

  function normalize(s) {
    return (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
  }

  function matchesButton(btn) {
    const text = normalize(btn.innerText || btn.textContent || '');
    if (!text || text.length > 60) return false;

    for (const ex of config.exclude) {
      if (ex && text.includes(normalize(ex))) return false;
    }
    for (const inc of config.include) {
      const n = normalize(inc);
      if (!n) continue;
      if (text === n) return true;
      // 允许"Continue" 后跟简短修饰，但避免匹配"Continue with Google"（已被 exclude 过滤）
      if (text.startsWith(n + ' ') && text.length <= n.length + 20) return true;
    }
    return false;
  }

  function isVisible(el) {
    if (!el || !el.isConnected) return false;
    if (el.disabled) return false;
    if (el.getAttribute('aria-disabled') === 'true') return false;
    if (!el.offsetParent && getComputedStyle(el).position !== 'fixed') return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }

  function scan() {
    if (!config.enabled) return;

    const now = Date.now();
    if (now - lastClickTime < config.minIntervalMs) return;

    const candidates = document.querySelectorAll('button, [role="button"]');
    for (const btn of candidates) {
      const lastTs = recentlyClicked.get(btn);
      if (lastTs && now - lastTs < config.cooldownAfterClickMs) continue;
      if (!isVisible(btn)) continue;
      if (!matchesButton(btn)) continue;

      try {
        btn.click();
        recentlyClicked.set(btn, now);
        lastClickTime = now;
        clickCount++;
        chrome.storage.local.set({
          clickCount,
          lastClickedAt: new Date().toISOString(),
          lastClickedText: (btn.innerText || btn.textContent || '').trim().slice(0, 80)
        });
        // eslint-disable-next-line no-console
        console.log('[Auto Continue] clicked:', btn.innerText?.trim());
      } catch (err) {
        console.warn('[Auto Continue] click failed:', err);
      }
      break; // 一次只点一个
    }
  }

  // DOM 变化时检测
  let scheduled = false;
  function schedule() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      scan();
    });
  }

  const observer = new MutationObserver(schedule);
  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });

  // 页面初始扫一次 + 每 2 秒兜底扫描一次（防止某些渲染未触发 mutation）
  scan();
  setInterval(scan, 2000);

  console.log('[Auto Continue] content script loaded');
})();
