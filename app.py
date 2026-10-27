
import os, hashlib, secrets, random, statistics
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, Query, Depends, status
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, func, text, or_
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload

BASE = Path(__file__).parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE/'kaushal360.db'}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, provider, officer, trainee
    name = Column(String, nullable=False)
    trainee_id = Column(Integer, ForeignKey("trainees.id"), nullable=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)

    trainee = relationship("Trainee", foreign_keys=[trainee_id])
    provider = relationship("Provider", foreign_keys=[provider_id])
    district = relationship("District", foreign_keys=[district_id])

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    score = Column(Float)

class Programme(Base):
    __tablename__ = "programmes"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    programme_id = Column(Integer, ForeignKey("programmes.id"))
    provider_id = Column(Integer, ForeignKey("providers.id"))
    duration_weeks = Column(Integer)

    programme = relationship("Programme")
    provider = relationship("Provider")

class Employer(Base):
    __tablename__ = "employers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    district_id = Column(Integer, ForeignKey("districts.id"))
    sector = Column(String)

    district = relationship("District")

class Trainee(Base):
    __tablename__ = "trainees"
    id = Column(Integer, primary_key=True)
    trainee_id = Column(String, unique=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    district_id = Column(Integer, ForeignKey("districts.id"))
    location = Column(String)
    language = Column(String)
    education = Column(String)
    urban_rural = Column(String)
    contact_status = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"))
    provider_id = Column(Integer, ForeignKey("providers.id"))
    programme_id = Column(Integer, ForeignKey("programmes.id"))
    batch = Column(String)
    enrolled_at = Column(DateTime)
    completed_at = Column(DateTime)
    certified = Column(Boolean)
    attendance = Column(Float)
    assessment = Column(Float)
    employment_status = Column(String)
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=True)
    job_role = Column(String)
    joining_date = Column(DateTime, nullable=True)
    salary = Column(Float, nullable=True)
    employment_type = Column(String, nullable=True)
    relevance = Column(Float)
    source = Column(String)
    verification = Column(String)
    confidence = Column(Float)
    consent = Column(Boolean, default=True)
    consent_updated = Column(DateTime)
    nonplacement_reason = Column(String, nullable=True)
    retention_3 = Column(Boolean)
    retention_6 = Column(Boolean)
    retention_12 = Column(Boolean)

    district = relationship("District", foreign_keys=[district_id])
    provider = relationship("Provider", foreign_keys=[provider_id])
    course = relationship("Course", foreign_keys=[course_id])
    programme = relationship("Programme", foreign_keys=[programme_id])
    employer = relationship("Employer", foreign_keys=[employer_id])

class SalaryRecord(Base):
    __tablename__ = "salary_records"
    id = Column(Integer, primary_key=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"))
    month = Column(String)
    salary = Column(Float)

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    demand = Column(Float)
    certified = Column(Float)
    required = Column(Float)

class SkillGap(Base):
    __tablename__ = "skill_gaps"
    id = Column(Integer, primary_key=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))
    severity = Column(String)
    score = Column(Float)

class FollowUp(Base):
    __tablename__ = "followups"
    id = Column(Integer, primary_key=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"))
    due_date = Column(DateTime)
    kind = Column(String)
    status = Column(String)
    channel = Column(String)
    notes = Column(Text, default="")

    trainee = relationship("Trainee", foreign_keys=[trainee_id])

class EmploymentVerification(Base):
    __tablename__ = "employment_verifications"
    id = Column(Integer, primary_key=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"))
    status = Column(String)
    source = Column(String)
    confidence = Column(Float)
    last_verified = Column(DateTime)
    evidence = Column(Text)

    trainee = relationship("Trainee", foreign_keys=[trainee_id])

class Consent(Base):
    __tablename__ = "consents"
    id = Column(Integer, primary_key=True)
    trainee_id = Column(Integer, ForeignKey("trainees.id"))
    employment_tracking = Column(Boolean)
    followup = Column(Boolean)
    analytics = Column(Boolean)
    revoked_at = Column(DateTime, nullable=True)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    priority = Column(String)
    title = Column(String)
    reason = Column(String)
    action = Column(String)
    status = Column(String)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    severity = Column(String)
    message = Column(String)
    target = Column(String)
    read = Column(Boolean, default=False)

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    target = Column(Integer)
    progress = Column(Integer)
    responses = Column(Integer)
    pending = Column(Integer)
    unreachable = Column(Integer)
    escalated = Column(Integer)
    status = Column(String)

class SessionRecord(Base):
    __tablename__ = "sessions"
    token = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)

def migrate_db():
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        cols = {col[1] for col in res}
        if "trainee_id" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN trainee_id INTEGER REFERENCES trainees(id)"))
        if "provider_id" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN provider_id INTEGER REFERENCES providers(id)"))
        if "district_id" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN district_id INTEGER REFERENCES districts(id)"))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()

migrate_db()

DISTRICTS = ["Pune","Nashik","Nagpur","Mumbai Suburban","Thane","Aurangabad","Kolhapur","Satara","Solapur","Ahmednagar","Nanded","Sangli","Amravati","Jalgaon","Raigad"]
PROVIDERS = ["Maharashtra Skill Hub","Pragati Training Trust","Udaan Skills Centre","TechForge Institute","Navnirman Academy","Sahyadri Skills","Yuva Kaushalya","Shakti Foundation","Digital Bharat Academy","Mitra Vocational Centre","FutureWorks","Aarohan Skills","Maharashtra ITI Network","SkillSpring","Gram Vikas Training"]
PROGRAMMES = ["PMKVY","State Skill Development","Apprenticeship Promotion","Digital Workforce","Green Jobs"]
COURSES = ["Advanced CNC Operator","PLC Programming","Industrial Robotics","AutoCAD Mechanical","Solar PV Maintenance","EV Diagnostics","Welding Fabrication","Digital Manufacturing","Electrician Technician","Machine Maintenance","Data Entry & Digital Office","Healthcare Assistant","Retail Operations","Logistics Associate","Beauty & Wellness","Construction Technician","Food Processing","Mobile Repair","Fitter Technician","Industrial Safety"]
SKILLS = ["CNC Programming","PLC Programming","Industrial Robotics","AutoCAD","Solar PV Maintenance","EV Diagnostics","Welding","Digital Manufacturing","Machine Maintenance","Electrical Troubleshooting"]
ROLES = ["CNC Operator","PLC Technician","Maintenance Technician","Production Associate","Electrical Technician","EV Service Technician","CAD Operator","Solar Technician","Machine Operator","Quality Technician"]

def hash_pw(pw):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), b"kaushal360-demo", 120000).hex()

