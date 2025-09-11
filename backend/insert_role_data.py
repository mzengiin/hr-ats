"""
Insert role management data
"""
import asyncio
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.role import Role, Permission, RolePermission

def insert_permissions():
    """Insert default permissions"""
    db = next(get_db())
    
    permissions = [
        # Kullanıcı Yönetimi
        {"name": "Kullanıcıları Görüntüle", "code": "users:read", "category": "Kullanıcı Yönetimi", "description": "Kullanıcı listesini görüntüleme yetkisi"},
        {"name": "Kullanıcı Oluştur", "code": "users:create", "category": "Kullanıcı Yönetimi", "description": "Yeni kullanıcı oluşturma yetkisi"},
        {"name": "Kullanıcı Düzenle", "code": "users:update", "category": "Kullanıcı Yönetimi", "description": "Kullanıcı bilgilerini düzenleme yetkisi"},
        {"name": "Kullanıcı Sil", "code": "users:delete", "category": "Kullanıcı Yönetimi", "description": "Kullanıcı silme yetkisi"},
        
        # Aday Yönetimi
        {"name": "Adayları Görüntüle", "code": "candidates:read", "category": "Aday Yönetimi", "description": "Aday listesini görüntüleme yetkisi"},
        {"name": "Aday Oluştur", "code": "candidates:create", "category": "Aday Yönetimi", "description": "Yeni aday oluşturma yetkisi"},
        {"name": "Aday Düzenle", "code": "candidates:update", "category": "Aday Yönetimi", "description": "Aday bilgilerini düzenleme yetkisi"},
        {"name": "Aday Sil", "code": "candidates:delete", "category": "Aday Yönetimi", "description": "Aday silme yetkisi"},
        
        # Mülakat Yönetimi
        {"name": "Mülakatları Görüntüle", "code": "interviews:read", "category": "Mülakat Yönetimi", "description": "Mülakat listesini görüntüleme yetkisi"},
        {"name": "Mülakat Oluştur", "code": "interviews:create", "category": "Mülakat Yönetimi", "description": "Yeni mülakat oluşturma yetkisi"},
        {"name": "Mülakat Düzenle", "code": "interviews:update", "category": "Mülakat Yönetimi", "description": "Mülakat bilgilerini düzenleme yetkisi"},
        {"name": "Mülakat Sil", "code": "interviews:delete", "category": "Mülakat Yönetimi", "description": "Mülakat silme yetkisi"},
        
        # Raporlar
        {"name": "Raporları Görüntüle", "code": "reports:read", "category": "Raporlar", "description": "Raporları görüntüleme yetkisi"},
        
        # Dashboard
        {"name": "Dashboard Görüntüle", "code": "dashboard:read", "category": "Dashboard", "description": "Dashboard'u görüntüleme yetkisi"},
        
        # Rol Yönetimi
        {"name": "Rolleri Görüntüle", "code": "roles:read", "category": "Rol Yönetimi", "description": "Rol listesini görüntüleme yetkisi"},
        {"name": "Rol Oluştur", "code": "roles:create", "category": "Rol Yönetimi", "description": "Yeni rol oluşturma yetkisi"},
        {"name": "Rol Düzenle", "code": "roles:update", "category": "Rol Yönetimi", "description": "Rol bilgilerini düzenleme yetkisi"},
        {"name": "Rol Sil", "code": "roles:delete", "category": "Rol Yönetimi", "description": "Rol silme yetkisi"},
    ]
    
    for perm_data in permissions:
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
    
    db.commit()
    print("Permissions inserted successfully!")

def insert_roles():
    """Insert default roles"""
    db = next(get_db())
    
    # Admin rolü - tüm yetkiler
    admin_role = Role(
        name="Yönetici",
        code="admin",
        description="Sistem yöneticisi - tüm yetkilere sahip",
        is_active=True
    )
    db.add(admin_role)
    db.flush()  # Get the role ID
    
    # Admin rolüne tüm yetkileri ekle
    all_permissions = db.query(Permission).all()
    for permission in all_permissions:
        role_permission = RolePermission(
            role_id=admin_role.id,
            permission_id=permission.id
        )
        db.add(role_permission)
    
    # HR Uzmanı rolü - sınırlı yetkiler
    hr_role = Role(
        name="İK Uzmanı",
        code="hr_specialist",
        description="İnsan kaynakları uzmanı - aday ve mülakat yönetimi",
        is_active=True
    )
    db.add(hr_role)
    db.flush()
    
    # HR rolüne sınırlı yetkileri ekle
    hr_permissions = db.query(Permission).filter(
        Permission.code.in_([
            "candidates:read", "candidates:create", "candidates:update", "candidates:delete",
            "interviews:read", "interviews:create", "interviews:update", "interviews:delete",
            "dashboard:read", "reports:read"
        ])
    ).all()
    
    for permission in hr_permissions:
        role_permission = RolePermission(
            role_id=hr_role.id,
            permission_id=permission.id
        )
        db.add(role_permission)
    
    # Görüntüleyici rolü - sadece okuma yetkileri
    viewer_role = Role(
        name="Görüntüleyici",
        code="viewer",
        description="Sadece görüntüleme yetkisi olan kullanıcı",
        is_active=True
    )
    db.add(viewer_role)
    db.flush()
    
    # Viewer rolüne sadece okuma yetkileri ekle
    viewer_permissions = db.query(Permission).filter(
        Permission.code.in_([
            "candidates:read", "interviews:read", "dashboard:read", "reports:read"
        ])
    ).all()
    
    for permission in viewer_permissions:
        role_permission = RolePermission(
            role_id=viewer_role.id,
            permission_id=permission.id
        )
        db.add(role_permission)
    
    db.commit()
    print("Roles inserted successfully!")

if __name__ == "__main__":
    insert_permissions()
    insert_roles()
    print("Role management data inserted successfully!")
