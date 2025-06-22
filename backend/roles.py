from fastapi import HTTPException, status, Depends
from .auth import get_current_user
from .models import User

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker

def require_manager(current_user: User = Depends(get_current_user)):
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Manager role required."
        )
    return current_user

def require_customer(current_user: User = Depends(get_current_user)):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Customer role required."
        )
    return current_user
