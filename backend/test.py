# # =========================================
# # IMPORTS
# # =========================================

# from fastapi import FastAPI
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
# from dotenv import load_dotenv
# import os


# # =========================================
# # PYDANTIC SCHEMA IMPORTS
# # =========================================

# from pydantic import BaseModel, EmailStr, Field
# from typing import Optional
# from uuid import UUID
# from datetime import datetime, date


# # =========================================
# # SQLALCHEMY MODEL IMPORTS
# # =========================================

# from sqlalchemy import (
#     Column,
#     String,
#     Text,
#     Boolean,
#     Date,
#     DateTime,
#     ForeignKey,
#     CheckConstraint
# )

# from sqlalchemy.dialects.postgresql import UUID as PG_UUID
# from sqlalchemy.orm import relationship

# import uuid

# # =========================================
# # AUTHENTICATION IMPORTS
# # =========================================

# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer

# from jose import jwt, JWTError
# from passlib.context import CryptContext

# from sqlalchemy.orm import Session

# from datetime import timedelta


# # =========================================
# # COMMENTS APIs
# # =========================================

# from fastapi import UploadFile, File
# from typing import List
# import shutil
# #import os



# # =========================================
# # PROJECT MANAGEMENT APIs
# # =========================================


# #from typing import List

# # dashboard apis

# from sqlalchemy import func
# #from typing import List


# from fastapi.middleware.cors import CORSMiddleware


# # =========================================
# # DOTENV CONFIGURATION
# # =========================================

# # Load environment variables from .env file


# load_dotenv(dotenv_path=".env")

# DATABASE_URL = os.getenv("DATABASE_URL")

# #print("DATABASE URL:", DATABASE_URL)

# # =========================================
# # DATABASE CONNECTION
# # =========================================

# # Create PostgreSQL engine
# engine = create_engine(DATABASE_URL)

# # Create database session
# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )


# # =========================================
# # SQLALCHEMY SETUP
# # =========================================

# # Base class for all database models
# Base = declarative_base()


# # =========================================
# # FASTAPI INITIALIZATION
# # =========================================

# app = FastAPI(
#     title="Team Task Manager API",
#     description="Production-style SaaS Team Collaboration Platform",
#     version="1.0.0"
# )

# # =========================================
# # CORS MIDDLEWARE
# # =========================================

# app.add_middleware(

#     CORSMiddleware,

#     allow_origins=[
#         "http://localhost:5173"
#     ],

#     allow_credentials=True,

#     allow_methods=["*"],

#     allow_headers=["*"]

# )






# # =========================================
# # 1. USER MODEL
# # =========================================

# class User(Base):
#     __tablename__ = "users"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     name = Column(String(100), nullable=False)

#     email = Column(String(150), unique=True, nullable=False)

#     hashed_password = Column(Text, nullable=False)

#     role = Column(
#         String(20),
#         nullable=False,
#         default="member"
#     )

#     is_active = Column(Boolean, default=True)

