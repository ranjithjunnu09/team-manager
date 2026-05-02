# =========================================
# IMPORTS
# =========================================

import os
import uuid
import shutil

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import create_engine, Column, String, Text, Boolean, Date, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv


# =========================================
# DOTENV CONFIGURATION
# =========================================

load_dotenv(dotenv_path=".env")

DATABASE_URL               = os.getenv("DATABASE_URL")
SECRET_KEY                 = os.getenv("SECRET_KEY")
ALGORITHM                  = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS  = 7


# =========================================
# DATABASE CONNECTION
# =========================================

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()


# =========================================
# FASTAPI INITIALIZATION
# =========================================

app = FastAPI(
    title="Team Task Manager API",
    description="Production-style SaaS Team Collaboration Platform",
    version="1.0.0"
)


# =========================================
# CORS MIDDLEWARE
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← change this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# UPLOAD FOLDER
# =========================================

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================
# 1. USER MODEL
# =========================================

class User(Base):
    __tablename__ = "users"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name            = Column(String(100), nullable=False)
    email           = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    role            = Column(String(20), nullable=False, default="member")
    is_active       = Column(Boolean, default=True)
    avatar_url      = Column(Text)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sessions             = relationship("UserSession",    back_populates="user",   cascade="all, delete")
    owned_projects       = relationship("Project",        back_populates="owner",  cascade="all, delete")
    project_memberships  = relationship("ProjectMember",  back_populates="user",   cascade="all, delete")
    assigned_tasks       = relationship("Task", foreign_keys="Task.assignee_id",  back_populates="assignee")
    created_tasks        = relationship("Task", foreign_keys="Task.created_by",   back_populates="creator")
    comments             = relationship("TaskComment",    back_populates="user",   cascade="all, delete")
    attachments          = relationship("TaskAttachment", back_populates="uploader", cascade="all, delete")
    activities           = relationship("ActivityLog",    back_populates="user")
    notifications        = relationship("Notification",   back_populates="user",   cascade="all, delete")

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'member')", name="check_user_role"),
    )


# =========================================
# 2. USER SESSION MODEL
# =========================================

class UserSession(Base):
    __tablename__ = "user_sessions"

    id            = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(Text, unique=True, nullable=False)
    expires_at    = Column(DateTime, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")


# =========================================
# 3. PROJECT MODEL
# =========================================

class Project(Base):
    __tablename__ = "projects"

    id          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String(200), nullable=False)
    description = Column(Text)
    status      = Column(String(20), nullable=False, default="active")
    owner_id    = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    deadline    = Column(Date)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner      = relationship("User",          back_populates="owned_projects")
    members    = relationship("ProjectMember", back_populates="project", cascade="all, delete")
    tasks      = relationship("Task",          back_populates="project", cascade="all, delete")
    activities = relationship("ActivityLog",   back_populates="project", cascade="all, delete")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'archived', 'completed')", name="check_project_status"),
    )


# =========================================
# 4. PROJECT MEMBER MODEL
# =========================================

class ProjectMember(Base):
    __tablename__ = "project_members"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(PG_UUID(as_uuid=True), ForeignKey("users.id",    ondelete="CASCADE"), nullable=False)
    role       = Column(String(20), nullable=False, default="member")
    joined_at  = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project",     back_populates="members")
    user    = relationship("User",        back_populates="project_memberships")

    __table_args__ = (
        CheckConstraint("role IN ('admin', 'member')", name="check_project_member_role"),
    )


# =========================================
# 5. TASK MODEL
# =========================================

class Task(Base):
    __tablename__ = "tasks"

    id           = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title        = Column(String(200), nullable=False)
    description  = Column(Text)
    status       = Column(String(20), nullable=False, default="todo")
    priority     = Column(String(20), nullable=False, default="medium")
    due_date     = Column(Date)
    completed_at = Column(DateTime)
    project_id   = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assignee_id  = Column(PG_UUID(as_uuid=True), ForeignKey("users.id",    ondelete="SET NULL"))
    created_by   = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"),   nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project     = relationship("Project",        back_populates="tasks")
    assignee    = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    creator     = relationship("User", foreign_keys=[created_by],  back_populates="created_tasks")
    comments    = relationship("TaskComment",    back_populates="task", cascade="all, delete")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete")
    activities  = relationship("ActivityLog",    back_populates="task", cascade="all, delete")

    __table_args__ = (
        CheckConstraint("status IN ('todo', 'in_progress', 'done')",    name="check_task_status"),
        CheckConstraint("priority IN ('low', 'medium', 'high')",        name="check_task_priority"),
    )


