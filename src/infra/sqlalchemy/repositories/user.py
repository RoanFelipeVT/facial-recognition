import cv2
import face_recognition
import numpy as np
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
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


    def create_user(self, user_data: UserCreate, image_file_content: bytes) -> User:
        """
        Cria um novo usuário, processa a imagem para reconhecimento facial
        e salva o encoding e o caminho da imagem.
        """
        # Converta os bytes da imagem para um array numpy
        np_image = np.frombuffer(image_file_content, np.uint8)
        image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if image_bgr is None:
            raise ValueError("Não foi possível decodificar a imagem enviada.")

        # Converta BGR para RGB para o face_recognition
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Encontre os encodings faciais na imagem
        encodings = face_recognition.face_encodings(image_rgb)
        
        if not encodings:
            raise ValueError("Nenhum rosto detectado na imagem fornecida.")
        if len(encodings) > 1:
            raise ValueError("Mais de um rosto detectado na imagem. Por favor, forneça uma imagem com apenas um rosto.")

        face_encoding = encodings[0]

        # Converta o encoding numpy array para uma lista e depois para JSON string
        encoding_str = json.dumps(face_encoding.tolist())

        # 1. Crie o usuário no banco de dados
        db_user = User(
            name=user_data.name,
            position=user_data.position,
            cellphone=user_data.cellphone,
            email=user_data.email,
            encoding=encoding_str,
            image_path="" # Temporariamente vazio ou None
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user) 

        # 2. Use o ID para criar o nome do arquivo da imagem
        image_filename = f"{user_data.name.replace(' ', '_').lower()}_{db_user.id}.jpg"
        image_path = os.path.join(self.IMAGE_DIR, image_filename)

        # 3. Salve a imagem com o nome final
        cv2.imwrite(image_path, image_bgr)

        # 4. Atualize o caminho da imagem no objeto do banco de dados e salve
        db_user.image_path = image_path
        self.db.commit() # Salva a atualização do caminho
        self.db.refresh(db_user) # Atualiza o objeto com o caminho salvo

        return db_user





    def recognize_face(self, image_file_content: bytes, tolerance: float = 0.5) -> dict:
        """
        Recebe uma imagem, detecta todos os rostos e os compara com os usuários cadastrados.
        Retorna um JSON com o status, uma lista de pessoas reconhecidas (com id, nome,
        posição, caminho da imagem e data/hora de entrada).
        """
        # Carregar todos os usuários do banco de dados
        all_users = self.db.query(User).all()
        known_face_encodings = []
        known_face_names = []
        known_face_ids = []
        known_face_positions = []      # NOVO: Lista para armazenar as posições
        known_face_image_paths = []    # NOVO: Lista para armazenar os caminhos das imagens

        if not all_users:
            logger.info("Tentativa de reconhecimento sem usuários cadastrados no banco de dados.")
            return {
                "status": False,
                "recognized_people": []
            }

        for user in all_users:
            try:
                # Converte a string JSON do encoding de volta para array numpy
                encoding_list = json.loads(user.encoding)
                known_face_encodings.append(np.array(encoding_list))
                known_face_names.append(user.name)
                known_face_ids.append(user.id)
                known_face_positions.append(user.position)        # NOVO: Adiciona a posição do usuário
                known_face_image_paths.append(user.image_path)    # NOVO: Adiciona o caminho da imagem do usuário
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar encoding para o usuário {user.name} (ID: {user.id}): {e}. Ignorando.")
                continue
            except Exception as e:
                logger.error(f"Erro inesperado ao processar encoding do usuário {user.name} (ID: {user.id}): {e}. Ignorando.")
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

        current_timestamp = datetime.now().isoformat()
        recognized_people_in_image = []

        if not face_encodings:
            logger.info("Nenhum rosto detectado na imagem fornecida.")
            return {
                "status": False,
                "recognized_people": []
            }

        # Processar cada rosto detectado na imagem
        for i, face_encoding_to_check in enumerate(face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding_to_check, tolerance=tolerance)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding_to_check)

            best_match_index = -1
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)

            if best_match_index != -1 and matches[best_match_index]:
                recognized_user_name = known_face_names[best_match_index]
                recognized_user_id = known_face_ids[best_match_index]
                recognized_user_position = known_face_positions[best_match_index]    # NOVO: Pega a posição
                recognized_user_image_path = known_face_image_paths[best_match_index] # NOVO: Pega o caminho da imagem

                recognized_people_in_image.append({
                    "id": recognized_user_id,
                    "name": recognized_user_name,
                    "position": recognized_user_position,    # NOVO: Inclui a posição
                    "image_path": recognized_user_image_path, # NOVO: Inclui o caminho da imagem
                    "timestamp": current_timestamp
                })
                logger.info(f"Rosto reconhecido: {recognized_user_name} (ID: {recognized_user_id})")
            else:
                logger.info(f"Rosto detectado (índice {i}) não reconhecido.")

        final_status = bool(recognized_people_in_image)

        return {
            "status": final_status,
            "recognized_people": recognized_people_in_image
        }

    def delete_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Opcional: remover a imagem do sistema de arquivos
            if os.path.exists(user.image_path):
                os.remove(user.image_path)
            self.db.delete(user)
            self.db.commit()
            return True
        return False