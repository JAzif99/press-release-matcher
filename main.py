from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# Load the press release database
with open("localization.json", "r") as f:
    press_release_db = json.load(f)["2024 Press Releases"]

@app.route("/", methods=["GET"])
def home():
    return "Press Release Matcher API is running!"

@app.route("/fetch_and_match_press_release", methods=["POST"])
def fetch_and_match_press_release():
    """
    Receives a website URL, extracts services, and finds matching press releases.
    """
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    # Step 1: Fetch Website Content
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        website_text = soup.get_text(separator=" ").strip().lower()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch website: {str(e)}"}), 500

    # Step 2: Categorize Services & Match
    matches = []
    for entry in press_release_db:
        confidence = 0
        industry = entry["Industry"].lower()
        sub_industry = entry["Sub-Industry"].lower()
        services = entry["Services"].lower()

        # Direct Service Match (90% confidence)
        if any(service in website_text for service in services.split(", ")):
            confidence = 90  

        # Sub-Industry Match (80% confidence)
        elif sub_industry in website_text:
            confidence = 80  

        # Industry Match (50% confidence) - Now removed, to avoid unrelated industries
        # elif industry in website_text:
        #    confidence = 50  

        # **NEW: Ensure only Roofing-Related Matches**
        if confidence >= 80 and ("roofing" in industry or "roofing" in sub_industry):
            matches.append({
                "Seller": entry["Seller"],
                "Industry": entry["Industry"],
                "Sub-Industry": entry["Sub-Industry"],
                "Services": entry["Services"],
                "Confidence": f"{confidence}%"
            })

    # Step 3: Sort by confidence & return only the best match
    if not matches:
        return jsonify({"message": "No relevant press releases found"})

    best_match = max(matches, key=lambda x: int(x["Confidence"].replace("%", "")))

    return jsonify({"best_match": best_match})

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
