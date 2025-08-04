from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..repositories.user import UserRepository
from fastapi import Request

router = APIRouter(prefix="/recognition", tags=["Face Recognition"])

@router.post("/recognize", summary="Reconhecer um rosto a partir de uma imagem (RAW JPEG)", response_model=dict)
async def recognize_face_endpoint(request: Request, db: Session = Depends(get_db)):
    """
    Novo endpoint que aceita imagem RAW (Content-Type: image/jpeg) diretamente no corpo da requisição.
    Compatível com a ESP-CAM.
    """
    user_repo = UserRepository(db)
    try:
        # Lê os bytes brutos enviados pela ESP-CAM
        image_content = await request.body()
        result = user_repo.recognize_face(image_content)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")