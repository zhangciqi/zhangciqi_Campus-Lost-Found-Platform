# backend/routers/claims.py —— 接口：POST /api/claims
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_conn
from deps import current_user

router = APIRouter()

class ClaimReq(BaseModel):
    item_id: int
    claim_detail: str

@router.post("")
def submit_claim(req: ClaimReq, user = Depends(current_user)):
    if not req.claim_detail.strip():
        raise HTTPException(400, "认领说明不能为空")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 事务内加锁读物品，确认可认领
            cur.execute(
                "SELECT review_status, item_status FROM items "
                "WHERE item_id=%s FOR UPDATE", (req.item_id,))
            item = cur.fetchone()
            if not item or item[0] != "approved" or item[1] != "unclaimed":
                raise HTTPException(400, "该物品当前不可认领")
            # 同一物品同时只允许一条待审核认领（原子校验，防并发绕过）
            cur.execute(
                "SELECT claim_id FROM claims "
                "WHERE item_id=%s AND review_result='pending' FOR UPDATE",
                (req.item_id,))
            if cur.fetchone():
                raise HTTPException(400, "该物品已有待审核的认领申请")
            cur.execute(
                "INSERT INTO claims(item_id, applicant_id, claim_detail, review_result) "
                "VALUES(%s, %s, %s, 'pending')",
                (req.item_id, user["uid"], req.claim_detail)
            )
        conn.commit()
        return {"message": "认领申请已提交"}
    finally:
        conn.close()
