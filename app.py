import csv
from pathlib import Path
from flask import Flask, render_template_string, redirect, url_for, abort

app = Flask(__name__)
CSV_PATH = Path("data/sample_bins.csv")

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EcoTrack | Smart Waste Operations</title>
  <link rel="preconnect" href="https://unpkg.com">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    :root {
      --green: #16835d; --green-dark: #116447; --green-soft: #e8f6ef;
      --ink: #172b25; --muted: #71817a; --line: #e5ece8;
      --canvas: #f5f8f6; --white: #fff; --red: #d94848; --amber: #c78318;
      --shadow: 0 8px 24px rgba(27, 61, 46, .06);
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--canvas); color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Arial, sans-serif; }
    button, a { font: inherit; }
    .app { min-height: 100vh; display: grid; grid-template-columns: 248px minmax(0, 1fr); }
    .sidebar { background: #123d30; color: #eaf6ef; padding: 26px 16px; display: flex; flex-direction: column; gap: 30px; }
    .brand { display: flex; align-items: center; gap: 12px; padding: 0 10px; }
    .brand-mark { width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center;
      background: #d5f4e2; color: #126143; font-size: 22px; font-weight: 900; }
    .brand strong { display: block; font-size: 17px; letter-spacing: -.4px; }
    .brand small { display: block; margin-top: 3px; color: #a9c9b8; font-size: 11px; letter-spacing: 1.4px; text-transform: uppercase; }
    .nav-label { padding: 0 12px; color: #8eb6a1; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; }
    .nav { display: grid; gap: 7px; }
    .nav a { display: flex; gap: 12px; align-items: center; color: #c6ded1; text-decoration: none;
      padding: 12px; border-radius: 11px; font-size: 13px; font-weight: 600; transition: .18s; }
    .nav a:hover, .nav a.active { background: #23634b; color: #fff; }
    .nav-icon { width: 22px; text-align: center; font-size: 17px; }
    .side-note { margin-top: auto; padding: 15px; border: 1px solid rgba(255,255,255,.12); border-radius: 14px;
      background: rgba(255,255,255,.05); }
    .side-note strong { display: block; font-size: 12px; margin-bottom: 7px; }
    .side-note p { color: #b7d2c3; font-size: 11px; line-height: 1.6; margin: 0; }
    main { min-width: 0; padding: 28px clamp(16px, 3vw, 38px) 38px; }
    .topbar { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 28px; }
    .eyebrow { color: var(--green); text-transform: uppercase; letter-spacing: 1.6px; font-size: 10px; font-weight: 800; margin-bottom: 7px; }
    h1 { margin: 0; font-size: clamp(24px, 3vw, 31px); letter-spacing: -1px; }
    .subtitle { color: var(--muted); font-size: 13px; margin: 8px 0 0; }
    .top-actions { display: flex; align-items: center; gap: 10px; }
    .demo-pill { background: #fff6df; color: #96630b; border: 1px solid #f2e2b8; padding: 9px 12px; border-radius: 999px; font-size: 11px; font-weight: 800; white-space: nowrap; }
    .date-label { color: var(--muted); font-size: 12px; white-space: nowrap; }
    .section-heading { display: flex; align-items: end; justify-content: space-between; gap: 12px; margin: 28px 0 14px; }
    h2 { margin: 0; font-size: 17px; letter-spacing: -.35px; }
    .section-caption { margin: 5px 0 0; color: var(--muted); font-size: 12px; }
    .cards { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
    .card, .panel { background: var(--white); border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow); }
    .metric { padding: 18px; position: relative; overflow: hidden; }
    .metric-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .metric-label { color: var(--muted); font-size: 12px; font-weight: 650; }
    .metric-icon { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 12px; background: var(--green-soft); font-size: 18px; }
    .metric-value { font-size: 30px; font-weight: 800; letter-spacing: -1px; margin-top: 16px; }
    .metric-foot { color: var(--muted); font-size: 11px; margin-top: 5px; }
    .metric-foot .danger { color: var(--red); font-weight: 750; }
    .two-col { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(280px, .9fr); gap: 16px; align-items: stretch; }
    .panel { padding: 19px; min-width: 0; }
    .panel-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 14px; }
    .panel-head h3 { font-size: 14px; margin: 0; }
    .panel-head p { color: var(--muted); font-size: 11px; margin: 5px 0 0; }
    .legend { display: flex; flex-wrap: wrap; gap: 12px; color: var(--muted); font-size: 11px; margin: 0 0 12px; }
    .legend span { display: inline-flex; align-items: center; gap: 6px; }
    .dot { width: 8px; height: 8px; display: inline-block; border-radius: 50%; }
    #map { height: 360px; border-radius: 12px; background: #edf2ef; overflow: hidden; }
    .route-summary { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }
    .mini-stat { background: #f5faf7; border: 1px solid #e5f1e9; border-radius: 12px; padding: 13px; }
    .mini-stat span { display: block; color: var(--muted); font-size: 11px; }
    .mini-stat strong { display: block; font-size: 23px; margin-top: 6px; letter-spacing: -.5px; }
    .route-list { margin: 0; padding: 0; list-style: none; display: grid; gap: 9px; max-height: 245px; overflow: auto; }
    .route-list li { display: flex; align-items: center; gap: 10px; padding: 9px 0; border-bottom: 1px solid #edf1ee; font-size: 12px; }
    .route-num { width: 27px; height: 27px; flex: 0 0 27px; display: grid; place-items: center; background: var(--green-soft); color: var(--green-dark); border-radius: 9px; font-weight: 800; }
    .route-item-main { font-weight: 750; }
    .route-item-sub { color: var(--muted); font-size: 10px; margin-top: 3px; }
    .route-empty { color: var(--muted); font-size: 12px; padding: 18px 0; }
    .alerts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
    .alert-card { padding: 14px; background: #fffaf0; border: 1px solid #f6e6c3; border-left: 4px solid var(--amber); border-radius: 12px; }
    .alert-card strong { font-size: 13px; }
    .alert-card p { color: #7e6b47; font-size: 11px; margin: 6px 0; }
    .alert-level { color: var(--red); font-weight: 800; font-size: 11px; }
    .analytics { display: grid; grid-template-columns: 1.2fr .8fr; gap: 16px; }
    .chart-wrap { height: 245px; position: relative; }
    .table-panel { margin-top: 16px; padding: 0; overflow: hidden; }
    .table-toolbar { padding: 18px 19px; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
    .search { width: min(100%, 260px); padding: 10px 12px; border: 1px solid var(--line); border-radius: 10px; outline: none; font-size: 12px; background: #fbfdfc; }
    .search:focus { border-color: #77b99b; box-shadow: 0 0 0 3px #e6f5ec; }
    .table-scroll { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; min-width: 760px; }
    th { text-align: left; padding: 12px 18px; color: #6e8177; background: #f7faf8; font-size: 10px; text-transform: uppercase; letter-spacing: .8px; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
    td { padding: 14px 18px; border-bottom: 1px solid #edf1ee; font-size: 12px; }
    tbody tr:hover { background: #fbfdfb; }
    .bin-id { font-weight: 800; }
    .area-name { color: var(--muted); margin-top: 3px; font-size: 10px; }
    .fill-cell { min-width: 130px; }
    .fill-top { display: flex; justify-content: space-between; gap: 8px; font-size: 11px; margin-bottom: 6px; }
    .progress { height: 6px; border-radius: 99px; background: #eaf0ec; overflow: hidden; }
    .progress span { display: block; height: 100%; border-radius: inherit; }
    .badge { display: inline-flex; align-items: center; padding: 5px 8px; border-radius: 99px; font-size: 10px; font-weight: 800; white-space: nowrap; }
    .high { background: #fdeaea; color: #ba3535; } .medium { background: #fff2d9; color: #98620b; }
    .low { background: #e8f5ed; color: #27724e; } .collected { background: #e8f5ed; color: #27724e; }
    .pending { background: #eef3f0; color: #61756a; }
    .action-form { margin: 0; }
    .btn { background: var(--green); color: white; border: 0; border-radius: 8px; padding: 8px 10px; font-size: 10px; font-weight: 800; cursor: pointer; white-space: nowrap; }
    .btn:hover { background: var(--green-dark); }
    .collected-label { color: var(--green); font-size: 11px; font-weight: 800; }
    .footer { text-align: center; color: #8a9991; font-size: 10px; padding: 25px 0 0; }
    .route-number { background: transparent; border: 0; }
    @media (max-width: 1100px) { .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); } .two-col { grid-template-columns: 1fr; } }
    @media (max-width: 760px) {
      .app { grid-template-columns: 1fr; }
      .sidebar { padding: 14px; gap: 15px; }
      .brand { padding: 0 4px; }
      .nav-label, .side-note { display: none; }
      .nav { display: flex; overflow-x: auto; gap: 5px; }
      .nav a { white-space: nowrap; padding: 10px; font-size: 11px; }
      .nav-icon { width: auto; }
      main { padding: 22px 14px; }
      .topbar { align-items: flex-start; flex-direction: column; margin-bottom: 22px; }
      .top-actions { width: 100%; justify-content: space-between; }
      .cards { gap: 10px; }
      .metric { padding: 14px; }
      .metric-value { font-size: 25px; }
      .metric-icon { width: 32px; height: 32px; }
      .alerts, .analytics { grid-template-columns: 1fr; }
      .section-heading { margin-top: 23px; }
      #map { height: 300px; }
      .panel { padding: 14px; }
      .table-toolbar { align-items: flex-start; flex-direction: column; }
      .search { width: 100%; }
    }
    @media (max-width: 390px) { .cards { grid-template-columns: 1fr 1fr; } .metric-label { font-size: 10px; } }
  </style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">♻</div>
      <div><strong>EcoTrack</strong><small>Smart City Operations</small></div>
    </div>
    <div class="nav-label">Workspace</div>
    <nav class="nav">
      <a class="active" href="#overview"><span class="nav-icon">▦</span>Overview</a>
      <a href="#locations"><span class="nav-icon">⌖</span>Bin locations</a>
      <a href="#route"><span class="nav-icon">↗</span>Collection route</a>
      <a href="#analytics"><span class="nav-icon">▥</span>Analytics</a>
      <a href="#bin-table"><span class="nav-icon">☷</span>Bin directory</a>
    </nav>
    <div class="side-note">
      <strong>♻ Cleaner city, smarter routes</strong>
      <p>Monitor fill levels, prioritize urgent bins and coordinate collection activity from one place.</p>
    </div>
  </aside>

  <main>
    <header class="topbar" id="overview">
      <div>
        <div class="eyebrow">Operations center / Overview</div>
        <h1>Waste Collection Dashboard</h1>
        <p class="subtitle">A clear view of bin status, urgent pickups and collection planning.</p>
      </div>
      <div class="top-actions">
        <span class="demo-pill">● DEMO DATA</span>
        <span class="date-label" id="todayLabel"></span>
      </div>
    </header>

    <section class="cards" aria-label="Summary metrics">
      <div class="card metric">
        <div class="metric-top"><span class="metric-label">Total bins</span><span class="metric-icon">▤</span></div>
        <div class="metric-value">{{ bins|length }}</div><div class="metric-foot">Bins tracked in this dataset</div>
      </div>
      <div class="card metric">
        <div class="metric-top"><span class="metric-label">High priority</span><span class="metric-icon">⚑</span></div>
        <div class="metric-value">{{ high_count }}</div><div class="metric-foot">Marked high priority</div>
      </div>
      <div class="card metric">
        <div class="metric-top"><span class="metric-label">Areas covered</span><span class="metric-icon">⌖</span></div>
        <div class="metric-value">{{ area_count }}</div><div class="metric-foot">Unique service areas</div>
      </div>
      <div class="card metric">
        <div class="metric-top"><span class="metric-label">Overflow alerts</span><span class="metric-icon">⚠</span></div>
        <div class="metric-value">{{ overflow_count }}</div><div class="metric-foot"><span class="danger">80%+ fill</span> and not collected</div>
      </div>
    </section>

    <div class="section-heading" id="locations">
      <div><h2>Live bin overview</h2><p class="section-caption">Locations and current collection status</p></div>
    </div>
    <section class="two-col">
      <div class="panel">
        <div class="panel-head"><div><h3>Waste bin location map</h3><p>Click a marker to see bin details</p></div></div>
        <div class="legend">
          <span><i class="dot" style="background:#dc4545"></i>Urgent · 80%+</span>
          <span><i class="dot" style="background:#287bc1"></i>Pending</span>
          <span><i class="dot" style="background:#16835d"></i>Collected</span>
        </div>
        <div id="map" role="img" aria-label="Map showing waste bin locations"></div>
      </div>
      <div class="panel" id="route">
        <div class="panel-head"><div><h3>Optimized collection route</h3><p>Nearest-next order for uncollected bins at 80%+ fill</p></div><span class="badge low">ROUTE PLAN</span></div>
        <div class="route-summary">
          <div class="mini-stat"><span>Priority pickups</span><strong id="routeCount">0</strong></div>
          <div class="mini-stat"><span>Estimated road distance</span><strong><span id="routeDistance">0.00</span> <small style="font-size:11px;color:#71817a">km</small></strong></div>
        </div>
        <ol class="route-list" id="collectionOrder"><li class="route-empty">Preparing collection order…</li></ol>
        <p class="section-caption" style="margin-top:13px">Distance uses road-routing data when available; straight-line estimate is shown as a fallback.</p>
      </div>
    </section>

    <div class="section-heading">
      <div><h2>Needs attention</h2><p class="section-caption">Uncollected bins at or above 80% full</p></div>
      <span class="badge high">{{ overflow_count }} urgent</span>
    </div>
    {% if overflow_bins %}
    <section class="alerts">
      {% for bin in overflow_bins %}
      <div class="alert-card">
        <strong>{{ bin["bin_id"] }} · {{ bin["area"] }}</strong>
        <p>Priority: {{ bin["priority"] }} · Collection required</p>
        <div class="alert-level">{{ bin["fill_level"] }}% full</div>
      </div>
      {% endfor %}
    </section>
    {% else %}
    <div class="panel"><p style="margin:0;color:#71817a;font-size:13px">No overflow bins currently. All clear!</p></div>
    {% endif %}

    <div class="section-heading" id="analytics">
      <div><h2>Waste analytics</h2><p class="section-caption">Fill-level and priority distribution across all bins</p></div>
    </div>
    <section class="analytics">
      <div class="panel"><div class="panel-head"><div><h3>Bin fill levels</h3><p>Fill percentage by bin</p></div></div><div class="chart-wrap"><canvas id="fillChart"></canvas></div></div>
      <div class="panel"><div class="panel-head"><div><h3>Priority distribution</h3><p>Bins grouped by assigned priority</p></div></div><div class="chart-wrap"><canvas id="priorityChart"></canvas></div></div>
    </section>

    <div class="section-heading" id="bin-table">
      <div><h2>Bin directory</h2><p class="section-caption">Review status and mark a bin as collected</p></div>
    </div>
    <section class="panel table-panel">
      <div class="table-toolbar">
        <div><h3 style="font-size:14px;margin:0">All waste bins</h3><p class="section-caption">Changes are saved to the CSV demo dataset.</p></div>
        <input class="search" id="binSearch" type="search" placeholder="Search bin, area or status…" aria-label="Search bins">
      </div>
      <div class="table-scroll">
        <table id="binsTable">
          <thead><tr><th>Bin / area</th><th>Fill level</th><th>Priority</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
          {% for bin in bins %}
          <tr>
            <td><div class="bin-id">{{ bin.bin_id }}</div><div class="area-name">{{ bin.area }}</div></td>
            <td class="fill-cell">
              <div class="fill-top"><span>Fill level</span><strong>{{ bin.fill_level }}%</strong></div>
              <div class="progress"><span style="width:{{ [0, [100, bin.fill_level|float]|min]|max }}%;background:{% if bin.fill_level|float >= 80 %}#d94848{% elif bin.fill_level|float >= 50 %}#d5a13a{% else %}#16835d{% endif %}"></span></div>
            </td>
            <td><span class="badge {{ bin.priority|lower if bin.priority|lower in ['high','medium','low'] else 'pending' }}">{{ bin.priority }}</span></td>
            <td><span class="badge {{ 'collected' if bin.status == 'Collected' else 'pending' }}">{{ bin.status }}</span></td>
            <td>
              {% if bin.status != "Collected" %}
              <form class="action-form" action="{{ url_for('mark_collected', bin_id=bin.bin_id) }}" method="POST">
                <button class="btn" type="submit">✓ Mark collected</button>
              </form>
              {% else %}<span class="collected-label">✓ Collected</span>{% endif %}
            </td>
          </tr>
          {% endfor %}
          </tbody>
        </table>
      </div>
    </section>
    <footer class="footer">EcoTrack Smart City Waste Optimizer · Demo data only — not live municipal data.</footer>
  </main>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
window.addEventListener("load", function () {
  document.getElementById("todayLabel").textContent = new Date().toLocaleDateString(undefined, {
    weekday: "short", month: "short", day: "numeric", year: "numeric"
  });

  const bins = {{ bins | tojson }};
  const startPoint = { latitude: 11.0183, longitude: 76.9680 };
  const map = L.map("map").setView([startPoint.latitude, startPoint.longitude], 12);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors", maxZoom: 19
  }).addTo(map);

  bins.forEach(function (bin) {
    const fill = Number(bin.fill_level) || 0;
    const collected = bin.status === "Collected";
    const color = collected ? "#16835d" : fill >= 80 ? "#dc4545" : "#287bc1";
    const marker = L.circleMarker([Number(bin.latitude), Number(bin.longitude)], {
      radius: 8, color: "#ffffff", weight: 2, fillColor: color, fillOpacity: 1
    }).addTo(map);
    const alertText = collected ? "COLLECTED" : fill >= 80 ? "URGENT — COLLECTION REQUIRED" : "PENDING COLLECTION";
    marker.bindPopup(
      "<strong>" + escapeHtml(bin.bin_id) + "</strong><br>" +
      "Area: " + escapeHtml(bin.area) + "<br>" +
      "Fill level: " + fill + "%<br>" +
      "Priority: " + escapeHtml(bin.priority) + "<br>" +
      "<span style='color:" + color + ";font-weight:700'>" + alertText + "</span>"
    );
  });

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, function (char) {
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char];
    });
  }
  function distanceKm(lat1, lon1, lat2, lon2) {
    const R = 6371, rad = Math.PI / 180;
    const dLat = (lat2 - lat1) * rad, dLon = (lon2 - lon1) * rad;
    const a = Math.sin(dLat/2)**2 + Math.cos(lat1*rad)*Math.cos(lat2*rad)*Math.sin(dLon/2)**2;
    return 2 * R * Math.asin(Math.sqrt(a));
  }

  const remaining = bins.filter(b => Number(b.fill_level) >= 80 && b.status !== "Collected")
    .filter(b => Number.isFinite(Number(b.latitude)) && Number.isFinite(Number(b.longitude)));
  const routeBins = [];
  let current = startPoint;
  while (remaining.length) {
    let nearestIndex = 0, nearestDistance = Infinity;
    remaining.forEach(function (bin, index) {
      const d = distanceKm(current.latitude, current.longitude, Number(bin.latitude), Number(bin.longitude));
      if (d < nearestDistance) { nearestDistance = d; nearestIndex = index; }
    });
    const next = remaining.splice(nearestIndex, 1)[0];
    routeBins.push(next);
    current = { latitude: Number(next.latitude), longitude: Number(next.longitude) };
  }

  const routePoints = [[startPoint.latitude, startPoint.longitude], ...routeBins.map(b => [Number(b.latitude), Number(b.longitude)])];
  let totalDistance = 0;
  for (let i = 0; i < routePoints.length - 1; i++) {
    totalDistance += distanceKm(routePoints[i][0], routePoints[i][1], routePoints[i+1][0], routePoints[i+1][1]);
  }
  document.getElementById("routeCount").textContent = routeBins.length;
  document.getElementById("routeDistance").textContent = totalDistance.toFixed(2);

  const orderList = document.getElementById("collectionOrder");
  orderList.innerHTML = "";
  if (!routeBins.length) {
    orderList.innerHTML = "<li class='route-empty'>No urgent pending bins. Great work!</li>";
  } else {
    routeBins.forEach(function (bin, index) {
      const li = document.createElement("li");
      li.innerHTML = "<span class='route-num'>" + (index + 1) + "</span>" +
        "<div><div class='route-item-main'>" + escapeHtml(bin.bin_id) + " · " + escapeHtml(bin.area) +
        "</div><div class='route-item-sub'>" + Number(bin.fill_level) + "% full · Priority " + escapeHtml(bin.priority) + "</div></div>";
      orderList.appendChild(li);
      L.marker([Number(bin.latitude), Number(bin.longitude)], {
        icon: L.divIcon({
          className: "route-number",
          html: "<div style='background:#123d30;color:white;border-radius:50%;width:25px;height:25px;display:flex;align-items:center;justify-content:center;font-weight:800;border:2px solid white;box-shadow:0 2px 6px #0003'>" + (index+1) + "</div>",
          iconSize: [25,25], iconAnchor: [12,12]
        })
      }).addTo(map).bindTooltip("Stop " + (index+1) + ": " + escapeHtml(bin.bin_id));
    });
  }

  if (routeBins.length > 0) {
    const routeUrl = "https://router.project-osrm.org/route/v1/driving/" +
      routePoints.map(p => p[1] + "," + p[0]).join(";") + "?overview=full&geometries=geojson";
    fetch(routeUrl).then(r => r.json()).then(data => {
      if (data.code === "Ok" && data.routes && data.routes.length) {
        const coords = data.routes[0].geometry.coordinates.map(p => [p[1], p[0]]);
        L.polyline(coords, { color: "#16835d", weight: 5, opacity: .85 }).addTo(map);
        document.getElementById("routeDistance").textContent = (data.routes[0].distance / 1000).toFixed(2);
      }
    }).catch(() => { /* Keep the straight-line estimate if road routing is unavailable. */ });
  }
  setTimeout(() => map.invalidateSize(), 300);

  if (window.Chart) {
    const chartBins = bins;
    new Chart(document.getElementById("fillChart"), {
      type: "bar",
      data: {
        labels: chartBins.map(b => b.bin_id),
        datasets: [{ label: "Fill level (%)", data: chartBins.map(b => Number(b.fill_level) || 0),
          backgroundColor: chartBins.map(b => Number(b.fill_level) >= 80 ? "#df6565" : "#57a982"),
          borderRadius: 5, maxBarThickness: 34 }]
      },
      options: { responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, max: 100, ticks: { stepSize: 20 }, grid: { color: "#edf1ee" } },
          x: { grid: { display: false }, ticks: { maxRotation: 45, minRotation: 0 } } } }
    });
    const priorities = ["High", "Medium", "Low"];
    new Chart(document.getElementById("priorityChart"), {
      type: "doughnut",
      data: { labels: priorities, datasets: [{ data: priorities.map(p => chartBins.filter(b => b.priority === p).length),
        backgroundColor: ["#dc6565", "#e5b34e", "#58a982"], borderWidth: 0, hoverOffset: 5 }] },
      options: { responsive: true, maintainAspectRatio: false, cutout: "68%",
        plugins: { legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 7, padding: 18 } } } }
    });
  }

  const search = document.getElementById("binSearch");
  search.addEventListener("input", function () {
    const query = search.value.toLowerCase().trim();
    document.querySelectorAll("#binsTable tbody tr").forEach(function (row) {
      row.style.display = row.textContent.toLowerCase().includes(query) ? "" : "none";
    });
  });
});
</script>
</body>
</html>
"""

def get_bins():
    with CSV_PATH.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

@app.route("/collect/<bin_id>", methods=["POST"])
def mark_collected(bin_id):
    bins = get_bins()
    if not bins:
        return redirect(url_for("home"))

    matched = False
    for bin_data in bins:
        if bin_data["bin_id"] == bin_id:
            bin_data["status"] = "Collected"
            matched = True
            break

    if not matched:
        abort(404)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        fieldnames = list(bins[0].keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bins)

    return redirect(url_for("home"))

@app.route("/")
def home():
    bins = get_bins()
    high_count = sum(1 for b in bins if b.get("priority") == "High")
    area_count = len(set(b.get("area", "") for b in bins if b.get("area")))
    overflow_bins = [
        b for b in bins
        if float(b.get("fill_level") or 0) >= 80 and b.get("status") != "Collected"
    ]
    return render_template_string(
        HTML,
        bins=bins,
        high_count=high_count,
        area_count=area_count,
        overflow_count=len(overflow_bins),
        overflow_bins=overflow_bins
    )

if __name__ == "__main__":
    app.run(debug=True)