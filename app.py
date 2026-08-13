from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_tracking_details(awb):

    try:
        response = requests.post(
            "https://criticalog.com/track_db.php",
            data={
                "doctype": "D",
                "docNumber": awb,
                "action": "t"
            },
            timeout=30
        )

        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # Determine status based on active steps
        active_steps = soup.select("div.track div.step.active")
        active_count = len(active_steps)

        if active_count >= 5:
            status = "Delivered"
        elif active_count == 4:
            status = "Out For Delivery"
        elif active_count == 3:
            status = "In Transit"
        elif active_count == 2:
            status = "Order Processed"
        elif active_count == 1:
            status = "Order Picked"
        else:
            status = "Unknown"

        # Extract Origin & Destination
        origin = ""
        destination = ""

        divs = soup.find_all("div", class_="col-md-6 border_row")

        for div in divs:
            text = div.get_text(" ", strip=True)

            if "Origin" in text:
                origin = text.replace("Origin", "").strip()

            if "Destination" in text:
                destination = text.replace("Destination", "").strip()

        return {
            "awb": awb,
            "status": status,
            "origin": origin,
            "destination": destination
        }

    except Exception as e:

        return {
            "awb": awb,
            "status": f"Error: {str(e)}",
            "origin": "",
            "destination": ""
        }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/track", methods=["POST"])
def track():

    awbs = request.json.get("awbs", [])

    results = []

    for awb in awbs:
        awb = awb.strip()

        if awb:
            results.append(get_tracking_details(awb))

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
