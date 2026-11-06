# backend/routers/auth.py —— 接口：POST /api/auth/register、POST /api/auth/login
import time, hmac, hashlib, json, base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
from database import get_conn

router = APIRouter()

SECRET = "campus-lf-secret"

class RegisterReq(BaseModel):
    account: str
    password: str
    name: str
    role: str = "student"
    phone: str | None = None

class LoginReq(BaseModel):
    account: str
    password: str

def make_token(user_id: int, role: str) -> str:
    payload = {"uid": user_id, "role": role, "exp": int(time.time()) + 86400}
    raw = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return raw + "." + sig

@router.post("/register")
def register(req: RegisterReq):
    if req.role not in ("student", "staff"):
        raise HTTPException(400, "角色不合法")
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE account=%s", (req.account,))
            if cur.fetchone():
                raise HTTPException(400, "该账号已注册")
            cur.execute(
                "INSERT INTO users(account, password, name, role, phone) "
                "VALUES(%s, %s, %s, %s, %s)",
                (req.account, hashed, req.name, req.role, req.phone)
            )
        conn.commit()
        return {"message": "注册成功"}
    finally:
        conn.close()

@router.post("/login")
def login(req: LoginReq):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, password, role, name FROM users WHERE account=%s",
                (req.account,))
            row = cur.fetchone()
    finally:
        conn.close()
    if not row or not bcrypt.checkpw(req.password.encode(), row[1].encode()):
        raise HTTPException(401, "账号或密码错误")
    return {"token": make_token(row[0], row[2]), "role": row[2], "name": row[3]}
