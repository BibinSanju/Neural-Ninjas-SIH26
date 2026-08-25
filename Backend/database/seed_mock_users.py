import sys, os, bcrypt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db import SessionLocal
from database.models import User, Role

def seed_users():
    db = SessionLocal()
    
    admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
    operator_role = db.query(Role).filter(Role.name == "Employee").first()
    
    users_to_add = [
        {"username": "admin_test", "password": "password", "role_id": admin_role.id if admin_role else None},
        {"username": "operator_test", "password": "password", "role_id": operator_role.id if operator_role else None}
    ]
    
    for u in users_to_add:
        if not db.query(User).filter(User.username == u["username"]).first():
            hashed_pw = bcrypt.hashpw(u["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = User(username=u["username"], password_hash=hashed_pw, role_id=u["role_id"])
            db.add(new_user)
            print(f"Added user: {u['username']}")
    
    db.commit()
    db.close()
    print("Mock users seeded successfully.")

if __name__ == "__main__":
    seed_users()
