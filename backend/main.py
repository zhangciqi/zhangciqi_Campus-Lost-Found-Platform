# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth, items, claims, admin

app = FastAPI(title="校园失物招领平台 V1.0")

# 跨域配置：允许前端页面跨来源调用接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,   prefix="/api/auth",   tags=["认证"])
app.include_router(items.router,  prefix="/api/items",  tags=["物品"])
app.include_router(claims.router, prefix="/api/claims", tags=["认领"])
app.include_router(admin.router,  prefix="/api/admin",  tags=["管理"])

# 物品照片静态访问（/uploads/items/xxx.jpg）
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 托管前端静态页面，启动后访问 http://127.0.0.1:8000/login.html
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

# 启动命令（在 backend 目录下执行）：uvicorn main:app --reload --port 8000
