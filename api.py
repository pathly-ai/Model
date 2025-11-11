from __future__ import annotations
from fastapi import FastAPI, HTTPException, Depends
from auth import router as auth_router
from assessment import router as assessment_router
from auth import get_current_user
from datetime import datetime
from db import assessments_collection
from progress import router as progress_router
from chatbot_service import get_chat_response, ChatRequest, ChatResponse
from auth import get_current_user


import os
import joblib
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

# --- Configuration ---
load_dotenv()
ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model.pkl"

app = FastAPI(title="Career Guidance API", version="1.0.0")
app.include_router(auth_router)
app.include_router(assessment_router)
app.include_router(progress_router)

# --- In-memory storage (for demonstration purposes) ---
conversation_history: Dict[str, List[Dict[str, str]]] = {}
DEFAULT_SESSION_ID = "global_session"

# --- Model Loading and Training ---
TRAIN_SAMPLES: Tuple[Tuple[str, str], ...] = (
    ("coding; programming; javascript; react; frontend; ui; design", "Frontend Developer"),
    ("python; backend; api; database; fastapi; server; rest", "Backend Developer"),
    ("python; pandas; statistics; machine learning; data; analysis; modeling", "Data Scientist"),
    ("excel; sql; reporting; dashboard; business intelligence; data cleaning", "Data Analyst"),
    ("figma; user research; wireframe; prototype; visual design; accessibility", "UI/UX Designer"),
    ("leadership; roadmap; product; market research; prioritization; stakeholder", "Product Manager"),
    ("seo; sem; content; campaign; social media; analytics; brand", "Digital Marketing Manager"),
    ("cad; solidworks; manufacturing; mechanical; design; engineering", "Mechanical Engineer"),
    ("biology; lab; research; experiment; clinical; biomedical", "Biomedical Researcher"),
    ("software engineering; programming; git; testing; deployment; cloud", "Software Engineer"),
)

def _train_and_save(model_path: Path) -> Path:
    X, y = [], []
    for text, label in TRAIN_SAMPLES:
        X.append(text)
        y.append(label)
    pipe: Pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("rf", RandomForestClassifier(n_estimators=200, random_state=42)),
    ])
    pipe.fit(X, y)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, model_path)
    return model_path

def ensure_model(model_path: Path) -> Path:
    model_path = Path(model_path)
    if not model_path.exists():
        return _train_and_save(model_path)
    return model_path

# --- CORS Middleware ---
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]
allow_all = len(origins) == 1 and origins[0] == "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False if allow_all else True,
    allow_methods=["*"],

    allow_headers=["*"],
)

# --- Pydantic Models ---
class AssessmentInput(BaseModel):
    p1: Optional[str] = Field(None)
    p2: Optional[str] = Field(None)
    p3: Optional[str] = Field(None)
    s1: Optional[List[str]] = Field(default_factory=list)
    s2: Optional[List[str]] = Field(default_factory=list)
    i1: Optional[List[str]] = Field(default_factory=list)
    i2: Optional[str] = Field(None)
    v1: Optional[str] = Field(None)
    v2: Optional[str] = Field(None)
    v3: Optional[str] = Field(None)

class CareerRecommendation(BaseModel):
    title: str
    matchPercentage: int
    description: str
    category: str
    salaryRange: str
    growthRate: str
    location: str
    requiredSkills: List[str]
    educationPath: List[str]
    examsCertifications: List[str]
    jobOutlook: str
    workEnvironment: str

class PredictionResponse(BaseModel):
    recommendations: List[CareerRecommendation]

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    recommendations: Optional[List[CareerRecommendation]] = None
    sessionId: str = DEFAULT_SESSION_ID

class ChatResponse(BaseModel):
    response: str

# --- Global Variables ---
_model = None
CAREER_DETAILS: Dict[str, Dict] = {
    # ... keep all career details as before ...
}

@app.on_event("startup")
def _load_model() -> None:
    global _model
    if not MODEL_PATH.exists():
        ensure_model(MODEL_PATH)
    _model = joblib.load(MODEL_PATH)

