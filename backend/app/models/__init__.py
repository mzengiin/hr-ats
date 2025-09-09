"""
Import all models to ensure they are registered with SQLAlchemy
"""
from .user import User
from .user_role import UserRole
from .refresh_token import RefreshToken
from .audit_log import AuditLog
from .cv_file import CVFile
from .candidate import Candidate
from .position import Position
from .application_channel import ApplicationChannel
from .candidate_status import CandidateStatus
