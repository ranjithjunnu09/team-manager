"""
seed.py — Run once to populate demo data
Usage: python seed.py
Place this file in the backend/ folder alongside backend.py
"""

import uuid
from datetime import date, timedelta
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

engine = create_engine(DATABASE_URL)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── PASSWORD ───────────────────────────────────────────
# All demo users share the same password for easy testing
DEMO_PASSWORD = "Password@123"
hashed = pwd_context.hash(DEMO_PASSWORD)

# ─── USER IDs ───────────────────────────────────────────
U1  = str(uuid.uuid4())  # Arjun Sharma   — admin
U2  = str(uuid.uuid4())  # Priya Nair     — admin
U3  = str(uuid.uuid4())  # Rahul Verma    — member
U4  = str(uuid.uuid4())  # Sneha Reddy    — member
U5  = str(uuid.uuid4())  # Karan Mehta    — member
U6  = str(uuid.uuid4())  # Divya Iyer     — member
U7  = str(uuid.uuid4())  # Amit Kulkarni  — member
U8  = str(uuid.uuid4())  # Neha Joshi     — member
U9  = str(uuid.uuid4())  # Vikram Singh   — member (inactive)
U10 = str(uuid.uuid4())  # Ananya Das     — member

# ─── PROJECT IDs ────────────────────────────────────────
P1 = str(uuid.uuid4())  # E-Commerce Platform Redesign
P2 = str(uuid.uuid4())  # Internal HR Portal
P3 = str(uuid.uuid4())  # Mobile App v2.0
P4 = str(uuid.uuid4())  # Legacy API Migration (archived)

# ─── TASK IDs ───────────────────────────────────────────
T1  = str(uuid.uuid4())
T2  = str(uuid.uuid4())
T3  = str(uuid.uuid4())
T4  = str(uuid.uuid4())
T5  = str(uuid.uuid4())
T6  = str(uuid.uuid4())
T7  = str(uuid.uuid4())
T8  = str(uuid.uuid4())
T9  = str(uuid.uuid4())
T10 = str(uuid.uuid4())
T11 = str(uuid.uuid4())
T12 = str(uuid.uuid4())

today = date.today()


