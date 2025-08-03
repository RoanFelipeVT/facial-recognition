from src.infra.sqlalchemy.repository.admin_repository import AdminRepository
from src.schemas.admin_schema import AdminCreate
from src.infra.sqlalchemy.database import SessionLocal
import getpass

def create_admin_user():
    """
    Script de linha de comando para criar um novo utilizador administrador.
    """
    print("--- Criação de Novo Administrador ---")
    
    name = input("Digite o nome de utilizador do novo admin: ")
    password = getpass.getpass("Digite a palavra-passe do novo admin: ")
    
    db = SessionLocal()
    
    try:
        admin_data = AdminCreate(name=name, password=password)
        
        repo = AdminRepository(db)
        repo.create_admin(admin_data)
        
        print(f"\n[SUCESSO] Administrador '{name}' criado com sucesso!")
        
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro ao criar o administrador: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
