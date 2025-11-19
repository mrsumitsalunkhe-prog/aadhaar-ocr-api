from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Home OK"

@app.route("/ocr", methods=["GET", "POST"])
def ocr():
    if request.method == "GET":
        return "OCR GET OK"
    return jsonify({"success": True, "msg": "OCR POST OK"})

if __name__ == "__main__":
    app.run()
