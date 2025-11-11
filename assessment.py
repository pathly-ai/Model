from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from auth import get_current_user
from db import assessments_collection

router = APIRouter(prefix="/assessment", tags=["Assessment"])


class AssessmentInput(BaseModel):
    p1: Optional[str] = None
    p2: Optional[str] = None
    p3: Optional[str] = None
    s1: Optional[List[str]] = None
    s2: Optional[List[str]] = None
    i1: Optional[List[str]] = None
    i2: Optional[str] = None
    v1: Optional[str] = None
    v2: Optional[str] = None
    v3: Optional[str] = None


class CareerRecommendation(BaseModel):
    title: str
    matchPercentage: int  # int for frontend
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


class SaveAssessmentRequest(BaseModel):
    assessment: AssessmentInput
    recommendations: List[CareerRecommendation]


@router.post("/save")
def save_assessment(request: SaveAssessmentRequest, current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    new_data = {
        "userId": user_id,
        "assessment": request.assessment.dict(),
        "recommendations": [r.dict() for r in request.recommendations],
        "updatedAt": datetime.utcnow(),
    }

    existing = assessments_collection.find_one({"userId": user_id})
    if existing:
        assessments_collection.update_one({"userId": user_id}, {"$set": new_data})
    else:
        assessments_collection.insert_one(new_data)

    return {"message": "Assessment saved successfully"}


@router.get("/fetch")
def get_assessment(current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])
    record = assessments_collection.find_one({"userId": user_id})

    if not record:
        raise HTTPException(status_code=404, detail="No assessment found")

    # Ensure arrays are not None
    recommendations = [
        {
            **r,
            "requiredSkills": r.get("requiredSkills") or [],
            "educationPath": r.get("educationPath") or [],
            "examsCertifications": r.get("examsCertifications") or [],
        }
        for r in record.get("recommendations", [])
    ]

    return {
        "assessment": record.get("assessment") or {},
        "recommendations": recommendations,
    }