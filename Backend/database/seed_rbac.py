import sys
import os

# Add Backend directory to sys.path so we can import from database module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import SessionLocal, engine
from database.models import Base, Department, Role, Permission

def seed_database():
    # 1. Create tables if they don't exist
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding Permissions...")
        permissions_data = [
            "VIEW", "CREATE", "UPDATE", "DELETE", "APPROVE", 
            "EXPORT", "AUDIT", "ADMIN", "USER_MANAGE", 
            "ROLE_MANAGE", "SECURITY_MANAGE", "EMERGENCY_ACCESS"
        ]
        
        db_permissions = {}
        for p_name in permissions_data:
            perm = db.query(Permission).filter(Permission.name == p_name).first()
            if not perm:
                perm = Permission(name=p_name)
                db.add(perm)
            db_permissions[p_name] = perm
            
        db.commit()

        print("Seeding Departments...")
        departments_data = [
            "Corporate Management", "Finance", "Refinery Operations", "Projects", 
            "Maintenance", "Materials / Procurement", "HSE", "Marketing", 
            "Impex & Shipping", "Human Resources", "Information Systems", 
            "Internal Audit", "Legal", "Vigilance", "Plant Security", "Quality Laboratory"
        ]
        
        for d_name in departments_data:
            dept = db.query(Department).filter(Department.name == d_name).first()
            if not dept:
                dept = Department(name=d_name)
                db.add(dept)
                
        db.commit()

        print("Seeding Roles...")
        roles_data = [
            {"name": "Super Admin", "type": "System", "perms": permissions_data}, # All perms
            {"name": "IT Administrator", "type": "System", "perms": ["VIEW", "ADMIN", "USER_MANAGE", "ROLE_MANAGE", "SECURITY_MANAGE"]},
            {"name": "Management", "type": "System", "perms": ["VIEW", "APPROVE", "EXPORT"]},
            {"name": "Department Head", "type": "System", "perms": ["VIEW", "CREATE", "UPDATE", "APPROVE", "EXPORT"]},
            {"name": "Department Manager", "type": "System", "perms": ["VIEW", "CREATE", "UPDATE", "APPROVE"]},
            {"name": "Department Officer", "type": "System", "perms": ["VIEW", "CREATE", "UPDATE"]},
            {"name": "Employee", "type": "System", "perms": ["VIEW", "CREATE"]},
            {"name": "Field Operator", "type": "Field", "perms": ["VIEW", "CREATE", "UPDATE"]},
            {"name": "Maintenance Technician", "type": "Field", "perms": ["VIEW", "UPDATE"]},
            {"name": "HSE / Safety Officer", "type": "Field", "perms": ["VIEW", "CREATE", "EMERGENCY_ACCESS"]},
            {"name": "Security User", "type": "Field", "perms": ["VIEW", "CREATE"]}
        ]
        
        for r_data in roles_data:
            role = db.query(Role).filter(Role.name == r_data["name"]).first()
            if not role:
                role = Role(name=r_data["name"], role_type=r_data["type"])
                db.add(role)
            
            # Assign permissions
            for p_name in r_data["perms"]:
                if db_permissions[p_name] not in role.permissions:
                    role.permissions.append(db_permissions[p_name])
                    
        db.commit()
        print("Database seeded successfully with MRPL RBAC architecture!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
