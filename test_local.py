"""
test_local.py
-------------
Trang CHAT THỬ ngay trong trình duyệt để tinh chỉnh giọng văn của bot
(KHÔNG cần Facebook, chỉ cần API key Claude trong .env).

CÁCH CHẠY:
  1. Mở PowerShell, gõ:
       cd "đường dẫn thư mục dự án"
       python test_local.py
  2. Mở trình duyệt (Chrome) vào địa chỉ:  http://localhost:5000
  3. Gõ thử như khách hàng. Có 2 chế độ:
       - "Tin nhắn"  : bot tư vấn đầy đủ như Messenger (nhớ hội thoại).
       - "Bình luận" : mô phỏng comment nhiều tầng (giấu giá -> inbox).
  4. Bấm "Trò chuyện mới" để bắt đầu lại từ đầu.
"""

import sys
from flask import Flask, request, jsonify
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

from claude_bot import tra_loi, tra_loi_comment
import store  # bộ nhớ bền — để test tính năng "nhớ ngữ cảnh"

app = Flask(__name__)

# Khi test, coi như 1 khách cố định để dùng chung bộ nhớ bền
UID_TEST = "TEST_LOCAL"
dem_tang_comment = 0   # đếm tầng cho chế độ bình luận
SO_TANG_CONG_KHAI = 2

