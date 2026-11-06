# backend/routers/admin.py —— 接口：GET /api/admin/items、POST /api/admin/items/{id}/review
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_conn
from deps import require_admin

router = APIRouter()

class ReviewReq(BaseModel):
    action: str   # approve / reject

@router.get("/items")
def pending_items(admin = Depends(require_admin)):   # 仅管理员
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT item_id, info_type, item_name, item_type, location, event_time "
                "FROM items WHERE review_status='pending' ORDER BY item_id")
            rows = cur.fetchall()
    finally:
        conn.close()
    return {"items": [{"item_id": r[0], "info_type": r[1], "item_name": r[2],
                       "item_type": r[3], "location": r[4], "event_time": str(r[5])}
                      for r in rows]}

@router.post("/items/{item_id}/review")
def review_item(item_id: int, req: ReviewReq, admin = Depends(require_admin)):
    if req.action not in ("approve", "reject"):
        raise HTTPException(400, "action 只能是 approve 或 reject")
    new_status = "approved" if req.action == "approve" else "rejected"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE items SET review_status=%s "
                "WHERE item_id=%s AND review_status='pending'",
                (new_status, item_id))
            if cur.rowcount == 0:
                raise HTTPException(404, "记录不存在或已被处理")
        conn.commit()
        return {"message": "操作成功", "review_status": new_status}
    finally:
        conn.close()
