from flask import Flask, request, jsonify
import pytesseract
import cv2
import re
from PIL import Image
import numpy as np
import os

app = Flask(__name__)

# Render container मधला Tesseract path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def extract_fields(img_bytes: bytes) -> dict:
    """
    Aadhaar image मधून raw text आणि Aadhaar number काढतो.
    """
    # bytes -> OpenCV image
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Image read failed")

    # थोडं basic preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # हलका threshold
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # OpenCV image -> PIL image
    pil_img = Image.fromarray(thresh)

    # OCR
    text = pytesseract.image_to_string(pil_img, lang="eng")

    # Aadhaar number – 1234 5678 9012 किंवा 123456789012
    clean = text.replace("\n", " ")
    aadhaar_match = re.search(r'(\d{4}\s\d{4}\s\d{4}|\d{12})', clean)
    aadhaar_no = aadhaar_match.group(1) if aadhaar_match else None

    return {
        "raw_text": text,
        "aadhaar_number": aadhaar_no,
    }


@app.route("/", methods=["GET", "POST"])
def home():
    # फक्त चेक करण्यासाठी
    if request.method == "GET":
        return "Aadhaar OCR API is Live 🎉 (POST image to this same URL)"

    # POST = इथे image येईल
    try:
        if "file" not in request.files:
            return jsonify({
                "success": False,
                "error": "No file field named 'file' in form-data"
            }), 400

        img_file = request.files["file"]
        img_bytes = img_file.read()

        if not img_bytes:
            return jsonify({
                "success": False,
                "error": "Empty file received"
            }), 400

        data = extract_fields(img_bytes)

        return jsonify({
            "success": True,
            "data": data
        })

    except Exception as e:
        # जे काही error असेल ते पाहायला सोपं जावं म्हणून direct message परत देतो
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    # Render सारख्या PaaS वर PORT env set असतो
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
