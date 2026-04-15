const API_BASE =
  window.location.protocol === 'file:'
    ? 'http://127.0.0.1:5000'
    : window.location.origin;

async function updateStatus() {
  const status = document.getElementById('status');

  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) {
      throw new Error(`Health check returned ${res.status}`);
    }

    const data = await res.json();
    status.textContent = data.using_fallback
      ? 'API is live. The fallback model is active.'
      : 'API is live. The trained model is loaded.';
  } catch (error) {
    status.textContent = `Could not reach the API at ${API_BASE}. Start the Flask server, then refresh.`;
  }
}

async function predict() {
  const payload = {
    park: document.getElementById('park').value,
    month: Number(document.getElementById('month').value),
    time_of_day: document.getElementById('time_of_day').value,
    region: document.getElementById('region').value || null,
    weather: document.getElementById('weather').value || null,
    temp_c: document.getElementById('temp_c').value ? Number(document.getElementById('temp_c').value) : null,
    top_n: Number(document.getElementById('top_n').value) || 5
  };

  const out = document.getElementById('output');
  out.textContent = 'Loading...';

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const text = await res.text();
      out.textContent = `Error ${res.status}: ${text}`;
      return;
    }

    const data = await res.json();
    const lines = (data.results || []).map(r =>
      `${r.species.padEnd(16, ' ')}  ${r.probability.toFixed(3)}`
    );
    out.textContent =
      `park: ${data.park}\nmonth: ${data.month}\ntime_of_day: ${data.time_of_day}\n\n` +
      lines.join('\n');

  } catch (err) {
    out.textContent = `Request failed: ${err}`;
  }
}
document.getElementById('predictBtn').addEventListener('click', predict);
updateStatus();
