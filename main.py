from ultralytics import YOLO
import cv2
import numpy as np
from datetime import datetime

# Better model than nano
model = YOLO("yolov8s.pt")


def analyze_video(video_path):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return {
            "camera_id": "CAM_01",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": "Unable to open video file",
            "risk_level": "Unknown",
            "alert": {
                "triggered": False,
                "severity": "Unknown",
                "recommended_action": "Check video source"
            }
        }

    people_counts = []

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 5 != 0:
            continue

        results = model(frame, conf=0.3, iou=0.5, verbose=False)

        count = 0
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == 0:
                    count += 1

        people_counts.append(count)

    cap.release()

    if not people_counts:
        return {
            "camera_id": "CAM_01",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "risk_level": "Unknown",
            "alert": {
                "triggered": False,
                "severity": "Unknown",
                "recommended_action": "No detections"
            }
        }

    avg_count = np.mean(people_counts)
    max_count = np.max(people_counts)

    # Smooth logic: use 75th percentile to avoid spikes
    percentile_75 = np.percentile(people_counts, 75)

    crowd_metric = (0.6 * percentile_75 + 0.4 * avg_count)

    # Wide realistic thresholds
    if crowd_metric < 5:
        final_risk = "Low"
        risk_score = 30

    elif crowd_metric < 15:
        final_risk = "Medium"
        risk_score = 60

    else:
        final_risk = "High"
        risk_score = 90

    alert_status = {
        "triggered": final_risk == "High",
        "severity": final_risk,
        "recommended_action": (
            "Open emergency exits and deploy crowd control"
            if final_risk == "High"
            else "Monitor situation closely"
            if final_risk == "Medium"
            else "Normal monitoring"
        )
    }

    return {
        "camera_id": "CAM_01",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "people_count": int(round(avg_count)),
        "average_risk_score": float(risk_score),
        "peak_risk_score": float(risk_score),
        "risk_level": final_risk,
        "risk_trend": "Stable",
        "alert": alert_status
    }


if __name__ == "__main__":
    print(analyze_video("test_video.mp4"))