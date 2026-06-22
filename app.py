"""
app.py
------
Máy chủ (server) kết nối Fanpage Facebook với chatbot.
File này nhận tin nhắn từ Messenger, gửi cho Claude trả lời, rồi gửi
câu trả lời ngược lại cho khách.

Bạn KHÔNG cần hiểu hết file này. Chỉ cần chạy nó theo HUONG_DAN.md.
"""

import os
import sys
import time
import threading
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Đảm bảo in tiếng Việt ra màn hình Windows không bị lỗi mã hoá
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Tự động đọc các giá trị trong file .env (phải gọi trước khi import claude_bot)
load_dotenv()

from claude_bot import tra_loi, tra_loi_comment
from leads import xu_ly_lead
import store  # bộ nhớ bền: nhớ ngữ cảnh khách lâu dài

app = Flask(__name__)

# Các thông tin lấy từ file .env
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "nhunghuouboda")  # tự đặt, dùng khi nối webhook
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")     # token của fanpage (điền sau cũng được)

# Số lần bot trả lời CÔNG KHAI tối đa trước khi chuyển sang nhắn tin riêng (inbox).
# Mặc định 3 -> trả lời công khai 3 lần, đến comment thứ 4 thì mời khách inbox.
SO_TANG_CONG_KHAI = int(os.environ.get("SO_TANG_CONG_KHAI", 3))

# Cho phép trả lời comment CÔNG KHAI? Cần quyền pages_manage_engagement (qua App Review).
# Mặc định TẮT ("0") -> khi khách comment, bot NHẮN RIÊNG (inbox) để tư vấn.
# Sau khi App Review xong, đặt COMMENT_CONG_KHAI=1 để bật trả lời công khai 3 tầng.
COMMENT_CONG_KHAI = os.environ.get("COMMENT_CONG_KHAI", "0") == "1"

# Đếm số lần bot đã trả lời comment cho mỗi khách (theo từng bài đăng).
dem_comment = {}


# ====================================================================
# MÁY ĐÁNH THỨC — server tự ping chính nó để không bị Render cho "ngủ"
# ====================================================================
def _giu_thuc():
    """Mỗi 10 phút tự gọi vào địa chỉ web của chính mình để giữ server luôn thức."""
    url = os.environ.get("RENDER_EXTERNAL_URL")  # Render tự cấp biến này
    if not url:
        return  # chạy ở máy cá nhân thì không cần
    while True:
        time.sleep(300)  # 5 phút (an toàn dưới ngưỡng ngủ 15 phút của Render)
        try:
            requests.get(url, timeout=15)
            print("⏰ Tự đánh thức server (giữ thức).")
        except Exception as e:
            print(f"[Keep-alive] {e}")


# Chỉ bật khi chạy trên Render (có RENDER_EXTERNAL_URL)
if os.environ.get("RENDER_EXTERNAL_URL"):
    threading.Thread(target=_giu_thuc, daemon=True).start()


@app.route("/", methods=["GET"])
def trang_chu():
    return "Chatbot Nhung Huou Bo Da dang chay!", 200


