import csv
from flask import Flask, render_template_string,redirect,url_for 
app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart City Waste Optimizer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <style>
    body {
        font-family: Arial, sans-serif;
        margin: 20px;
        background: #f1f5f9;
        color: #1e293b;
    }

    h1 {
        color: #166534;
        font-size: 30px;
    }

    h2, h3 {
        color: #166534;
    }

    .cards {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
    }

    .card {
        background: white;
        padding: 22px;
        border-radius: 12px;
        flex: 1;
        min-width: 120px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }

    #map {
        height: 450px;
        background: #e5e5e5;
        margin-top: 15px;
        border-radius: 12px;
    }

    table {
        width: 100%;
        background: white;
        border-collapse: collapse;
        margin-top: 20px;
        border-radius: 10px;
        overflow: hidden;
    }

    th, td {
        padding: 12px;
        border: 1px solid #e2e8f0;
        text-align: left;
    }

    th {
        background: #166534;
        color: white;
    }

    button {
        background: #16a34a;
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
    }

    button:hover {
        background: #15803d;
    }
</style>
</head>
<body>
    <h1>Smart City Waste Collection Dashboard</h1>

    <div class="cards">
        <div class="card">
            <h3>Total Bins</h3><p>{{ bins|length }}</p>
        </div>
        <div class="card">
            <h3>High Priority</h3><p>{{ high_count }}</p>
        </div>
        <div class="card">
            <h3>Areas</h3><p>{{ area_count }}</p>
        </div>
    </div>

    <h2>Waste Bin Location Map</h2>
    <p>Red markers: bins at 80% fill or above.</p>
    <div id="map"></div>

    <h2>Waste Bin Details</h2>
    <table>
        <tr>
            <th>Bin ID</th><th>Area</th>
            <th>Fill Level</th>
            <th>Priority</th>
            <th>Status</th>
             <th>Action</th>
        </tr>
        {% for bin in bins %}
        <tr>
            <td>{{ bin.bin_id }}</td>
            <td>{{ bin.area }}</td>
            <td>{{ bin.fill_level }}%</td>
            <td>{{ bin.priority }}</td>
            <td>{{ bin.status }}</td>
            <td>
    {% if bin.status != "Collected" %}
    <form action="{{ url_for('mark_collected', bin_id=bin.bin_id) }}" method="POST">
        <button type="submit" style="background:#198754; color:white; border:0; padding:6px 10px; border-radius:6px;">
            Mark as Collected
        </button>
    </form>
    {% else %}
    <span style="color:green; font-weight:bold;">Collected ✓</span>
    {% endif %}
</td>
        </tr>
        {% endfor %}
    </table>

    <p><small>Demo data only — not live municipal data.</small></p>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
    window.addEventListener("load", function () {
        const bins = {{ bins | tojson }};
        const map = L.map("map").setView([11.0183, 76.9680], 12);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap contributors"
        }).addTo(map);
        const routeBins = bins.filter(function(bin) {
             return Number(bin.fill_level) >= 80 &&
                  bin.status !== "Collected";
        });

        const startPoint = {
    latitude: 11.0183,
    longitude: 76.9680
};

function distanceKm(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;

    const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(lat1 * Math.PI / 180) *
        Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) ** 2;

    return 2 * R * Math.asin(Math.sqrt(a));
}

const remainingBins = [...routeBins];
const optimizedBins = [];
let currentPoint = startPoint;

while (remainingBins.length > 0) {
    let nearestIndex = 0;
    let nearestDistance = Infinity;

    remainingBins.forEach(function(bin, index) {
        const distance = distanceKm(
            currentPoint.latitude,
            currentPoint.longitude,
            Number(bin.latitude),
            Number(bin.longitude)
        );

        if (distance < nearestDistance) {
            nearestDistance = distance;
            nearestIndex = index;
        }
    });

    const nextBin = remainingBins.splice(nearestIndex, 1)[0];
    optimizedBins.push(nextBin);

    currentPoint = {
        latitude: Number(nextBin.latitude),
        longitude: Number(nextBin.longitude)
    };
}

routeBins.length = 0;
routeBins.push(...optimizedBins);

routeBins.forEach(function(bin, index) {
    bin.collectionOrder = index + 1;
});
        bins.forEach(function(bin) {
            const fill = Number(bin.fill_level);
            const color = bin.status === "Collected"
    ? "green"
    : fill >= 80
        ? "red"
        : "blue";

            L.circleMarker(
                [Number(bin.latitude), Number(bin.longitude)],
                {
                    radius: 8,
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.8
                }
            ).addTo(map).bindPopup(`
   <b>${bin.bin_id}</b><br>
Area: ${bin.area}<br>
Fill Level: ${bin.fill_level}%<br>
Priority: ${bin.priority}<br>
${bin.status === "Collected"
    ? '<span style="color:green;font-weight:bold;">✓ COLLECTED</span>'
    : Number(bin.fill_level) >= 80
        ? '<span style="color:red;font-weight:bold;">🚨 URGENT - COLLECTION REQUIRED</span>'
        : '<span style="color:blue;">Normal - Pending Collection</span>'}
`);
});
        const routePoints = [
    [11.0183, 76.9680],
    ...routeBins.map(function(bin) {
        return [
            Number(bin.latitude),
            Number(bin.longitude)
        ];
    })
];
let totalDistance = 0;