def seed():
    db = SessionLocal()
    if db.query(User).count():
        db.close()
        return
    random.seed(36026135)
    for email, pw, role, name in [
        ("admin@kaushal360.demo", "admin123", "admin", "Programme Administrator"),
        ("provider@kaushal360.demo", "provider123", "provider", "Provider Manager"),
        ("pragati@kaushal360.demo", "pragati123", "provider", "Pragati Provider Manager"),
        ("officer@kaushal360.demo", "officer123", "officer", "Field Officer"),
        ("trainee@kaushal360.demo", "trainee123", "trainee", "Priya Sharma")]:
        db.add(User(email=email, password_hash=hash_pw(pw), role=role, name=name))
    districts = [District(name=x) for x in DISTRICTS]; db.add_all(districts)
    providers = [Provider(name=x, score=random.randint(66, 91)) for x in PROVIDERS]; db.add_all(providers)
    programmes = [Programme(name=x) for x in PROGRAMMES]; db.add_all(programmes)
    db.flush()
    courses = []
    for i, name in enumerate(COURSES):
        courses.append(Course(name=name, programme_id=programmes[i % len(programmes)].id, provider_id=providers[i % len(providers)].id, duration_weeks=random.choice([8, 12, 16, 20])))
    db.add_all(courses)
    employers = []
    sectors = ["Manufacturing","Energy","Automotive","Construction","Healthcare","Logistics","Retail","IT Services"]
    for i in range(110):
        employers.append(Employer(name=f"{random.choice(['Apex','Pragati','Shree','Nova','Sahyadri','Prime','Metro','Bharat'])} {random.choice(['Industries','Engineering','Solutions','Works','Services','Manufacturing'])} {i+1}", district_id=districts[i % 15].id, sector=random.choice(sectors)))
    db.add_all(employers); db.flush()
    skills = []
    for s in SKILLS:
        skills.append(Skill(name=s, demand=random.uniform(60, 95), certified=random.uniform(45, 80), required=random.uniform(65, 98)))
    db.add_all(skills); db.flush()
    now = datetime.now()
    trainees = []
    names = ["Priya Sharma","Rahul Patil","Sneha Deshmukh","Amit Jadhav","Neha Kulkarni","Rohit Pawar","Anjali More","Vikas Shinde","Pooja Gaikwad","Suresh Chavan"]
    statuses = ["EMPLOYED","EMPLOYED","EMPLOYED","SEEKING","SELF_EMPLOYED","APPRENTICE","EMPLOYED","UNREACHABLE"]
    reasons = ["Skill mismatch","Location constraints","Salary mismatch","Insufficient openings","Further education","Personal reasons","Lack of interview opportunities","Employer demand reduction","Trainee unreachable"]
    for i in range(1200):
        course = courses[i % len(courses)]; provider = providers[(course.provider_id - 1) % len(providers)]
        enrolled = now - timedelta(days=random.randint(180, 900))
        completed = enrolled + timedelta(days=course.duration_weeks * 7)
        certified = random.random() < 0.9
        status = random.choice(statuses)
        emp = None if status not in ["EMPLOYED","APPRENTICE"] else random.choice(employers)
        salary = random.randint(13000, 32000) if status == "EMPLOYED" else (random.randint(9000, 18000) if status == "APPRENTICE" else None)
        t = Trainee(
            trainee_id=f"K360-{i+1:05d}",
            name=f"{random.choice(names)} {random.randint(1,99)}",
            age=random.randint(18, 45), gender=random.choice(["Female","Male","Other"]),
            district_id=districts[i % 15].id, location=f"{districts[i % 15].name}, Maharashtra",
            language=random.choice(["Marathi","Hindi","English"]), education=random.choice(["10th","12th","ITI","Diploma","Graduate"]),
            urban_rural=random.choice(["Urban","Rural"]), contact_status=random.choice(["Active","Active","Active","Changed"]),
            course_id=course.id, provider_id=provider.id, programme_id=course.programme_id,
            batch=f"2025-{(i % 8) + 1}", enrolled_at=enrolled, completed_at=completed,
            certified=certified, attendance=random.uniform(72, 99), assessment=random.uniform(54, 96),
            employment_status=status, employer_id=emp.id if emp else None,
            job_role=random.choice(ROLES), joining_date=completed + timedelta(days=random.randint(10, 80)) if emp else None,
            salary=salary, employment_type=random.choice(["Full-time","Contract","Apprenticeship"]) if emp else None,
            relevance=random.uniform(48, 98), source=random.choice(["Trainee Self-Report","Provider Update","Employer Report"]),
            verification=random.choice(["Verified","Verified","Partially Verified","Pending","Unverified"]),
            confidence=random.uniform(0.55, 0.98), consent=random.random() > 0.04,
            consent_updated=now - timedelta(days=random.randint(1, 300)),
            nonplacement_reason=random.choice(reasons) if status in ["SEEKING","UNREACHABLE"] else None,
            retention_3=(random.random() < .91) if emp else False,
            retention_6=(random.random() < .84) if emp else False,
            retention_12=(random.random() < .72) if emp else False
        )
        trainees.append(t)
    db.add_all(trainees); db.flush()
    for t in trainees:
        if t.salary:
            base = t.salary
            for months, mult in [(0, .78), (3, .86), (6, .94), (12, 1.0)]:
                db.add(SalaryRecord(trainee_id=t.id, month=f"M{months}", salary=round(base * mult)))
        if random.random() < .65:
            sk = skills[random.randrange(len(skills))]
            gap = max(0, sk.required - sk.certified + random.uniform(-10, 15))
            sev = "HIGH" if gap > 25 else "MEDIUM" if gap > 12 else "LOW"
            db.add(SkillGap(trainee_id=t.id, skill_id=sk.id, severity=sev, score=round(gap, 1)))
        if t.consent:
            db.add(Consent(trainee_id=t.id, employment_tracking=True, followup=True, analytics=True))
        if t.employment_status in ["EMPLOYED","APPRENTICE"]:
            db.add(EmploymentVerification(trainee_id=t.id, status=t.verification, source=t.source, confidence=t.confidence, last_verified=now - timedelta(days=random.randint(1, 90)), evidence="Trainee declaration + provider record" if t.verification != "Verified" else "Trainee declaration + employer confirmation"))
        due = now + timedelta(days=random.randint(-10, 20))
        db.add(FollowUp(trainee_id=t.id, due_date=due, kind=random.choice(["3-month","6-month","12-month"]), status=random.choice(["Pending","Pending","Completed","Unreachable"]), channel=random.choice(["WhatsApp","SMS","Phone Call","Field Officer"])))
    db.add_all([
        Recommendation(priority="HIGH", title="Add advanced PLC module to the next training cycle.", reason="PLC Programming shows a high gap between certified proficiency and employment requirements.", action="Create Improvement Plan", status="Open"),
        Recommendation(priority="MEDIUM", title="Launch retention follow-up for Provider B graduates.", reason="6-month retention is below the programme benchmark in the affected cohort.", action="Launch Campaign", status="Open"),
        Recommendation(priority="MEDIUM", title="Review salary expectations for selected cohorts.", reason="Salary mismatch is a recurring non-placement reason.", action="View Evidence", status="Open")
    ])
    db.add_all([
        Notification(severity="HIGH", message="6-month retention falling in Advanced CNC cohort.", target="analytics/retention"),
        Notification(severity="MEDIUM", message="12 employment records require verification.", target="employment"),
        Notification(severity="WARNING", message="27 trainees are currently unreachable.", target="followups"),
        Notification(severity="INSIGHT", message="Wage progression is improving for advanced PLC skills.", target="wages")
    ])
    db.add(Campaign(name="6-Month Employment Outcome Survey", target=2450, progress=1734, responses=1421, pending=313, unreachable=86, escalated=42, status="Ready"))
    db.commit(); db.close()

