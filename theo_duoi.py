"""
theo_duoi.py
------------
TÍNH NĂNG THEO ĐUỔI KHÁCH HÀNG trên Messenger.

Cách hoạt động:
- Quét danh sách khách đã nhắn tin nhưng chưa phản hồi sau X giờ (mặc định 24h).
- Với mỗi khách, AI tự soạn 1 tin theo đuổi NHẸ NHÀNG dựa trên ngữ cảnh trước đó.
- Gửi tin qua Messenger (nếu đã nối Facebook); nếu chưa, chỉ in ra để xem trước.
- Khách vẫn chưa phản hồi -> lần chạy sau tiếp tục theo đuổi (giãn cách X giờ).

CÁCH CHẠY:
  python theo_duoi.py          -> theo đuổi khách quá hạn 24h (chạy thật)
  python theo_duoi.py test     -> theo đuổi MỌI khách ngay (để xem thử cách bot nhắn)

LƯU Ý CHÍNH SÁCH FACEBOOK:
  Facebook chỉ cho nhắn tự do trong 24 GIỜ kể từ tin cuối của khách. Sau 24h, để
  gửi tin chủ động cần dùng "message tag" (vd HUMAN_AGENT — cho phép tới 7 ngày)
  hoặc One-Time Notification. Mã bên dưới đã gắn sẵn tag HUMAN_AGENT.

ĐỂ CHẠY TỰ ĐỘNG HÀNG NGÀY: dùng Windows Task Scheduler gọi file này (xem HUONG_DAN.md).
"""

import os
import sys
import requests
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

from claude_bot import tao_tin_theo_duoi
import store

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "").strip()
GIO_CHO = float(os.environ.get("FOLLOWUP_GIO_CHO", 24))      # số giờ chờ trước khi theo đuổi
TOI_DA = os.environ.get("FOLLOWUP_TOI_DA")                    # số lần theo đuổi tối đa (trống = không giới hạn)
TOI_DA = int(TOI_DA) if TOI_DA else None


def gui_messenger(uid: str, noi_dung: str) -> bool:
    """Gửi tin theo đuổi qua Messenger. Nếu chưa có token -> chỉ xem trước (dry-run)."""
    if not PAGE_ACCESS_TOKEN:
        print(f"   [XEM TRƯỚC - chưa nối Facebook] gửi cho {uid}:\n   → {noi_dung}\n")
        return True
    url = "https://graph.facebook.com/v21.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": uid},
        "message": {"text": noi_dung},
        # MESSAGE_TAG + HUMAN_AGENT: cho phép nhắn ngoài cửa sổ 24h (tối đa 7 ngày)
        "messaging_type": "MESSAGE_TAG",
        "tag": "HUMAN_AGENT",
    }
    r = requests.post(url, params=params, json=payload)
    if r.status_code == 200:
        print(f"   ✅ Đã gửi tin theo đuổi cho {uid}")
        return True
    print(f"   ❌ Lỗi gửi cho {uid}: {r.status_code} {r.text}")
    return False


def chay(gio_cho: float = GIO_CHO):
    danh_sach = store.danh_sach_can_theo_duoi(gio_cho=gio_cho, toi_da=TOI_DA)
    if not danh_sach:
        print(f"Không có khách nào cần theo đuổi (ngưỡng {gio_cho}h).")
        return

    print(f"Có {len(danh_sach)} khách cần theo đuổi:\n")
    for uid, kh in danh_sach:
        ten = kh.get("ten") or uid
        lan_thu = kh.get("so_lan_theo_duoi", 0) + 1
        print(f"• Khách {ten} (lần theo đuổi thứ {lan_thu})")
        tin = tao_tin_theo_duoi(kh.get("lich_su", []), lan_thu=lan_thu)
        if not tin:
            print("   (không tạo được tin, bỏ qua)")
            continue
        if gui_messenger(uid, tin):
            store.ghi_theo_duoi(uid, tin)


if __name__ == "__main__":
    che_do_test = len(sys.argv) > 1 and sys.argv[1].lower() == "test"
    # Chế độ test: theo đuổi mọi khách ngay (gio_cho = 0) để xem thử
    chay(gio_cho=0 if che_do_test else GIO_CHO)
