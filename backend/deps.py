# backend/deps.py —— 公共鉴权依赖（各接口统一引用）
import time, hmac, hashlib, json, base64
from fastapi import Header, HTTPException

SECRET = "campus-lf-secret"   # 与 routers/auth.py 签发 token 使用的密钥一致

def parse_token(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "缺少登录凭证")
    raw, _, sig = authorization[7:].rpartition(".")
    expect = hmac.new(SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expect):
        raise HTTPException(401, "凭证无效")
    payload = json.loads(base64.urlsafe_b64decode(raw.encode()).decode())
    if payload.get("exp", 0) < int(time.time()):
        raise HTTPException(401, "登录已过期")
    return payload

def current_user(authorization: str = Header(default="")):
    return parse_token(authorization)

def require_admin(authorization: str = Header(default="")):
    payload = parse_token(authorization)
    if payload.get("role") != "admin":
        raise HTTPException(403, "仅管理员可操作")
    return payload