def link_demo_users():
    db = SessionLocal()
    try:
        admin = db.query(User).filter_by(email="admin@kaushal360.demo").first()
        if admin:
            admin.trainee_id = None
            admin.provider_id = None
            admin.district_id = None

        provider_u = db.query(User).filter_by(email="provider@kaushal360.demo").first()
        if provider_u:
            provider_u.provider_id = 1  # Maharashtra Skill Hub
            provider_u.district_id = None
            provider_u.trainee_id = None

        pragati_u = db.query(User).filter_by(email="pragati@kaushal360.demo").first()
        if not pragati_u:
            pragati_u = User(
                email="pragati@kaushal360.demo",
                password_hash=hash_pw("pragati123"),
                role="provider",
                name="Pragati Provider Manager",
                provider_id=2,  # Pragati Training Trust
                district_id=None,
                trainee_id=None
            )
            db.add(pragati_u)
        else:
            pragati_u.provider_id = 2
            pragati_u.role = "provider"

        officer_u = db.query(User).filter_by(email="officer@kaushal360.demo").first()
        if officer_u:
            officer_u.district_id = 1  # Pune
            officer_u.provider_id = None
            officer_u.trainee_id = None

        trainee_u = db.query(User).filter_by(email="trainee@kaushal360.demo").first()
        if trainee_u:
            trainee_u.trainee_id = 1
            trainee_u.provider_id = 1
            trainee_u.district_id = 1

        t1 = db.get(Trainee, 1)
        if t1:
            t1.name = "Priya Sharma"
            t1.gender = "Female"
            t1.district_id = 1
            t1.provider_id = 1
            t1.course_id = 1
            t1.employment_status = "EMPLOYED"
            t1.job_role = "CNC Operator"
            t1.salary = 24500.0
            t1.employer_id = 1
            t1.verification = "Verified"
            t1.confidence = 0.96
            t1.certified = True
            t1.retention_3 = True
            t1.retention_6 = True
            t1.retention_12 = True
            t1.consent = True

            sal_cnt = db.query(SalaryRecord).filter_by(trainee_id=1).count()
            if not sal_cnt:
                db.add_all([
                    SalaryRecord(trainee_id=1, month="M0", salary=19000.0),
                    SalaryRecord(trainee_id=1, month="M3", salary=21000.0),
                    SalaryRecord(trainee_id=1, month="M6", salary=22800.0),
                    SalaryRecord(trainee_id=1, month="M12", salary=24500.0),
                ])
            fu_cnt = db.query(FollowUp).filter_by(trainee_id=1).count()
            if not fu_cnt:
                now = datetime.now()
                db.add_all([
                    FollowUp(trainee_id=1, due_date=now - timedelta(days=90), kind="3-month", status="Completed", channel="WhatsApp", notes="Trainee confirmed full-time CNC role"),
                    FollowUp(trainee_id=1, due_date=now - timedelta(days=10), kind="6-month", status="Completed", channel="Field Officer", notes="Verified on-site at Apex Industries"),
                    FollowUp(trainee_id=1, due_date=now + timedelta(days=80), kind="12-month", status="Pending", channel="WhatsApp", notes="Upcoming 12-month review")
                ])

        # Trainee 2: Anjali More (Pragati Training Trust, provider_id=2)
        t2 = db.get(Trainee, 2)
        if t2:
            t2.name = "Anjali More"
            t2.gender = "Female"
            t2.provider_id = 2  # Pragati Training Trust
            t2.district_id = 2  # Nashik
            t2.course_id = 2    # PLC Programming
            t2.employment_status = "EMPLOYED"
            t2.job_role = "PLC Automation Technician"
            t2.salary = 28000.0
            t2.verification = "Verified"
            t2.confidence = 0.95
            t2.certified = True
            t2.retention_3 = True
            t2.retention_6 = True
            t2.retention_12 = True
            t2.consent = True

        # Trainee 17: Nikhil Joshi (Pragati Training Trust, provider_id=2)
        t17 = db.get(Trainee, 17)
        if t17:
            t17.name = "Nikhil Joshi"
            t17.gender = "Male"
            t17.provider_id = 2  # Pragati Training Trust
            t17.district_id = 2  # Nashik
            t17.course_id = 2    # PLC Programming
            t17.employment_status = "EMPLOYED"
            t17.job_role = "Junior PLC Programmer"
            t17.salary = 26500.0
            t17.verification = "Verified"
            t17.confidence = 0.92
            t17.certified = True
            t17.retention_3 = True
            t17.retention_6 = True
            t17.consent = True

        # Trainee 22: Kavita Desai (Pragati Training Trust, provider_id=2)
        t22 = db.get(Trainee, 22)
        if t22:
            t22.name = "Kavita Desai"
            t22.gender = "Female"
            t22.provider_id = 2  # Pragati Training Trust
            t22.district_id = 7  # Kolhapur
            t22.course_id = 5    # Solar PV Maintenance
            t22.employment_status = "SELF_EMPLOYED"
            t22.job_role = "Solar PV Technician"
            t22.salary = 24000.0
            t22.verification = "Verified"
            t22.confidence = 0.90
            t22.certified = True
            t22.retention_3 = True
            t22.retention_6 = True
            t22.consent = True
        db.commit()
    finally:
        db.close()

seed()
link_demo_users()

app = FastAPI(title="KAUSHAL360 API")
app.mount("/static", StaticFiles(directory=str(BASE/"static")), name="static")

SESSIONS = {}

def get_current_user(authorization: str | None = Header(None), token: str | None = Query(None)) -> User:
    raw_token = None
    if isinstance(authorization, str) and authorization.strip().lower().startswith("bearer "):
        raw_token = authorization.strip().split(" ", 1)[1].strip()
    elif isinstance(token, str) and token.strip():
        raw_token = token.strip()

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in."
        )

    db = SessionLocal()
    try:
        rec = db.query(SessionRecord).filter_by(token=raw_token).first()
        if not rec:
            SESSIONS.pop(raw_token, None)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session invalid or expired. Please sign in again."
            )

        uid = rec.user_id
        SESSIONS[raw_token] = uid

        u = db.query(User).options(
            joinedload(User.trainee),
            joinedload(User.provider),
            joinedload(User.district)
        ).get(uid)

        if not u:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not found."
            )
        return u
    finally:
        db.close()

def require_role(user: User, allowed_roles: list[str]):
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: role '{user.role}' lacks permission for this action. Allowed: {allowed_roles}"
        )

class LoginIn(BaseModel):
    email: str
    password: str

class FollowUpIn(BaseModel):
    status: str
    notes: str = ""
    employer: str | None = None
    salary: float | None = None
    relevant: bool | None = None

class ConsentIn(BaseModel):
    employment_tracking: bool = True
    followup: bool = True
    analytics: bool = True

class VerifyIn(BaseModel):
    status: str

class TraineeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    trainee_id: str | None = None
    age: int | None = 22
    gender: str | None = "Other"
    district_id: int
    location: str | None = None
    language: str | None = "Marathi"
    education: str | None = "10th"
    urban_rural: str | None = "Rural"
    course_id: int
    provider_id: int
    programme_id: int | None = None
    batch: str | None = "2026-1"
    attendance: float | None = 85.0
    assessment: float | None = 75.0
    certified: bool = True
    employment_status: str = "SEEKING"
    employer_id: int | None = None
    job_role: str | None = None
    salary: float | None = None
    employment_type: str | None = None
    relevance: float | None = 70.0
    source: str | None = "Trainee Self-Report"
    verification: str | None = "Pending"
    consent: bool = True

@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse(BASE/"static/index.html")

@app.post("/api/login")
def login(data: LoginIn):
    db = SessionLocal()
    try:
        u = db.query(User).filter_by(email=data.email.strip().lower()).first()
        if not u or not secrets.compare_digest(u.password_hash, hash_pw(data.password)):
            raise HTTPException(401, "Invalid demo credentials")
        token = secrets.token_urlsafe(32)
        SESSIONS[token] = u.id

        rec = SessionRecord(token=token, user_id=u.id)
        db.add(rec)
        db.commit()

        return {
            "token": token,
            "role": u.role,
            "name": u.name,
            "email": u.email,
            "trainee_id": u.trainee_id,
            "provider_id": u.provider_id,
            "district_id": u.district_id
        }
    finally:
        db.close()

