"""
User service for business logic
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid

from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.user import UserCreate, UserUpdate, UserFilter
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate, created_by: Optional[uuid.UUID] = None) -> User:
        """
        Create a new user
        
        Args:
            user_data: User creation data
            created_by: ID of user creating this user
            
        Returns:
            User: The created user
            
        Raises:
            ValueError: If email already exists or role not found
        """
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Verify role exists
        role = self.db.query(UserRole).filter(UserRole.id == user_data.role_id).first()
        if not role:
            raise ValueError("Role not found")
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role_id=user_data.role_id,
            created_by=created_by,
            updated_by=created_by
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User: The user if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User: The user if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[UserFilter] = None
    ) -> Dict[str, Any]:
        """
        List users with pagination and filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply
            
        Returns:
            Dict containing users, total count, and pagination info
        """
        query = self.db.query(User)
        
        # Apply filters
        if filters:
            if filters.role_id:
                query = query.filter(User.role_id == filters.role_id)
            
            if filters.is_active is not None:
                query = query.filter(User.is_active == filters.is_active)
            
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            
            if filters.created_after:
                query = query.filter(User.created_at >= filters.created_after)
            
            if filters.created_before:
                query = query.filter(User.created_at <= filters.created_before)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit
        page = (skip // limit) + 1
        
        return {
            "users": users,
            "total": total,
            "page": page,
            "pages": pages,
            "limit": limit
        }
    
    def update_user(
        self,
        user_id: uuid.UUID,
        user_data: UserUpdate,
        updated_by: Optional[uuid.UUID] = None
    ) -> Optional[User]:
        """
        Update user
        
        Args:
            user_id: User ID to update
            user_data: Update data
            updated_by: ID of user making the update
            
        Returns:
            User: The updated user if found, None otherwise
            
        Raises:
            ValueError: If user not found or role not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if role exists (if being updated)
        if user_data.role_id and user_data.role_id != user.role_id:
            role = self.db.query(UserRole).filter(UserRole.id == user_data.role_id).first()
            if not role:
                raise ValueError("Role not found")
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_by = updated_by
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def deactivate_user(self, user_id: uuid.UUID, deactivated_by: Optional[uuid.UUID] = None) -> Optional[User]:
        """
        Deactivate user
        
        Args:
            user_id: User ID to deactivate
            deactivated_by: ID of user deactivating
            
        Returns:
            User: The deactivated user if found, None otherwise
            
        Raises:
            ValueError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.is_active = False
        user.updated_by = deactivated_by
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def activate_user(self, user_id: uuid.UUID, activated_by: Optional[uuid.UUID] = None) -> Optional[User]:
        """
        Activate user
        
        Args:
            user_id: User ID to activate
            activated_by: ID of user activating
            
        Returns:
            User: The activated user if found, None otherwise
            
        Raises:
            ValueError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.is_active = True
        user.updated_by = activated_by
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
        changed_by: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            changed_by: ID of user changing password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            ValueError: If user not found or current password incorrect
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        user.updated_by = changed_by
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics
        
        Returns:
            Dict containing user statistics
        """
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        inactive_users = total_users - active_users
        
        # Users by role
        role_stats = self.db.query(
            UserRole.name,
            func.count(User.id).label('count')
        ).join(User).group_by(UserRole.name).all()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "users_by_role": {role.name: role.count for role in role_stats}
        }
    
    def search_users(self, search_term: str, limit: int = 10) -> List[User]:
        """
        Search users by name or email
        
        Args:
            search_term: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching users
        """
        search_pattern = f"%{search_term}%"
        
        return self.db.query(User).filter(
            or_(
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        ).limit(limit).all()
    
    def get_users_by_role(self, role_id: uuid.UUID) -> List[User]:
        """
        Get all users with a specific role
        
        Args:
            role_id: Role ID
            
        Returns:
            List of users with the role
        """
        return self.db.query(User).filter(
            User.role_id == role_id,
            User.is_active == True
        ).all()
    
    def delete_user(self, user_id: uuid.UUID, deleted_by: Optional[uuid.UUID] = None) -> bool:
        """
        Delete user (soft delete by deactivating)
        
        Args:
            user_id: User ID to delete
            deleted_by: ID of user deleting
            
        Returns:
            bool: True if user deleted successfully
            
        Raises:
            ValueError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Soft delete by deactivating
        user.is_active = False
        user.updated_by = deleted_by
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True



