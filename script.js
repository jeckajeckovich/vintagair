const SOURCES = [
  'chukotavia_sales.csv',
  'chukotavia_api_results.csv'
];

async function loadCSV(url) {
  const res = await fetch(url);
  const text = await res.text();

  const lines = text.trim().split('\n');
  const headers = lines[0].split(',');

  return lines.slice(1).map(line => {
    const values = line.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = values[i]?.trim() || '';
    });
    return normalizeFlight(obj);
  });
}

function normalizeFlight(f) {
  return {
    date: f.date,
    flight_number: f.flight_number || f.flight || '',
    origin: f.origin,
    destination: f.destination,
    departure: f.departure,
    arrival: f.arrival,
    aircraft: f.aircraft || '',
    price: f.price ? Number(f.price) : null,
    available: f.available === '' ? null : Number(f.available)
  };
}

async function loadAllFlights() {
  const datasets = await Promise.all(
    SOURCES.map(src => loadCSV(src))
  );

  const allFlights = datasets.flat();

  const unique = {};
  allFlights.forEach(f => {
    const key = `${f.date}_${f.flight_number}_${f.origin}_${f.destination}`;
    if (!unique[key]) unique[key] = f;
  });

  return Object.values(unique);
}

async function render() {
  const flights = await loadAllFlights();
  const tbody = document.getElementById('flights');
  tbody.innerHTML = '';

  flights.forEach(f => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${f.date}</td>
      <td>${f.flight_number}</td>
      <td>${f.origin}</td>
      <td>${f.destination}</td>
      <td>${f.departure}</td>
      <td>${f.arrival}</td>
      <td>${f.aircraft}</td>
      <td>${f.price ? f.price + ' ₽' : '—'}</td>
      <td>${f.available ?? '—'}</td>
    `;
    tbody.appendChild(tr);
  });
}

render();