@app.route("/webhook", methods=["GET"])
def xac_minh_webhook():
    """Facebook gọi vào đây 1 lần để xác minh khi bạn kết nối webhook."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook đã được xác minh!")
        return challenge, 200
    return "Sai verify token", 403


@app.route("/webhook", methods=["POST"])
def nhan_su_kien():
    """Facebook gửi MỌI sự kiện (tin nhắn Messenger + comment) vào đây."""
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            page_id = entry.get("id")  # ID của fanpage (để bỏ qua chính bot)

            # 1) Tin nhắn Messenger
            for event in entry.get("messaging", []):
                xu_ly_messenger(event)

            # 2) Comment dưới bài đăng (feed)
            for change in entry.get("changes", []):
                if change.get("field") == "feed":
                    xu_ly_comment(change.get("value", {}), page_id)

    return "ok", 200


def xu_ly_messenger(event: dict):
    """Xử lý 1 tin nhắn Messenger."""
    if not event.get("message") or not event["message"].get("text"):
        return
    sender_id = event["sender"]["id"]
    noi_dung = event["message"]["text"]
    print(f"[Messenger {sender_id}]: {noi_dung}")

    # Hiện "đã xem" + "đang soạn tin..." NGAY để khách thấy được phản hồi liền
    gui_hanh_dong(sender_id, "mark_seen")
    gui_hanh_dong(sender_id, "typing_on")

    # Nếu khách để lại số điện thoại / email -> tự động lưu khách hàng
    xu_ly_lead(f"Messenger {sender_id}", noi_dung, "Messenger")

    # Lấy ngữ cảnh cũ từ bộ nhớ bền (khách quay lại bot vẫn nhớ)
    lich_su = store.lay_lich_su(sender_id)
    cau_tra_loi = tra_loi(noi_dung, lich_su)

    # Lưu lại lượt trò chuyện này (đồng thời reset bộ đếm theo đuổi)
    store.ghi_tin_khach(sender_id, "", noi_dung, cau_tra_loi)

    gui_tin_nhan(sender_id, cau_tra_loi)  # gửi tin sẽ tự tắt "đang soạn tin"


def xu_ly_comment(value: dict, page_id: str):
    """Xử lý 1 comment dưới bài đăng theo cơ chế nhiều tầng."""
    # Chỉ xử lý khi có comment MỚI được thêm vào
    if value.get("item") != "comment" or value.get("verb") != "add":
        return

    comment_id = value.get("comment_id")
    noi_dung = value.get("message", "")
    nguoi_cmt = value.get("from", {})
    nguoi_cmt_id = nguoi_cmt.get("id")
    ten_khach = nguoi_cmt.get("name", "")
    post_id = value.get("post_id", "")

    # BỎ QUA comment do chính fanpage đăng (tránh bot tự trả lời mình)
    if not nguoi_cmt_id or nguoi_cmt_id == page_id:
        return
    if not noi_dung.strip():
        return

    # Nếu khách để lại số điện thoại / email ngay trong comment -> lưu khách hàng
    xu_ly_lead(ten_khach, noi_dung, "Comment")

    if not COMMENT_CONG_KHAI:
        # ===== CHẾ ĐỘ HIỆN TẠI: NHẮN RIÊNG (inbox) cho khách comment =====
        # (Trả lời công khai cần quyền pages_manage_engagement -> để dành sau App Review)
        print(f"[Comment -> inbox | {ten_khach}]: {noi_dung}")
        cau_tra_loi = tra_loi_comment(noi_dung, tang=99, ten_khach=ten_khach,
                                      nguong_cong_khai=0)  # ép kiểu nhắn riêng
        gui_tin_nhan_rieng(comment_id, cau_tra_loi)
        return

    # ===== CHẾ ĐỘ CÔNG KHAI (bật sau khi App Review): 3 tầng công khai rồi inbox =====
    khoa = f"{post_id}:{nguoi_cmt_id}"
    so_lan = dem_comment.get(khoa, 0)
    tang = so_lan + 1
    print(f"[Comment tầng {tang} | {ten_khach}]: {noi_dung}")

    cau_tra_loi = tra_loi_comment(noi_dung, tang=tang, ten_khach=ten_khach,
                                  nguong_cong_khai=SO_TANG_CONG_KHAI)

    if tang <= SO_TANG_CONG_KHAI:
        tra_loi_cong_khai(comment_id, cau_tra_loi)
    else:
        gui_tin_nhan_rieng(comment_id, cau_tra_loi)
        tra_loi_cong_khai(comment_id, "Em đã nhắn tin riêng cho mình rồi nhé, mình kiểm tra tin nhắn giúp shop ạ ❤️")

    dem_comment[khoa] = tang


def gui_hanh_dong(nguoi_nhan_id: str, action: str):
    """Gửi trạng thái cho khách: 'mark_seen' (đã xem) / 'typing_on' (đang soạn tin)."""
    url = "https://graph.facebook.com/v21.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {"recipient": {"id": nguoi_nhan_id}, "sender_action": action}
    try:
        requests.post(url, params=params, json=payload, timeout=10)
    except Exception as e:
        print(f"[sender_action] {e}")


def gui_tin_nhan(nguoi_nhan_id: str, noi_dung: str):
    """Gửi 1 tin nhắn văn bản tới khách qua Messenger Send API."""
    url = "https://graph.facebook.com/v21.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": nguoi_nhan_id},
        "message": {"text": noi_dung},
        "messaging_type": "RESPONSE",
    }
    r = requests.post(url, params=params, json=payload)
    if r.status_code != 200:
        print(f"[LỖI gửi tin] {r.status_code}: {r.text}")


def tra_loi_cong_khai(comment_id: str, noi_dung: str):
    """Trả lời công khai bên dưới một comment."""
    url = f"https://graph.facebook.com/v21.0/{comment_id}/comments"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    r = requests.post(url, params=params, json={"message": noi_dung})
    if r.status_code != 200:
        print(f"[LỖI trả lời comment] {r.status_code}: {r.text}")


def gui_tin_nhan_rieng(comment_id: str, noi_dung: str):
    """Nhắn tin riêng (inbox) cho người đã comment.
    Lưu ý: Facebook chỉ cho phép gửi private reply 1 lần cho mỗi comment,
    trong vòng 7 ngày kể từ khi khách comment."""
    url = f"https://graph.facebook.com/v21.0/{comment_id}/private_replies"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    r = requests.post(url, params=params, json={"message": noi_dung})
    if r.status_code != 200:
        print(f"[LỖI nhắn tin riêng] {r.status_code}: {r.text}")


if __name__ == "__main__":
    # Chạy server ở cổng 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