@app.post("/api/logout")
def logout(authorization: str | None = Header(None), token: str | None = Query(None), user: User = Depends(get_current_user)):
    raw_token = None
    if isinstance(authorization, str) and authorization.strip().lower().startswith("bearer "):
        raw_token = authorization.strip().split(" ", 1)[1].strip()
    elif isinstance(token, str) and token.strip():
        raw_token = token.strip()

    db = SessionLocal()
    try:
        if raw_token:
            SESSIONS.pop(raw_token, None)
            db.query(SessionRecord).filter_by(token=raw_token).delete()
            db.commit()
        return {"success": True, "message": "Session invalidated successfully"}
    finally:
        db.close()

@app.get("/api/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "role": user.role,
        "name": user.name,
        "email": user.email,
        "trainee_id": user.trainee_id,
        "provider_id": user.provider_id,
        "district_id": user.district_id,
        "provider_name": user.provider.name if user.provider else None,
        "district_name": user.district.name if user.district else None,
        "trainee_code": user.trainee.trainee_id if user.trainee else None
    }

def apply_trainee_filters(q, user: User, district: str | None = None, provider: str | None = None, course: str | None = None):
    # 1. Role-based scoping
    if user.role == "provider":
        prov_name = user.provider.name if user.provider else ""
        if provider and provider != prov_name and provider != str(user.provider_id):
            raise HTTPException(403, "Access forbidden: Providers can only view their own institute's data")
        q = q.filter(Trainee.provider_id == user.provider_id)
    elif user.role == "officer":
        dist_name = user.district.name if user.district else ""
        if district and district != dist_name and district != str(user.district_id):
            raise HTTPException(403, "Access forbidden: Field officers can only view their assigned district data")
        q = q.filter(Trainee.district_id == user.district_id)
    elif user.role == "trainee":
        q = q.filter(Trainee.id == user.trainee_id)

    # 2. Filter application
    if district and user.role != "officer":
        if str(district).isdigit():
            q = q.filter(Trainee.district_id == int(district))
        else:
            q = q.join(District, Trainee.district_id == District.id).filter(District.name == district)
    if provider and user.role != "provider":
        if str(provider).isdigit():
            q = q.filter(Trainee.provider_id == int(provider))
        else:
            q = q.join(Provider, Trainee.provider_id == Provider.id).filter(Provider.name == provider)
    if course:
        if str(course).isdigit():
            q = q.filter(Trainee.course_id == int(course))
        else:
            q = q.join(Course, Trainee.course_id == Course.id).filter(Course.name == course)
    return q

