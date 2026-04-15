const speciesCatalog = {
  bison: "Bison",
  elk: "Elk",
  wolf: "Gray Wolf",
  grizzly_bear: "Grizzly Bear",
  black_bear: "Black Bear",
  moose: "Moose",
  mountain_goat: "Mountain Goat",
  bighorn_sheep: "Bighorn Sheep",
  otter: "River Otter",
  eagle: "Bald Eagle",
};

const parkBaseScores = {
  Yellowstone: { bison: 3.8, elk: 3.1, wolf: 2.7, grizzly_bear: 1.7, eagle: 1.5, moose: 1.4 },
  Glacier: { grizzly_bear: 3.5, mountain_goat: 3.4, moose: 2.5, bighorn_sheep: 2.1, eagle: 1.6, wolf: 1.2 },
  "Grand Teton": { elk: 3.7, moose: 3.0, bison: 2.2, eagle: 1.8, otter: 1.1, wolf: 1.3 },
  Olympic: { black_bear: 3.1, otter: 3.0, eagle: 2.0, wolf: 1.2, elk: 1.4, moose: 0.8 },
  "Mount Rainier": { mountain_goat: 3.9, black_bear: 2.2, eagle: 2.0, bighorn_sheep: 1.9, elk: 1.3, wolf: 0.9 },
};

const timeBoosts = {
  dawn: { bison: 1.1, elk: 1.0, wolf: 0.8, moose: 0.6 },
  day: { mountain_goat: 1.0, eagle: 0.9, otter: 0.7, bighorn_sheep: 0.7 },
  dusk: { elk: 1.0, grizzly_bear: 0.8, wolf: 0.9, black_bear: 0.7, moose: 0.6 },
  night: { wolf: 1.2, black_bear: 0.9, otter: 0.8, moose: 0.5 },
};

const seasonBoosts = {
  winter: { wolf: 0.8, eagle: 0.7, otter: 0.5, bison: 0.3 },
  spring: { moose: 0.9, black_bear: 0.8, bighorn_sheep: 0.6, elk: 0.4 },
  summer: { bison: 0.8, mountain_goat: 0.8, otter: 0.7, eagle: 0.5 },
  fall: { elk: 1.0, grizzly_bear: 0.8, wolf: 0.7, moose: 0.5 },
};

const weatherBoosts = {
  sunny: { eagle: 0.8, mountain_goat: 0.7, bighorn_sheep: 0.5 },
  cloudy: { moose: 0.6, elk: 0.5, black_bear: 0.4 },
  rainy: { otter: 0.9, black_bear: 0.6, moose: 0.4 },
};

const regionBoosts = {
  north: { bison: 0.6, moose: 0.6, eagle: 0.4 },
  south: { elk: 0.6, black_bear: 0.5, otter: 0.3 },
  east: { mountain_goat: 0.6, bighorn_sheep: 0.6, eagle: 0.3 },
  west: { otter: 0.7, wolf: 0.5, black_bear: 0.4 },
};

const sampleScenario = {
  park: "Yellowstone",
  month: 9,
  time_of_day: "dawn",
  region: "north",
  weather: "cloudy",
  temp_c: 7,
};

function seasonFromMonth(month) {
  if ([12, 1, 2].includes(month)) return "winter";
  if ([3, 4, 5].includes(month)) return "spring";
  if ([6, 7, 8].includes(month)) return "summer";
  return "fall";
}

function createScoreTable() {
  return Object.keys(speciesCatalog).reduce((scores, key) => {
    scores[key] = { value: 0.25, reasons: [] };
    return scores;
  }, {});
}

function applyBoosts(scores, boosts, reasonLabel) {
  if (!boosts) return;

  Object.entries(boosts).forEach(([species, amount]) => {
    if (!scores[species]) return;
    scores[species].value += amount;
    scores[species].reasons.push(`${reasonLabel} +${amount.toFixed(1)}`);
  });
}

