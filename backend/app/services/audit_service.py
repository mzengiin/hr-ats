"""
Audit service for logging security events
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import json

from app.models.audit_log import AuditLog
from app.models.user import User


class AuditService:
    """Service for audit logging operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_event(
        self,
        user_id: Optional[uuid.UUID],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an audit event
        
        Args:
            user_id: ID of user performing the action
            action: Action performed (e.g., LOGIN, LOGOUT, CREATE_USER)
            resource_type: Type of resource affected (e.g., USER, CANDIDATE)
            resource_id: ID of resource affected
            details: Additional details about the event
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            AuditLog: The created audit log entry
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def log_authentication_event(
        self,
        user_id: Optional[uuid.UUID],
        action: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Log authentication-related events
        
        Args:
            user_id: ID of user (None for failed attempts)
            action: Authentication action (LOGIN, LOGOUT, REFRESH_TOKEN, etc.)
            success: Whether the action was successful
            ip_address: IP address of the request
            user_agent: User agent of the request
            details: Additional details
            
        Returns:
            AuditLog: The created audit log entry
        """
        event_details = {
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {})
        }
        
        return self.log_event(
            user_id=user_id,
            action=action,
            resource_type="AUTHENTICATION",
            resource_id=str(user_id) if user_id else None,
            details=event_details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_user_management_event(
        self,
        actor_user_id: uuid.UUID,
        action: str,
        target_user_id: uuid.UUID,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log user management events
        
        Args:
            actor_user_id: ID of user performing the action
            action: Action performed (CREATE_USER, UPDATE_USER, DELETE_USER, etc.)
            target_user_id: ID of user being affected
            details: Additional details
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            AuditLog: The created audit log entry
        """
        event_details = {
            "target_user_id": str(target_user_id),
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {})
        }
        
        return self.log_event(
            user_id=actor_user_id,
            action=action,
            resource_type="USER",
            resource_id=str(target_user_id),
            details=event_details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_permission_event(
        self,
        user_id: uuid.UUID,
        action: str,
        resource_type: str,
        resource_id: str,
        permission: str,
        granted: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log permission-related events
        
        Args:
            user_id: ID of user
            action: Action attempted (ACCESS_DENIED, PERMISSION_GRANTED, etc.)
            resource_type: Type of resource
            resource_id: ID of resource
            permission: Permission required
            granted: Whether permission was granted
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            AuditLog: The created audit log entry
        """
        event_details = {
            "permission": permission,
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self.log_event(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=event_details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_security_event(
        self,
        user_id: Optional[uuid.UUID],
        action: str,
        severity: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log security-related events
        
        Args:
            user_id: ID of user (None for system events)
            action: Security action (RATE_LIMIT_EXCEEDED, SUSPICIOUS_ACTIVITY, etc.)
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            details: Additional details
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            AuditLog: The created audit log entry
        """
        event_details = {
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            **(details or {})
        }
        
        return self.log_event(
            user_id=user_id,
            action=action,
            resource_type="SECURITY",
            resource_id=str(user_id) if user_id else "SYSTEM",
            details=event_details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def get_audit_logs(
        self,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get audit logs with filtering
        
        Args:
            user_id: Filter by user ID
            action: Filter by action
            resource_type: Filter by resource type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Dict containing audit logs and pagination info
        """
        query = self.db.query(AuditLog)
        
        # Apply filters
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "logs": logs,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_user_audit_logs(
        self,
        user_id: uuid.UUID,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        Get audit logs for a specific user
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            List of audit logs
        """
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    def get_security_events(
        self,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Get security-related audit logs
        
        Args:
            severity: Filter by severity level
            limit: Maximum number of results
            
        Returns:
            List of security audit logs
        """
        query = self.db.query(AuditLog).filter(
            AuditLog.resource_type == "SECURITY"
        )
        
        if severity:
            query = query.filter(
                AuditLog.details["severity"].astext == severity
            )
        
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    def cleanup_old_logs(self, days: int = 90) -> int:
        """
        Cleanup old audit logs
        
        Args:
            days: Number of days to keep logs
            
        Returns:
            int: Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_logs = self.db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).all()
        
        count = len(old_logs)
        
        for log in old_logs:
            self.db.delete(log)
        
        self.db.commit()
        
        return count
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """
        Get audit statistics
        
        Returns:
            Dict containing audit statistics
        """
        from sqlalchemy import func
        
        # Total logs
        total_logs = self.db.query(AuditLog).count()
        
        # Logs by action
        action_stats = self.db.query(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action).all()
        
        # Logs by resource type
        resource_stats = self.db.query(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.resource_type).all()
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_logs = self.db.query(AuditLog).filter(
            AuditLog.created_at >= recent_cutoff
        ).count()
        
        return {
            "total_logs": total_logs,
            "recent_logs_24h": recent_logs,
            "logs_by_action": {action: count for action, count in action_stats},
            "logs_by_resource": {resource: count for resource, count in resource_stats}
        }








