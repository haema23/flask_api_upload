from flask import Flask, request
import os
import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "received_images"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET"])
def index():
    return "✅ 이미지 & 센서 수신 API 작동 중"

# ----------------------------
# 이미지 업로드
# ----------------------------
@app.route("/upload", methods=["POST"])
def upload_image():
    if 'image' not in request.files:
        return "❌ 이미지 파일이 없습니다.", 400

    image = request.files['image']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{image.filename}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(save_path)
    print(f"✅ 이미지 수신 및 저장: {save_path}")
    return "ok", 200

# ----------------------------
# pH
# ----------------------------
@app.route("/upload_ph", methods=["POST"])
def upload_ph():
    data = request.json
    print(f"✅ pH 데이터 수신: {data}")
    return "ok", 200

# ----------------------------
# 온도
# ----------------------------
@app.route("/upload_temp", methods=["POST"])
def upload_temp():
    data = request.json
    print(f"✅ 온도 데이터 수신: {data}")
    return "ok", 200

# ----------------------------
# 습도
# ----------------------------
@app.route("/upload_hum", methods=["POST"])
def upload_hum():
    data = request.json
    print(f"✅ 습도 데이터 수신: {data}")
    return "ok", 200

# ----------------------------
# CO2
# ----------------------------
@app.route("/upload_co2", methods=["POST"])
def upload_co2():
    data = request.json
    print(f"✅ CO2 데이터 수신: {data}")
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
