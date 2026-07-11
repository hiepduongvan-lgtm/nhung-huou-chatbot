"""
leads.py — Thu thập khách hàng (phiên bản CRM)
------------------------------------------------
Tự phát hiện SỐ ĐIỆN THOẠI trong tin nhắn/comment của khách rồi:
1. Đẩy vào CRM chung (Google Sheet, qua biến CRM_SCRIPT_URL) — sổ khách hợp nhất
   của mọi kênh: Facebook, Zalo, Landing page, TikTok...
2. Ghi thêm vào khach_hang.csv trên server làm bản dự phòng.

Bạn KHÔNG cần sửa file này. Chỉ cần đặt biến CRM_SCRIPT_URL trên Render.
"""

import csv
import os
import re
import sys
import threading
from datetime import datetime
from pathlib import Path

import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FILE_KHACH = Path(__file__).with_name("khach_hang.csv")
CRM_URL = os.environ.get("CRM_SCRIPT_URL", "")

# SĐT Việt Nam: 0xxxxxxxxx hoặc +84/84, cho phép cách/chấm/gạch giữa các số
_MAU_SDT = re.compile(r"(?:(?:\+?84)|0)(?:[\s.\-]?\d){9}")


def tim_so_dien_thoai(text: str) -> str | None:
    """Trả về SĐT đầu tiên tìm thấy (chuẩn hóa 0xxxxxxxxx), hoặc None."""
    if not text:
        return None
    for match in _MAU_SDT.finditer(text):
        so = re.sub(r"[\s.\-]", "", match.group())
        if so.startswith("+84"):
            so = "0" + so[3:]
        elif so.startswith("84") and len(so) == 11:
            so = "0" + so[2:]
        if len(so) == 10 and so.startswith("0"):
            return so
    return None


def _gui_len_crm(ten: str, so_dt: str, noi_dung: str, nguon: str):
    """Đẩy khách vào CRM chung. Chạy ở luồng riêng để không làm chậm bot."""
    if not CRM_URL:
        return
    kenh = "Facebook - " + nguon if nguon else "Facebook"
    def _gui():
        try:
            r = requests.post(CRM_URL, json={
                "loai": "lead",
                "kenh": kenh,
                "ten": ten or "",
                "sdt": so_dt,
                "noi_dung": (noi_dung or "").replace("\n", " ").strip()[:500],
            }, timeout=20)
            print(f"📇 CRM: {r.text[:30]} — {ten} {so_dt}")
        except Exception as e:
            print(f"[CRM] Lỗi gửi: {e}")
    threading.Thread(target=_gui, daemon=True).start()


def luu_khach_hang(ten: str, so_dt: str, noi_dung: str, nguon: str):
    """Lưu khách: CRM chung + CSV dự phòng trên server."""
    _gui_len_crm(ten, so_dt, noi_dung, nguon)
    try:
        file_moi = not FILE_KHACH.exists()
        with FILE_KHACH.open("a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if file_moi:
                writer.writerow(["Thời gian", "Tên khách", "Số điện thoại", "Nguồn", "Nội dung"])
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ten or "", so_dt, nguon,
                (noi_dung or "").replace("\n", " ").strip(),
            ])
    except Exception as e:
        print(f"[CSV] Lỗi ghi: {e}")
    print(f"📋 ĐÃ LƯU KHÁCH: {ten} - {so_dt} ({nguon})")


def xu_ly_lead(ten: str, noi_dung: str, nguon: str) -> str | None:
    """Tìm SĐT trong nội dung, nếu có thì lưu và trả về số đó."""
    so = tim_so_dien_thoai(noi_dung)
    if so:
        luu_khach_hang(ten, so, noi_dung, nguon)
    return so


if __name__ == "__main__":
    test = [
        "Shop ơi cho mình hỏi giá, sđt mình 0987654321 nhé",
        "Liên hệ 098.765.4321 ạ",
        "+84912345678 gọi cho em",
        "không có số nào ở đây",
    ]
    for t in test:
        print(f"{t!r:55} -> {tim_so_dien_thoai(t)}")
