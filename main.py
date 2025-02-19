# Step 2: Categorize Services & Match
matches = []
for entry in press_release_db:
    confidence = 0

    # Extract industry-related fields
    services = entry["Services"].lower()
    sub_industry = entry["Sub-Industry"].lower()
    industry = entry["Industry"].lower()

    # **Direct Service Match (90% Confidence)**
    if any(service.lower() in website_text.lower() for service in services.split(", ")):
        confidence = 90  

    # **Sub-Industry Match (80% Confidence)**
    elif sub_industry in website_text.lower():
        confidence = 80  

    # **Industry Match (70% Confidence)**
    elif industry in website_text.lower():
        confidence = 70  

    # Only add strong matches (70%+ confidence)
    if confidence >= 70:
        matches.append({
            "Seller": entry["Seller"],
            "Industry": entry["Industry"],
            "Sub-Industry": entry["Sub-Industry"],
            "Services": entry["Services"],
            "Confidence": f"{confidence}%"
        })

# Step 3: Sort by confidence & return top 5 matches
matches = sorted(matches, key=lambda x: int(x["Confidence"].replace("%", "")), reverse=True)[:5]

# Step 4: Format Response for Better Readability
if not matches:
    return jsonify({"message": "No relevant press releases found"})

return jsonify({"matches": matches})
