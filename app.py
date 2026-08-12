from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/track", methods=["POST"])
def track():

    awbs = request.json["awbs"]
    results = []

    for awb in awbs:

        try:

            r = requests.post(
                "https://criticalog.com/track_db.php",
                data={
                    "doctype":"D",
                    "docNumber":awb,
                    "action":"t"
                },
                timeout=30
            )

            html = r.text

            status = "Unknown"

            if "Delivered" in html:
                status = "Delivered"
            elif "Out For Delivery" in html:
                status = "Out For Delivery"
            elif "In Transit" in html:
                status = "In Transit"

            results.append({
                "awb": awb,
                "status": status
            })

        except Exception:
            results.append({
                "awb": awb,
                "status": "Error"
            })

    return jsonify(results)

if __name__ == "__main__":
    app.run()
