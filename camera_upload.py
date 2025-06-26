import cv2
import time
import os
import datetime
import requests

RTSP_URL = "rtsp://admin:dasung35$$@192.168.0.64/Streaming/Channels/101"
SAVE_PATH = "captured_images"
CAPTURE_INTERVAL_SECONDS = 29
FILENAME_PREFIX = "cam01_"
SHOW_PREVIEW = True

API_ENDPOINT = "https://your-api-server.onrender.com/upload"  # 여기에 Render 또는 실제 API 주소 넣기

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def upload_to_api(filepath):
    try:
        with open(filepath, 'rb') as f:
            files = {'image': f}
            response = requests.post(API_ENDPOINT, files=files)
            if response.status_code == 200:
                print(f"✅ 업로드 성공: {os.path.basename(filepath)}")
            else:
                print(f"❌ 업로드 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 업로드 오류: {e}")

def main():
    ensure_dir(SAVE_PATH)
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print(f"❌ 카메라 연결 실패: {RTSP_URL}")
        return

    last_capture_time = time.time()
    frame_count = 0
    last_minute_marker = datetime.datetime.now().strftime("%y%m%d_%H%M")

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("⚠️ 프레임 수신 실패, 재연결 시도...")
                time.sleep(5)
                cap.release()
                cap = cv2.VideoCapture(RTSP_URL)
                continue

            current_time = time.time()

            if SHOW_PREVIEW:
                preview_frame = cv2.resize(frame, (640, 360))
                cv2.imshow('Live Preview', preview_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()

            if current_time - last_capture_time >= CAPTURE_INTERVAL_SECONDS:
                now = datetime.datetime.now()
                current_minute_marker = now.strftime("%y%m%d_%H%M")

                if current_minute_marker != last_minute_marker:
                    frame_count = 0
                    last_minute_marker = current_minute_marker

                frame_count += 1
                filename = os.path.join(SAVE_PATH, f"{FILENAME_PREFIX}{current_minute_marker}_{frame_count:04d}.jpg")

                try:
                    cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
                    print(f"📸 저장됨: {filename}")
                    upload_to_api(filename)
                    last_capture_time = current_time
                except Exception as e:
                    print(f"❌ 저장 실패: {filename}, {e}")

    except KeyboardInterrupt:
        print("\n프로그램 종료.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
