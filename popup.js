const DEFAULTS = {
  include: [
    'continue',
    'continue generating',
    'continue anyway',
    '继续',
    '继续生成'
  ],
  exclude: [
    'continue with',
    'continue as',
    'cancel',
    'discard',
    'delete',
    'log out',
    'sign out',
    '取消',
    '删除',
    '退出'
  ]
};

const $ = (id) => document.getElementById(id);

function toText(arr) {
  return (arr || []).join('\n');
}

function toArr(text) {
  return text
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
}

function toast(msg) {
  const el = $('toast');
  el.textContent = msg;
  setTimeout(() => {
    if (el.textContent === msg) el.textContent = '';
  }, 2000);
}

function formatTime(iso) {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    const now = Date.now();
    const diff = Math.floor((now - d.getTime()) / 1000);
    if (diff < 60) return `${diff} 秒前`;
    if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`;
    return d.toLocaleString('zh-CN');
  } catch {
    return '';
  }
}

function load() {
  chrome.storage.local.get(
    ['enabled', 'include', 'exclude', 'clickCount', 'lastClickedAt', 'lastClickedText'],
    (r) => {
      $('enabled').checked = r.enabled !== false;
      $('include').value = toText(r.include && r.include.length ? r.include : DEFAULTS.include);
      $('exclude').value = toText(r.exclude || DEFAULTS.exclude);
      $('count').textContent = r.clickCount || 0;
      if (r.lastClickedAt) {
        $('last').textContent = `上次：${formatTime(r.lastClickedAt)}${
          r.lastClickedText ? '（' + r.lastClickedText + '）' : ''
        }`;
      }
    }
  );
}

$('enabled').addEventListener('change', (e) => {
  chrome.storage.local.set({ enabled: e.target.checked });
  toast(e.target.checked ? '已启用' : '已暂停');
});

$('save').addEventListener('click', () => {
  const include = toArr($('include').value);
  const exclude = toArr($('exclude').value);
  if (!include.length) {
    toast('匹配列表不能为空');
    return;
  }
  chrome.storage.local.set({ include, exclude }, () => toast('已保存'));
});

$('reset').addEventListener('click', () => {
  $('include').value = toText(DEFAULTS.include);
  $('exclude').value = toText(DEFAULTS.exclude);
  chrome.storage.local.set({ include: DEFAULTS.include, exclude: DEFAULTS.exclude }, () =>
    toast('已重置')
  );
});

$('clear-count').addEventListener('click', () => {
  chrome.storage.local.set({ clickCount: 0, lastClickedAt: '', lastClickedText: '' }, () => {
    $('count').textContent = '0';
    $('last').textContent = '';
    toast('计数已清零');
  });
});

load();
