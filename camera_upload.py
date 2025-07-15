# -*- coding: utf-8 -*-
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
CAPTURE_INTERVAL_SECONDS = 24

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUDRATE = 9600

API_IMAGE_UPLOAD = "https://flask-api-upload.onrender.com/upload"
API_PH = "https://flask-api-upload.onrender.com/upload_ph"
API_TEMP = "https://flask-api-upload.onrender.com/upload_temp"
API_HUM = "https://flask-api-upload.onrender.com/upload_hum"
API_CO2 = "https://flask-api-upload.onrender.com/upload_co2"

# ================================
# 전역 플래그
# ================================
force_capture = False
force_capture_lock = threading.Lock()

# ================================
# 공통 함수
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
                print(f"[이미지] 업로드 성공: {os.path.basename(filepath)}")
            else:
                print(f"[이미지] 업로드 실패: {response.status_code}")
    except Exception as e:
        print(f"[이미지] 업로드 오류: {e}")

def upload_ph(ph):
    try:
        response = requests.post(API_PH, json={"ph": ph})
        print(f"[pH] 업로드: {ph}, 응답: {response.status_code}")
    except Exception as e:
        print(f"[pH] 업로드 오류: {e}")

def upload_temp(temp):
    try:
        response = requests.post(API_TEMP, json={"temp": temp})
        print(f"[온도] 업로드: {temp}, 응답: {response.status_code}")
    except Exception as e:
        print(f"[온도] 업로드 오류: {e}")

def upload_hum(hum):
    try:
        response = requests.post(API_HUM, json={"humidity": hum})
        print(f"[습도] 업로드: {hum}, 응답: {response.status_code}")
    except Exception as e:
        print(f"[습도] 업로드 오류: {e}")

def upload_co2(co2):
    try:
        response = requests.post(API_CO2, json={"co2": co2})
        print(f"[CO2] 업로드: {co2}, 응답: {response.status_code}")
    except Exception as e:
        print(f"[CO2] 업로드 오류: {e}")

# ================================
# 카메라 루프
# ================================
def camera_loop():
    global force_capture
    ensure_dir(SAVE_PATH)
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print(f"[카메라] 연결 실패: {RTSP_URL}")
        return

    last_capture_time = time.time()
    frame_count = 0
    last_minute_marker = datetime.datetime.now().strftime("%y%m%d_%H%M")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[카메라] 프레임 읽기 실패")
            time.sleep(5)
            continue

        current_time = time.time()
        do_capture = False

        with force_capture_lock:
            if force_capture:
                print("[카메라] LIMIT SWITCH 감지 → 즉시 캡처")
                force_capture = False
                # 타이머와 카운터 초기화
                last_capture_time = current_time
                frame_count = 0
                last_minute_marker = datetime.datetime.now().strftime("%y%m%d_%H%M")
                do_capture = True

        if current_time - last_capture_time >= CAPTURE_INTERVAL_SECONDS or do_capture:
            now = datetime.datetime.now()
            current_minute_marker = now.strftime("%y%m%d_%H%M")
            if current_minute_marker != last_minute_marker:
                frame_count = 0
                last_minute_marker = current_minute_marker
            frame_count += 1

            filename = os.path.join(SAVE_PATH, f"{current_minute_marker}_{frame_count:04d}.jpg")
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            print(f"[카메라] 이미지 저장: {filename}")
            upload_image(filename)
            last_capture_time = current_time

        cv2.waitKey(1)

# ================================
# 센서 루프
# ================================
def sensor_loop():
    global force_capture
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        ser.reset_input_buffer()
        print(f"[센서] 시리얼 연결: {SERIAL_PORT}")

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[센서] 수신: {line}")
                if line.startswith("# READY"):
                    ser.write(b"START\n")
                    print("[센서] START 전송")
                elif line.startswith("# LIMIT"):
                    print("[센서] LIMIT SWITCH 수신 → 즉시 캡처 플래그 ON")
                    with force_capture_lock:
                        force_capture = True
                else:
                    try:
                        ph, temp, hum, co2 = map(float, line.split(","))
                        upload_ph(ph)
                        upload_temp(temp)
                        upload_hum(hum)
                        upload_co2(co2)
                    except Exception as e:
                        print(f"[센서] 파싱 오류: '{line}' → {e}")
    except Exception as e:
        print(f"[센서] 시리얼 오류: {e}")

# ================================
# 메인
# ================================
if __name__ == "__main__":
    threading.Thread(target=camera_loop, daemon=True).start()
    threading.Thread(target=sensor_loop, daemon=True).start()
    while True:
        time.sleep(1)