# --- Helper Functions ---
_DEFAULT_DETAILS: Dict[str, Any] = {
    "description": "",
    "category": "General",
    "salaryRange": "Varies",
    "growthRate": "N/A",
    "location": "Varies",
    "requiredSkills": [],
    "educationPath": [],
    "examsCertifications": [],
    "jobOutlook": "N/A",
    "workEnvironment": "Varies",
}
CAREER_DETAILS: Dict[str, Dict[str, Any]] = {
    "Frontend Developer": {
        "description": "Build responsive, accessible user interfaces for web applications using modern frameworks and design principles.",
        "category": "Technology",
        "salaryRange": "$65,000 - $130,000",
        "growthRate": "20%",
        "location": "Remote/Hybrid",
        "requiredSkills": ["HTML", "CSS", "JavaScript", "React", "UI Design", "Accessibility"],
        "educationPath": ["Bachelor's in Computer Science or related field", "Internships or Portfolio Projects", "Optional: Frontend Certifications"],
        "examsCertifications": ["Certified Frontend Developer", "React Certification"],
        "jobOutlook": "Strong - High demand for web apps",
        "workEnvironment": "Remote or Hybrid",
    },
    "Backend Developer": {
        "description": "Develop server-side logic, APIs, and databases to support web and mobile applications.",
        "category": "Technology",
        "salaryRange": "$70,000 - $140,000",
        "growthRate": "18%",
        "location": "Remote/Hybrid",
        "requiredSkills": ["Python", "Node.js", "REST APIs", "Database Design", "FastAPI", "Git"],
        "educationPath": ["Bachelor's in Computer Science", "Backend Projects or Internships", "Optional: Cloud/Database Certifications"],
        "examsCertifications": ["AWS Certified Developer", "Python Backend Certification"],
        "jobOutlook": "Strong - High demand for backend systems",
        "workEnvironment": "Office, Remote, or Hybrid",
    },
    "Data Scientist": {
        "description": "Analyze complex datasets to extract insights and support data-driven decision making.",
        "category": "Technology",
        "salaryRange": "$80,000 - $160,000",
        "growthRate": "35%",
        "location": "Major Cities",
        "requiredSkills": ["Python", "Pandas", "NumPy", "Machine Learning", "Data Visualization", "Statistics"],
        "educationPath": ["Bachelor's in Data Science, Statistics, or Computer Science", "Master's in Data Science (optional)", "Internships/Projects"],
        "examsCertifications": ["Data Science Professional Certificate", "Machine Learning Certification", "SQL Certification"],
        "jobOutlook": "Excellent - Fastest growing field",
        "workEnvironment": "Office, Remote, or Hybrid",
    },
    "Data Analyst": {
        "description": "Transform raw data into actionable insights and reports for business decisions.",
        "category": "Technology",
        "salaryRange": "$60,000 - $110,000",
        "growthRate": "25%",
        "location": "Remote/Hybrid",
        "requiredSkills": ["Excel", "SQL", "Data Cleaning", "Data Visualization", "Dashboarding", "Business Intelligence"],
        "educationPath": ["Bachelor's in Data Analytics, Statistics, or related field", "Internships or Projects"],
        "examsCertifications": ["Microsoft Excel Certification", "Power BI Certification"],
        "jobOutlook": "Good - Increasing demand for data-driven decision making",
        "workEnvironment": "Office, Remote, or Hybrid",
    },
    "UI/UX Designer": {
        "description": "Design intuitive, user-centered interfaces and experiences for digital products.",
        "category": "Design",
        "salaryRange": "$55,000 - $120,000",
        "growthRate": "15%",
        "location": "Remote/Hybrid",
        "requiredSkills": ["Figma", "Wireframing", "Prototyping", "User Research", "Visual Design", "Accessibility"],
        "educationPath": ["Bachelor's in Design or related field", "Portfolio Projects", "Certifications (optional)"],
        "examsCertifications": ["UX Design Certification", "Interaction Design Certification"],
        "jobOutlook": "Good - Growing demand for UX/UI professionals",
        "workEnvironment": "Office, Remote, or Hybrid",
    },
    "Product Manager": {
        "description": "Lead product development from ideation to launch, aligning business goals with user needs.",
        "category": "Management",
        "salaryRange": "$80,000 - $150,000",
        "growthRate": "12%",
        "location": "Office/Hybrid",
        "requiredSkills": ["Leadership", "Roadmap Planning", "Market Research", "Prioritization", "Stakeholder Management"],
        "educationPath": ["Bachelor's in Business, Engineering, or related field", "MBA (optional)", "Product Management Experience"],
        "examsCertifications": ["Certified Scrum Product Owner", "Product Management Certification"],
        "jobOutlook": "Stable - Increasing need for cross-functional leadership",
        "workEnvironment": "Office or Hybrid",
    },
    "Digital Marketing Manager": {
        "description": "Plan and execute digital marketing campaigns to build brand awareness and drive growth.",
        "category": "Marketing",
        "salaryRange": "$60,000 - $130,000",
        "growthRate": "18%",
        "location": "Remote/Hybrid",
        "requiredSkills": ["SEO", "SEM", "Content Marketing", "Social Media", "Analytics", "Campaign Management", "Brand Strategy"],
        "educationPath": ["Bachelor's in Marketing, Communications, or related field", "Internships/Experience"],
        "examsCertifications": ["Google Ads Certification", "HubSpot Marketing Certification"],
        "jobOutlook": "Good - Continuous growth in digital channels",
        "workEnvironment": "Office, Remote, or Hybrid",
    },
    "Mechanical Engineer": {
        "description": "Design mechanical systems and components, run simulations, and support manufacturing processes.",
        "category": "Engineering",
        "salaryRange": "$65,000 - $120,000",
        "growthRate": "10%",
        "location": "Onsite/Hybrid",
        "requiredSkills": ["CAD (SolidWorks/AutoCAD)", "Thermodynamics", "Materials", "Manufacturing", "FEA"],
        "educationPath": ["BS in Mechanical Engineering", "PE license (optional)"],
        "examsCertifications": ["Professional Engineer (PE) License", "SolidWorks Certification"],
        "jobOutlook": "Stable - Diverse industries",
        "workEnvironment": "Onsite/Hybrid",
    },
    "Biomedical Researcher": {
        "description": "Conduct experiments, analyze biological data, and contribute to scientific discoveries.",
        "category": "Research",
        "salaryRange": "$55,000 - $105,000",
        "growthRate": "15%",
        "location": "Research Labs/Universities",
        "requiredSkills": ["Biology", "Lab Techniques", "Research", "Clinical Studies", "Data Analysis"],
        "educationPath": ["Bachelor's in Biology or Biomedical Science", "Master's or PhD (optional)"],
        "examsCertifications": ["Clinical Research Certification", "Laboratory Safety Certification"],
        "jobOutlook": "Stable - Research demand continues",
        "workEnvironment": "Lab, Office",
    },
    "Software Engineer": {
        "description": "Develop software solutions, write clean code, test and deploy applications in the cloud.",
        "category": "Technology",
        "salaryRange": "$70,000 - $150,000",
        "growthRate": "22%",
        "location": "Remote/Hybrid",
        "requiredSkills": ["Programming", "Git", "Testing", "Deployment", "Cloud Platforms", "Software Architecture"],
        "educationPath": ["Bachelor's in Computer Science", "Internships/Projects"],
        "examsCertifications": ["AWS Certified Developer", "Software Engineering Certification"],
        "jobOutlook": "Strong - High demand for software development",
        "workEnvironment": "Office, Remote, or Hybrid",
    },
}

