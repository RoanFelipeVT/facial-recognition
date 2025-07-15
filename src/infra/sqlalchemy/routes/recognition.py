from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import numpy as np
import cv2
import json
from ..database import get_db
from ..repositories.user import UserRepository

router = APIRouter(prefix="/recognition", tags=["Face Recognition"])

@router.post("/", summary="Reconhecer um rosto a partir de uma imagem", response_model=dict)
async def recognize_face_endpoint(
    image_file: UploadFile = File(..., description="Imagem do rosto para reconhecimento"),
    db: Session = Depends(get_db)
):
    """
    Este endpoint recebe uma imagem e tenta reconhecer um rosto nela.
    Compara o rosto detectado com os usuários cadastrados no banco de dados.
    """
    user_repo = UserRepository(db)
    try:
        image_content = await image_file.read()
        result = user_repo.recognize_face(image_content)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno no servidor: {e}")