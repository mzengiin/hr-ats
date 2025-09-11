"""
Create admin user
"""
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.role import Role
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Create admin user"""
    db = next(get_db())
    
    # Get admin role
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    if not admin_role:
        print("Admin role not found!")
        return
    
    # Check if admin user already exists
    existing_user = db.query(User).filter(User.email == "admin@hrats.com").first()
    if existing_user:
        print("Admin user already exists!")
        return
    
    # Create admin user
    admin_user = User(
        email="admin@hrats.com",
        password_hash=pwd_context.hash("admin123"),
        first_name="Admin",
        last_name="User",
        phone="+90 555 000 0001",
        role_id=admin_role.id,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    
    print("Admin user created successfully!")
    print("Email: admin@hrats.com")
    print("Password: admin123")

if __name__ == "__main__":
    create_admin_user()
