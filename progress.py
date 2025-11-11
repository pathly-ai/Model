# progress.py
from fastapi import APIRouter, Depends
from auth import get_current_user
from db import users_collection, assessments_collection
from datetime import datetime
from typing import List, Dict

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/")
def get_user_progress(current_user=Depends(get_current_user)):
    user_id = str(current_user["_id"])

    # --- Fetch latest assessment record ---
    assessment_record = assessments_collection.find_one({"userId": user_id})

    # --- Calculate assessment progress ---
    assessment_details: List[Dict] = []
    total_assessments = 0
    completed_assessments = 0
    if assessment_record and "assessment" in assessment_record:
        for key, value in assessment_record["assessment"].items():
            status = "completed" if value else "pending"
            if value:
                completed_assessments += 1
            total_assessments += 1
            assessment_details.append({
                "title": key,
                "status": status
            })

    overall_progress = round((completed_assessments / total_assessments) * 100) if total_assessments else 0

    # --- Careers explored from recommendations ---
    recommendations = assessment_record.get("recommendations", []) if assessment_record else []
    careers_explored = len(recommendations)

    # --- Profile-related stats ---
    skills_identified = current_user.get("skillsIdentified", 0)
    goals_set = current_user.get("goalsSet", 0)
    goals_completed = current_user.get("goalsCompleted", 0)
    resources_viewed = current_user.get("resourcesViewed", 0)

    # --- Recent activities ---
    recent_activities: List[Dict] = []

    # 1️⃣ Completed assessments
    if assessment_record:
        recent_activities.append({
            "id": 1,
            "type": "assessment",
            "title": f"Completed {completed_assessments}/{total_assessments} assessments",
            "date": assessment_record.get("updatedAt", datetime.utcnow()).strftime("%Y-%m-%d"),
            "status": "completed" if completed_assessments > 0 else "in-progress"
        })

    # 2️⃣ Recommendations generated
    if recommendations:
        recent_activities.append({
            "id": 2,
            "type": "recommendation",
            "title": f"Received {len(recommendations)} career recommendations",
            "date": assessment_record.get("updatedAt", datetime.utcnow()).strftime("%Y-%m-%d"),
            "status": "completed"
        })

    # 3️⃣ Optional: track goals/resources activities if timestamps exist
    # Can extend to pull from a "user activities" collection if you have one

    # --- Milestones ---
    milestones: List[Dict] = [
        {
            "title": "Profile Created",
            "date": current_user.get("createdAt", datetime.utcnow()).strftime("%Y-%m-%d"),
            "completed": True
        },
        {
            "title": "First Assessment Completed",
            "date": assessment_record.get("updatedAt", datetime.utcnow()).strftime("%Y-%m-%d") if completed_assessments > 0 else None,
            "completed": completed_assessments > 0
        },
        {
            "title": "Career Recommendations Generated",
            "date": assessment_record.get("updatedAt", datetime.utcnow()).strftime("%Y-%m-%d") if careers_explored > 0 else None,
            "completed": careers_explored > 0
        },
        {
            "title": "Complete All Assessments",
            "date": "In Progress",
            "completed": completed_assessments == total_assessments and total_assessments > 0
        },
        {
            "title": "Create Action Plan",
            "date": "Upcoming",
            "completed": False
        }
    ]

    # --- Assemble final response ---
    response = {
        "progressData": {
            "overallProgress": overall_progress,
            "assessmentsCompleted": completed_assessments,
            "totalAssessments": total_assessments,
            "careersExplored": careers_explored,
            "resourcesViewed": resources_viewed,
            "skillsIdentified": skills_identified,
            "goalsSet": goals_set,
            "goalsCompleted": goals_completed
        },
        "recentActivities": recent_activities,
        "milestones": milestones,
        "assessmentDetails": assessment_details
    }

    return response