"""
test_comment.py
---------------
Giả lập khách COMMENT dưới bài đăng để bạn xem bot trả lời nhiều tầng thế nào,
mà CHƯA cần nối Facebook. Cũng kiểm tra việc tự lưu số điện thoại.

Chạy:  python test_comment.py
(Cần đã điền ANTHROPIC_API_KEY trong file .env)
"""

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from claude_bot import tra_loi_comment
from leads import xu_ly_lead

SO_TANG_CONG_KHAI = 2  # giống cấu hình mặc định


def gia_lap(ten_khach: str, cac_comment: list[str]):
    print(f"\n========== KHÁCH: {ten_khach} ==========")
    for i, cmt in enumerate(cac_comment, start=1):
        print(f"\n💬 Khách comment (tầng {i}): {cmt}")

        # Tự lưu nếu có số điện thoại
        xu_ly_lead(ten_khach, cmt, "Comment (test)")

        tra_loi = tra_loi_comment(cmt, tang=i, ten_khach=ten_khach)

        if i <= SO_TANG_CONG_KHAI:
            print(f"   ↳ 🤖 Bot trả lời CÔNG KHAI: {tra_loi}")
        else:
            print(f"   ↳ 📩 Bot NHẮN TIN RIÊNG (inbox): {tra_loi}")
            print(f"   ↳ 🤖 Bot công khai: Em đã nhắn tin riêng cho mình rồi nhé ❤️")


if __name__ == "__main__":
    # Kịch bản 1: khách hỏi giá nhiều lần -> bot kéo về inbox dần
    gia_lap("Nguyễn Thị Lan", [
        "Nhung hươu tươi giá bao nhiêu shop?",
        "Sao không báo giá luôn đi ạ?",
        "Ừ vậy mình muốn mua 1 lạng",
    ])

    # Kịch bản 2: khách để lại số điện thoại ngay -> tự lưu vào khach_hang.csv
    gia_lap("Trần Văn Hùng", [
        "Cho mình hỏi cao nhung hươu, sđt mình 0987654321 nhé",
    ])

    print("\n\n✅ Xong! Mở file 'khach_hang.csv' để xem khách đã được lưu lại.")
