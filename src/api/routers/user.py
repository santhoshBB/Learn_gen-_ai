from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(tags=["login"])

# Define the request body model
class LoginRequest(BaseModel):
    mobile: str


@router.post("/login")
async def user_login(request: LoginRequest):
    mobile_number = request.mobile
    # Add your logic here (e.g., validate mobile, check database, etc.)
    return {"message": f"Login request received for mobile: {mobile_number}"}