def seed():
    with engine.begin() as conn:

        # ── Check if already seeded ──────────────────────
        result = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if result > 0:
            print(f"Database already has {result} users. Skipping seed.")
            print("To re-seed, manually run: TRUNCATE users CASCADE;")
            return

        print("Seeding users...")

        # ── USERS ────────────────────────────────────────
        users = [
            (U1,  "Arjun Sharma",   "arjun.sharma@taskflow.io",   hashed, "admin",  True),
            (U2,  "Priya Nair",     "priya.nair@taskflow.io",     hashed, "admin",  True),
            (U3,  "Rahul Verma",    "rahul.verma@taskflow.io",    hashed, "member", True),
            (U4,  "Sneha Reddy",    "sneha.reddy@taskflow.io",    hashed, "member", True),
            (U5,  "Karan Mehta",    "karan.mehta@taskflow.io",    hashed, "member", True),
            (U6,  "Divya Iyer",     "divya.iyer@taskflow.io",     hashed, "member", True),
            (U7,  "Amit Kulkarni",  "amit.kulkarni@taskflow.io",  hashed, "member", True),
            (U8,  "Neha Joshi",     "neha.joshi@taskflow.io",     hashed, "member", True),
            (U9,  "Vikram Singh",   "vikram.singh@taskflow.io",   hashed, "member", False),
            (U10, "Ananya Das",     "ananya.das@taskflow.io",     hashed, "member", True),
        ]

        conn.execute(text("""
            INSERT INTO users (id, name, email, hashed_password, role, is_active)
            VALUES (:id, :name, :email, :hashed_password, :role, :is_active)
        """), [
            {"id": u[0], "name": u[1], "email": u[2],
             "hashed_password": u[3], "role": u[4], "is_active": u[5]}
            for u in users
        ])
        print(f"  + {len(users)} users created")

        # ── PROJECTS ─────────────────────────────────────
        print("Seeding projects...")

        projects = [
            (P1, "E-Commerce Platform Redesign",
             "Full redesign of the storefront UI, checkout flow, and mobile responsiveness. Targeting 40% improvement in conversion rate.",
             "active", U1, str(today + timedelta(days=60))),

            (P2, "Internal HR Portal",
             "Build a self-service HR portal for leave management, payroll slips, and org chart.",
             "active", U2, str(today + timedelta(days=75))),

            (P3, "Mobile App v2.0",
             "Major version release with offline mode, push notifications, and revamped onboarding.",
             "active", U1, str(today + timedelta(days=90))),

            (P4, "Legacy API Migration",
             "Migrate REST v1 endpoints to GraphQL. Deprecate 34 legacy endpoints.",
             "archived", U2, str(today - timedelta(days=30))),
        ]

        conn.execute(text("""
            INSERT INTO projects (id, name, description, status, owner_id, deadline)
            VALUES (:id, :name, :description, :status, :owner_id, :deadline)
        """), [
            {"id": p[0], "name": p[1], "description": p[2],
             "status": p[3], "owner_id": p[4], "deadline": p[5]}
            for p in projects
        ])
        print(f"  + {len(projects)} projects created")

        # ── PROJECT MEMBERS ──────────────────────────────
        print("Seeding project members...")

        members = [
            # Project 1 — E-Commerce
            (str(uuid.uuid4()), P1, U1,  "admin"),
            (str(uuid.uuid4()), P1, U3,  "member"),
            (str(uuid.uuid4()), P1, U4,  "member"),
            (str(uuid.uuid4()), P1, U5,  "member"),
            (str(uuid.uuid4()), P1, U10, "member"),

            # Project 2 — HR Portal
            (str(uuid.uuid4()), P2, U2,  "admin"),
            (str(uuid.uuid4()), P2, U6,  "member"),
            (str(uuid.uuid4()), P2, U7,  "admin"),
            (str(uuid.uuid4()), P2, U8,  "member"),

            # Project 3 — Mobile App
            (str(uuid.uuid4()), P3, U1,  "admin"),
            (str(uuid.uuid4()), P3, U3,  "member"),
            (str(uuid.uuid4()), P3, U5,  "member"),

            # Project 4 — Legacy API (archived)
            (str(uuid.uuid4()), P4, U2,  "admin"),
            (str(uuid.uuid4()), P4, U7,  "member"),
            (str(uuid.uuid4()), P4, U10, "member"),
        ]

        conn.execute(text("""
            INSERT INTO project_members (id, project_id, user_id, role)
            VALUES (:id, :project_id, :user_id, :role)
        """), [
            {"id": m[0], "project_id": m[1], "user_id": m[2], "role": m[3]}
            for m in members
        ])
        print(f"  + {len(members)} project members added")

        # ── TASKS ────────────────────────────────────────
        print("Seeding tasks...")

        tasks = [
            # Project 1 tasks
            (T1,  P1, "Redesign homepage hero section",     "Update hero layout, copy, and CTA buttons",             "high",   "in_progress", U3,  str(today + timedelta(days=7))),
            (T2,  P1, "Fix mobile checkout flow",           "Resolve 3-step checkout breaking on iOS Safari",        "high",   "todo",        U4,  str(today + timedelta(days=3))),
            (T3,  P1, "Write product page copy",            "Update all 120 product descriptions for SEO",           "medium", "todo",        U5,  str(today + timedelta(days=14))),
            (T4,  P1, "Performance audit",                  "Run Lighthouse audit and fix all critical issues",      "medium", "done",        U10, str(today - timedelta(days=5))),
            (T5,  P1, "A/B test banner variants",           "Set up 3 banner variants and measure CTR",              "low",    "todo",        U3,  str(today - timedelta(days=2))),  # overdue

            # Project 2 tasks
            (T6,  P2, "Leave request module",               "Build form, approval workflow, and email notifications", "high",   "in_progress", U6,  str(today + timedelta(days=10))),
            (T7,  P2, "Payroll slip PDF generator",         "Generate monthly payslips as downloadable PDFs",        "high",   "todo",        U8,  str(today - timedelta(days=1))),  # overdue
            (T8,  P2, "Org chart component",                "Interactive org chart with search and zoom",            "medium", "todo",        U7,  str(today + timedelta(days=20))),

            # Project 3 tasks
            (T9,  P3, "Offline mode implementation",        "Cache critical screens using service workers",          "high",   "todo",        U3,  str(today + timedelta(days=30))),
            (T10, P3, "Push notification integration",      "Integrate FCM for Android and APNs for iOS",            "high",   "in_progress", U5,  str(today + timedelta(days=15))),
            (T11, P3, "Onboarding flow redesign",           "4-screen onboarding with skip option and animations",   "medium", "done",        U3,  str(today - timedelta(days=10))),

            # Project 4 tasks (archived)
            (T12, P4, "Document deprecated endpoints",      "Write migration guide for all 34 legacy endpoints",    "low",    "done",        U7,  str(today - timedelta(days=35))),
        ]

        conn.execute(text("""
            INSERT INTO tasks (id, project_id, title, description, priority, status, assignee_id, due_date, created_by)
            VALUES (:id, :project_id, :title, :description, :priority, :status, :assignee_id, :due_date, :created_by)
        """), [
            {
                "id": t[0], "project_id": t[1], "title": t[2],
                "description": t[3], "priority": t[4], "status": t[5],
                "assignee_id": t[6], "due_date": t[7],
                "created_by": U1 if t[1] in [P1, P3] else U2
            }
            for t in tasks
        ])
        print(f"  + {len(tasks)} tasks created")

        # ── NOTIFICATIONS ────────────────────────────────
        print("Seeding notifications...")

        notifications = [
            (str(uuid.uuid4()), U3,  "task_assigned",  "You have been assigned: Redesign homepage hero section", False),
            (str(uuid.uuid4()), U4,  "task_assigned",  "You have been assigned: Fix mobile checkout flow",       False),
            (str(uuid.uuid4()), U6,  "task_assigned",  "You have been assigned: Leave request module",           False),
            (str(uuid.uuid4()), U5,  "task_assigned",  "You have been assigned: Push notification integration",  False),
            (str(uuid.uuid4()), U3,  "overdue",        "Task overdue: A/B test banner variants",                 False),
            (str(uuid.uuid4()), U8,  "overdue",        "Task overdue: Payroll slip PDF generator",               False),
            (str(uuid.uuid4()), U1,  "project_invite", "You have been added to: E-Commerce Platform Redesign",   True),
            (str(uuid.uuid4()), U2,  "project_invite", "You have been added to: Internal HR Portal",             True),
        ]

        conn.execute(text("""
            INSERT INTO notifications (id, user_id, type, message, is_read)
            VALUES (:id, :user_id, :type, :message, :is_read)
        """), [
            {"id": n[0], "user_id": n[1], "type": n[2], "message": n[3], "is_read": n[4]}
            for n in notifications
        ])
        print(f"  + {len(notifications)} notifications created")

        print("\nSeed complete.")
        print("─" * 40)
        print("Login credentials (all users):")
        print("  Password: Password@123")
        print()
        print("  Admin accounts:")
        print("  arjun.sharma@taskflow.io")
        print("  priya.nair@taskflow.io")
        print()
        print("  Member accounts:")
        print("  rahul.verma@taskflow.io")
        print("  sneha.reddy@taskflow.io")
        print("  karan.mehta@taskflow.io")
        print("  divya.iyer@taskflow.io")
        print("  amit.kulkarni@taskflow.io")
        print("  neha.joshi@taskflow.io")
        print("  ananya.das@taskflow.io")
        print("  (vikram.singh — inactive account)")
        print("─" * 40)


if __name__ == "__main__":
    seed()