#     avatar_url = Column(Text)

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     updated_at = Column(
#         DateTime,
#         default=datetime.utcnow,
#         onupdate=datetime.utcnow
#     )

#     # Relationships
#     sessions = relationship(
#         "UserSession",
#         back_populates="user",
#         cascade="all, delete"
#     )

#     owned_projects = relationship(
#         "Project",
#         back_populates="owner",
#         cascade="all, delete"
#     )

#     project_memberships = relationship(
#         "ProjectMember",
#         back_populates="user",
#         cascade="all, delete"
#     )

#     assigned_tasks = relationship(
#         "Task",
#         foreign_keys="Task.assignee_id",
#         back_populates="assignee"
#     )

#     created_tasks = relationship(
#         "Task",
#         foreign_keys="Task.created_by",
#         back_populates="creator"
#     )

#     comments = relationship(
#         "TaskComment",
#         back_populates="user",
#         cascade="all, delete"
#     )

#     attachments = relationship(
#         "TaskAttachment",
#         back_populates="uploader",
#         cascade="all, delete"
#     )

#     activities = relationship(
#         "ActivityLog",
#         back_populates="user"
#     )

#     notifications = relationship(
#         "Notification",
#         back_populates="user",
#         cascade="all, delete"
#     )

#     __table_args__ = (
#         CheckConstraint(
#             "role IN ('admin', 'member')",
#             name="check_user_role"
#         ),
#     )


# # =========================================
# # 2. USER SESSION MODEL
# # =========================================

# class UserSession(Base):
#     __tablename__ = "user_sessions"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     user_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     refresh_token = Column(
#         Text,
#         unique=True,
#         nullable=False
#     )

#     expires_at = Column(
#         DateTime,
#         nullable=False
#     )

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     # Relationships
#     user = relationship(
#         "User",
#         back_populates="sessions"
#     )


# # =========================================
# # 3. PROJECT MODEL
# # =========================================

# class Project(Base):
#     __tablename__ = "projects"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     name = Column(
#         String(200),
#         nullable=False
#     )

#     description = Column(Text)

#     status = Column(
#         String(20),
#         nullable=False,
#         default="active"
#     )

#     owner_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     deadline = Column(Date)

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     updated_at = Column(
#         DateTime,
#         default=datetime.utcnow,
#         onupdate=datetime.utcnow
#     )

#     # Relationships
#     owner = relationship(
#         "User",
#         back_populates="owned_projects"
#     )

#     members = relationship(
#         "ProjectMember",
#         back_populates="project",
#         cascade="all, delete"
#     )

#     tasks = relationship(
#         "Task",
#         back_populates="project",
#         cascade="all, delete"
#     )

#     activities = relationship(
#         "ActivityLog",
#         back_populates="project",
#         cascade="all, delete"
#     )

#     __table_args__ = (
#         CheckConstraint(
#             "status IN ('active', 'archived', 'completed')",
#             name="check_project_status"
#         ),
#     )


# # =========================================
# # 4. PROJECT MEMBER MODEL
# # =========================================

# class ProjectMember(Base):
#     __tablename__ = "project_members"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     project_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("projects.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     user_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     role = Column(
#         String(20),
#         nullable=False,
#         default="member"
#     )

#     joined_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     # Relationships
#     project = relationship(
#         "Project",
#         back_populates="members"
#     )

#     user = relationship(
#         "User",
#         back_populates="project_memberships"
#     )

#     __table_args__ = (
#         CheckConstraint(
#             "role IN ('admin', 'member')",
#             name="check_project_member_role"
#         ),
#     )


# # =========================================
# # 5. TASK MODEL
# # =========================================

# class Task(Base):
#     __tablename__ = "tasks"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     title = Column(
#         String(200),
#         nullable=False
#     )

#     description = Column(Text)

#     status = Column(
#         String(20),
#         nullable=False,
#         default="todo"
#     )

#     priority = Column(
#         String(20),
#         nullable=False,
#         default="medium"
#     )

#     due_date = Column(Date)

#     completed_at = Column(DateTime)

#     project_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("projects.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     assignee_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL")
#     )

#     created_by = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id"),
#         nullable=False
#     )

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     updated_at = Column(
#         DateTime,
#         default=datetime.utcnow,
#         onupdate=datetime.utcnow
#     )

#     # Relationships
#     project = relationship(
#         "Project",
#         back_populates="tasks"
#     )

#     assignee = relationship(
#         "User",
#         foreign_keys=[assignee_id],
#         back_populates="assigned_tasks"
#     )

#     creator = relationship(
#         "User",
#         foreign_keys=[created_by],
#         back_populates="created_tasks"
#     )

#     comments = relationship(
#         "TaskComment",
#         back_populates="task",
#         cascade="all, delete"
#     )

#     attachments = relationship(
#         "TaskAttachment",
#         back_populates="task",
#         cascade="all, delete"
#     )

#     activities = relationship(
#         "ActivityLog",
#         back_populates="task",
#         cascade="all, delete"
#     )

#     __table_args__ = (
#         CheckConstraint(
#             "status IN ('todo', 'in_progress', 'done')",
#             name="check_task_status"
#         ),
#         CheckConstraint(
#             "priority IN ('low', 'medium', 'high')",
#             name="check_task_priority"
#         ),
#     )


# # =========================================
# # 6. TASK COMMENT MODEL
# # =========================================

# class TaskComment(Base):
#     __tablename__ = "task_comments"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     task_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("tasks.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     user_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     comment = Column(
#         Text,
#         nullable=False
#     )

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     # Relationships
#     task = relationship(
#         "Task",
#         back_populates="comments"
#     )

#     user = relationship(
#         "User",
#         back_populates="comments"
#     )


# # =========================================
# # 7. TASK ATTACHMENT MODEL
# # =========================================

# class TaskAttachment(Base):
#     __tablename__ = "task_attachments"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     task_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("tasks.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     uploaded_by = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     file_name = Column(
#         String(255),
#         nullable=False
#     )

#     file_url = Column(
#         Text,
#         nullable=False
#     )

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     # Relationships
#     task = relationship(
#         "Task",
#         back_populates="attachments"
#     )

#     uploader = relationship(
#         "User",
#         back_populates="attachments"
#     )


# # =========================================
# # 8. ACTIVITY LOG MODEL
# # =========================================

# class ActivityLog(Base):
#     __tablename__ = "activity_logs"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     user_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL")
#     )

#     project_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("projects.id", ondelete="CASCADE")
#     )

#     task_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("tasks.id", ondelete="CASCADE")
#     )

#     action = Column(
#         String(255),
#         nullable=False
#     )

#     old_value = Column(Text)

#     new_value = Column(Text)

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     # Relationships
#     user = relationship(
#         "User",
#         back_populates="activities"
#     )

#     project = relationship(
#         "Project",
#         back_populates="activities"
#     )

#     task = relationship(
#         "Task",
#         back_populates="activities"
#     )


# # =========================================
# # 9. NOTIFICATION MODEL
# # =========================================

# class Notification(Base):
#     __tablename__ = "notifications"

#     id = Column(
#         PG_UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4
#     )

#     user_id = Column(
#         PG_UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False
#     )

#     type = Column(
#         String(50),
#         nullable=False
#     )

#     message = Column(
#         Text,
#         nullable=False
#     )

#     link = Column(Text)

#     is_read = Column(
#         Boolean,
#         default=False
#     )

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     # Relationships
#     user = relationship(
#         "User",
#         back_populates="notifications"
#     )

#     __table_args__ = (
#         CheckConstraint(
#             """
#             type IN (
#                 'task_assigned',
#                 'task_updated',
#                 'comment_added',
#                 'project_invite',
#                 'due_soon',
#                 'overdue'
#             )
#             """,
#             name="check_notification_type"
#         ),
#     )






# # =========================================
# # AUTH SCHEMAS
# # =========================================

# # -----------------------------------------
# # USER REGISTER / SIGNUP
# # -----------------------------------------

# class UserCreateSchema(BaseModel):

#     name: str

#     email: EmailStr

#     password: str

#     role: str = "member"

#     avatar_url: Optional[str] = None


# # -----------------------------------------
# # USER LOGIN
# # -----------------------------------------

# class UserLoginSchema(BaseModel):
#     email: EmailStr

#     password: str


# # -----------------------------------------
# # ACCESS TOKEN RESPONSE
# # -----------------------------------------

# class TokenSchema(BaseModel):
#     access_token: str

#     refresh_token: str

#     token_type: str = "bearer"


# # -----------------------------------------
# # REFRESH TOKEN REQUEST
# # -----------------------------------------

# class RefreshTokenSchema(BaseModel):
#     refresh_token: str


# # =========================================
# # USER SCHEMAS
# # =========================================

# # -----------------------------------------
# # USER RESPONSE
# # -----------------------------------------

# class UserResponseSchema(BaseModel):
#     id: UUID

#     name: str

#     email: EmailStr

#     role: str

#     is_active: bool

#     avatar_url: Optional[str]

#     created_at: datetime

#     updated_at: datetime

#     class Config:
#         from_attributes = True


# # -----------------------------------------
# # USER UPDATE
# # -----------------------------------------

# class UserUpdateSchema(BaseModel):
#     name: Optional[str] = None

#     avatar_url: Optional[str] = None

#     is_active: Optional[bool] = None


# # =========================================
# # USER SESSION SCHEMAS
# # =========================================

# class UserSessionSchema(BaseModel):
#     id: UUID

#     user_id: UUID

#     refresh_token: str

#     expires_at: datetime

#     created_at: datetime

#     class Config:
#         from_attributes = True


# # =========================================
# # PROJECT SCHEMAS
# # =========================================

# # -----------------------------------------
# # PROJECT CREATE
# # -----------------------------------------

# class ProjectCreateSchema(BaseModel):
#     name: str = Field(..., min_length=3, max_length=200)

#     description: Optional[str] = None

#     status: Optional[str] = "active"

#     deadline: Optional[date] = None


# # -----------------------------------------
# # PROJECT UPDATE
# # -----------------------------------------

# class ProjectUpdateSchema(BaseModel):
#     name: Optional[str] = None

#     description: Optional[str] = None

#     status: Optional[str] = None

#     deadline: Optional[date] = None


# # -----------------------------------------
# # PROJECT RESPONSE
# # -----------------------------------------

# class ProjectResponseSchema(BaseModel):
#     id: UUID

#     name: str

#     description: Optional[str]

#     status: str

#     owner_id: UUID

#     deadline: Optional[date]

#     created_at: datetime

#     updated_at: datetime

#     class Config:
#         from_attributes = True


# # =========================================
# # PROJECT MEMBER SCHEMAS
# # =========================================

# # -----------------------------------------
# # ADD PROJECT MEMBER
# # -----------------------------------------

# class ProjectMemberCreateSchema(BaseModel):
#     project_id: UUID

#     user_id: UUID

#     role: Optional[str] = "member"


# # -----------------------------------------
# # PROJECT MEMBER RESPONSE
# # -----------------------------------------

# class ProjectMemberResponseSchema(BaseModel):
#     id: UUID

#     project_id: UUID

#     user_id: UUID

#     role: str

#     joined_at: datetime

#     class Config:
#         from_attributes = True


# # =========================================
# # TASK SCHEMAS
# # =========================================

# # -----------------------------------------
# # TASK CREATE
# # -----------------------------------------

# class TaskCreateSchema(BaseModel):
#     title: str = Field(..., min_length=3, max_length=200)

#     description: Optional[str] = None

#     status: Optional[str] = "todo"

#     priority: Optional[str] = "medium"

#     due_date: Optional[date] = None

#     project_id: UUID

#     assignee_id: Optional[UUID] = None


# # -----------------------------------------
# # TASK UPDATE
# # -----------------------------------------

# class TaskUpdateSchema(BaseModel):
#     title: Optional[str] = None

#     description: Optional[str] = None

#     status: Optional[str] = None

#     priority: Optional[str] = None

#     due_date: Optional[date] = None

#     assignee_id: Optional[UUID] = None

#     completed_at: Optional[datetime] = None


# # -----------------------------------------
# # TASK RESPONSE
# # -----------------------------------------

# class TaskResponseSchema(BaseModel):
#     id: UUID

#     title: str

#     description: Optional[str]

#     status: str

#     priority: str

#     due_date: Optional[date]

#     completed_at: Optional[datetime]

#     project_id: UUID

#     assignee_id: Optional[UUID]

#     created_by: UUID

#     created_at: datetime

#     updated_at: datetime

#     class Config:
#         from_attributes = True


# # =========================================
# # TASK COMMENT SCHEMAS
# # =========================================

# # -----------------------------------------
# # CREATE COMMENT
# # -----------------------------------------

# class CommentCreateSchema(BaseModel):
#     task_id: UUID

#     comment: str = Field(..., min_length=1)


# # -----------------------------------------
# # COMMENT RESPONSE
# # -----------------------------------------

# class CommentResponseSchema(BaseModel):
#     id: UUID

#     task_id: UUID

#     user_id: UUID

#     comment: str

#     created_at: datetime

#     class Config:
#         from_attributes = True


# # =========================================
# # TASK ATTACHMENT SCHEMAS
# # =========================================

# # -----------------------------------------
# # ATTACHMENT RESPONSE
# # -----------------------------------------

# class AttachmentResponseSchema(BaseModel):
#     id: UUID

#     task_id: UUID

#     uploaded_by: UUID

#     file_name: str

#     file_url: str

#     created_at: datetime

#     class Config:
#         from_attributes = True


# # =========================================
# # ACTIVITY LOG SCHEMAS
# # =========================================

# # -----------------------------------------
# # ACTIVITY RESPONSE
# # -----------------------------------------

# class ActivityLogResponseSchema(BaseModel):
#     id: UUID

#     user_id: Optional[UUID]

#     project_id: Optional[UUID]

#     task_id: Optional[UUID]

#     action: str

#     old_value: Optional[str]

#     new_value: Optional[str]

#     created_at: datetime

#     class Config:
#         from_attributes = True


# # =========================================
# # NOTIFICATION SCHEMAS
# # =========================================

# # -----------------------------------------
# # NOTIFICATION RESPONSE
# # -----------------------------------------

# class NotificationResponseSchema(BaseModel):
#     id: UUID

#     user_id: UUID

#     type: str

#     message: str

#     link: Optional[str]

#     is_read: bool

#     created_at: datetime

#     class Config:
#         from_attributes = True


# # -----------------------------------------
# # NOTIFICATION UPDATE
# # -----------------------------------------

# class NotificationUpdateSchema(BaseModel):
#     is_read: bool





# # =========================================
# # JWT CONFIGURATION
# # =========================================

# SECRET_KEY = os.getenv("SECRET_KEY")

# ALGORITHM = os.getenv("ALGORITHM")

# ACCESS_TOKEN_EXPIRE_MINUTES = int(
#     os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
# )

# REFRESH_TOKEN_EXPIRE_DAYS = 7


# # =========================================
# # PASSWORD HASHING (bcrypt)
# # =========================================

# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto"
# )


# # -----------------------------------------
# # HASH PASSWORD
# # -----------------------------------------

# def hash_password(password: str):
#     return pwd_context.hash(password)


# # -----------------------------------------
# # VERIFY PASSWORD
# # -----------------------------------------

# def verify_password(
#     plain_password: str,
#     hashed_password: str
# ):
#     return pwd_context.verify(
#         plain_password,
#         hashed_password
#     )


# # =========================================
# # OAUTH2 SCHEME
# # =========================================

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/login"
# )


# # =========================================
# # DATABASE DEPENDENCY
# # =========================================

# def get_db():

#     db = SessionLocal()

#     try:
#         yield db

#     finally:
#         db.close()


# # =========================================
# # JWT TOKEN FUNCTIONS
# # =========================================

# # -----------------------------------------
# # CREATE ACCESS TOKEN
# # -----------------------------------------

# def create_access_token(data: dict):

#     to_encode = data.copy()

#     expire = datetime.utcnow() + timedelta(
#         minutes=ACCESS_TOKEN_EXPIRE_MINUTES
#     )

#     to_encode.update({
#         "exp": expire
#     })

#     encoded_jwt = jwt.encode(
#         to_encode,
#         SECRET_KEY,
#         algorithm=ALGORITHM
#     )

#     return encoded_jwt


# # -----------------------------------------
# # CREATE REFRESH TOKEN
# # -----------------------------------------

# def create_refresh_token(data: dict):

#     to_encode = data.copy()

#     expire = datetime.utcnow() + timedelta(
#         days=REFRESH_TOKEN_EXPIRE_DAYS
#     )

#     to_encode.update({
#         "exp": expire
#     })

#     refresh_token = jwt.encode(
#         to_encode,
#         SECRET_KEY,
#         algorithm=ALGORITHM
#     )

#     return refresh_token


# # =========================================
# # GET CURRENT USER
# # =========================================

# def get_current_user(

#     token: str = Depends(oauth2_scheme),

#     db: Session = Depends(get_db)

# ):

#     credentials_exception = HTTPException(

#         status_code=status.HTTP_401_UNAUTHORIZED,

#         detail="Invalid authentication credentials",

#         headers={"WWW-Authenticate": "Bearer"}

#     )

#     try:

#         payload = jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM]
#         )

#         user_id: str = payload.get("sub")

#         if user_id is None:
#             raise credentials_exception

#     except JWTError:
#         raise credentials_exception

#     user = db.query(User).filter(
#         User.id == user_id
#     ).first()

#     if user is None:
#         raise credentials_exception

#     return user


# # =========================================
# # REQUIRE ADMIN (RBAC)
# # =========================================

# def require_admin(

#     current_user: User = Depends(get_current_user)

# ):

#     if current_user.role != "admin":

#         raise HTTPException(
#             status_code=403,
#             detail="Admin access required"
#         )

#     return current_user




# # =========================================
# # CREATE PROJECT
# # =========================================

# @app.post(
#     "/projects",
#     response_model=ProjectResponseSchema
# )

# def create_project(

#     project_data: ProjectCreateSchema,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Create project
#     new_project = Project(

#         name=project_data.name,

#         description=project_data.description,

#         status=project_data.status,

#         deadline=project_data.deadline,

#         owner_id=current_user.id

#     )

#     db.add(new_project)

#     db.commit()

#     db.refresh(new_project)

#     # Automatically add owner as admin member
#     owner_member = ProjectMember(

#         project_id=new_project.id,

#         user_id=current_user.id,

#         role="admin"

#     )

#     db.add(owner_member)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=new_project.id,

#         action=f"Created project '{new_project.name}'"

#     )

#     db.add(activity)

#     db.commit()

#     return new_project


# # =========================================
# # GET ALL PROJECTS
# # =========================================

# @app.get(
#     "/projects",
#     response_model=List[ProjectResponseSchema]
# )

# def get_projects(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Projects user owns
#     owned_projects = db.query(Project).filter(
#         Project.owner_id == current_user.id
#     )

#     # Projects user is member of
#     member_projects = db.query(Project).join(
#         ProjectMember
#     ).filter(
#         ProjectMember.user_id == current_user.id
#     )

#     # Combine and remove duplicates
#     projects = owned_projects.union(member_projects).all()

#     return projects


# # =========================================
# # GET SINGLE PROJECT
# # =========================================

# @app.get(
#     "/projects/{project_id}",
#     response_model=ProjectResponseSchema
# )

# def get_project(

#     project_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     project = db.query(Project).filter(
#         Project.id == project_id
#     ).first()

#     if not project:

#         raise HTTPException(
#             status_code=404,
#             detail="Project not found"
#         )

#     # Check membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     return project


# # =========================================
# # UPDATE PROJECT
# # =========================================

# @app.put(
#     "/projects/{project_id}",
#     response_model=ProjectResponseSchema
# )

# def update_project(

#     project_id: UUID,

#     project_data: ProjectUpdateSchema,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     project = db.query(Project).filter(
#         Project.id == project_id
#     ).first()

#     if not project:

#         raise HTTPException(
#             status_code=404,
#             detail="Project not found"
#         )

#     # Check admin/owner access
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id,
#         ProjectMember.user_id == current_user.id,
#         ProjectMember.role == "admin"
#     ).first()

#     if (
#         current_user.id != project.owner_id
#         and not membership
#     ):

#         raise HTTPException(
#             status_code=403,
#             detail="Admin access required"
#         )

#     # Update fields
#     if project_data.name is not None:
#         project.name = project_data.name

#     if project_data.description is not None:
#         project.description = project_data.description

#     if project_data.status is not None:
#         project.status = project_data.status

#     if project_data.deadline is not None:
#         project.deadline = project_data.deadline

#     project.updated_at = datetime.utcnow()

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=project.id,

#         action=f"Updated project '{project.name}'"

#     )

#     db.add(activity)

#     db.commit()

#     db.refresh(project)

#     return project


# # =========================================
# # DELETE PROJECT
# # =========================================

# @app.delete("/projects/{project_id}")

# def delete_project(

#     project_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     project = db.query(Project).filter(
#         Project.id == project_id
#     ).first()

#     if not project:

#         raise HTTPException(
#             status_code=404,
#             detail="Project not found"
#         )

#     # Only owner can delete
#     if current_user.id != project.owner_id:

#         raise HTTPException(
#             status_code=403,
#             detail="Only project owner can delete"
#         )

#     db.delete(project)

#     db.commit()

#     return {
#         "message": "Project deleted successfully"
#     }


# # =========================================
# # ADD PROJECT MEMBER
# # =========================================

# @app.post(
#     "/projects/{project_id}/members",
#     response_model=ProjectMemberResponseSchema
# )

# def add_project_member(

#     project_id: UUID,

#     member_data: ProjectMemberCreateSchema,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     project = db.query(Project).filter(
#         Project.id == project_id
#     ).first()

#     if not project:

#         raise HTTPException(
#             status_code=404,
#             detail="Project not found"
#         )

#     # Only admin/owner can add members
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id,
#         ProjectMember.user_id == current_user.id,
#         ProjectMember.role == "admin"
#     ).first()

#     if (
#         current_user.id != project.owner_id
#         and not membership
#     ):

#         raise HTTPException(
#             status_code=403,
#             detail="Admin access required"
#         )

#     # Check if user exists
#     user = db.query(User).filter(
#         User.id == member_data.user_id
#     ).first()

#     if not user:

#         raise HTTPException(
#             status_code=404,
#             detail="User not found"
#         )

#     # Prevent duplicate membership
#     existing_member = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id,
#         ProjectMember.user_id == member_data.user_id
#     ).first()

#     if existing_member:

#         raise HTTPException(
#             status_code=400,
#             detail="User already a member"
#         )

#     # Add member
#     new_member = ProjectMember(

#         project_id=project_id,

#         user_id=member_data.user_id,

#         role=member_data.role

#     )

#     db.add(new_member)

#     # Notification
#     notification = Notification(

#         user_id=user.id,

#         type="project_invite",

#         message=f"You were added to project '{project.name}'"

#     )

#     db.add(notification)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=project_id,

#         action=f"Added member '{user.name}'"

#     )

#     db.add(activity)

#     db.commit()

#     db.refresh(new_member)

#     return new_member


# # =========================================
# # GET PROJECT MEMBERS
# # =========================================

# @app.get(
#     "/projects/{project_id}/members",
#     response_model=List[ProjectMemberResponseSchema]
# )

# def get_project_members(

#     project_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Verify project exists
#     project = db.query(Project).filter(
#         Project.id == project_id
#     ).first()

#     if not project:

#         raise HTTPException(
#             status_code=404,
#             detail="Project not found"
#         )

#     # Verify membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     members = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id
#     ).all()

#     return members


# # =========================================
# # REMOVE PROJECT MEMBER
# # =========================================

# @app.delete("/projects/{project_id}/members/{user_id}")

# def remove_project_member(

#     project_id: UUID,

#     user_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     project = db.query(Project).filter(
#         Project.id == project_id
#     ).first()

#     if not project:

#         raise HTTPException(
#             status_code=404,
#             detail="Project not found"
#         )

#     # Only admin/owner can remove members
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id,
#         ProjectMember.user_id == current_user.id,
#         ProjectMember.role == "admin"
#     ).first()

#     if (
#         current_user.id != project.owner_id
#         and not membership
#     ):

#         raise HTTPException(
#             status_code=403,
#             detail="Admin access required"
#         )

#     member = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id,
#         ProjectMember.user_id == user_id
#     ).first()

#     if not member:

#         raise HTTPException(
#             status_code=404,
#             detail="Member not found"
#         )

#     db.delete(member)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=project_id,

#         action="Removed member from project"

#     )

#     db.add(activity)

#     db.commit()

#     return {
#         "message": "Member removed successfully"
#     }




# # =========================================
# # SIGNUP API
# # =========================================

# @app.post(
#     "/signup",
#     response_model=UserResponseSchema
# )

# def signup(

#     user_data: UserCreateSchema,

#     db: Session = Depends(get_db)

# ):

#     # Check existing email
#     existing_user = db.query(User).filter(
#         User.email == user_data.email
#     ).first()

#     if existing_user:

#         raise HTTPException(
#             status_code=400,
#             detail="Email already registered"
#         )

#     # Hash password
#     hashed_pw = hash_password(
#         user_data.password
#     )

#     # Create user
#     new_user = User(

#         name=user_data.name,

#         email=user_data.email,

#         hashed_password=hashed_pw,

#         role=user_data.role,

#         avatar_url=user_data.avatar_url

#     )

#     db.add(new_user)

#     db.commit()

#     db.refresh(new_user)

#     return new_user


# # =========================================
# # LOGIN API
# # =========================================

# @app.post(
#     "/login",
#     response_model=TokenSchema
# )

# def login(

#     user_data: UserLoginSchema,

#     db: Session = Depends(get_db)

# ):

#     # Find user
#     user = db.query(User).filter(
#         User.email == user_data.email
#     ).first()

#     if not user:

#         raise HTTPException(
#             status_code=401,
#             detail="Invalid email or password"
#         )

#     # Verify password
#     valid_password = verify_password(
#         user_data.password,
#         user.hashed_password
#     )

#     if not valid_password:

#         raise HTTPException(
#             status_code=401,
#             detail="Invalid email or password"
#         )

#     # Create JWT payload
#     token_data = {
#         "sub": str(user.id),
#         "role": user.role
#     }

#     # Generate tokens
#     access_token = create_access_token(
#         token_data
#     )

#     refresh_token = create_refresh_token(
#         token_data
#     )

#     # Save refresh token session
#     session = UserSession(

#         user_id=user.id,

#         refresh_token=refresh_token,

#         expires_at=datetime.utcnow() + timedelta(
#             days=REFRESH_TOKEN_EXPIRE_DAYS
#         )

#     )

#     db.add(session)

#     db.commit()

#     return {

#         "access_token": access_token,

#         "refresh_token": refresh_token,

#         "token_type": "bearer"

#     }


# # =========================================
# # CURRENT USER PROFILE API
# # =========================================

# @app.get("/me")

# def get_current_user_profile(

#     current_user: User = Depends(get_current_user)

# ):

#     return {

#         "id": str(current_user.id),

#         "name": current_user.name,

#         "email": current_user.email,

#         "role": current_user.role,

#         "avatar_url": current_user.avatar_url,

#         "is_active": current_user.is_active,

#         "created_at": current_user.created_at

#     }



# # =========================================
# # CREATE TASK
# # =========================================

# @app.post(
#     "/tasks",
#     response_model=TaskResponseSchema
# )

# def create_task(

#     task_data: TaskCreateSchema,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Check project exists
#     project = db.query(Project).filter(
#         Project.id == task_data.project_id
#     ).first()

#     if not project:

#         raise HTTPException(
#             status_code=404,
#             detail="Project not found"
#         )

#     # Check membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == task_data.project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     # Validate assignee if provided
#     if task_data.assignee_id:

#         assignee_member = db.query(ProjectMember).filter(
#             ProjectMember.project_id == task_data.project_id,
#             ProjectMember.user_id == task_data.assignee_id
#         ).first()

#         if not assignee_member:

#             raise HTTPException(
#                 status_code=400,
#                 detail="Assignee is not project member"
#             )

#     # Create task
#     new_task = Task(

#         title=task_data.title,

#         description=task_data.description,

#         status=task_data.status,

#         priority=task_data.priority,

#         due_date=task_data.due_date,

#         project_id=task_data.project_id,

#         assignee_id=task_data.assignee_id,

#         created_by=current_user.id

#     )

#     db.add(new_task)

#     db.commit()

#     db.refresh(new_task)

#     # Create notification
#     if task_data.assignee_id:

#         notification = Notification(

#             user_id=task_data.assignee_id,

#             type="task_assigned",

#             message=f"You were assigned task '{new_task.title}'"

#         )

#         db.add(notification)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=task_data.project_id,

#         task_id=new_task.id,

#         action=f"Created task '{new_task.title}'"

#     )

#     db.add(activity)

#     db.commit()

#     return new_task


# # =========================================
# # GET TASKS BY PROJECT
# # =========================================

# @app.get(
#     "/projects/{project_id}/tasks",
#     response_model=List[TaskResponseSchema]
# )

# def get_project_tasks(

#     project_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Check membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     tasks = db.query(Task).filter(
#         Task.project_id == project_id
#     ).all()

#     return tasks


# # =========================================
# # GET SINGLE TASK
# # =========================================

# @app.get(
#     "/tasks/{task_id}",
#     response_model=TaskResponseSchema
# )

# def get_task(

#     task_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     # Check membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == task.project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     return task


# # =========================================
# # UPDATE TASK
# # =========================================

# @app.put(
#     "/tasks/{task_id}",
#     response_model=TaskResponseSchema
# )

# def update_task(

#     task_id: UUID,

#     task_data: TaskUpdateSchema,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     # Check membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == task.project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     # Validate assignee if changed
#     if task_data.assignee_id:

#         assignee_member = db.query(ProjectMember).filter(
#             ProjectMember.project_id == task.project_id,
#             ProjectMember.user_id == task_data.assignee_id
#         ).first()

#         if not assignee_member:

#             raise HTTPException(
#                 status_code=400,
#                 detail="Assignee is not project member"
#             )

#     # Update fields
#     if task_data.title is not None:
#         task.title = task_data.title

#     if task_data.description is not None:
#         task.description = task_data.description

#     if task_data.status is not None:
#         task.status = task_data.status

#     if task_data.priority is not None:
#         task.priority = task_data.priority

#     if task_data.due_date is not None:
#         task.due_date = task_data.due_date

#     if task_data.assignee_id is not None:
#         task.assignee_id = task_data.assignee_id

#     if task_data.completed_at is not None:
#         task.completed_at = task_data.completed_at

#     task.updated_at = datetime.utcnow()

#     # Notification if reassigned
#     if task_data.assignee_id:

#         notification = Notification(

#             user_id=task_data.assignee_id,

#             type="task_updated",

#             message=f"Task '{task.title}' was updated"

#         )

#         db.add(notification)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=task.project_id,

#         task_id=task.id,

#         action=f"Updated task '{task.title}'"

#     )

#     db.add(activity)

#     db.commit()

#     db.refresh(task)

#     return task


# # =========================================
# # DELETE TASK
# # =========================================

# @app.delete("/tasks/{task_id}")

# def delete_task(

#     task_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     # Check admin/owner access
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == task.project_id,
#         ProjectMember.user_id == current_user.id,
#         ProjectMember.role == "admin"
#     ).first()

#     project = db.query(Project).filter(
#         Project.id == task.project_id
#     ).first()

#     if (
#         current_user.id != project.owner_id
#         and not membership
#     ):

#         raise HTTPException(
#             status_code=403,
#             detail="Admin access required"
#         )

#     db.delete(task)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=task.project_id,

#         action="Deleted a task"

#     )

#     db.add(activity)

#     db.commit()

#     return {
#         "message": "Task deleted successfully"
#     }


# # =========================================
# # UPDATE TASK STATUS
# # =========================================

# @app.patch(
#     "/tasks/{task_id}/status",
#     response_model=TaskResponseSchema
# )

# def update_task_status(

#     task_id: UUID,

#     status_value: str,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     allowed_status = [
#         "todo",
#         "in_progress",
#         "done"
#     ]

#     if status_value not in allowed_status:

#         raise HTTPException(
#             status_code=400,
#             detail="Invalid status"
#         )

#     task.status = status_value

#     task.updated_at = datetime.utcnow()

#     # Auto complete timestamp
#     if status_value == "done":
#         task.completed_at = datetime.utcnow()

#     # Notification
#     if task.assignee_id:

#         notification = Notification(

#             user_id=task.assignee_id,

#             type="task_updated",

#             message=f"Task '{task.title}' status updated to '{status_value}'"

#         )

#         db.add(notification)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=task.project_id,

#         task_id=task.id,

#         action=f"Updated task status to '{status_value}'"

#     )

#     db.add(activity)

#     db.commit()

#     db.refresh(task)

#     return task


# # =========================================
# # MARK TASK COMPLETE
# # =========================================

# @app.patch(
#     "/tasks/{task_id}/complete",
#     response_model=TaskResponseSchema
# )

# def mark_task_complete(

#     task_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     task.status = "done"

#     task.completed_at = datetime.utcnow()

#     task.updated_at = datetime.utcnow()

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=task.project_id,

#         task_id=task.id,

#         action=f"Completed task '{task.title}'"

#     )

#     db.add(activity)

#     db.commit()

#     db.refresh(task)

#     return task






# # =========================================
# # ADD COMMENT
# # =========================================

# @app.post(
#     "/tasks/{task_id}/comments",
#     response_model=CommentResponseSchema
# )

# def add_comment(

#     task_id: UUID,

#     comment_data: CommentCreateSchema,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Check task exists
#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     # Check membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == task.project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     # Create comment
#     new_comment = TaskComment(

#         task_id=task.id,

#         user_id=current_user.id,

#         comment=comment_data.comment

#     )

#     db.add(new_comment)

#     # Notification to assignee
#     if task.assignee_id and task.assignee_id != current_user.id:

#         notification = Notification(

#             user_id=task.assignee_id,

#             type="comment_added",

#             message=f"New comment added to task '{task.title}'"

#         )

#         db.add(notification)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=task.project_id,

#         task_id=task.id,

#         action=f"Added comment to task '{task.title}'"

#     )

#     db.add(activity)

#     db.commit()

#     db.refresh(new_comment)

#     return new_comment


# # =========================================
# # GET TASK COMMENTS
# # =========================================

# @app.get(
#     "/tasks/{task_id}/comments",
#     response_model=List[CommentResponseSchema]
# )

# def get_task_comments(

#     task_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Check task exists
#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     # Verify membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == task.project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     comments = db.query(TaskComment).filter(
#         TaskComment.task_id == task_id
#     ).all()

#     return comments


# # =========================================
# # DELETE COMMENT
# # =========================================

# @app.delete("/comments/{comment_id}")

# def delete_comment(

#     comment_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     comment = db.query(TaskComment).filter(
#         TaskComment.id == comment_id
#     ).first()

#     if not comment:

#         raise HTTPException(
#             status_code=404,
#             detail="Comment not found"
#         )

#     # Only comment owner can delete
#     if comment.user_id != current_user.id:

#         raise HTTPException(
#             status_code=403,
#             detail="You can only delete your own comments"
#         )

#     db.delete(comment)

#     db.commit()

#     return {
#         "message": "Comment deleted successfully"
#     }


# # =========================================
# # ATTACHMENT APIs
# # =========================================

# # Create uploads folder automatically
# UPLOAD_FOLDER = "uploads"

# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# # =========================================
# # UPLOAD ATTACHMENT
# # =========================================

# @app.post(
#     "/tasks/{task_id}/attachments",
#     response_model=AttachmentResponseSchema
# )

# def upload_attachment(

#     task_id: UUID,

#     file: UploadFile = File(...),

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Check task exists
#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     # Check membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == task.project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     # Generate file path
#     file_path = f"{UPLOAD_FOLDER}/{file.filename}"

#     # Save file locally
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Create attachment record
#     attachment = TaskAttachment(

#         task_id=task.id,

#         uploaded_by=current_user.id,

#         file_name=file.filename,

#         file_url=file_path

#     )

#     db.add(attachment)

#     # Activity log
#     activity = ActivityLog(

#         user_id=current_user.id,

#         project_id=task.project_id,

#         task_id=task.id,

#         action=f"Uploaded attachment '{file.filename}'"

#     )

#     db.add(activity)

#     db.commit()

#     db.refresh(attachment)

#     return attachment


# # =========================================
# # GET TASK ATTACHMENTS
# # =========================================

# @app.get(
#     "/tasks/{task_id}/attachments",
#     response_model=List[AttachmentResponseSchema]
# )

# def get_task_attachments(

#     task_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Check task exists
#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     # Verify membership
#     membership = db.query(ProjectMember).filter(
#         ProjectMember.project_id == task.project_id,
#         ProjectMember.user_id == current_user.id
#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     attachments = db.query(TaskAttachment).filter(
#         TaskAttachment.task_id == task_id
#     ).all()

#     return attachments


# # =========================================
# # DELETE ATTACHMENT
# # =========================================

# @app.delete("/attachments/{attachment_id}")

# def delete_attachment(

#     attachment_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     attachment = db.query(TaskAttachment).filter(
#         TaskAttachment.id == attachment_id
#     ).first()

#     if not attachment:

#         raise HTTPException(
#             status_code=404,
#             detail="Attachment not found"
#         )

#     # Only uploader can delete
#     if attachment.uploaded_by != current_user.id:

#         raise HTTPException(
#             status_code=403,
#             detail="You can only delete your own attachments"
#         )

#     # Delete local file if exists
#     if os.path.exists(attachment.file_url):
#         os.remove(attachment.file_url)

#     db.delete(attachment)

#     db.commit()

#     return {
#         "message": "Attachment deleted successfully"
#     }




# # =========================================
# # NOTIFICATIONS APIs
# # =========================================

# #from typing import List


# # =========================================
# # GET USER NOTIFICATIONS
# # =========================================

# @app.get(
#     "/notifications",
#     response_model=List[NotificationResponseSchema]
# )

# def get_notifications(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     notifications = db.query(Notification).filter(
#         Notification.user_id == current_user.id
#     ).order_by(
#         Notification.created_at.desc()
#     ).all()

#     return notifications


# # =========================================
# # GET UNREAD NOTIFICATIONS
# # =========================================

# @app.get(
#     "/notifications/unread",
#     response_model=List[NotificationResponseSchema]
# )

# def get_unread_notifications(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     notifications = db.query(Notification).filter(

#         Notification.user_id == current_user.id,

#         Notification.is_read.is_(False)

#     ).order_by(
#         Notification.created_at.desc()
#     ).all()

#     return notifications


# # =========================================
# # MARK SINGLE NOTIFICATION AS READ
# # =========================================

# @app.patch(
#     "/notifications/{notification_id}/read",
#     response_model=NotificationResponseSchema
# )

# def mark_notification_read(

#     notification_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     notification = db.query(Notification).filter(

#         Notification.id == notification_id,

#         Notification.user_id == current_user.id

#     ).first()

#     if not notification:

#         raise HTTPException(
#             status_code=404,
#             detail="Notification not found"
#         )

#     notification.is_read = True

#     db.commit()

#     db.refresh(notification)

#     return notification


# # =========================================
# # MARK ALL NOTIFICATIONS AS READ
# # =========================================

# @app.patch("/notifications/read-all")

# def mark_all_notifications_read(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     notifications = db.query(Notification).filter(

#         Notification.user_id == current_user.id,

#         Notification.is_read.is_(False)

#     ).all()

#     for notification in notifications:
#         notification.is_read = True

#     db.commit()

#     return {
#         "message": "All notifications marked as read"
#     }


# # =========================================
# # DELETE NOTIFICATION
# # =========================================

# @app.delete("/notifications/{notification_id}")

# def delete_notification(

#     notification_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     notification = db.query(Notification).filter(

#         Notification.id == notification_id,

#         Notification.user_id == current_user.id

#     ).first()

#     if not notification:

#         raise HTTPException(
#             status_code=404,
#             detail="Notification not found"
#         )

#     db.delete(notification)

#     db.commit()

#     return {
#         "message": "Notification deleted successfully"
#     }


# # =========================================
# # GET UNREAD NOTIFICATION COUNT
# # =========================================

# @app.get("/notifications/unread-count")

# def get_unread_notification_count(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     unread_count = db.query(Notification).filter(

#         Notification.user_id == current_user.id,

#         Notification.is_read.is_(False)

#     ).count()

#     return {
#         "unread_notifications": unread_count
#     }


# # =========================================
# # CLEAR ALL NOTIFICATIONS
# # =========================================

# @app.delete("/notifications")

# def clear_all_notifications(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     notifications = db.query(Notification).filter(
#         Notification.user_id == current_user.id
#     ).all()

#     for notification in notifications:
#         db.delete(notification)

#     db.commit()

#     return {
#         "message": "All notifications cleared"
#     }




# # =========================================
# # DASHBOARD ANALYTICS APIs
# # =========================================




# # =========================================
# # DASHBOARD SUMMARY
# # =========================================

# @app.get("/dashboard/summary")

# def dashboard_summary(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Total projects
#     total_projects = db.query(ProjectMember).filter(
#         ProjectMember.user_id == current_user.id
#     ).count()

#     # Total tasks
#     total_tasks = db.query(Task).join(
#         ProjectMember,
#         Task.project_id == ProjectMember.project_id
#     ).filter(
#         ProjectMember.user_id == current_user.id
#     ).count()

#     # Completed tasks
#     completed_tasks = db.query(Task).join(
#         ProjectMember,
#         Task.project_id == ProjectMember.project_id
#     ).filter(

#         ProjectMember.user_id == current_user.id,

#         Task.status == "done"

#     ).count()

#     # Pending tasks
#     pending_tasks = db.query(Task).join(
#         ProjectMember,
#         Task.project_id == ProjectMember.project_id
#     ).filter(

#         ProjectMember.user_id == current_user.id,

#         Task.status != "done"

#     ).count()

#     # Overdue tasks
#     overdue_tasks = db.query(Task).join(
#         ProjectMember,
#         Task.project_id == ProjectMember.project_id
#     ).filter(

#         ProjectMember.user_id == current_user.id,

#         Task.due_date < date.today(),

#         Task.status != "done"

#     ).count()

#     return {

#         "total_projects": total_projects,

#         "total_tasks": total_tasks,

#         "completed_tasks": completed_tasks,

#         "pending_tasks": pending_tasks,

#         "overdue_tasks": overdue_tasks

#     }


# # =========================================
# # TASK STATUS ANALYTICS
# # =========================================

# @app.get("/dashboard/task-status")

# def task_status_analytics(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     results = db.query(

#         Task.status,

#         func.count(Task.id)

#     ).join(

#         ProjectMember,
#         Task.project_id == ProjectMember.project_id

#     ).filter(

#         ProjectMember.user_id == current_user.id

#     ).group_by(
#         Task.status
#     ).all()

#     analytics = {
#     str(status): count
#     for status, count in results
#     }

#     return analytics


# # =========================================
# # TASK PRIORITY ANALYTICS
# # =========================================

# @app.get("/dashboard/task-priority")

# def task_priority_analytics(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     results = db.query(

#         Task.priority,

#         func.count(Task.id)

#     ).join(

#         ProjectMember,
#         Task.project_id == ProjectMember.project_id

#     ).filter(

#         ProjectMember.user_id == current_user.id

#     ).group_by(
#         Task.priority
#     ).all()

#     analytics = {}

#     for priority, count in results:
#         analytics[priority] = count

#     return analytics


# # =========================================
# # RECENT TASKS
# # =========================================

# @app.get(
#     "/dashboard/recent-tasks",
#     response_model=List[TaskResponseSchema]
# )

# def recent_tasks(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     tasks = db.query(Task).join(

#         ProjectMember,
#         Task.project_id == ProjectMember.project_id

#     ).filter(

#         ProjectMember.user_id == current_user.id

#     ).order_by(
#         Task.created_at.desc()
#     ).limit(10).all()

#     return tasks


# # =========================================
# # ASSIGNED TASKS
# # =========================================

# @app.get(
#     "/dashboard/assigned-tasks",
#     response_model=List[TaskResponseSchema]
# )

# def assigned_tasks(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     tasks = db.query(Task).filter(
#         Task.assignee_id == current_user.id
#     ).order_by(
#         Task.created_at.desc()
#     ).all()

#     return tasks


# # =========================================
# # OVERDUE TASKS
# # =========================================

# @app.get(
#     "/dashboard/overdue-tasks",
#     response_model=List[TaskResponseSchema]
# )

# def overdue_tasks_dashboard(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     tasks = db.query(Task).join(

#         ProjectMember,
#         Task.project_id == ProjectMember.project_id

#     ).filter(

#         ProjectMember.user_id == current_user.id,

#         Task.due_date < date.today(),

#         Task.status != "done"

#     ).order_by(
#         Task.due_date.asc()
#     ).all()

#     return tasks


# # =========================================
# # RECENT ACTIVITY TIMELINE
# # =========================================

# @app.get(
#     "/activities",
#     response_model=List[ActivityLogResponseSchema]
# )

# def get_activity_timeline(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     activities = db.query(ActivityLog).join(

#         ProjectMember,
#         ActivityLog.project_id == ProjectMember.project_id

#     ).filter(

#         ProjectMember.user_id == current_user.id

#     ).order_by(
#         ActivityLog.created_at.desc()
#     ).limit(50).all()

#     return activities


# # =========================================
# # PROJECT ACTIVITY TIMELINE
# # =========================================

# @app.get(
#     "/projects/{project_id}/activities",
#     response_model=List[ActivityLogResponseSchema]
# )

# def get_project_activities(

#     project_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     # Verify membership
#     membership = db.query(ProjectMember).filter(

#         ProjectMember.project_id == project_id,

#         ProjectMember.user_id == current_user.id

#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     activities = db.query(ActivityLog).filter(
#         ActivityLog.project_id == project_id
#     ).order_by(
#         ActivityLog.created_at.desc()
#     ).all()

#     return activities


# # =========================================
# # TASK ACTIVITY TIMELINE
# # =========================================

# @app.get(
#     "/tasks/{task_id}/activities",
#     response_model=List[ActivityLogResponseSchema]
# )

# def get_task_activities(

#     task_id: UUID,

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     task = db.query(Task).filter(
#         Task.id == task_id
#     ).first()

#     if not task:

#         raise HTTPException(
#             status_code=404,
#             detail="Task not found"
#         )

#     # Verify membership
#     membership = db.query(ProjectMember).filter(

#         ProjectMember.project_id == task.project_id,

#         ProjectMember.user_id == current_user.id

#     ).first()

#     if not membership:

#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )

#     activities = db.query(ActivityLog).filter(
#         ActivityLog.task_id == task_id
#     ).order_by(
#         ActivityLog.created_at.desc()
#     ).all()

#     return activities


# # =========================================
# # GET OVERDUE TASKS
# # =========================================

# @app.get(
#     "/tasks/overdue",
#     response_model=List[TaskResponseSchema]
# )

# def get_overdue_tasks(

#     db: Session = Depends(get_db),

#     current_user: User = Depends(get_current_user)

# ):

#     today = date.today()

#     overdue_tasks = db.query(Task).join(
#         ProjectMember,
#         Task.project_id == ProjectMember.project_id
#     ).filter(

#         ProjectMember.user_id == current_user.id,

#         Task.due_date < today,

#         Task.status != "done"

#     ).all()

#     return overdue_tasks






# # =========================================
# # CURRENT USER ROUTE
# # Protected Route
# # =========================================

# @app.get(
#     "/me",
#     response_model=UserResponseSchema
# )

# def get_me(

#     current_user: User = Depends(get_current_user)

# ):

#     return current_user


# # =========================================
# # ADMIN TEST ROUTE
# # RBAC Protected
# # =========================================

# @app.get("/admin-only")

# def admin_only(

#     current_user: User = Depends(require_admin)

# ):

#     return {

#         "message": "Welcome Admin",

#         "admin_name": current_user.name

#     }









# import React, {
#   createContext,
#   useContext,
#   useEffect,
#   useState
# } from "react";

# import ReactDOM from "react-dom/client";

# import {
#   BrowserRouter,
#   Routes,
#   Route,
#   Navigate,
#   Link,
#   useNavigate
# } from "react-router-dom";

# import axios from "axios";

# import "./index.css";


# // ======================================================
# // AXIOS CONFIG
# // ======================================================

# const API = axios.create({
#   baseURL: "http://127.0.0.1:8000",
# });


# // ======================================================
# // AUTH CONTEXT
# // ======================================================

# const AuthContext = createContext();

# const useAuth = () => useContext(AuthContext);

# function AuthProvider({ children }) {

#   const [token, setToken] = useState(
#     localStorage.getItem("token")
#   );

#   const [user, setUser] = useState(null);

#  useEffect(() => {

#   const fetchCurrentUser = async () => {

#     try {

#       if (token) {

#         API.defaults.headers.common[
#           "Authorization"
#         ] = `Bearer ${token}`;

#         const response = await API.get("/me");

#         setUser(response.data);

#       }

#     } catch (err) {

#       console.log(err);

#       logout();

#     }

#   };

#   fetchCurrentUser();

# }, [token]);

#   const login = (tokenValue) => {

#     localStorage.setItem("token", tokenValue);

#     setToken(tokenValue);

#     API.defaults.headers.common[
#       "Authorization"
#     ] = `Bearer ${tokenValue}`;
#   };

#   const logout = () => {

#     localStorage.removeItem("token");

#     setToken(null);

#     setUser(null);

#     delete API.defaults.headers.common[
#       "Authorization"
#     ];
#   };

#   return (

#     <AuthContext.Provider
#       value={{
#         token,
#         user,
#         setUser,
#         login,
#         logout
#       }}
#     >
#       {children}
#     </AuthContext.Provider>

#   );
# }


# // ======================================================
# // PROTECTED ROUTE
# // ======================================================

# function ProtectedRoute({ children }) {

#   const { token } = useAuth();

#   if (!token) {
#     return <Navigate to="/login" />;
#   }

#   return children;
# }


# // ======================================================
# // NAVBAR
# // ======================================================

# function Navbar() {

#   const { token, user, logout } = useAuth();

#   return (

#     <div className="bg-gray-900 text-white px-8 py-4 flex justify-between items-center">

#       <h1 className="text-2xl font-bold">
#         Team Task Manager
#       </h1>

#       <div className="flex gap-4 items-center">

#         {token && (
#           <>
            
#             {user && (

#             <div className="flex items-center gap-2">

#                 <span>
#                 {user.name}
#                 </span>

#                 <span className="bg-blue-500 px-2 py-1 rounded text-sm">
#                 {user.role}
#                 </span>

#             </div>

#             )}
        
#             <Link to="/dashboard">
#             Dashboard
#             </Link>

#             <button
#               onClick={logout}
#               className="bg-red-500 px-4 py-1 rounded"
#             >
#               Logout
#             </button>
#           </>
#         )}

#       </div>

#     </div>

#   );
# }


# // ======================================================
# // SIGNUP PAGE
# // ======================================================

# function SignupPage() {

#   const navigate = useNavigate();

#   const [formData, setFormData] = useState({

#     name: "",
#     email: "",
#     password: "",
#     role: "member"

#   });

#   const [loading, setLoading] = useState(false);

#   const [error, setError] = useState("");

#   const handleChange = (e) => {

#     setFormData({

#       ...formData,

#       [e.target.name]: e.target.value

#     });

#   };

#   const handleSignup = async (e) => {

#     e.preventDefault();

#     setLoading(true);

#     setError("");

#     try {

#       await API.post("/signup", formData);

#       navigate("/login");

#     } catch (err) {

#       setError(
#         err.response?.data?.detail ||
#         "Signup failed"
#       );

#     } finally {

#       setLoading(false);

#     }
#   };

#   return (

#     <div className="min-h-screen bg-gray-100 flex items-center justify-center">

#       <form
#         onSubmit={handleSignup}
#         className="bg-white p-8 rounded-xl shadow-xl w-[400px]"
#       >

#         <h2 className="text-3xl font-bold mb-6 text-center">
#           Signup
#         </h2>

#         {error && (
#           <p className="text-red-500 mb-4">
#             {error}
#           </p>
#         )}

#         <input
#           type="text"
#           name="name"
#           placeholder="Full Name"
#           className="w-full border p-3 rounded mb-4"
#           onChange={handleChange}
#         />

#         <input
#           type="email"
#           name="email"
#           placeholder="Email"
#           className="w-full border p-3 rounded mb-4"
#           onChange={handleChange}
#         />

#         <input
#           type="password"
#           name="password"
#           placeholder="Password"
#           className="w-full border p-3 rounded mb-4"
#           onChange={handleChange}
#         />

#         <select

#             name="role"

#             value={formData.role}

#             onChange={handleChange}

#             className="w-full p-3 rounded bg-gray-800 text-white mb-4"

#         >

#             <option value="member">
#                 Member
#             </option>

#             <option value="admin">
#                 Admin
#             </option>

#         </select>


#         <button
#           type="submit"
#           disabled={loading}
#           className="w-full bg-black text-white py-3 rounded"
#         >

#           {loading ? "Creating..." : "Signup"}

#         </button>

#         <p className="mt-4 text-center">

#           Already have account?

#           <Link
#             to="/login"
#             className="text-blue-500 ml-2"
#           >
#             Login
#           </Link>

#         </p>

#       </form>

#     </div>

#   );
# }


# // ======================================================
# // LOGIN PAGE
# // ======================================================

# function LoginPage() {

#   const navigate = useNavigate();

#   const { login } = useAuth();

#   const [formData, setFormData] = useState({

#     email: "",
#     password: ""

#   });

#   const [loading, setLoading] = useState(false);

#   const [error, setError] = useState("");

#   const handleChange = (e) => {

#     setFormData({

#       ...formData,

#       [e.target.name]: e.target.value

#     });

#   };

#   const handleLogin = async (e) => {

#     e.preventDefault();

#     setLoading(true);

#     setError("");

#     try {

#       const response = await API.post(
#         "/login",
#         formData
#       );

#       login(response.data.access_token);

#       navigate("/dashboard");

#     } catch (err) {

#       setError(
#         err.response?.data?.detail ||
#         "Login failed"
#       );

#     } finally {

#       setLoading(false);

#     }
#   };

#   return (

#     <div className="min-h-screen bg-gray-100 flex items-center justify-center">

#       <form
#         onSubmit={handleLogin}
#         className="bg-white p-8 rounded-xl shadow-xl w-[400px]"
#       >

#         <h2 className="text-3xl font-bold mb-6 text-center">
#           Login
#         </h2>

#         {error && (
#           <p className="text-red-500 mb-4">
#             {error}
#           </p>
#         )}

#         <input
#           type="email"
#           name="email"
#           placeholder="Email"
#           className="w-full border p-3 rounded mb-4"
#           onChange={handleChange}
#         />

#         <input
#           type="password"
#           name="password"
#           placeholder="Password"
#           className="w-full border p-3 rounded mb-4"
#           onChange={handleChange}
#         />

#         <button
#           type="submit"
#           disabled={loading}
#           className="w-full bg-black text-white py-3 rounded"
#         >

#           {loading ? "Logging in..." : "Login"}

#         </button>

#         <p className="mt-4 text-center">

#           Don't have account?

#           <Link
#             to="/signup"
#             className="text-blue-500 ml-2"
#           >
#             Signup
#           </Link>

#         </p>

#       </form>

#     </div>

#   );
# }


# // ======================================================
# // DASHBOARD PAGE
# // ======================================================

# function DashboardPage() {

#   const [summary, setSummary] = useState(null);

#   useEffect(() => {

#     fetchDashboard();

#   }, []);

#   const fetchDashboard = async () => {

#     try {

#       const response = await API.get(
#         "/dashboard/summary"
#       );

#       setSummary(response.data);

#     } catch (err) {

#       console.log(err);

#     }
#   };

#   return (

#     <div className="min-h-screen bg-gray-100">

#       <Navbar />

#       <div className="p-8">

#         <h1 className="text-4xl font-bold mb-8">
#           Dashboard
#         </h1>
#         {user?.role === "admin" && (

#         <button className="bg-black text-white px-6 py-3 rounded-lg mb-8">

#             Create Project

#         </button>

#         )}

#         {summary && (

#           <div className="grid grid-cols-5 gap-6">

#             <div className="bg-white p-6 rounded-xl shadow">
#               <h2 className="text-xl font-semibold">
#                 Projects
#               </h2>

#               <p className="text-4xl mt-4">
#                 {summary.total_projects}
#               </p>
#             </div>

#             <div className="bg-white p-6 rounded-xl shadow">
#               <h2 className="text-xl font-semibold">
#                 Tasks
#               </h2>

#               <p className="text-4xl mt-4">
#                 {summary.total_tasks}
#               </p>
#             </div>

#             <div className="bg-white p-6 rounded-xl shadow">
#               <h2 className="text-xl font-semibold">
#                 Completed
#               </h2>

#               <p className="text-4xl mt-4 text-green-500">
#                 {summary.completed_tasks}
#               </p>
#             </div>

#             <div className="bg-white p-6 rounded-xl shadow">
#               <h2 className="text-xl font-semibold">
#                 Pending
#               </h2>

#               <p className="text-4xl mt-4 text-yellow-500">
#                 {summary.pending_tasks}
#               </p>
#             </div>

#             <div className="bg-white p-6 rounded-xl shadow">
#               <h2 className="text-xl font-semibold">
#                 Overdue
#               </h2>

#               <p className="text-4xl mt-4 text-red-500">
#                 {summary.overdue_tasks}
#               </p>
#             </div>

#           </div>

#         )}

#       </div>

#     </div>

#   );
# }


# // ======================================================
# // APP
# // ======================================================

# function App() {

#   return (

#     <BrowserRouter>

#       <AuthProvider>

#         <Routes>

#           <Route
#             path="/"
#             element={<Navigate to="/login" />}
#           />

#           <Route
#             path="/signup"
#             element={<SignupPage />}
#           />

#           <Route
#             path="/login"
#             element={<LoginPage />}
#           />

#           <Route
#             path="/dashboard"
#             element={
#               <ProtectedRoute>
#                 <DashboardPage />
#               </ProtectedRoute>
#             }
#           />

#         </Routes>

#       </AuthProvider>

#     </BrowserRouter>

#   );
# }


# // ======================================================
# // RENDER
# // ======================================================

# ReactDOM.createRoot(
#   document.getElementById("root")
# ).render(
#   <React.StrictMode>
#     <App />
#   </React.StrictMode>
# );










