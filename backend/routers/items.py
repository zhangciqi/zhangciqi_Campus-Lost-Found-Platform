# backend/routers/items.py —— 接口：GET /api/items、POST /api/items、GET /api/items/{id}
import os, time, random
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from database import get_conn
from deps import current_user

router = APIRouter()

UPLOAD_DIR = "uploads/items"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
def list_items(keyword: str = "", item_type: str = "",
               location: str = "", info_type: str = ""):
    sql = ("SELECT item_id, info_type, item_name, item_type, location, event_time "
           "FROM items WHERE review_status='approved'")
    args = []
    if keyword:
        sql += " AND item_name LIKE %s"
        args.append("%" + keyword + "%")
    if item_type:
        sql += " AND item_type=%s"
        args.append(item_type)
    if location:
        sql += " AND location LIKE %s"
        args.append("%" + location + "%")
    if info_type:
        sql += " AND info_type=%s"
        args.append(info_type)
    sql += " ORDER BY item_id DESC LIMIT 50"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            rows = cur.fetchall()
    finally:
        conn.close()
    items = [{"item_id": r[0], "info_type": r[1], "item_name": r[2],
              "item_type": r[3], "location": r[4], "event_time": str(r[5])}
             for r in rows]
    return {"items": items}

@router.post("")
def publish_item(
    info_type:   str = Form(...),
    item_name:   str = Form(...),
    item_type:   str = Form(...),
    location:    str = Form(...),
    event_time:  str = Form(...),
    description: str = Form(""),
    photos: list[UploadFile] = File(default=[]),
    user = Depends(current_user)          # 需登录
):
    if len(photos) > 3:
        raise HTTPException(400, "最多上传3张照片")
    urls = []
    for f in photos:
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            raise HTTPException(400, "仅支持 jpg/png 格式")
        content = f.file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(400, "单张照片不能超过 5MB")
        fname = time.strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999)) + ext
        with open(os.path.join(UPLOAD_DIR, fname), "wb") as fp:
            fp.write(content)
        urls.append("/" + UPLOAD_DIR + "/" + fname)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO items(info_type, item_name, item_type, location, "
                "event_time, photos, description, review_status, item_status, "
                "publisher_id) VALUES(%s,%s,%s,%s,%s,%s,%s,'pending','unclaimed',%s)",
                (info_type, item_name, item_type, location, event_time,
                 ",".join(urls), description, user["uid"])
            )
        conn.commit()
        return {"message": "提交成功，等待审核"}
    finally:
        conn.close()

@router.get("/{item_id}")
def item_detail(item_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT item_id, info_type, item_name, item_type, location, "
                "event_time, photos, description, item_status "
                "FROM items WHERE item_id=%s AND review_status='approved'",
                (item_id,))
            r = cur.fetchone()
    finally:
        conn.close()
    if not r:
        raise HTTPException(404, "信息不存在或未通过审核")
    return {"item_id": r[0], "info_type": r[1], "item_name": r[2],
            "item_type": r[3], "location": r[4], "event_time": str(r[5]),
            "photos": r[6] or "", "description": r[7] or "", "item_status": r[8]}
