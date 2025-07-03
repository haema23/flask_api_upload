import cv2
import time
import os
import datetime
import requests
import serial
import threading

# ================================
# 설정값
# ================================
RTSP_URL = "rtsp://admin:dasung35$$@192.168.0.64/Streaming/Channels/101"
SAVE_PATH = "captured_images"
CAPTURE_INTERVAL_SECONDS = 29

SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 9600

API_IMAGE_UPLOAD = "https://flask-api-upload.onrender.com/upload"
API_SENSOR_UPLOAD = "https://flask-api-upload.onrender.com/upload_sensor"

# ================================
# 함수
# ================================
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def upload_image(filepath):
    try:
        with open(filepath, 'rb') as f:
            files = {'image': f}
            response = requests.post(API_IMAGE_UPLOAD, files=files)
            if response.status_code == 200:
                print(f"✅ 이미지 업로드 성공: {os.path.basename(filepath)}")
            else:
                print(f"❌ 이미지 업로드 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 이미지 업로드 오류: {e}")

def upload_sensor_data(sensor_dict):
    try:
        response = requests.post(API_SENSOR_UPLOAD, json=sensor_dict)
        if response.status_code == 200:
            print(f"✅ 센서 업로드 성공: {sensor_dict}")
        else:
            print(f"❌ 센서 업로드 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 센서 업로드 오류: {e}")

# ================================
# 카메라 루프
# ================================
def camera_loop():
    ensure_dir(SAVE_PATH)
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print(f"❌ 카메라 연결 실패: {RTSP_URL}")
        return

    last_capture_time = time.time()
    frame_count = 0
    last_minute_marker = datetime.datetime.now().strftime("%y%m%d_%H%M")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ 카메라 프레임 실패")
            time.sleep(5)
            continue

        current_time = time.time()
        if current_time - last_capture_time >= CAPTURE_INTERVAL_SECONDS:
            now = datetime.datetime.now()
            current_minute_marker = now.strftime("%y%m%d_%H%M")
            if current_minute_marker != last_minute_marker:
                frame_count = 0
                last_minute_marker = current_minute_marker
            frame_count += 1

            filename = os.path.join(SAVE_PATH, f"{current_minute_marker}_{frame_count:04d}.jpg")
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            print(f"📸 이미지 저장: {filename}")
            upload_image(filename)
            last_capture_time = current_time

        cv2.waitKey(1)

# ================================
# 센서 루프
# ================================
def sensor_loop():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        print(f"[센서] 시리얼 연결됨: {SERIAL_PORT}")
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    temp, ph, hum = map(float, line.split(","))
                    payload = {"temp": temp, "ph": ph, "humidity": hum}
                    upload_sensor_data(payload)
                except Exception as e:
                    print(f"[센서] 데이터 파싱 실패: '{line}' → {e}")
    except Exception as e:
        print(f"[센서] 시리얼 연결 실패: {e}")

# ================================
# 메인
# ================================
if __name__ == "__main__":
    threading.Thread(target=camera_loop, daemon=True).start()
    #threading.Thread(target=sensor_loop, daemon=True).start()

    # 메인 쓰레드를 유지
    while True:
        time.sleep(1)
