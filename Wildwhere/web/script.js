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

  const API = 'http://127.0.0.1:5000/predict';
  const out = document.getElementById('output');
  out.textContent = 'Loading...';

  try {
    const res = await fetch(API, {
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

