import cv2
import face_recognition
import numpy as np
import json
import os
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
        self.IMAGE_DIR = "images" # Certifique-se que esta pasta exista na raiz do projeto

        if not os.path.exists(self.IMAGE_DIR):
            os.makedirs(self.IMAGE_DIR)

    def get_user(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user_data: UserCreate, image_file_content: bytes):
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


    def recognize_face(self, image_file_content: bytes, tolerance: float = 0.5):
        """
        Recebe uma imagem, detecta todos os rostos e os compara com os usuários cadastrados.
        Retorna uma lista de resultados de reconhecimento para cada rosto detectado.
        """
        # Carregar todos os usuários do banco de dados
        all_users = self.db.query(User).all()
        known_face_encodings = []
        known_face_names = []
        known_face_ids = []

        if not all_users:
            return {    
                "status": "success"
                #"message": "Nenhum rosto cadastrado para reconhecimento."
                #"results": []
                    }

        for user in all_users:
            try:
                # Converte a string JSON do encoding de volta para array numpy
                encoding_list = json.loads(user.encoding)
                known_face_encodings.append(np.array(encoding_list))
                known_face_names.append(user.name)
                known_face_ids.append(user.id)
            except json.JSONDecodeError:
                print(f"Erro ao decodificar encoding para o usuário {user.name} (ID: {user.id}). Ignorando.")
                continue
            except Exception as e:
                print(f"Erro ao processar encoding do usuário {user.name} (ID: {user.id}): {e}. Ignorando.")
                continue

        # Processar a imagem recebida
        np_image = np.frombuffer(image_file_content, np.uint8)
        image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        if image_bgr is None:
            raise ValueError("Não foi possível decodificar a imagem enviada. Verifique o formato.")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image_rgb)
        face_encodings = face_recognition.face_encodings(image_rgb, face_locations)

        if not face_encodings:
            return {"status": "success", "message": "Nenhum rosto detectado na imagem.", "results": []}

        # Processar cada rosto detectado
        recognition_results = []
        for i, face_encoding_to_check in enumerate(face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding_to_check, tolerance=tolerance)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding_to_check)

            best_match_index = -1
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)

            if best_match_index != -1 and matches[best_match_index]:
                recognized_user_name = known_face_names[best_match_index]
                recognized_user_id = known_face_ids[best_match_index]
                recognition_results.append({
                    "face_index": i, # Índice do rosto na imagem (para referência)
                    "status": "recognized",
                    "user": {
                        "id": recognized_user_id,
                        "name": recognized_user_name
                    }
                })
            else:
                recognition_results.append({
                    #"face_index": i,
                    "status": False
                    #"message": "Rosto não reconhecido."
                })

        return {
            "status": True,
            #"message": f"{len(face_encodings)} rosto(s) processado(s) na imagem.",
            #"results": recognition_results
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