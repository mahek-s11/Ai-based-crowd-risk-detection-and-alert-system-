from fastapi import FastAPI, UploadFile, File
from typing import List
import shutil
import os
from main import analyze_video

app = FastAPI()

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.get("/")
def home():
    return {"message": "Stampede Risk Detection API Running"}


# -------------------------
# Single Camera
# -------------------------
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_video(file_path)
    return result


# -------------------------
# Multi-Camera System
# -------------------------
@app.post("/analyze_system")
async def analyze_system(files: List[UploadFile] = File(...)):

    system_results = []
    total_persons = 0

    for index, file in enumerate(files):
        camera_id = f"CAM-B{index+1}"

        file_path = os.path.join(UPLOAD_FOLDER, f"{camera_id}_{file.filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = analyze_video(file_path)
        result["camera_id"] = camera_id

        total_persons += result.get("people_count", 0)
        system_results.append(result)

    # Count zones
    high_risk_zones = sum(1 for r in system_results if r.get("risk_level") == "High")
    medium_risk_zones = sum(1 for r in system_results if r.get("risk_level") == "Medium")
    low_risk_zones = sum(1 for r in system_results if r.get("risk_level") == "Low")

    # Determine system status
    if high_risk_zones >= 1:
        system_status = "CRITICAL"
    elif medium_risk_zones >= 1:
        system_status = "WARNING"
    else:
        system_status = "STABLE"

    return {
        "system_status": system_status,
        "total_persons": total_persons,
        "high_risk_zones": high_risk_zones,
        "medium_risk_zones": medium_risk_zones,
        "low_risk_zones": low_risk_zones,
        "active_incidents": high_risk_zones,
        "zones": system_results
    }