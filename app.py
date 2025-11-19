from flask import Flask, request, jsonify
import requests, re

app = Flask(__name__)

# Free OCR AI API
OCR_API = "https://api.ocr.space/parse/image"
OCR_KEY = "helloworld"  # free demo key (works without signup)

def find_aadhaar(text):
    text = text.replace("\n", " ")
    match = re.search(r'(\d{4}\s\d{4}\s\d{4}|\d{12})', text)
    return match.group(1) if match else None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return "Aadhaar OCR API Live 🚀 | Upload Aadhaar Image via POST"

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]

    response = requests.post(
        OCR_API,
        files={"file": file},
        data={"apikey": OCR_KEY}
    )

    result = response.json()

    if result.get("IsErroredOnProcessing"):
        return jsonify({"success": False, "error": result.get("ErrorMessage")}), 500

    raw = result["ParsedResults"][0]["ParsedText"]
    aadhaar = find_aadhaar(raw)

    return jsonify({
        "success": True,
        "raw_text": raw,
        "aadhaar_number": aadhaar
    })

if __name__ == "__main__":
    app.run()