TRANG_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chat thử — Nhung Hươu Bổ Đà</title>
<style>
  * { box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }
  body { margin: 0; background: #e9ebee; }
  .wrap { max-width: 480px; margin: 0 auto; height: 100vh; display: flex; flex-direction: column; background: #fff; }
  .top { background: #0084ff; color: #fff; padding: 12px 16px; }
  .top h1 { margin: 0; font-size: 17px; }
  .top p { margin: 2px 0 0; font-size: 12px; opacity: .85; }
  .modes { display: flex; gap: 8px; padding: 10px 12px; background: #f5f6f7; border-bottom: 1px solid #ddd; align-items: center; }
  .modes button { flex: 1; padding: 8px; border: 1px solid #0084ff; background: #fff; color: #0084ff; border-radius: 18px; cursor: pointer; font-size: 13px; }
  .modes button.active { background: #0084ff; color: #fff; }
  .reset { flex: 0 0 auto !important; border-color: #999 !important; color: #666 !important; }
  .chat { flex: 1; overflow-y: auto; padding: 14px; }
  .msg { margin: 8px 0; display: flex; }
  .msg.user { justify-content: flex-end; }
  .bubble { max-width: 78%; padding: 9px 13px; border-radius: 18px; font-size: 14.5px; line-height: 1.45; white-space: pre-wrap; word-wrap: break-word; }
  .user .bubble { background: #0084ff; color: #fff; border-bottom-right-radius: 4px; }
  .bot .bubble { background: #f1f0f0; color: #1c1e21; border-bottom-left-radius: 4px; }
  .tag { font-size: 11px; color: #888; margin: 2px 8px; }
  .typing { color: #999; font-size: 13px; padding: 4px 14px; }
  .inputbar { display: flex; padding: 10px; gap: 8px; border-top: 1px solid #ddd; }
  .inputbar input { flex: 1; padding: 11px 14px; border: 1px solid #ccc; border-radius: 20px; font-size: 14.5px; outline: none; }
  .inputbar button { padding: 0 18px; background: #0084ff; color: #fff; border: none; border-radius: 20px; cursor: pointer; font-size: 14px; }
  .inputbar button:disabled { background: #9bc7ff; }
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <h1>🦌 Nhung Hươu Bổ Đà — Chat thử</h1>
    <p>Công cụ test giọng văn (không phải Facebook thật)</p>
  </div>
  <div class="modes">
    <button id="mode-tin" class="active" onclick="doiCheDo('tin')">💬 Tin nhắn</button>
    <button id="mode-comment" onclick="doiCheDo('comment')">📢 Bình luận</button>
    <button class="reset" onclick="lamMoi()">🔄 Mới</button>
  </div>
  <div class="chat" id="chat"></div>
  <div class="typing" id="typing" style="display:none">Bot đang soạn tin…</div>
  <div class="inputbar">
    <input id="msg" placeholder="Nhập như khách hàng…" onkeydown="if(event.key==='Enter')gui()">
    <button id="send" onclick="gui()">Gửi</button>
  </div>
</div>
<script>
let cheDo = 'tin';

function doiCheDo(m) {
  cheDo = m;
  document.getElementById('mode-tin').classList.toggle('active', m==='tin');
  document.getElementById('mode-comment').classList.toggle('active', m==='comment');
}

function themBubble(text, ai, tag) {
  const chat = document.getElementById('chat');
  if (tag) {
    const t = document.createElement('div');
    t.className = 'tag';
    t.textContent = tag;
    chat.appendChild(t);
  }
  const row = document.createElement('div');
  row.className = 'msg ' + ai;
  row.innerHTML = '<div class="bubble"></div>';
  row.querySelector('.bubble').textContent = text;
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
}

async function gui() {
  const inp = document.getElementById('msg');
  const text = inp.value.trim();
  if (!text) return;
  inp.value = '';
  document.getElementById('send').disabled = true;
  themBubble(text, 'user');
  document.getElementById('typing').style.display = 'block';

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ message: text, mode: cheDo })
    });
    const data = await res.json();
    document.getElementById('typing').style.display = 'none';
    themBubble(data.reply, 'bot', data.tag);
  } catch (e) {
    document.getElementById('typing').style.display = 'none';
    themBubble('[Lỗi kết nối: ' + e + ']', 'bot');
  }
  document.getElementById('send').disabled = false;
  inp.focus();
}

async function lamMoi() {
  await fetch('/reset', { method: 'POST' });
  document.getElementById('chat').innerHTML = '';
}
</script>
</body>
</html>
"""


@app.route("/")
def trang_chu():
    return TRANG_HTML


@app.route("/chat", methods=["POST"])
def chat():
    global dem_tang_comment
    data = request.get_json()
    noi_dung = data.get("message", "")
    mode = data.get("mode", "tin")

    if mode == "comment":
        dem_tang_comment += 1
        tang = dem_tang_comment
        reply = tra_loi_comment(noi_dung, tang=tang, ten_khach="")
        if tang <= SO_TANG_CONG_KHAI:
            tag = f"Bình luận công khai · tầng {tang}"
        else:
            tag = f"Nhắn tin riêng (inbox) · tầng {tang}"
        return jsonify({"reply": reply, "tag": tag})

    # Chế độ tin nhắn (Messenger) — dùng bộ nhớ bền để test "nhớ ngữ cảnh"
    lich_su = store.lay_lich_su(UID_TEST)
    reply = tra_loi(noi_dung, lich_su)
    store.ghi_tin_khach(UID_TEST, "", noi_dung, reply)
    return jsonify({"reply": reply, "tag": None})


@app.route("/reset", methods=["POST"])
def reset():
    global dem_tang_comment
    store.xoa_khach(UID_TEST)   # xóa bộ nhớ khách test -> bắt đầu lại từ lượt 1
    dem_tang_comment = 0
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  CHAT THỬ NHUNG HƯƠU BỔ ĐÀ")
    print("  Mở trình duyệt vào địa chỉ:  http://localhost:5000")
    print("  (hoặc http://127.0.0.1:5000 nếu localhost bị chặn)")
    print("  TỰ ĐỘNG cập nhật khi code/kiến thức thay đổi.")
    print("  (Bấm Ctrl+C trong cửa sổ này để dừng)")
    print("=" * 55 + "\n")

    # Theo dõi thêm các file kiến thức .md để server tự nạp lại khi chúng thay đổi
    from pathlib import Path
    _HERE = Path(__file__).parent
    file_theo_doi = [
        str(_HERE / "SYSTEM_PROMPT_NHBD_v1.md"),
        str(_HERE / "NHBD_KNOWLEDGE_BASE_COMPACT.md"),
        str(_HERE / "claude_bot.py"),
    ]
    # debug=True + use_reloader=True: tự khởi động lại khi file thay đổi
    app.run(host="127.0.0.1", port=5000, debug=True,
            use_reloader=True, extra_files=file_theo_doi)
