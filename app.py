from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TRACK_URL = "https://criticalog.com/track_db.php"


def get_tracking_details(awb):

    try:

        response = requests.post(
            TRACK_URL,
            data={
                "doctype": "D",
                "docNumber": awb,
                "action": "t"
            },
            timeout=30
        )

        soup = BeautifulSoup(response.text, "html.parser")

        active_steps = soup.select("div.track div.step.active")
        count = len(active_steps)

        if count >= 5:
            status = "Delivered"
        elif count == 4:
            status = "Out For Delivery"
        elif count == 3:
            status = "In Transit"
        elif count == 2:
            status = "Order Processed"
        elif count == 1:
            status = "Order Picked"
        else:
            status = "Pickup Pending"

        origin = ""
        destination = ""

        locations = soup.select("div.col-md-6.border_row")

        if len(locations) >= 2:
            origin = locations[0].get_text(" ", strip=True).replace("Origin", "").strip()
            destination = locations[1].get_text(" ", strip=True).replace("Destination", "").strip()

        pickup_date = ""
        edd = ""
        delivered_date = ""

        cards = soup.find_all("article", class_="card")

        for card in cards:

            text = card.get_text(" ", strip=True)

            if "Pickup Date/Time" in text:
                try:
                    pickup_date = text.split("Pickup Date/Time")[-1].strip()
                except:
                    pass

            if "Estimated Delivery Date" in text:
                try:
                    edd = text.split("Estimated Delivery Date/Time:")[-1].strip()
                except:
                    pass

            if "Received date/Time" in text:
                try:
                    delivered_date = text.split("Received date/Time")[-1].strip()
                except:
                    pass

        return {
            "awb": awb,
            "status": status,
            "origin": origin,
            "destination": destination,
            "pickup_date": pickup_date,
            "edd": edd,
            "delivered_date": delivered_date
        }

    except Exception:

        return {
            "awb": awb,
            "status": "Error",
            "origin": "",
            "destination": "",
            "pickup_date": "",
            "edd": "",
            "delivered_date": ""
        }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/track", methods=["POST"])
def track():

    data = request.get_json()
    awbs = data.get("awbs", [])

    results = []

    for awb in awbs:

        awb = awb.strip()

        if awb:
            results.append(get_tracking_details(awb))

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
