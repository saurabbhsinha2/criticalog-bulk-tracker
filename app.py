from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_field(soup, label):

    strongs = soup.find_all("strong")

    for s in strongs:

        if label.lower() in s.get_text().lower():

            parent = s.parent.get_text(" ", strip=True)

            value = parent.replace(s.get_text(), "").strip()

            return value

    return ""


def get_tracking_details(awb):

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

        soup = BeautifulSoup(r.text,"html.parser")

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

        divs = soup.find_all("div")

        for div in divs:

            text = div.get_text(" ", strip=True)

            if "Origin" in text and not origin:
                origin = text.replace("Origin","").strip()

            if "Destination" in text and not destination:
                destination = text.replace("Destination","").strip()

        pickup_date = extract_field(soup,"Pickup Date")
        edd = extract_field(soup,"Estimated Delivery Date")
        received_date = extract_field(soup,"Received date")
        received_by = extract_field(soup,"Received By")

        return {
            "awb":awb,
            "status":status,
            "origin":origin,
            "destination":destination,
            "pickup_date":pickup_date,
            "edd":edd,
            "received_date":received_date,
            "received_by":received_by
        }

    except Exception as e:

        return {
            "awb":awb,
            "status":"Error",
            "origin":"",
            "destination":"",
            "pickup_date":"",
            "edd":"",
            "received_date":"",
            "received_by":""
        }


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/track",methods=["POST"])
def track():

    awbs = request.json.get("awbs",[])

    results=[]

    for awb in awbs:

        awb = awb.strip()

        if awb:
            results.append(get_tracking_details(awb))

    return jsonify(results)


if __name__=="__main__":
    app.run(debug=True)
