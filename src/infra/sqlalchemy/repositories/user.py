import cv2
import face_recognition
import numpy as np
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from  src.infra.sqlalchemy.models.user_log import UserLog
from ..models.user import User
from ..schemas.user import UserCreate
from src.infra.sqlalchemy.repositories.user_log import UserLogRepository
import logging

# Configuração do logger
logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
        self.IMAGE_DIR = "images" # Certifique-se que esta pasta exista na raiz do projeto

        if not os.path.exists(self.IMAGE_DIR):
            os.makedirs(self.IMAGE_DIR)

    def get_user(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self):
        return self.db.query(User).all()

    def extract_face_encoding(self, image_file_content: bytes) -> np.ndarray:

    # Converte os bytes da imagem para um array numpy
        np_image = np.frombuffer(image_file_content, np.uint8)
        image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if image_bgr is None:
            raise ValueError("Não foi possível decodificar a imagem enviada.")

    # Converte BGR para RGB
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    # Detecta e extrai encodings
        encodings = face_recognition.face_encodings(image_rgb)

        if not encodings:
            raise ValueError("Nenhum rosto detectado na imagem fornecida.")
        if len(encodings) > 1:
            raise ValueError("Mais de um rosto detectado na imagem. Por favor, forneça uma imagem com apenas um rosto.")

        return encodings[0]

    def create_user(self, user_data: UserCreate, image_file_content: bytes) -> User:

        # Extrai o encoding facial
        face_encoding = self.extract_face_encoding(image_file_content)

        # Converta o encoding numpy array para uma lista e depois para JSON string
        encoding_str = json.dumps(face_encoding.tolist())

        # 1. Crie o usuário no banco de dados
        db_user = User(
            name=user_data.name,
            cellphone=user_data.cellphone,
            encoding=encoding_str,
            image_path=""
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        # 2. Crie o nome do arquivo da imagem
        image_filename = f"{user_data.name.replace(' ', '_').lower()}_{db_user.id}.jpg"
        image_path = os.path.join(self.IMAGE_DIR, image_filename)

        # 3. Salve a imagem com o nome final
        np_image = np.frombuffer(image_file_content, np.uint8)
        image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
        cv2.imwrite(image_path, image_bgr)

        # 4. Atualize o caminho da imagem no banco
        db_user.image_path = image_path
        self.db.commit()
        self.db.refresh(db_user)

        return db_user



    def recognize_face(self, image_file_content: bytes, tolerance: float = 0.5) -> dict:
        """
        Recebe uma imagem, detecta todos os rostos e os compara com os usuários cadastrados.
        Retorna um JSON com o status, uma lista de pessoas reconhecidas (com id, nome,
        telefone, caminho da imagem e data/hora de entrada).
        """
        # Carregar todos os usuários do banco de dados
        users = self.db.query(User).all() 


        user_encodings = []
        user_names = []
        user_ids = []
        user_cellphones = []
        user_image_paths = []

        if not users:
            logger.info("Tentativa de reconhecimento sem usuários cadastrados no banco de dados.")
            return {
                "status": False,
                "recognized_people": []
            }

        for user in users:
            try:
                # Converte a string JSON do encoding de volta para array numpy
                encoding_list = json.loads(user.encoding)
                user_encodings.append(np.array(encoding_list))
                user_names.append(user.name)
                user_ids.append(user.id)
                user_cellphones.append(user.cellphone)
                user_image_paths.append(user.image_path)
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar encoding para o usuário {user.name} (ID: {user.id}): {e}. Ignorando.")
                continue
            except AttributeError as e:
                logger.error(f"Atributo ausente no usuário {user.name} (ID: {user.id}): {e}. Ignorando.")
                continue
            except Exception as e:
                logger.error(f"Erro inesperado ao processar dados do usuário {user.name} (ID: {user.id}): {e}. Ignorando.")
                continue

        # Processar a imagem recebida
        np_image = np.frombuffer(image_file_content, np.uint8)
        image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if image_bgr is None:
            logger.error("Falha ao decodificar a imagem enviada. Imagem pode estar corrompida ou formato inválido.")
            raise ValueError("Não foi possível decodificar a imagem enviada. Verifique o formato.")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image_rgb)
        face_encodings = face_recognition.face_encodings(image_rgb, face_locations)

        log_time = datetime.now().isoformat()
        recognized_people_in_image = []

        if not face_encodings:
            logger.info("Nenhum rosto detectado na imagem fornecida.")
            return {
                "status": False,
                "recognized_people": []
            }

        # Processar cada rosto detectado na imagem
        for i, face_encoding_to_check in enumerate(face_encodings):
            # Compara com os encodings dos usuários conhecidos
            matches = face_recognition.compare_faces(user_encodings, face_encoding_to_check, tolerance=tolerance)
            face_distances = face_recognition.face_distance(user_encodings, face_encoding_to_check)

            best_match_index = -1
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)

            if best_match_index != -1 and matches[best_match_index]:
                recognized_user_name = user_names[best_match_index]
                recognized_user_id = user_ids[best_match_index]
                recognized_user_cellphone = user_cellphones[best_match_index]
                recognized_user_image_path = user_image_paths[best_match_index]

                recognized_people_in_image.append({
                    "id": recognized_user_id,
                    "name": recognized_user_name,
                    "cellphone": recognized_user_cellphone,
                    "image_path": recognized_user_image_path,
                    "log_time": log_time
                })
                logger.info(f"Rosto reconhecido: {recognized_user_name} (ID: {recognized_user_id})")
            else:
                logger.info(f"Rosto detectado (índice {i}) não reconhecido.")

        final_status = bool(recognized_people_in_image)
        user_repo_log_repo = UserLogRepository(self.db) # Assumindo que UserLogRepository está disponível
        #log_time = datetime.now()
        for person in recognized_people_in_image:
            try:
                user_repo_log_repo.create(
                    user_id=person["id"],
                    log_time= log_time
                )
            except Exception as e:
                logger.error(f"Erro ao registrar log para o usuário {person['name']} (ID: {person['id']}): {e}")

        return {
            "status": final_status,
            "recognized_people": recognized_people_in_image
        }

    def delete_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            if os.path.exists(user.image_path):
                os.remove(user.image_path)
        
            self.db.query(UserLog).filter(UserLog.user_id == user_id).delete(synchronize_session=False)

           
            self.db.delete(user)

            
            self.db.commit()
            return True
        return False

    
    def update_user_name(self, user_id: int, name: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        if name:
            user.name = name
        
        self.db.commit()
        self.db.refresh(user)
        return user
    

    def update_user_image(self, user_id: int, image_file_content: bytes):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Extrai o novo encoding facial
        face_encoding = self.extract_face_encoding(image_file_content)

        # Converta o encoding numpy array para uma lista e depois para JSON string
        encoding_str = json.dumps(face_encoding.tolist())

        # Atualiza o encoding e a imagem do usuário
        user.encoding = encoding_str

        # Cria o nome do arquivo da nova imagem
        image_filename = f"{user.name.replace(' ', '_').lower()}_{user.id}.jpg"
        image_path = os.path.join(self.IMAGE_DIR, image_filename)

        # Salva a nova imagem
        np_image = np.frombuffer(image_file_content, np.uint8)
        image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
        cv2.imwrite(image_path, image_bgr)

        user.image_path = image_path

        self.db.commit()
        self.db.refresh(user)

        return user

    def update_user_cellphone(self, user_id: int, cellphone: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        if cellphone:
            user.cellphone = cellphone
        
        self.db.commit()
        self.db.refresh(user)
        return user