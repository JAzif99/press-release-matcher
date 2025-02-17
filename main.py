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
        website_text = soup.get_text(separator=" ").strip()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch website: {str(e)}"}), 500

    # Step 2: Categorize Services & Match
    matches = []
    for entry in press_release_db:
        confidence = 0

        # Direct service match (90% confidence)
        if any(service.lower() in website_text.lower() for service in entry["Services"].split(", ")):
            confidence = 90  

        # Sub-industry match (70% confidence)
        elif entry["Sub-Industry"].lower() in website_text.lower():
            confidence = 70  

        # Industry match (50% confidence)
        elif entry["Industry"].lower() in website_text.lower():
            confidence = 50  

        # Only add strong matches (50%+ confidence)
        if confidence >= 50:
            matches.append({
                "Seller": entry["Seller"],
                "Industry": entry["Industry"],
                "Sub-Industry": entry["Sub-Industry"],
                "Services": entry["Services"],
                "Confidence": confidence
            })

    # Step 3: Sort by confidence & limit to top 5 results
    matches = sorted(matches, key=lambda x: x["Confidence"], reverse=True)[:5]

    # Step 4: Format Response for Better Readability
    if not matches:
        return jsonify({"message": "No relevant press releases found"})

    # Ensure confidence score is displayed properly
    formatted_matches = []
    for match in matches:
        formatted_matches.append({
            "Seller": match["Seller"],
            "Industry": match["Industry"],
            "Sub-Industry": match["Sub-Industry"],
            "Services": match["Services"],
            "Confidence": f"{match['Confidence']}%"
        })

    return jsonify({"matches": formatted_matches})

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
