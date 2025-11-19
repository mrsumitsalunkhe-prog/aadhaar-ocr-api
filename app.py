from flask import Flask, request, jsonify
import requests, re

app = Flask(__name__)

OCR_API = "https://api.ocr.space/parse/image"
API_KEY = "helloworld"  # free demo key

def extract_aadhaar(text):
    text = text.replace("\n", " ")
    match = re.search(r'(\d{4}\s\d{4}\s\d{4}|\d{12})', text)
    return match.group(1) if match else None

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return "Aadhaar OCR API Live ✔ (Upload Aadhaar to this same URL)"

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file received"})

    file = request.files["file"]

    r = requests.post(
        OCR_API,
        files={"file": file},
        data={"apikey": API_KEY}
    ).json()

    if r.get("IsErroredOnProcessing"):
        return jsonify({"success": False, "error": r.get("ErrorMessage")})

    raw_text = r["ParsedResults"][0]["ParsedText"]
    aadhaar = extract_aadhaar(raw_text)

    return jsonify({"success": True, "raw_text": raw_text, "aadhaar_number": aadhaar})

if __name__ == "__main__":
    app.run()
