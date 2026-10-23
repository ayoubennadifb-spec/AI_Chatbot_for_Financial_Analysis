/* GFC Financial Chatbot — Frontend JS */

const messagesEl = document.getElementById('chat-messages');
const inputEl    = document.getElementById('user-input');
const formEl     = document.getElementById('input-form');
const sendBtn    = document.getElementById('send-btn');
const debugPanel = document.getElementById('debug-panel');
const debugClose = document.getElementById('debug-close');
const debugContent = document.getElementById('debug-content');

// ── Simple markdown renderer ─────────────────────────────────────────────
function renderMarkdown(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,     '<em>$1</em>')
    .replace(/`(.+?)`/g,       '<code>$1</code>')
    .replace(/^---$/gm,        '<hr>')
    .replace(/^- (.+)$/gm,     '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>')
    .replace(/<\/ul>\s*<ul>/g, '')
    .replace(/\n\n/g,          '</p><p>')
    .replace(/\n/g,            '<br>')
    .replace(/^(.+)$/,         '<p>$1</p>');
}

// ── Append a message bubble ───────────────────────────────────────────────
function appendMessage(role, content, meta = null) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'user' ? 'A' : 'AI';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = role === 'bot' ? renderMarkdown(content) : escapeHtml(content);

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  messagesEl.appendChild(wrapper);

  // Meta line (intent, confidence, latency)
  if (meta) {
    const metaEl = document.createElement('div');
    metaEl.className = 'message-meta';
    metaEl.innerHTML =
      `<span class="intent-tag">${meta.intent}</span>` +
      `<span>conf: ${(meta.confidence * 100).toFixed(0)}%</span>` +
      `<span>${meta.elapsed_ms}ms</span>` +
      (meta.entities.company ? `<span>${meta.entities.company}</span>` : '') +
      (meta.entities.year    ? `<span>FY${meta.entities.year}</span>`  : '');
    messagesEl.appendChild(metaEl);
  }

  scrollToBottom();
  return bubble;
}

// ── Typing indicator ─────────────────────────────────────────────────────
function showTyping() {
  const wrapper = document.createElement('div');
  wrapper.className = 'message bot';
  wrapper.id = 'typing-wrapper';

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = 'AI';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = `
    <div class="typing-indicator">
      <span></span><span></span><span></span>
    </div>`;

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  messagesEl.appendChild(wrapper);
  scrollToBottom();
}

function hideTyping() {
  const el = document.getElementById('typing-wrapper');
  if (el) el.remove();
}

// ── Send query to API ─────────────────────────────────────────────────────
async function sendQuery(query) {
  if (!query.trim()) return;

  appendMessage('user', query);
  inputEl.value = '';
  setLoading(true);
  showTyping();

  try {
    const res  = await fetch('/api/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ query }),
    });
    const data = await res.json();
    hideTyping();

    if (!res.ok) {
      appendMessage('bot', `Error: ${data.error || 'Something went wrong.'}`);
      return;
    }

    appendMessage('bot', data.response, {
      intent:     data.intent,
      confidence: data.confidence,
      elapsed_ms: data.elapsed_ms,
      entities:   data.entities,
    });

    // Update debug panel
    debugContent.textContent = JSON.stringify({
      intent:     data.intent,
      confidence: data.confidence,
      entities:   data.entities,
      elapsed_ms: data.elapsed_ms,
      rag_context: data.context?.slice(0, 300) + '...',
    }, null, 2);

  } catch (err) {
    hideTyping();
    appendMessage('bot', 'Connection error. Make sure the server is running.');
  } finally {
    setLoading(false);
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────
function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setLoading(state) {
  sendBtn.disabled = state;
  inputEl.disabled = state;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ── Event listeners ───────────────────────────────────────────────────────
formEl.addEventListener('submit', e => {
  e.preventDefault();
  sendQuery(inputEl.value.trim());
});

// Quick query buttons
document.querySelectorAll('.quick-btn').forEach(btn => {
  btn.addEventListener('click', () => sendQuery(btn.dataset.query));
});

// Debug panel toggle (Ctrl+D)
document.addEventListener('keydown', e => {
  if (e.ctrlKey && e.key === 'd') {
    e.preventDefault();
    debugPanel.style.display = debugPanel.style.display === 'none' ? 'block' : 'none';
  }
});
debugClose.addEventListener('click', () => {
  debugPanel.style.display = 'none';
});

// ── Welcome message ───────────────────────────────────────────────────────
window.addEventListener('load', () => {
  appendMessage('bot',
    "**Welcome to the GFC Financial Analysis Chatbot!**\n\n" +
    "I can answer questions about **Microsoft**, **Tesla**, and **Apple** " +
    "based on their 10-K filings from **FY2021 to FY2023**.\n\n" +
    "Try asking:\n" +
    "- *What is Apple's total revenue for 2023?*\n" +
    "- *Compare all companies*\n" +
    "- *How has Tesla grown over the years?*\n\n" +
    "Or click a quick query in the sidebar. Type **help** to see all options."
  );
});
