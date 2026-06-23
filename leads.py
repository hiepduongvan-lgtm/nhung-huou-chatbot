"""
leads.py
--------
Tự động phát hiện SỐ ĐIỆN THOẠI trong tin nhắn/comment của khách và lưu lại
để chủ shop gọi lại chốt đơn.

Lưu vào 2 nơi:
  1. GOOGLE SHEET (nếu đã cấu hình) — xem được mọi lúc trên điện thoại/máy tính.
  2. File khach_hang.csv (luôn luôn, làm bản dự phòng).

Mọi khách lưu lại đều được ghi rõ nguồn "Chatbot FB - ..." để phân biệt
với khách từ kênh khác.
"""

import os
import re
import csv
import sys
import requests
from datetime import datetime
from pathlib import Path

# Đảm bảo in tiếng Việt ra màn hình Windows không bị lỗi mã hoá
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_DIR = Path(__file__).parent
FILE_KHACH = _DIR / "khach_hang.csv"

# Nhãn nguồn — luôn ghi rõ đây là khách từ Chatbot Facebook
NHAN_NGUON = "Chatbot FB"

# Tiêu đề cột (dùng chung cho cả CSV và Google Sheet)
TIEU_DE = ["Thời gian", "Tên khách", "Số điện thoại", "Email", "Nguồn", "Nội dung"]

# Link Google Apps Script Web App (ghi thẳng vào file Google Sheet có sẵn của bạn).
# Cấu hình trong .env: GOOGLE_SCRIPT_URL=https://script.google.com/macros/s/.../exec
GOOGLE_SCRIPT_URL = os.environ.get("GOOGLE_SCRIPT_URL", "").strip()

# Mẫu nhận diện số điện thoại Việt Nam (0xxxxxxxxx hoặc +84/84...)
_MAU_SDT = re.compile(r"(?:(?:\+?84)|0)(?:[\s.\-]?\d){9}")
# Mẫu nhận diện email
_MAU_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


# ====================================================================
# 1) PHÁT HIỆN SỐ ĐIỆN THOẠI & EMAIL
# ====================================================================
def tim_so_dien_thoai(text: str) -> str | None:
    """Trả về số điện thoại đầu tiên tìm thấy (đã chuẩn hoá 0xxxxxxxxx), hoặc None."""
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


def tim_email(text: str) -> str | None:
    """Trả về email đầu tiên tìm thấy, hoặc None."""
    if not text:
        return None
    m = _MAU_EMAIL.search(text)
    return m.group().strip().lower() if m else None


# ====================================================================
# 2) GHI VÀO GOOGLE SHEET (tùy chọn)
# ====================================================================
# Cấu hình trong .env:
#   GOOGLE_SHEET_ID=...           (ID của Google Sheet)
#   GOOGLE_CREDENTIALS_FILE=google_credentials.json
#   GOOGLE_SHEET_TAB=Khách Chatbot FB
_ws_cache = None          # giữ kết nối worksheet sau lần đầu
_google_loi = False       # nếu lỗi 1 lần thì thôi không thử lại liên tục


def _lay_worksheet():
    """Kết nối tới Google Sheet (chỉ làm 1 lần). Trả về worksheet hoặc None."""
    global _ws_cache, _google_loi
    if _ws_cache is not None:
        return _ws_cache
    if _google_loi:
        return None

    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "").strip()
    cred_file = os.environ.get("GOOGLE_CREDENTIALS_FILE", "google_credentials.json").strip()
    tab = os.environ.get("GOOGLE_SHEET_TAB", "Khách Chatbot FB").strip()

    # Chưa cấu hình -> bỏ qua, chỉ dùng CSV
    if not sheet_id or not (_DIR / cred_file).exists():
        _google_loi = True
        return None

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(str(_DIR / cred_file), scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)

        # Lấy đúng tab, tạo mới nếu chưa có
        try:
            ws = sh.worksheet(tab)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=tab, rows=1000, cols=len(TIEU_DE))
            ws.append_row(TIEU_DE)

        # Đảm bảo có dòng tiêu đề
        if not ws.row_values(1):
            ws.append_row(TIEU_DE)

        _ws_cache = ws
        print(f"✅ Đã kết nối Google Sheet (tab: {tab})")
        return ws
    except Exception as e:
        print(f"[Cảnh báo] Không kết nối được Google Sheet, chỉ lưu CSV. Lỗi: {e}")
        _google_loi = True
        return None