function applyTemperature(scores, tempC) {
  if (Number.isNaN(tempC)) return;

  if (tempC <= 4) {
    applyBoosts(scores, { wolf: 0.8, moose: 0.6, eagle: 0.4 }, `cold ${tempC}C`);
    return;
  }

  if (tempC >= 20) {
    applyBoosts(scores, { bison: 0.7, otter: 0.5, black_bear: 0.3 }, `warm ${tempC}C`);
    return;
  }

  applyBoosts(scores, { elk: 0.5, black_bear: 0.4, mountain_goat: 0.3 }, `mild ${tempC}C`);
}

function normalize(scores) {
  const values = Object.entries(scores).map(([species, data]) => {
    const softened = Math.exp(data.value / 2.7);
    return { species, softened, reasons: data.reasons };
  });
  const total = values.reduce((sum, item) => sum + item.softened, 0);

  return values
    .map((item) => ({
      species: item.species,
      probability: total === 0 ? 0 : item.softened / total,
      reasons: item.reasons.slice().sort().slice(-3),
    }))
    .sort((left, right) => right.probability - left.probability);
}

function computePredictions(payload) {
  const scores = createScoreTable();
  const season = seasonFromMonth(payload.month);

  applyBoosts(scores, parkBaseScores[payload.park], payload.park);
  applyBoosts(scores, timeBoosts[payload.time_of_day], payload.time_of_day);
  applyBoosts(scores, seasonBoosts[season], season);
  applyBoosts(scores, weatherBoosts[payload.weather], payload.weather || "weather");
  applyBoosts(scores, regionBoosts[payload.region], payload.region || "region");
  applyTemperature(scores, payload.temp_c);

  return {
    season,
    results: normalize(scores).slice(0, 5),
  };
}

function buildResultCard(result, rank) {
  const percent = Math.round(result.probability * 100);
  const card = document.createElement("article");
  card.className = "result-card";

  const reasonsMarkup = result.reasons.length
    ? result.reasons.map((reason) => `<span>${reason}</span>`).join("")
    : "<span>baseline habitat fit</span>";

  card.innerHTML = `
    <div class="result-head">
      <div>
        <div class="result-name">${rank}. ${speciesCatalog[result.species]}</div>
      </div>
      <div class="result-score">${percent}% match</div>
    </div>
    <div class="result-bar"><span style="width: ${percent}%"></span></div>
    <p>This sighting ranks well for the selected park conditions and seasonal context.</p>
    <div class="result-reasons">${reasonsMarkup}</div>
  `;

  return card;
}

function renderResults(payload) {
  const container = document.getElementById("results");
  const summary = document.getElementById("summary-text");
  const { season, results } = computePredictions(payload);

  container.innerHTML = "";
  summary.textContent = `${payload.park}, ${season}, ${payload.time_of_day} conditions. These are transparent demo predictions for quick public exploration.`;

  results.forEach((result, index) => {
    container.appendChild(buildResultCard(result, index + 1));
  });
}

function currentPayload() {
  const month = Number(document.getElementById("month").value);
  const tempRaw = document.getElementById("temp_c").value;

  return {
    park: document.getElementById("park").value,
    month: Number.isFinite(month) && month >= 1 && month <= 12 ? month : 7,
    time_of_day: document.getElementById("time_of_day").value,
    region: document.getElementById("region").value,
    weather: document.getElementById("weather").value,
    temp_c: tempRaw === "" ? Number.NaN : Number(tempRaw),
  };
}

function loadSample() {
  document.getElementById("park").value = sampleScenario.park;
  document.getElementById("month").value = String(sampleScenario.month);
  document.getElementById("time_of_day").value = sampleScenario.time_of_day;
  document.getElementById("region").value = sampleScenario.region;
  document.getElementById("weather").value = sampleScenario.weather;
  document.getElementById("temp_c").value = String(sampleScenario.temp_c);
  renderResults(sampleScenario);
}

document.getElementById("predict-form").addEventListener("submit", (event) => {
  event.preventDefault();
  renderResults(currentPayload());
});

document.getElementById("load-sample").addEventListener("click", loadSample);

document.getElementById("results").innerHTML =
  '<div class="empty-state">Try Yellowstone at dawn or Glacier on a sunny day to see the rankings come alive.</div>';