# =========================================
# 6. TASK COMMENT MODEL
# =========================================

class TaskComment(Base):
    __tablename__ = "task_comments"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id    = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    comment    = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")


# =========================================
# 7. TASK ATTACHMENT MODEL
# =========================================

class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    id          = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id     = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_name   = Column(String(255), nullable=False)
    file_url    = Column(Text, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    task     = relationship("Task", back_populates="attachments")
    uploader = relationship("User", back_populates="attachments")


# =========================================
# 8. ACTIVITY LOG MODEL
# =========================================

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(PG_UUID(as_uuid=True), ForeignKey("users.id",    ondelete="SET NULL"))
    project_id = Column(PG_UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    task_id    = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id",    ondelete="CASCADE"))
    action     = Column(String(255), nullable=False)
    old_value  = Column(Text)
    new_value  = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user    = relationship("Project", back_populates="activities", foreign_keys=[project_id], overlaps="user,activities")
    project = relationship("Project", back_populates="activities", foreign_keys=[project_id])
    task    = relationship("Task",    back_populates="activities", foreign_keys=[task_id])

    # Fix overlapping relationships
    user    = relationship("User",    back_populates="activities", foreign_keys=[user_id])
    project = relationship("Project", back_populates="activities", foreign_keys=[project_id])
    task    = relationship("Task",    back_populates="activities", foreign_keys=[task_id])


# =========================================
# 9. NOTIFICATION MODEL
# =========================================

class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id    = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type       = Column(String(50), nullable=False)
    message    = Column(Text, nullable=False)
    link       = Column(Text)
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        CheckConstraint(
            "type IN ('task_assigned','task_updated','comment_added','project_invite','due_soon','overdue')",
            name="check_notification_type"
        ),
    )


# =========================================
# PYDANTIC SCHEMAS
# =========================================

# --- Auth ---
class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "member"
    avatar_url: Optional[str] = None

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenSchema(BaseModel):
    refresh_token: str

# --- User ---
class UserResponseSchema(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    is_active: bool
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None

# --- Project ---
class ProjectCreateSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = "active"
    deadline: Optional[date] = None

class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[date] = None

class ProjectResponseSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: str
    owner_id: UUID
    deadline: Optional[date]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- Project Member ---
class ProjectMemberCreateSchema(BaseModel):
    user_id: UUID
    role: Optional[str] = "member"

class ProjectMemberResponseSchema(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime
    class Config:
        from_attributes = True

# --- Task ---
class TaskCreateSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "medium"
    due_date: Optional[date] = None
    project_id: UUID
    assignee_id: Optional[UUID] = None

class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    assignee_id: Optional[UUID] = None
    completed_at: Optional[datetime] = None

class TaskStatusUpdateSchema(BaseModel):
    status: str

class TaskResponseSchema(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[date]
    completed_at: Optional[datetime]
    project_id: UUID
    assignee_id: Optional[UUID]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# --- Comment ---
class CommentCreateSchema(BaseModel):
    comment: str = Field(..., min_length=1)

class CommentResponseSchema(BaseModel):
    id: UUID
    task_id: UUID
    user_id: UUID
    comment: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- Attachment ---
class AttachmentResponseSchema(BaseModel):
    id: UUID
    task_id: UUID
    uploaded_by: UUID
    file_name: str
    file_url: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- Activity ---
class ActivityLogResponseSchema(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    project_id: Optional[UUID]
    task_id: Optional[UUID]
    action: str
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# --- Notification ---
class NotificationResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    message: str
    link: Optional[str]
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

class NotificationUpdateSchema(BaseModel):
    is_read: bool


# =========================================
# SECURITY — PASSWORD HASHING
# =========================================

# Fix bcrypt compatibility with passlib
import bcrypt as _bcrypt
if not hasattr(_bcrypt, '__about__'):
    _bcrypt.__about__ = type('about', (), {'__version__': _bcrypt.__version__})()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
# =========================================
# DATABASE DEPENDENCY
# =========================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================
# JWT FUNCTIONS
# =========================================

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================================
# AUTH DEPENDENCIES
# =========================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# =========================================
# HELPER: LOG ACTIVITY
# =========================================

def log_activity(db, user_id, action, project_id=None, task_id=None, old_value=None, new_value=None):
    activity = ActivityLog(
        user_id=user_id,
        project_id=project_id,
        task_id=task_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(activity)


# =========================================
# HELPER: CREATE NOTIFICATION
# =========================================

def create_notification(db, user_id, type: str, message: str, link: str = None):
    notification = Notification(
        user_id=user_id,
        type=type,
        message=message,
        link=link,
    )
    db.add(notification)



# =========================================
# CREATE TABLES ON STARTUP
# =========================================

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

# =========================================
# AUTH ROUTES
# =========================================

@app.post("/signup", response_model=UserResponseSchema)
def signup(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        avatar_url=user_data.avatar_url,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=TokenSchema)
def login(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_data     = {"sub": str(user.id), "role": user.role}
    access_token   = create_access_token(token_data)
    refresh_token  = create_refresh_token(token_data)

    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(session)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/logout")
def logout(
    refresh_data: RefreshTokenSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(UserSession).filter(
        UserSession.refresh_token == refresh_data.refresh_token
    ).first()
    if session:
        db.delete(session)
        db.commit()
    return {"message": "Logged out successfully"}


@app.post("/refresh", response_model=TokenSchema)
def refresh_token(refresh_data: RefreshTokenSchema, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(
        UserSession.refresh_token == refresh_data.refresh_token
    ).first()
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    try:
        payload = jwt.decode(refresh_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token_data    = {"sub": str(user.id), "role": user.role}
    access_token  = create_access_token(token_data)
    new_refresh   = create_refresh_token(token_data)

    session.refresh_token = new_refresh
    session.expires_at    = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.commit()

    return {"access_token": access_token, "refresh_token": new_refresh, "token_type": "bearer"}


# =========================================
# USER ROUTES
# =========================================

@app.get("/me", response_model=UserResponseSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.put("/me", response_model=UserResponseSchema)
def update_me(
    user_data: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_data.name        is not None: current_user.name       = user_data.name
    if user_data.avatar_url  is not None: current_user.avatar_url = user_data.avatar_url
    if user_data.is_active   is not None: current_user.is_active  = user_data.is_active
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/users", response_model=List[UserResponseSchema])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return db.query(User).all()


@app.get("/admin-only")
def admin_only(current_user: User = Depends(require_admin)):
    return {"message": "Welcome Admin", "admin_name": current_user.name}


# =========================================
# PROJECT ROUTES
# =========================================

@app.post("/projects", response_model=ProjectResponseSchema)
def create_project(
    project_data: ProjectCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        status=project_data.status,
        deadline=project_data.deadline,
        owner_id=current_user.id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Auto-add owner as admin member
    db.add(ProjectMember(project_id=new_project.id, user_id=current_user.id, role="admin"))
    log_activity(db, current_user.id, f"Created project '{new_project.name}'", project_id=new_project.id)
    db.commit()
    return new_project


@app.get("/projects", response_model=List[ProjectResponseSchema])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owned   = db.query(Project).filter(Project.owner_id == current_user.id)
    membered = db.query(Project).join(ProjectMember).filter(ProjectMember.user_id == current_user.id)
    return owned.union(membered).all()


@app.get("/projects/{project_id}", response_model=ProjectResponseSchema)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")
    return project


@app.put("/projects/{project_id}", response_model=ProjectResponseSchema)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role == "admin",
    ).first()
    if current_user.id != project.owner_id and not membership:
        raise HTTPException(status_code=403, detail="Admin access required")

    if project_data.name        is not None: project.name        = project_data.name
    if project_data.description is not None: project.description = project_data.description
    if project_data.status      is not None: project.status      = project_data.status
    if project_data.deadline    is not None: project.deadline    = project_data.deadline
    project.updated_at = datetime.utcnow()

    log_activity(db, current_user.id, f"Updated project '{project.name}'", project_id=project.id)
    db.commit()
    db.refresh(project)
    return project


@app.delete("/projects/{project_id}")
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user.id != project.owner_id:
        raise HTTPException(status_code=403, detail="Only project owner can delete")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


# =========================================
# PROJECT MEMBER ROUTES
# =========================================

@app.post("/projects/{project_id}/members", response_model=ProjectMemberResponseSchema)
def add_project_member(
    project_id: UUID,
    member_data: ProjectMemberCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role == "admin",
    ).first()
    if current_user.id != project.owner_id and not membership:
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == member_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_data.user_id,
    ).first():
        raise HTTPException(status_code=400, detail="User already a member")

    new_member = ProjectMember(project_id=project_id, user_id=member_data.user_id, role=member_data.role)
    db.add(new_member)

    create_notification(db, user.id, "project_invite", f"You were added to project '{project.name}'")
    log_activity(db, current_user.id, f"Added member '{user.name}'", project_id=project_id)
    db.commit()
    db.refresh(new_member)
    return new_member


@app.get("/projects/{project_id}/members", response_model=List[ProjectMemberResponseSchema])
def get_project_members(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()


@app.delete("/projects/{project_id}/members/{user_id}")
def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role == "admin",
    ).first()
    if current_user.id != project.owner_id and not membership:
        raise HTTPException(status_code=403, detail="Admin access required")

    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    db.delete(member)
    log_activity(db, current_user.id, "Removed member from project", project_id=project_id)
    db.commit()
    return {"message": "Member removed successfully"}


# =========================================
# TASK ROUTES
# NOTE: Static routes (/overdue) MUST come
# before dynamic routes (/{task_id})
# =========================================

@app.post("/tasks", response_model=TaskResponseSchema)
def create_task(
    task_data: TaskCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == task_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task_data.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    if task_data.assignee_id:
        if not db.query(ProjectMember).filter(
            ProjectMember.project_id == task_data.project_id,
            ProjectMember.user_id == task_data.assignee_id,
        ).first():
            raise HTTPException(status_code=400, detail="Assignee is not a project member")

    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        project_id=task_data.project_id,
        assignee_id=task_data.assignee_id,
        created_by=current_user.id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    if task_data.assignee_id:
        create_notification(db, task_data.assignee_id, "task_assigned", f"You were assigned task '{new_task.title}'")
    log_activity(db, current_user.id, f"Created task '{new_task.title}'", project_id=task_data.project_id, task_id=new_task.id)
    db.commit()
    return new_task


# STATIC route — must be above /{task_id}
@app.get("/tasks/my-tasks", response_model=List[TaskResponseSchema])
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Task).filter(Task.assignee_id == current_user.id).order_by(Task.created_at.desc()).all()


@app.get("/tasks/{task_id}", response_model=TaskResponseSchema)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponseSchema)
def update_task(
    task_id: UUID,
    task_data: TaskUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    if task_data.assignee_id:
        if not db.query(ProjectMember).filter(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == task_data.assignee_id,
        ).first():
            raise HTTPException(status_code=400, detail="Assignee is not a project member")

    old_status = task.status

    if task_data.title        is not None: task.title        = task_data.title
    if task_data.description  is not None: task.description  = task_data.description
    if task_data.status       is not None: task.status       = task_data.status
    if task_data.priority     is not None: task.priority     = task_data.priority
    if task_data.due_date     is not None: task.due_date     = task_data.due_date
    if task_data.assignee_id  is not None: task.assignee_id  = task_data.assignee_id
    if task_data.completed_at is not None: task.completed_at = task_data.completed_at

    if task_data.status == "done" and old_status != "done":
        task.completed_at = datetime.utcnow()

    task.updated_at = datetime.utcnow()

    if task_data.assignee_id:
        create_notification(db, task_data.assignee_id, "task_updated", f"Task '{task.title}' was updated")

    log_activity(db, current_user.id, f"Updated task '{task.title}'",
                 project_id=task.project_id, task_id=task.id,
                 old_value=old_status, new_value=task.status)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = db.query(Project).filter(Project.id == task.project_id).first()
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role == "admin",
    ).first()
    if current_user.id != project.owner_id and not membership:
        raise HTTPException(status_code=403, detail="Admin access required")

    log_activity(db, current_user.id, f"Deleted task '{task.title}'", project_id=task.project_id)
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


# FIX: uses request body (TaskStatusUpdateSchema) not query param
@app.patch("/tasks/{task_id}/status", response_model=TaskResponseSchema)
def update_task_status(
    task_id: UUID,
    body: TaskStatusUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if body.status not in ["todo", "in_progress", "done"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be todo, in_progress, or done")

    old_status  = task.status
    task.status = body.status
    task.updated_at = datetime.utcnow()

    if body.status == "done":
        task.completed_at = datetime.utcnow()

    if task.assignee_id:
        create_notification(db, task.assignee_id, "task_updated",
                            f"Task '{task.title}' status changed to '{body.status}'")

    log_activity(db, current_user.id, f"Changed task status",
                 project_id=task.project_id, task_id=task.id,
                 old_value=old_status, new_value=body.status)
    db.commit()
    db.refresh(task)
    return task


@app.patch("/tasks/{task_id}/complete", response_model=TaskResponseSchema)
def mark_task_complete(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status       = "done"
    task.completed_at = datetime.utcnow()
    task.updated_at   = datetime.utcnow()

    log_activity(db, current_user.id, f"Completed task '{task.title}'",
                 project_id=task.project_id, task_id=task.id)
    db.commit()
    db.refresh(task)
    return task


@app.get("/projects/{project_id}/tasks", response_model=List[TaskResponseSchema])
def get_project_tasks(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(Task).filter(Task.project_id == project_id).all()


# =========================================
# COMMENT ROUTES
# =========================================

@app.post("/tasks/{task_id}/comments", response_model=CommentResponseSchema)
def add_comment(
    task_id: UUID,
    comment_data: CommentCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    new_comment = TaskComment(task_id=task.id, user_id=current_user.id, comment=comment_data.comment)
    db.add(new_comment)

    if task.assignee_id and task.assignee_id != current_user.id:
        create_notification(db, task.assignee_id, "comment_added",
                            f"New comment on task '{task.title}'")

    log_activity(db, current_user.id, f"Commented on task '{task.title}'",
                 project_id=task.project_id, task_id=task.id)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@app.get("/tasks/{task_id}/comments", response_model=List[CommentResponseSchema])
def get_task_comments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(TaskComment).filter(TaskComment.task_id == task_id).all()


@app.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")

    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


# =========================================
# ATTACHMENT ROUTES
# =========================================

@app.post("/tasks/{task_id}/attachments", response_model=AttachmentResponseSchema)
def upload_attachment(
    task_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    file_path = f"{UPLOAD_FOLDER}/{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    attachment = TaskAttachment(
        task_id=task.id,
        uploaded_by=current_user.id,
        file_name=file.filename,
        file_url=file_path,
    )
    db.add(attachment)
    log_activity(db, current_user.id, f"Uploaded '{file.filename}'",
                 project_id=task.project_id, task_id=task.id)
    db.commit()
    db.refresh(attachment)
    return attachment


@app.get("/tasks/{task_id}/attachments", response_model=List[AttachmentResponseSchema])
def get_task_attachments(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(TaskAttachment).filter(TaskAttachment.task_id == task_id).all()


@app.delete("/attachments/{attachment_id}")
def delete_attachment(
    attachment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attachment = db.query(TaskAttachment).filter(TaskAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own attachments")

    if os.path.exists(attachment.file_url):
        os.remove(attachment.file_url)

    db.delete(attachment)
    db.commit()
    return {"message": "Attachment deleted successfully"}


# =========================================
# NOTIFICATION ROUTES
# NOTE: Static routes MUST come before
# dynamic /{notification_id} routes
# =========================================

@app.get("/notifications", response_model=List[NotificationResponseSchema])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()


# STATIC — must be above /{notification_id}
@app.get("/notifications/unread", response_model=List[NotificationResponseSchema])
def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    ).order_by(Notification.created_at.desc()).all()


# STATIC — must be above /{notification_id}
@app.get("/notifications/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    ).count()
    return {"unread_notifications": count}


# STATIC — must be above /{notification_id}
@app.patch("/notifications/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read.is_(False),
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


# STATIC — must be above /{notification_id}
@app.delete("/notifications/clear-all")
def clear_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).delete()
    db.commit()
    return {"message": "All notifications cleared"}


# DYNAMIC — must be BELOW all static /notifications/* routes
@app.patch("/notifications/{notification_id}/read", response_model=NotificationResponseSchema)
def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@app.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted"}


# =========================================
# DASHBOARD ROUTES
# =========================================

@app.get("/dashboard/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    total_projects = db.query(ProjectMember).filter(
        ProjectMember.user_id == current_user.id
    ).count()

    base_tasks = db.query(Task).join(
        ProjectMember, Task.project_id == ProjectMember.project_id
    ).filter(ProjectMember.user_id == current_user.id)

    total_tasks     = base_tasks.count()
    completed_tasks = base_tasks.filter(Task.status == "done").count()
    pending_tasks   = base_tasks.filter(Task.status != "done").count()
    overdue_tasks   = base_tasks.filter(Task.due_date < today, Task.status != "done").count()

    return {
        "total_projects":  total_projects,
        "total_tasks":     total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks":   pending_tasks,
        "overdue_tasks":   overdue_tasks,
    }


@app.get("/dashboard/task-status")
def task_status_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = db.query(Task.status, func.count(Task.id)).join(
        ProjectMember, Task.project_id == ProjectMember.project_id
    ).filter(ProjectMember.user_id == current_user.id).group_by(Task.status).all()
    return {str(s): c for s, c in results}


@app.get("/dashboard/task-priority")
def task_priority_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = db.query(Task.priority, func.count(Task.id)).join(
        ProjectMember, Task.project_id == ProjectMember.project_id
    ).filter(ProjectMember.user_id == current_user.id).group_by(Task.priority).all()
    return {str(p): c for p, c in results}


@app.get("/dashboard/recent-tasks", response_model=List[TaskResponseSchema])
def recent_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Task).join(
        ProjectMember, Task.project_id == ProjectMember.project_id
    ).filter(
        ProjectMember.user_id == current_user.id
    ).order_by(Task.created_at.desc()).limit(10).all()


@app.get("/dashboard/assigned-tasks", response_model=List[TaskResponseSchema])
def assigned_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Task).filter(
        Task.assignee_id == current_user.id
    ).order_by(Task.created_at.desc()).all()


@app.get("/dashboard/overdue-tasks", response_model=List[TaskResponseSchema])
def overdue_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Task).join(
        ProjectMember, Task.project_id == ProjectMember.project_id
    ).filter(
        ProjectMember.user_id == current_user.id,
        Task.due_date < date.today(),
        Task.status != "done",
    ).order_by(Task.due_date.asc()).all()


# =========================================
# ACTIVITY ROUTES
# =========================================

@app.get("/activities", response_model=List[ActivityLogResponseSchema])
def get_activity_timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(ActivityLog).join(
        ProjectMember, ActivityLog.project_id == ProjectMember.project_id
    ).filter(
        ProjectMember.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(50).all()


@app.get("/projects/{project_id}/activities", response_model=List[ActivityLogResponseSchema])
def get_project_activities(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(ActivityLog).filter(
        ActivityLog.project_id == project_id
    ).order_by(ActivityLog.created_at.desc()).all()


@app.get("/tasks/{task_id}/activities", response_model=List[ActivityLogResponseSchema])
def get_task_activities(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == task.project_id,
        ProjectMember.user_id == current_user.id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(ActivityLog).filter(
        ActivityLog.task_id == task_id
    ).order_by(ActivityLog.created_at.desc()).all()