from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os

app = FastAPI(title="Zero Trust Risk Engine")

# --- 1. LOAD AI MODELS ---
# We use absolute paths or relative paths. Ensure these files are in the same folder as app.py
try:
    model = joblib.load('risk_model.joblib')
    encoders = joblib.load('encoders.joblib')
    target_le = joblib.load('target_encoder.joblib')
    print("✅ System: Risk Engine Loaded Successfully.")
except Exception as e:
    model = None
    print(f"❌ System Error: Model not found. {e}")
    print("   -> Did you run train_model.py first?")

# --- 2. SERVE FRONTEND ---
# This makes the "frontend" folder accessible at /static
# Ensure you have a folder named "frontend" with index.html, style.css, script.js inside it.
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
else:
    print("⚠️ Warning: 'frontend' folder not found. GUI will not load.")

@app.get("/")
def read_root():
    """Serves the Home Page"""
    return FileResponse('frontend/index.html')

# --- 3. API INPUT SCHEMA ---
class IncidentTelemetry(BaseModel):
    Category: str
    MitreTechniques: str
    ActionGrouped: str
    EntityType: str
    OSFamily: str
    SuspicionLevel: str
    CountryCode: str

# --- 4. HEALTH CHECK (Kubernetes Requirement) ---
@app.get("/healthz")
def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not initialized")
    return {"status": "healthy", "service": "risk-engine"}

# --- 5. PREDICTION ENDPOINT ---
@app.post("/predict")
def predict_risk(telemetry: IncidentTelemetry):
    """
    Zero-Trust Policy Decision Point.
    Logic: Block if AI predicts 'TruePositive' OR if SuspicionLevel is explicitly 'High'.
    """
    if not model:
        raise HTTPException(status_code=503, detail="Service unavailable (Model missing)")

    # A. Preprocessing (Encode Data)
    data_dict = telemetry.dict()
    df = pd.DataFrame([data_dict])

    # Apply the same encoders used in training
    for col, le in encoders.items():
        if col in df.columns:
            val = str(df[col].values[0])
            # Handle unknown categories safely (map to 0)
            if val in le.classes_:
                df[col] = le.transform([val])[0] 
            else:
                df[col] = 0
    
    # B. AI Prediction
    probs = model.predict(df)[0] # Returns array [Prob_Benign, Prob_FalsePos, Prob_TruePos]
    
    # Identify the AI's top choice
    pred_idx = np.argmax(probs)
    confidence = float(probs[pred_idx])
    predicted_grade = target_le.inverse_transform([pred_idx])[0]

    # C. Hybrid Zero Trust Logic
    # 1. AI Rule: If model thinks it's a TruePositive -> DENY
    # 2. Hard Rule: If input says "High" Suspicion -> DENY (Override AI)
    
    is_high_risk_input = (telemetry.SuspicionLevel == 'High')
    is_ai_flagged = (predicted_grade == 'TruePositive')

    if is_ai_flagged or is_high_risk_input:
        decision = "DENIED"
        
        # Create a helpful reason string
        if is_high_risk_input and not is_ai_flagged:
            reason = f"Policy Block: High Suspicion Input (AI predicted {predicted_grade})"
        else:
            reason = f"AI Block: Predicted {predicted_grade}"
            
    else:
        decision = "ALLOWED"
        reason = f"Access Granted: Verified Safe ({predicted_grade})"

    # D. Probability Breakdown (for the UI)
    class_names = target_le.classes_
    breakdown = {name: float(p) for name, p in zip(class_names, probs)}

    response = {
        "decision": decision,
        "predicted_grade": predicted_grade,
        "confidence": confidence,
        "breakdown": breakdown,
        "reason": reason
    }

    # E. Return Response
    # If DENIED, we send a 403 error but include the full JSON details so the UI can display stats.
    if decision == "DENIED":
        raise HTTPException(status_code=403, detail=response)

    return response