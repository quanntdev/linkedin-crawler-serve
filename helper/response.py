# helper/response.py

from fastapi import HTTPException

def Success(message: str, data: dict = None):
    return {
        "success": True,
        "message": message,
        "data": data
    }

def Error(message: str, status_code: int = 400):
    raise HTTPException(status_code=status_code, detail={
        "success": False,
        "message": message
    })