for (let i = 0; i < routePoints.length - 1; i++) {
    const lat1 = routePoints[i][0];
    const lon1 = routePoints[i][1];
    const lat2 = routePoints[i + 1][0];
    const lon2 = routePoints[i + 1][1];

    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;

    const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(lat1 * Math.PI / 180) *
        Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) ** 2;

    totalDistance +=
        2 * R * Math.asin(Math.sqrt(a));
}
document.getElementById("routeCount").textContent =
    routeBins.length;

document.getElementById("routeDistance").textContent =
    totalDistance.toFixed(2);

const orderList = document.getElementById("collectionOrder");

routeBins.forEach(function(bin) {
    const item = document.createElement("li");
    item.textContent =
        bin.bin_id + " - " + bin.area +
        " (" + bin.fill_level + "% full)";
    orderList.appendChild(item);
});
routeBins.forEach(function(bin) {
    L.marker(
        [Number(bin.latitude), Number(bin.longitude)],
        {
            icon: L.divIcon({
                className: "route-number",
                html: '<div style="background:#198754;color:white;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-weight:bold;border:2px solid white;">' +
                    bin.collectionOrder + '</div>',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            })
        }
    ).addTo(map).bindTooltip(
        "Collection Order: " + bin.collectionOrder +
        " - " + bin.bin_id
    );
});
if (routeBins.length > 0) {
    fetch(
    "https://router.project-osrm.org/route/v1/driving/" +
    routePoints.map(function(point) {
        return point[1] + "," + point[0];
    }).join(";") +
    "?overview=full&geometries=geojson"
)
.then(function(response) {
    return response.json();
})
.then(function(data) {
    if (data.code === "Ok" && data.routes.length > 0) {
        const roadCoordinates =
            data.routes[0].geometry.coordinates.map(function(point) {
                return [point[1], point[0]];
            });

        L.polyline(roadCoordinates, {
            color: "green",
            weight: 5,
            opacity: 0.85
        }).addTo(map);

        document.getElementById("routeDistance").textContent =
            (data.routes[0].distance / 1000).toFixed(2);
    } else {
        console.log("Road route unavailable.");
    }
})
.catch(function(error) {
    console.log("Routing error:", error);
});
}
        SetTimeout(function() {
            map.invalidateSize();
        }, 300);
    });
    </script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <h3 style="background:#fff3cd; color:#856404; padding:10px; border-radius:8px;">
    Overflow Alerts: {{ overflow_count }} bins need collection!
</h3>
    <h2>🚛 Optimized Collection Route</h2>

<p>
    <strong>Pending Priority Bins:</strong>
    <span id="routeCount">0</span>
</p>

<p>
    <strong>Estimated Road Distance:</strong>
    <span id="routeDistance">0</span> km
</p>

<h3>Collection Order</h3>
<ol id="collectionOrder"></ol>
    <h2>Waste Analytics</h2>
    <h3>🚨 Bins Requiring Collection</h3>

{% if overflow_bins %}
<div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px;">
    {% for bin in overflow_bins %}
    <div style="background:#fff3cd; padding:12px; border-radius:10px; border-left:4px solid #dc3545;">
        <strong>{{ bin["bin_id"] }}</strong>
        <p>Area: {{ bin["area"] }}</p>
        <p>Fill Level: {{ bin["fill_level"] }}%</p>
        <strong style="color:#dc3545;">Needs Collection</strong>
    </div>
    {% endfor %}
</div>
{% else %}
<p>No overflow bins currently.</p>
{% endif %}

<div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px;">

    <div style="background:white; padding:8px; border-radius:10px;">
        <h4>Bin Fill Levels</h4>
        <div style="height:140px;">
            <canvas id="fillChart"></canvas>
        </div>
    </div>

    <div style="background:white; padding:8px; border-radius:10px;">
        <h4>Priority Distribution</h4>
        <div style="height:140px;">
            <canvas id="priorityChart"></canvas>
        </div>
    </div>

</div>
<script>
const chartBins = {{ bins | tojson }};

new Chart(document.getElementById("fillChart"), {
    type: "bar",
    data: {
        labels: chartBins.map(b => b.bin_id),
        datasets: [{
            label: "Fill Level (%)",
            data: chartBins.map(b => Number(b.fill_level))
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 100
            }
        }
    }
});

const priorities = ["High", "Medium", "Low"];

new Chart(document.getElementById("priorityChart"), {
    type: "doughnut",
    data: {
        labels: priorities,
        datasets: [{
            data: priorities.map(
                p => chartBins.filter(b => b.priority === p).length
            )
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});
</script>


</body>
</html>
"""


def get_bins():
    with open("data/sample_bins.csv", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))

@app.route("/collect/<bin_id>", methods=["POST"])
def mark_collected(bin_id):
    bins = get_bins()

    for b in bins:
        if b["bin_id"] == bin_id:
            b["status"] = "Collected"
            break

    with open("data/sample_bins.csv", "w", newline="", encoding="utf-8") as file:
        fieldnames = bins[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bins)

    return redirect(url_for("home"))
@app.route("/")
def home():
    bins = get_bins()
    high_count = sum(1 for b in bins if b["priority"] == "High")
    area_count = len(set(b["area"] for b in bins))
    overflow_bins = [
    b for b in bins
    if float(b["fill_level"]) >= 80
    and b["status"] != "Collected"
    ]
    overflow_count = len(overflow_bins)
    return render_template_string(
        HTML,
        bins=bins,
        high_count=high_count,
        area_count=area_count,
        overflow_count=overflow_count,
        overflow_bins=overflow_bins
    )

if __name__ == "__main__":
    app.run(debug=True)