from flask import Flask, request
import os
import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "received_images"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET"])
def index():
    return "✅ 이미지 수신 API 작동 중"

@app.route("/upload", methods=["POST"])
def upload():
    if 'image' not in request.files:
        return "❌ 이미지 파일이 없습니다.", 400

    image = request.files['image']
    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    filename = f"{timestamp}.jpg"  # 간단한 파일명
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(save_path)
    print(f"✅ 이미지 수신 및 저장: {save_path}")
    return "ok", 200


@app.route("/files", methods=["GET"])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return "<br>".join(files)

@app.route("/upload_sensor", methods=["POST"])
def upload_sensor():
    data = request.get_json()
    print(f" 센서 데이터 수신 : {data}")
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
