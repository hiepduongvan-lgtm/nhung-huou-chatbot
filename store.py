"""
store.py
--------
BỘ NHỚ BỀN của chatbot — lưu hội thoại từng khách hàng ra file khach_data.json
để bot NHỚ ngữ cảnh cũ khi khách quay lại (kể cả sau khi tắt/mở lại server),
và phục vụ tính năng THEO ĐUỔI khách hàng.

Cấu trúc mỗi khách (key = ID khách trên Facebook / Messenger):
{
  "ten": "...",
  "lich_su": [{"role":"user/assistant","content":"..."}, ...],
  "lan_cuoi_khach": "2026-06-22T10:00:00",   # lần cuối KHÁCH nhắn
  "lan_theo_duoi_cuoi": null,                # lần cuối BOT nhắn theo đuổi
  "so_lan_theo_duoi": 0
}
"""

import json
import sys
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_DIR = Path(__file__).parent
FILE_DATA = _DIR / "khach_data.json"

GIOI_HAN_LICH_SU = 40  # giữ tối đa 40 tin gần nhất / khách cho gọn
SESSION_GAP_GIO = 2    # nghỉ quá 2 tiếng coi như PHIÊN MỚI -> tư vấn lại từ đầu


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def luot_phien_hien_tai(uid: str) -> int:
    """Trả về số thứ tự lượt của khách TRONG PHIÊN hiện tại (để quyết định
    đã tới bước báo giá chưa). Nghỉ lâu (>SESSION_GAP_GIO) -> phiên mới, về 1."""
    kh = lay_khach(uid)
    if not kh or not kh.get("lan_cuoi_khach"):
        return 1
    try:
        gap = (datetime.now() - datetime.fromisoformat(kh["lan_cuoi_khach"])).total_seconds() / 3600
    except Exception:
        return 1
    if gap > SESSION_GAP_GIO:
        return 1  # phiên mới
    return kh.get("so_luot_phien", 0) + 1


def _load() -> dict:
    if FILE_DATA.exists():
        try:
            return json.loads(FILE_DATA.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(data: dict):
    FILE_DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def lay_khach(uid: str) -> dict | None:
    return _load().get(str(uid))


def lay_lich_su(uid: str) -> list:
    kh = lay_khach(uid)
    return kh.get("lich_su", []) if kh else []


def ghi_tin_khach(uid: str, ten: str, noi_dung_khach: str, reply_bot: str,
                  luot_phien: int | None = None) -> dict:
    """Lưu 1 lượt khách-bot. Khách vừa phản hồi -> reset bộ đếm theo đuổi.
    luot_phien: số lượt trong phiên hiện tại (để bot biết giai đoạn tư vấn)."""
    data = _load()
    uid = str(uid)
    kh = data.get(uid) or {"ten": "", "lich_su": [], "so_lan_theo_duoi": 0}
    if ten:
        kh["ten"] = ten
    kh["lich_su"].append({"role": "user", "content": noi_dung_khach})
    kh["lich_su"].append({"role": "assistant", "content": reply_bot})
    kh["lich_su"] = kh["lich_su"][-GIOI_HAN_LICH_SU:]
    if luot_phien is None:
        luot_phien = luot_phien_hien_tai(uid)
    kh["so_luot_phien"] = luot_phien
    kh["lan_cuoi_khach"] = _now()
    kh["lan_theo_duoi_cuoi"] = None
    kh["so_lan_theo_duoi"] = 0
    data[uid] = kh
    _save(data)
    return kh


def ghi_theo_duoi(uid: str, noi_dung: str):
    """Ghi nhận 1 tin theo đuổi do bot chủ động gửi."""
    data = _load()
    uid = str(uid)
    kh = data.get(uid)
    if not kh:
        return
    kh["lich_su"].append({"role": "assistant", "content": noi_dung})
    kh["lich_su"] = kh["lich_su"][-GIOI_HAN_LICH_SU:]
    kh["so_lan_theo_duoi"] = kh.get("so_lan_theo_duoi", 0) + 1
    kh["lan_theo_duoi_cuoi"] = _now()
    data[uid] = kh
    _save(data)


def danh_sach_can_theo_duoi(gio_cho: float = 24, toi_da: int | None = None) -> list:
    """Trả về [(uid, khách)] cần theo đuổi: đã qua `gio_cho` giờ kể từ mốc gần
    nhất (khách nhắn cuối hoặc lần theo đuổi cuối) mà khách chưa phản hồi.
    toi_da: số lần theo đuổi tối đa (None = không giới hạn)."""
    data = _load()
    ket = []
    now = datetime.now()
    for uid, kh in data.items():
        moc = kh.get("lan_theo_duoi_cuoi") or kh.get("lan_cuoi_khach")
        if not moc:
            continue
        try:
            gio_qua = (now - datetime.fromisoformat(moc)).total_seconds() / 3600
        except Exception:
            continue
        if gio_qua >= gio_cho:
            if toi_da is None or kh.get("so_lan_theo_duoi", 0) < toi_da:
                ket.append((uid, kh))
    return ket


def xoa_khach(uid: str):
    """Xóa dữ liệu 1 khách (dùng khi bấm 'Trò chuyện mới' lúc test)."""
    data = _load()
    if str(uid) in data:
        del data[str(uid)]
        _save(data)
