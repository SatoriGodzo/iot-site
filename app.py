# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, send_file
import io, csv, random
from datetime import datetime, timedelta

app = Flask(__name__)

# Фейковые устройства
DEVICES = [
    {"id": "myRasp", "name": "Raspberry Pi 1"}
]

# Фейковые сенсорные данные для теста
FAKE_DATA = []
now = datetime.now()
for i in range(100):
    FAKE_DATA.append({
        "timestamp": (now - timedelta(minutes=i*10)).strftime("%Y-%m-%dT%H:%M:%S"),
        "sensor_type": "temperature",
        "value": round(random.uniform(20, 30), 2)
    })

@app.route("/")
def index():
    return render_template("index.html", devices=DEVICES)


@app.route("/device/<int:device_id>/sensors")
def get_sensors(device_id):
    t_from = request.args.get("from")
    t_to = request.args.get("to")
    mtype = request.args.get("type", "temperature")

    try:
        from_dt = datetime.fromisoformat(t_from.replace("Z", "+00:00").split('.')[0])
        to_dt = datetime.fromisoformat(t_to.replace("Z", "+00:00").split('.')[0])
    except:
        from_dt = datetime.utcnow() - timedelta(days=1)
        to_dt = datetime.utcnow()

    data = [
        d for d in FAKE_DATA
        if d["sensor_type"] == mtype and from_dt <= datetime.fromisoformat(d["timestamp"]) <= to_dt
    ]

    return jsonify(data)

@app.route("/device/<int:device_id>/alerts")
def get_alerts(device_id):
    alerts = [
        {"timestamp": "2025-10-26 13:00:00", "message": "Temperature high!"}
    ]
    return jsonify(alerts)

@app.route("/device/<int:device_id>/sensors/csv")
def download_csv(device_id):
    t_from = request.args.get("from")
    t_to = request.args.get("to")
    mtype = request.args.get("type", "temperature")

    resp = get_sensors(device_id)
    sensors = resp.get_json()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "sensor_type", "value"])
    for row in sensors:
        writer.writerow([row["timestamp"], row["sensor_type"], row["value"]])

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv",
                     download_name=f"device_{device_id}_sensors.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