def build_details(title: str) -> Dict[str, Any]:
    details = CAREER_DETAILS.get(title)
    if details is None:
        return {**_DEFAULT_DETAILS, "description": f"A career path in {title}."}
    return {**_DEFAULT_DETAILS, **details}

def _flatten_assessment(a: AssessmentInput) -> str:
    parts: List[str] = []
    for field in [a.p1, a.p2, a.p3, a.i2, a.v1, a.v2, a.v3]:
        if field:
            parts.append(str(field))
    for lst in [a.s1, a.s2, a.i1]:
        if lst:
            parts.append("; ".join(lst))
    return " | ".join(parts)

# --- API Endpoints ---
@app.post("/predict", response_model=PredictionResponse)
def predict_and_save(payload: AssessmentInput, current_user=Depends(get_current_user)) -> PredictionResponse:
    if not _model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    text = _flatten_assessment(payload)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Empty assessment input")

    probabilities = _model.predict_proba([text])[0]
    classes = _model.named_steps["rf"].classes_
    top_3_indices = np.argsort(probabilities)[-3:][::-1]

    recommendations = []
    for i in top_3_indices:
        career_title = classes[i]
        probability = probabilities[i]
        details = build_details(career_title)
        recommendations.append(CareerRecommendation(
            title=career_title,
            matchPercentage=int(probability * 100),
            **details
        ))

    user_id = str(current_user["_id"])
    data_to_save = {
        "userId": user_id,
        "assessment": payload.dict(),
        "recommendations": [r.dict() for r in recommendations],
        "updatedAt": datetime.utcnow(),
    }

    existing = assessments_collection.find_one({"userId": user_id})
    if existing:
        assessments_collection.update_one({"userId": user_id}, {"$set": data_to_save})
    else:
        assessments_collection.insert_one(data_to_save)

    return PredictionResponse(recommendations=recommendations)

@app.post("/chatbot", response_model=ChatResponse)
def chatbot_endpoint(req: ChatRequest, current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    return get_chat_response(req, user_id)
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}