def _ghi_google_sheet(dong: list) -> bool:
    ws = _lay_worksheet()
    if ws is None:
        return False
    try:
        ws.append_row(dong, value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        print(f"[Cảnh báo] Ghi Google Sheet thất bại: {e}")
        return False


# ====================================================================
# 3) GHI VÀO CSV (luôn luôn, làm dự phòng)
# ====================================================================
def _ghi_csv(dong: list):
    file_moi = not FILE_KHACH.exists()
    with FILE_KHACH.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if file_moi:
            writer.writerow(TIEU_DE)
        writer.writerow(dong)


# ====================================================================
# 3b) GHI VÀO GOOGLE SHEET QUA APPS SCRIPT (ghi thẳng vào file có sẵn của bạn)
# ====================================================================
def _ghi_apps_script(dong: list) -> bool:
    if not GOOGLE_SCRIPT_URL:
        return False
    try:
        r = requests.post(GOOGLE_SCRIPT_URL, data={
            "thoi_gian": dong[0], "ten": dong[1], "sdt": dong[2],
            "email": dong[3], "nguon": dong[4], "noi_dung": dong[5],
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[Apps Script] {e}")
        return False


# ====================================================================
# 4) HÀM CHÍNH — phát hiện SĐT và lưu khách
# ====================================================================
def luu_khach_hang(ten: str, so_dt: str, email: str, noi_dung: str, kenh: str):
    """Lưu 1 khách hàng (SĐT và/hoặc Email) vào Google Sheet + CSV."""
    dong = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ten or "",
        so_dt or "",
        email or "",
        f"{NHAN_NGUON} - {kenh}",          # vd: "Chatbot FB - Comment"
        noi_dung.replace("\n", " ").strip(),
    ]
    # Ưu tiên ghi vào file Google Sheet có sẵn qua Apps Script; nếu không có thì gspread
    ket_qua_script = _ghi_apps_script(dong)
    ket_qua_gs = False if ket_qua_script else _ghi_google_sheet(dong)
    _ghi_csv(dong)
    noi_luu = "Google Sheet" if (ket_qua_script or ket_qua_gs) else "CSV"
    lien_he = " / ".join([x for x in (so_dt, email) if x])
    print(f"📋 ĐÃ LƯU KHÁCH: {ten} - {lien_he} ({NHAN_NGUON} - {kenh}) -> {noi_luu} + CSV")


def xu_ly_lead(ten: str, noi_dung: str, kenh: str):
    """Tìm SĐT và/hoặc Email trong nội dung; nếu có thì lưu khách.
    Trả về (so_dien_thoai, email) — None nếu không có."""
    so = tim_so_dien_thoai(noi_dung)
    email = tim_email(noi_dung)
    if so or email:
        luu_khach_hang(ten, so, email, noi_dung, kenh)
    return so, email


# Chạy thử nhanh: python leads.py
if __name__ == "__main__":
    test = [
        "Shop ơi cho mình hỏi giá, sđt mình 0987654321 nhé",
        "Liên hệ 098.765.4321 ạ",
        "Mail mình la nguyenvana@gmail.com gui bao gia nhe",
        "+84912345678 hoac email b.tran@yahoo.com.vn",
        "không có gì ở đây",
    ]
    for t in test:
        print(f"{t!r:55} -> SĐT={tim_so_dien_thoai(t)} | Email={tim_email(t)}")
