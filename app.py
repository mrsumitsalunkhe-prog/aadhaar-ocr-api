from flask import Flask, request, jsonify
import pytesseract, cv2, re
from PIL import Image
import numpy as np
import os

app = Flask(__name__)

# Render container मधला tesseract path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def extract_fields(img_bytes):
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if img is None:
        return {"error": "Image read failed"}

    # simple preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    pil_img = Image.fromarray(thresh)

    text = pytesseract.image_to_string(pil_img, lang="eng")

    # Aadhaar number – 1234 5678 9012 किंवा 123456789012
    aadhaar = re.search(r'(\d{4}\s\d{4}\s\d{4}|\d{12})', text.replace("\n", " "))
    aadhaar_no = aadhaar.group(1) if aadhaar else None

    return {
        "raw_text": text,
        "aadhaar_number": aadhaar_no
    }

@app.route("/")
def home():
    return "Aadhaar OCR API is Live 🎉"

@app.route("/ocr", methods=["GET", "POST"])
def ocr():
    if request.method == "GET":
        return "OCR endpoint OK. Send POST with 'file' field."

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file"}), 400

    img_bytes = request.files["file"].read()
    data = extract_fields(img_bytes)
    return jsonify({"success": True, "data": data})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