@app.get("/api/dashboard")
def dashboard(
    district: str | None = None,
    provider: str | None = None,
    course: str | None = None,
    user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        q = db.query(Trainee)
        q = apply_trainee_filters(q, user, district, provider, course)

        ts = q.all()
        total = len(ts)
        certified = sum(1 for x in ts if x.certified)
        placed = sum(1 for x in ts if x.employment_status in ["EMPLOYED", "APPRENTICE", "SELF_EMPLOYED"])
        employed = sum(1 for x in ts if x.employment_status == "EMPLOYED")
        ret = sum(1 for x in ts if x.employment_status == "EMPLOYED" and x.retention_6)
        wages = [x.salary for x in ts if x.salary]
        avg = round(statistics.mean(wages)) if wages else 0
        verified = sum(1 for x in ts if x.verification == "Verified")

        # 3. Accurate wage growth via SalaryRecord table (M0 to M12)
        growth = 0.0
        trainee_ids = [x.id for x in ts if x.salary]
        if trainee_ids:
            sal_rows = db.query(SalaryRecord.trainee_id, SalaryRecord.month, SalaryRecord.salary).filter(
                SalaryRecord.trainee_id.in_(trainee_ids),
                SalaryRecord.month.in_(["M0", "M12"])
            ).all()
            trainee_m0 = {}
            trainee_m12 = {}
            for tid, month, sal in sal_rows:
                if month == "M0": trainee_m0[tid] = sal
                elif month == "M12": trainee_m12[tid] = sal
            
            paired_m0 = [trainee_m0[tid] for tid in trainee_m0 if tid in trainee_m12]
            paired_m12 = [trainee_m12[tid] for tid in trainee_m0 if tid in trainee_m12]
            if paired_m0 and paired_m12 and statistics.mean(paired_m0) > 0:
                growth = round((statistics.mean(paired_m12) / statistics.mean(paired_m0) - 1) * 100, 1)
            elif trainee_m0 and trainee_m12 and statistics.mean(trainee_m0.values()) > 0:
                growth = round((statistics.mean(trainee_m12.values()) / statistics.mean(trainee_m0.values()) - 1) * 100, 1)

        return {
            "total": total,
            "certified": certified,
            "placement_rate": round(placed / total * 100, 1) if total else 0.0,
            "employment_rate": round(employed / total * 100, 1) if total else 0.0,
            "retention_6": round(ret / employed * 100, 1) if employed else 0.0,
            "avg_wage": avg,
            "wage_growth": growth,
            "verified": verified,
            "filtered_by": {
                "district": district or (user.district.name if user.district else None),
                "provider": provider or (user.provider.name if user.provider else None),
                "course": course
            }
        }
    finally:
        db.close()

@app.get("/api/trainees")
def trainees(
    search: str = "",
    limit: int = 50,
    user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        q = db.query(Trainee).options(
            joinedload(Trainee.district),
            joinedload(Trainee.provider),
            joinedload(Trainee.course)
        )

        # Scoping
        if user.role == "provider":
            q = q.filter(Trainee.provider_id == user.provider_id)
        elif user.role == "officer":
            q = q.filter(Trainee.district_id == user.district_id)
        elif user.role == "trainee":
            q = q.filter(Trainee.id == user.trainee_id)

        if search:
            like = f"%{search}%"
            q = q.filter(or_(Trainee.name.ilike(like), Trainee.trainee_id.ilike(like)))

        rows = q.limit(limit).all()
        out = []
        for t in rows:
            out.append({
                "id": t.id,
                "trainee_id": t.trainee_id,
                "name": t.name,
                "district": t.district.name if t.district else "—",
                "provider": t.provider.name if t.provider else "—",
                "course": t.course.name if t.course else "—",
                "status": t.employment_status,
                "salary": t.salary,
                "verification": t.verification,
                "consent": t.consent
            })
        return out
    finally:
        db.close()

@app.get("/api/trainees/{tid}")
def trainee(tid: int, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        t = db.query(Trainee).options(
            joinedload(Trainee.district),
            joinedload(Trainee.provider),
            joinedload(Trainee.course),
            joinedload(Trainee.programme),
            joinedload(Trainee.employer)
        ).filter(Trainee.id == tid).first()

        if not t:
            raise HTTPException(404, "Trainee not found")

        # Authorization checks
        if user.role == "trainee" and t.id != user.trainee_id:
            raise HTTPException(403, "Access forbidden: You can only view your own trainee profile")
        elif user.role == "provider" and t.provider_id != user.provider_id:
            raise HTTPException(403, "Access forbidden: You can only view trainees from your training institute")
        elif user.role == "officer" and t.district_id != user.district_id:
            raise HTTPException(403, "Access forbidden: You can only view trainees within your assigned district")

        sal = db.query(SalaryRecord).filter_by(trainee_id=t.id).order_by(SalaryRecord.id).all()
        fus = db.query(FollowUp).filter_by(trainee_id=t.id).order_by(FollowUp.due_date).all()
        ev = db.query(EmploymentVerification).filter_by(trainee_id=t.id).order_by(EmploymentVerification.id.desc()).first()

        return {
            "id": t.id,
            "trainee_id": t.trainee_id,
            "name": t.name,
            "age": t.age,
            "gender": t.gender,
            "district": t.district.name if t.district else "—",
            "location": t.location,
            "language": t.language,
            "education": t.education,
            "urban_rural": t.urban_rural,
            "contact_status": t.contact_status,
            "course": t.course.name if t.course else "—",
            "provider": t.provider.name if t.provider else "—",
            "programme": t.programme.name if t.programme else "—",
            "batch": t.batch,
            "enrolled_at": t.enrolled_at.isoformat() if t.enrolled_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "attendance": round(t.attendance, 1) if t.attendance is not None else 0.0,
            "assessment": round(t.assessment, 1) if t.assessment is not None else 0.0,
            "certified": t.certified,
            "employment_status": t.employment_status,
            "employer": t.employer.name if t.employer else None,
            "job_role": t.job_role,
            "joining_date": t.joining_date.isoformat() if t.joining_date else None,
            "salary": t.salary,
            "employment_type": t.employment_type,
            "relevance": round(t.relevance, 1) if t.relevance is not None else 0.0,
            "source": t.source,
            "verification": t.verification,
            "confidence": round(t.confidence * 100) if t.confidence is not None else 0,
            "consent": t.consent,
            "consent_updated": t.consent_updated.isoformat() if t.consent_updated else None,
            "retention_3": t.retention_3,
            "retention_6": t.retention_6,
            "retention_12": t.retention_12,
            "salary_history": [{"month": x.month, "salary": x.salary} for x in sal],
            "followups": [{"id": x.id, "due": x.due_date.isoformat(), "kind": x.kind, "status": x.status, "channel": x.channel, "notes": x.notes} for x in fus],
            "verification_record": {
                "status": ev.status,
                "source": ev.source,
                "confidence": round(ev.confidence * 100),
                "last_verified": ev.last_verified.isoformat(),
                "evidence": ev.evidence
            } if ev else None
        }
    finally:
        db.close()

@app.post("/api/trainees", status_code=status.HTTP_201_CREATED)
def create_trainee(data: TraineeCreate, user: User = Depends(get_current_user)):
    require_role(user, ["admin", "provider", "officer"])
    db = SessionLocal()
    try:
        # Provider role must only create for their provider
        if user.role == "provider":
            if data.provider_id != user.provider_id:
                raise HTTPException(403, "Providers can only register trainees under their own institute")
        elif user.role == "officer":
            if data.district_id != user.district_id:
                raise HTTPException(403, "Field officers can only register trainees in their assigned district")

        # Validate existence of foreign keys
        district = db.get(District, data.district_id)
        if not district:
            raise HTTPException(400, f"District ID {data.district_id} does not exist")

        provider = db.get(Provider, data.provider_id)
        if not provider:
            raise HTTPException(400, f"Provider ID {data.provider_id} does not exist")

        course = db.get(Course, data.course_id)
        if not course:
            raise HTTPException(400, f"Course ID {data.course_id} does not exist")

        # Validate that course belongs to the provider
        if course.provider_id != data.provider_id:
            raise HTTPException(400, f"Course '{course.name}' belongs to Provider ID {course.provider_id}, not Provider ID {data.provider_id}")

        programme_id = data.programme_id or course.programme_id
        if data.employer_id:
            emp = db.get(Employer, data.employer_id)
            if not emp:
                raise HTTPException(400, f"Employer ID {data.employer_id} does not exist")

        # Unique trainee_id validation or generation
        if data.trainee_id:
            existing = db.query(Trainee).filter_by(trainee_id=data.trainee_id.strip()).first()
            if existing:
                raise HTTPException(400, f"Trainee ID '{data.trainee_id}' already exists")
            tid_code = data.trainee_id.strip()
        else:
            max_id = db.query(func.max(Trainee.id)).scalar() or 0
            candidate = max_id + 1
            while db.query(Trainee).filter_by(trainee_id=f"K360-{candidate:05d}").first():
                candidate += 1
            tid_code = f"K360-{candidate:05d}"

        now = datetime.now()
        enrolled = now - timedelta(days=course.duration_weeks * 7 + 30)
        completed = now - timedelta(days=30)
        is_emp = data.employment_status in ["EMPLOYED", "APPRENTICE"]
        source_val = data.source or ("Provider Update" if user.role == "provider" else ("Field Verification" if user.role == "officer" else "Administrative Entry"))

        new_t = Trainee(
            trainee_id=tid_code,
            name=data.name.strip(),
            age=data.age or 22,
            gender=data.gender or "Other",
            district_id=data.district_id,
            location=data.location or f"{district.name}, Maharashtra",
            language=data.language or "Marathi",
            education=data.education or "10th",
            urban_rural=data.urban_rural or "Rural",
            contact_status="Active",
            course_id=data.course_id,
            provider_id=data.provider_id,
            programme_id=programme_id,
            batch=data.batch or "2026-1",
            enrolled_at=enrolled,
            completed_at=completed,
            certified=data.certified,
            attendance=data.attendance or 85.0,
            assessment=data.assessment or 75.0,
            employment_status=data.employment_status,
            employer_id=data.employer_id,
            job_role=data.job_role or ("Trainee Operator" if is_emp else None),
            joining_date=now - timedelta(days=15) if is_emp else None,
            salary=data.salary,
            employment_type=data.employment_type or ("Full-time" if is_emp else None),
            relevance=data.relevance or 75.0,
            source=source_val,
            verification=data.verification or ("Verified" if is_emp else "Pending"),
            confidence=0.88 if is_emp else 0.60,
            consent=data.consent,
            consent_updated=now,
            retention_3=True if is_emp else False,
            retention_6=False,
            retention_12=False
        )
        db.add(new_t)
        db.flush()

        # Associated records
        if data.salary:
            db.add(SalaryRecord(trainee_id=new_t.id, month="M0", salary=data.salary))
        if data.consent:
            db.add(Consent(trainee_id=new_t.id, employment_tracking=True, followup=True, analytics=True))
        if is_emp:
            db.add(EmploymentVerification(
                trainee_id=new_t.id,
                status=new_t.verification,
                source=new_t.source,
                confidence=new_t.confidence,
                last_verified=now,
                evidence=f"{source_val} registration declaration"
            ))

        # Initial longitudinal follow-up schedule
        db.add_all([
            FollowUp(trainee_id=new_t.id, due_date=now + timedelta(days=60), kind="3-month", status="Pending", channel="WhatsApp", notes="Automated digital intake follow-up"),
            FollowUp(trainee_id=new_t.id, due_date=now + timedelta(days=150), kind="6-month", status="Pending", channel="Field Officer", notes="Assisted field follow-up scheduled"),
            FollowUp(trainee_id=new_t.id, due_date=now + timedelta(days=330), kind="12-month", status="Pending", channel="WhatsApp", notes="Annual longitudinal review scheduled")
        ])

        db.commit()
        return {
            "success": True,
            "id": new_t.id,
            "trainee_id": new_t.trainee_id,
            "name": new_t.name,
            "district": district.name,
            "provider": provider.name,
            "course": course.name,
            "status": new_t.employment_status,
            "salary": new_t.salary,
            "verification": new_t.verification
        }
    finally:
        db.close()

@app.post("/api/trainees/{tid}/consent")
def consent(tid: int, data: ConsentIn, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        t = db.get(Trainee, tid)
        if not t:
            raise HTTPException(404, "Trainee not found")

        # Authorization
        if user.role == "trainee" and t.id != user.trainee_id:
            raise HTTPException(403, "You can only manage your own consent preferences")
        elif user.role == "officer" and t.district_id != user.district_id:
            raise HTTPException(403, "Field officers can only update consent for trainees in their district")
        elif user.role == "provider":
            raise HTTPException(403, "Training providers cannot unilaterally alter trainee consent")

        t.consent = data.employment_tracking or data.followup or data.analytics
        t.consent_updated = datetime.now()
        c = db.query(Consent).filter_by(trainee_id=tid).first()
        if not c:
            c = Consent(trainee_id=tid)
            db.add(c)
        c.employment_tracking = data.employment_tracking
        c.followup = data.followup
        c.analytics = data.analytics
        c.revoked_at = None if t.consent else datetime.now()
        db.commit()
        return {"success": True, "consent": t.consent}
    finally:
        db.close()

@app.post("/api/followups/{fid}/complete")
def complete_followup(fid: int, data: FollowUpIn, user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        f = db.get(FollowUp, fid)
        if not f:
            raise HTTPException(404, "Follow-up not found")
        t = db.get(Trainee, f.trainee_id)

        # Authorization
        if user.role == "trainee" and t.id != user.trainee_id:
            raise HTTPException(403, "You can only complete your own follow-up survey")
        elif user.role == "officer" and t.district_id != user.district_id:
            raise HTTPException(403, "Field officers can only conduct follow-ups for their assigned district")
        elif user.role == "provider":
            raise HTTPException(403, "Training providers cannot conduct or complete field follow-ups")

        if not t.consent:
            raise HTTPException(403, "Consent revoked by trainee; follow-up disabled under DPDP guidelines")

        f.status = data.status
        f.notes = data.notes
        if data.status == "Completed":
            if f.kind == "6-month" and t.employment_status == "EMPLOYED":
                t.retention_6 = True
            elif f.kind == "12-month" and t.employment_status == "EMPLOYED":
                t.retention_12 = True
            elif f.kind == "3-month" and t.employment_status == "EMPLOYED":
                t.retention_3 = True

            if data.salary is not None:
                t.salary = data.salary
                # Append or update salary record
                sal_m = "M6" if f.kind == "6-month" else ("M12" if f.kind == "12-month" else "M3")
                existing_sal = db.query(SalaryRecord).filter_by(trainee_id=t.id, month=sal_m).first()
                if existing_sal:
                    existing_sal.salary = data.salary
                else:
                    db.add(SalaryRecord(trainee_id=t.id, month=sal_m, salary=data.salary))
            if data.relevant is not None:
                t.relevance = 100.0 if data.relevant else 45.0

        db.commit()
        return {"success": True, "followup_id": f.id, "status": f.status}
    finally:
        db.close()

@app.get("/api/employment")
def employment(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        q = db.query(Trainee).options(
            joinedload(Trainee.employer)
        ).filter(Trainee.employment_status.in_(["EMPLOYED", "APPRENTICE"]))

        if user.role == "provider":
            q = q.filter(Trainee.provider_id == user.provider_id)
        elif user.role == "officer":
            q = q.filter(Trainee.district_id == user.district_id)
        elif user.role == "trainee":
            q = q.filter(Trainee.id == user.trainee_id)

        rows = q.limit(80).all()
        out = []
        for t in rows:
            out.append({
                "id": t.id,
                "trainee": t.name,
                "employer": t.employer.name if t.employer else "—",
                "role": t.job_role or "—",
                "salary": t.salary,
                "joining": t.joining_date.strftime("%d %b %Y") if t.joining_date else "—",
                "source": t.source,
                "verification": t.verification,
                "confidence": round(t.confidence * 100) if t.confidence else 0
            })
        return out
    finally:
        db.close()

@app.post("/api/employment/{tid}/verify")
def verify(tid: int, data: VerifyIn, user: User = Depends(get_current_user)):
    require_role(user, ["admin", "officer", "provider"])
    db = SessionLocal()
    try:
        t = db.get(Trainee, tid)
        if not t:
            raise HTTPException(404, "Trainee not found")

        if user.role == "officer" and t.district_id != user.district_id:
            raise HTTPException(403, "Field officers can only verify employment records in their district")
        elif user.role == "provider" and t.provider_id != user.provider_id:
            raise HTTPException(403, "Providers can only verify placement records for their graduates")

        t.verification = data.status
        t.confidence = 0.96 if data.status == "Verified" else 0.65
        ev = db.query(EmploymentVerification).filter_by(trainee_id=tid).order_by(EmploymentVerification.id.desc()).first()
        if ev:
            ev.status = data.status
            ev.confidence = t.confidence
            ev.last_verified = datetime.now()
        else:
            db.add(EmploymentVerification(
                trainee_id=tid,
                status=data.status,
                source=f"{user.role.title()} Verification",
                confidence=t.confidence,
                last_verified=datetime.now(),
                evidence=f"Verified by {user.name} ({user.role})"
            ))
        db.commit()
        return {"success": True, "status": data.status, "confidence": t.confidence}
    finally:
        db.close()

@app.get("/api/followups")
def followups(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        q = db.query(FollowUp).options(
            joinedload(FollowUp.trainee)
        ).join(Trainee, FollowUp.trainee_id == Trainee.id)

        if user.role == "provider":
            q = q.filter(Trainee.provider_id == user.provider_id)
        elif user.role == "officer":
            q = q.filter(Trainee.district_id == user.district_id)
        elif user.role == "trainee":
            q = q.filter(Trainee.id == user.trainee_id)

        rows = q.order_by(FollowUp.due_date).limit(100).all()
        out = []
        for f in rows:
            out.append({
                "id": f.id,
                "trainee_id": f.trainee.id,
                "trainee": f.trainee.name,
                "kind": f.kind,
                "due": f.due_date.strftime("%d %b %Y"),
                "status": f.status,
                "channel": f.channel,
                "notes": f.notes
            })
        return out
    finally:
        db.close()

@app.get("/api/courses")
def courses(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        cq = db.query(Course).options(
            joinedload(Course.programme),
            joinedload(Course.provider)
        )
        if user.role == "provider":
            cq = cq.filter(Course.provider_id == user.provider_id)
        course_list = cq.all()

        t_query = db.query(
            Trainee.course_id,
            Trainee.certified,
            Trainee.employment_status,
            Trainee.retention_6,
            Trainee.salary,
            Trainee.attendance,
            Trainee.assessment,
            Trainee.relevance
        )
        if user.role == "provider":
            t_query = t_query.filter(Trainee.provider_id == user.provider_id)
        elif user.role == "officer":
            t_query = t_query.filter(Trainee.district_id == user.district_id)
        elif user.role == "trainee":
            t_query = t_query.filter(Trainee.id == user.trainee_id)

        trainee_stats = {}
        for cid, cert, st_status, ret6, sal, att, assess, rel in t_query.all():
            st = trainee_stats.setdefault(cid, {
                "total": 0, "certified": 0, "placed": 0, "employed": 0, "retention_6": 0,
                "salaries": [], "attendances": [], "assessments": [], "relevances": []
            })
            st["total"] += 1
            if cert: st["certified"] += 1
            if st_status in ["EMPLOYED", "APPRENTICE", "SELF_EMPLOYED"]: st["placed"] += 1
            if st_status == "EMPLOYED":
                st["employed"] += 1
                if ret6: st["retention_6"] += 1
            if sal: st["salaries"].append(sal)
            if att: st["attendances"].append(att)
            if assess: st["assessments"].append(assess)
            if rel: st["relevances"].append(rel)

        out = []
        for c in course_list:
            st = trainee_stats.get(c.id, {
                "total": 0, "certified": 0, "placed": 0, "employed": 0, "retention_6": 0,
                "salaries": [], "attendances": [], "assessments": [], "relevances": []
            })
            tot = st["total"] or 1
            emp = st["employed"] or 1
            out.append({
                "id": c.id,
                "name": c.name,
                "programme": c.programme.name if c.programme else "General",
                "provider": c.provider.name if c.provider else "State Provider",
                "provider_id": c.provider_id,
                "duration_weeks": c.duration_weeks,
                "total_trainees": st["total"],
                "certified": st["certified"],
                "completion_rate": round(st["certified"] / tot * 100, 1),
                "placement_rate": round(st["placed"] / tot * 100, 1),
                "employment_rate": round(st["employed"] / tot * 100, 1),
                "retention_6_rate": round(st["retention_6"] / emp * 100, 1) if st["employed"] else 0.0,
                "avg_salary": round(statistics.mean(st["salaries"])) if st["salaries"] else 0,
                "avg_attendance": round(statistics.mean(st["attendances"]), 1) if st["attendances"] else 0.0,
                "avg_assessment": round(statistics.mean(st["assessments"]), 1) if st["assessments"] else 0.0,
                "avg_relevance": round(statistics.mean(st["relevances"]), 1) if st["relevances"] else 0.0
            })
        return sorted(out, key=lambda x: x["total_trainees"], reverse=True)
    finally:
        db.close()

@app.get("/api/skills")
def skills(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        rows = db.query(Skill).all()
        gap_q = db.query(
            SkillGap.skill_id,
            func.sum(func.case((SkillGap.severity == "HIGH", 1), else_=0)),
            func.sum(func.case((SkillGap.severity == "MEDIUM", 1), else_=0))
        )
        if user.role == "provider":
            gap_q = gap_q.join(Trainee, SkillGap.trainee_id == Trainee.id).filter(Trainee.provider_id == user.provider_id)
        elif user.role == "officer":
            gap_q = gap_q.join(Trainee, SkillGap.trainee_id == Trainee.id).filter(Trainee.district_id == user.district_id)
        elif user.role == "trainee":
            gap_q = gap_q.filter(SkillGap.trainee_id == user.trainee_id)

        gap_aggregates = dict(gap_q.group_by(SkillGap.skill_id).all())
        out = []
        for s in rows:
            gaps = gap_aggregates.get(s.id, (0, 0))
            high = gaps[0] or 0
            med = gaps[1] or 0
            out.append({
                "skill": s.name,
                "demand": round(s.demand),
                "certified": round(s.certified),
                "required": round(s.required),
                "gap": round(max(0, s.required - s.certified)),
                "high": high,
                "medium": med
            })
        return sorted(out, key=lambda x: x["gap"], reverse=True)
    finally:
        db.close()

@app.get("/api/providers")
def providers(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        pq = db.query(Provider)
        if user.role == "provider":
            pq = pq.filter(Provider.id == user.provider_id)
        elif user.role == "trainee":
            pq = pq.filter(Provider.id == user.provider_id)
        provs = pq.all()

        t_query = db.query(
            Trainee.provider_id,
            Trainee.certified,
            Trainee.employment_status,
            Trainee.retention_6,
            Trainee.salary,
            Trainee.verification
        )
        if user.role == "provider":
            t_query = t_query.filter(Trainee.provider_id == user.provider_id)
        elif user.role == "officer":
            t_query = t_query.filter(Trainee.district_id == user.district_id)
        elif user.role == "trainee":
            t_query = t_query.filter(Trainee.id == user.trainee_id)

        grouped = {}
        for pid, cert, emp_status, ret6, sal, ver in t_query.all():
            g = grouped.setdefault(pid, {"total": 0, "cert": 0, "placed": 0, "emp": 0, "ret": 0, "wages": [], "ver": 0})
            g["total"] += 1
            if cert: g["cert"] += 1
            if emp_status in ["EMPLOYED", "APPRENTICE", "SELF_EMPLOYED"]: g["placed"] += 1
            if emp_status == "EMPLOYED":
                g["emp"] += 1
                if ret6: g["ret"] += 1
                if sal: g["wages"].append(sal)
                if ver == "Verified": g["ver"] += 1

        out = []
        for p in provs:
            g = grouped.get(p.id, {"total": 0, "cert": 0, "placed": 0, "emp": 0, "ret": 0, "wages": [], "ver": 0})
            n = g["total"] or 1
            emp_cnt = g["emp"] or 1
            ret_rate = (g["ret"] / emp_cnt * 100) if g["emp"] else 0.0
            avg_wage = statistics.mean(g["wages"]) if g["wages"] else 0.0
            vr_rate = (g["ver"] / emp_cnt * 100) if g["emp"] else 0.0
            score = round(.35 * (g["placed"] / n * 100) + .25 * ret_rate + .2 * vr_rate + .2 * min(100, (avg_wage / 25000) * 100))

            out.append({
                "id": p.id,
                "provider": p.name,
                "trainees": g["total"],
                "completion": round(g["cert"] / n * 100, 1),
                "placement": round(g["placed"] / n * 100, 1),
                "employment": round(g["emp"] / n * 100, 1),
                "retention": round(ret_rate, 1),
                "wage": round(avg_wage),
                "verification": round(vr_rate, 1),
                "impact": score
            })
        return sorted(out, key=lambda x: x["impact"], reverse=True)
    finally:
        db.close()

@app.get("/api/districts")
def districts(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        dq = db.query(District)
        if user.role == "officer":
            dq = dq.filter(District.id == user.district_id)
        elif user.role == "trainee":
            dq = dq.filter(District.id == user.district_id)
        dists = dq.all()

        t_query = db.query(
            Trainee.district_id,
            Trainee.employment_status,
            Trainee.retention_6,
            Trainee.salary,
            Trainee.contact_status
        )
        if user.role == "provider":
            t_query = t_query.filter(Trainee.provider_id == user.provider_id)
        elif user.role == "officer":
            t_query = t_query.filter(Trainee.district_id == user.district_id)
        elif user.role == "trainee":
            t_query = t_query.filter(Trainee.id == user.trainee_id)

        grouped = {}
        for did, emp_status, ret6, sal, contact in t_query.all():
            g = grouped.setdefault(did, {"total": 0, "placed": 0, "emp": 0, "ret": 0, "wages": [], "unreachable": 0})
            g["total"] += 1
            if emp_status in ["EMPLOYED", "APPRENTICE", "SELF_EMPLOYED"]: g["placed"] += 1
            if emp_status == "EMPLOYED":
                g["emp"] += 1
                if ret6: g["ret"] += 1
                if sal: g["wages"].append(sal)
            if contact == "Changed" or emp_status == "UNREACHABLE":
                g["unreachable"] += 1

        out = []
        for d in dists:
            g = grouped.get(d.id, {"total": 0, "placed": 0, "emp": 0, "ret": 0, "wages": [], "unreachable": 0})
            n = g["total"] or 1
            emp_cnt = g["emp"] or 1
            ret_rate = (g["ret"] / emp_cnt * 100) if g["emp"] else 0.0
            avg_wage = statistics.mean(g["wages"]) if g["wages"] else 0.0
            out.append({
                "id": d.id,
                "district": d.name,
                "trainees": g["total"],
                "placement": round(g["placed"] / n * 100, 1),
                "employment": round(g["emp"] / n * 100, 1),
                "retention": round(ret_rate, 1),
                "wage": round(avg_wage),
                "unreachable": g["unreachable"]
            })
        return sorted(out, key=lambda x: x["placement"], reverse=True)
    finally:
        db.close()

@app.get("/api/analytics/nonplacement")
def nonplacement(
    district: str | None = None,
    provider: str | None = None,
    course: str | None = None,
    user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        q = db.query(Trainee.nonplacement_reason, func.count(Trainee.id)).filter(Trainee.nonplacement_reason != None)
        q = apply_trainee_filters(q, user, district, provider, course)
        rows = q.group_by(Trainee.nonplacement_reason).all()
        total = sum(x[1] for x in rows) or 1
        return [{"reason": r, "count": c, "percent": round(c / total * 100, 1)} for r, c in sorted(rows, key=lambda x: x[1], reverse=True)]
    finally:
        db.close()

@app.get("/api/analytics/retention")
def retention(
    district: str | None = None,
    provider: str | None = None,
    course: str | None = None,
    user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        q = db.query(Trainee).filter(Trainee.employment_status == "EMPLOYED")
        q = apply_trainee_filters(q, user, district, provider, course)
        emp = q.all()
        n = len(emp) or 1
        return [
            {"month": 0, "rate": 100.0 if emp else 0.0},
            {"month": 3, "rate": round(sum(t.retention_3 for t in emp) / n * 100, 1) if emp else 0.0},
            {"month": 6, "rate": round(sum(t.retention_6 for t in emp) / n * 100, 1) if emp else 0.0},
            {"month": 12, "rate": round(sum(t.retention_12 for t in emp) / n * 100, 1) if emp else 0.0}
        ]
    finally:
        db.close()

@app.get("/api/analytics/wages")
def wages(
    district: str | None = None,
    provider: str | None = None,
    course: str | None = None,
    user: User = Depends(get_current_user)
):
    db = SessionLocal()
    try:
        q = db.query(Trainee.id).filter(Trainee.salary != None)
        q = apply_trainee_filters(q, user, district, provider, course)
        tids = [r[0] for r in q.all()]
        if not tids:
            return [{"month": "M0", "avg": 0}, {"month": "M3", "avg": 0}, {"month": "M6", "avg": 0}, {"month": "M12", "avg": 0}]

        rows = db.query(SalaryRecord.month, func.avg(SalaryRecord.salary)).filter(
            SalaryRecord.trainee_id.in_(tids)
        ).group_by(SalaryRecord.month).all()

        sal_map = {m: round(avg) for m, avg in rows}
        order = ["M0", "M3", "M6", "M12"]
        return [{"month": m, "avg": sal_map.get(m, 0)} for m in order]
    finally:
        db.close()

@app.get("/api/recommendations")
def recommendations(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        rows = db.query(Recommendation).order_by(Recommendation.id).all()
        return [{"id": r.id, "priority": r.priority, "title": r.title, "reason": r.reason, "action": r.action, "status": r.status} for r in rows]
    finally:
        db.close()

@app.get("/api/alerts")
def alerts(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        rows = db.query(Notification).order_by(Notification.id.desc()).all()
        return [{"id": n.id, "severity": n.severity, "message": n.message, "target": n.target, "read": n.read} for n in rows]
    finally:
        db.close()

@app.post("/api/campaigns")
def campaign(user: User = Depends(get_current_user)):
    require_role(user, ["admin", "officer"])
    db = SessionLocal()
    try:
        c = db.query(Campaign).order_by(Campaign.id.desc()).first()
        if c:
            c.progress = min(c.target, c.progress + 125)
            c.responses = min(c.target, c.responses + 90)
            c.pending = max(0, c.target - c.responses)
            c.status = "Running"
            db.commit()
            return {"target": c.target, "progress": c.progress, "responses": c.responses, "pending": c.pending, "unreachable": c.unreachable, "escalated": c.escalated, "status": c.status}
        return {"status": "No campaign configured"}
    finally:
        db.close()

@app.get("/api/campaigns")
def campaigns(user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        c = db.query(Campaign).order_by(Campaign.id.desc()).first()
        if not c:
            return {}
        return {"target": c.target, "progress": c.progress, "responses": c.responses, "pending": c.pending, "unreachable": c.unreachable, "escalated": c.escalated, "status": c.status}
    finally:
        db.close()

@app.get("/api/search")
def search(q: str = Query(..., min_length=1), user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        like = f"%{q}%"
        tq = db.query(Trainee).filter(or_(Trainee.name.ilike(like), Trainee.trainee_id.ilike(like)))
        if user.role == "provider":
            tq = tq.filter(Trainee.provider_id == user.provider_id)
        elif user.role == "officer":
            tq = tq.filter(Trainee.district_id == user.district_id)
        elif user.role == "trainee":
            tq = tq.filter(Trainee.id == user.trainee_id)

        ts = tq.limit(8).all()
        ps = db.query(Provider).filter(Provider.name.ilike(like)).limit(5).all() if user.role in ["admin", "officer", "provider"] else []
        es = db.query(Employer).filter(Employer.name.ilike(like)).limit(5).all()
        cs = db.query(Course).filter(Course.name.ilike(like)).limit(5).all()

        return {
            "trainees": [{"id": t.id, "name": t.name, "id_code": t.trainee_id} for t in ts],
            "providers": [{"id": p.id, "name": p.name} for p in ps],
            "employers": [{"id": e.id, "name": e.name} for e in es],
            "courses": [{"id": c.id, "name": c.name} for c in cs]
        }
    finally:
        db.close()

@app.post("/api/reset")
def reset(user: User = Depends(get_current_user)):
    require_role(user, ["admin"])
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed()
    link_demo_users()
    return {"success": True, "message": "Demo database reset and seeded with initial demo relationships"}

@app.get("/api/report")
def report(user: User = Depends(get_current_user)):
    require_role(user, ["admin", "provider"])
    db = SessionLocal()
    try:
        tq = db.query(Trainee)
        if user.role == "provider":
            tq = tq.filter(Trainee.provider_id == user.provider_id)
            prov_name = user.provider.name if user.provider else f"Provider {user.provider_id}"
            scope_title = f"PROVIDER REPORT: {prov_name}"
        else:
            scope_title = "STATE EXECUTIVE REPORT: MAHARASHTRA SKILL DEVELOPMENT MISSION"

        ts = tq.all()
        total = len(ts)
        certified = sum(1 for x in ts if x.certified)
        emp = sum(1 for x in ts if x.employment_status == "EMPLOYED")
        verified = sum(1 for x in ts if x.verification == "Verified")

        data = f"""KAUSHAL360 — PROGRAMME IMPACT REPORT
DEMO / SYNTHETIC DATA
{scope_title}
Generated: {datetime.now():%d %b %Y %H:%M}
User: {user.name} ({user.role.upper()})

Training reach: {total:,} trainees
Certification: {certified / (total or 1) * 100:.1f}%
Employment: {emp / (total or 1) * 100:.1f}%
Verified employment records: {verified:,}

Longitudinal outcome tracking includes placement, employment, retention, wage progression and training relevance.
Priority skill gap: PLC Programming / advanced industrial automation.
Recommended action: Add advanced PLC module to the next training cycle.

This report contains synthetic prototype data for SIH26135 evaluation and is not an official government statistic.
"""
        path = BASE / "kaushal360_report.txt"
        try:
            path.write_text(data, encoding="utf-8")
        except Exception:
            pass
        return PlainTextResponse(
            content=data,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="kaushal360_programme_report.txt"'}
        )
    finally:
        db.close()
