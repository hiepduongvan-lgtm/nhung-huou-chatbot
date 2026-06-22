# 📖 HƯỚNG DẪN CHẠY CHATBOT NHUNG HƯƠU BỔ ĐÀ

> Dành cho người **chưa biết lập trình**. Cứ làm theo từng bước, từ trên xuống.
> Khi nào bí, chụp màn hình lỗi và hỏi lại, sẽ có người gỡ cùng bạn.

Có **7 bước**:
1. Cài Python (phần mềm chạy code)
2. Tải các thư viện cần thiết
3. Lấy API key của Claude
4. Sửa kiến thức sản phẩm
5. Chạy thử trên máy (chưa cần Facebook)
6. Đưa lên mạng (deploy)
7. Kết nối Fanpage Facebook

---

## ✅ BƯỚC 1 — Cài Python

1. Vào trang: https://www.python.org/downloads/
2. Bấm nút vàng **"Download Python"** (bản mới nhất).
3. Mở file vừa tải. **QUAN TRỌNG:** ở màn hình đầu tiên, tích vào ô
   ☑️ **"Add Python to PATH"** rồi bấm **Install Now**.
4. Cài xong, mở **PowerShell** (bấm nút Start, gõ "PowerShell", Enter) và gõ:
   ```
   python --version
   ```
   Nếu hiện ra ví dụ `Python 3.12.x` là thành công.

---

## ✅ BƯỚC 2 — Tải các thư viện cần thiết

1. Mở **PowerShell**.
2. Di chuyển vào thư mục chứa chatbot bằng lệnh (copy y nguyên):
   ```
   cd C:\Users\hls\nhung-huou-chatbot
   ```
3. Cài các thư viện:
   ```
   pip install -r requirements.txt
   ```
   Chờ vài phút cho nó tải xong. Nếu hiện chữ "Successfully installed" là OK.

---

## ✅ BƯỚC 3 — Lấy API key của Claude

1. Vào https://console.anthropic.com và đăng ký/đăng nhập.
2. Nạp một ít tiền vào tài khoản (mục **Billing** → Add credits). Chỉ cần
   khoảng 5 USD là dùng được rất lâu cho fanpage nhỏ.
3. Vào mục **API Keys** → bấm **Create Key** → đặt tên bất kỳ → bấm tạo.
4. **Copy** chuỗi key (bắt đầu bằng `sk-ant-...`). ⚠️ Chỉ hiện 1 lần, copy ngay.

---

## ✅ BƯỚC 4 — Tạo file cấu hình & sửa kiến thức sản phẩm

### 4a. Tạo file .env
1. Trong thư mục `nhung-huou-chatbot`, có sẵn file tên **`.env.example`**.
2. Copy nó ra và đổi tên bản copy thành **`.env`** (đúng dấu chấm ở đầu, không có đuôi).
   - Cách nhanh trong PowerShell:
     ```
     copy .env.example .env
     ```
   > Lưu ý: file `.env` đã được tạo sẵn và **đã điền API key Claude**. Bạn chỉ cần
   > nạp tiền (credit) cho tài khoản Claude là chạy được (xem Bước 3).
3. Mở file `.env` bằng Notepad nếu cần chỉnh:
   - `ANTHROPIC_API_KEY=` (đã điền sẵn).
   - `PAGE_ACCESS_TOKEN=` để trống tạm, sẽ điền ở Bước 7.
   - `VERIFY_TOKEN=` để nguyên hoặc tự đổi thành chuỗi bạn thích.
4. Lưu lại.

### 4b. Kiến thức bán hàng (ĐÃ NẠP SẴN KIẾN THỨC THẬT)
Bot dùng 2 file kiến thức thật của Nhung Hươu Bổ Đà:
- **`SYSTEM_PROMPT_NHBD_v1.md`** — tính cách bot, quy tắc tư vấn, **bảng giá thật**,
  sản phẩm, USP, kịch bản xử lý. ⬅️ Sửa file này khi đổi giá / thêm sản phẩm.
- **`NHBD_KNOWLEDGE_BASE_COMPACT.md`** — kiến thức chuyên sâu (y khoa, chăn nuôi).

> Bot đã biết: giá nhung mật ong 850k/hũ, nhung tươi 1.8tr/lạng, rượu nhung,
> con giống, hotline Ms. Hạnh 0977 469 988... Bạn chỉ cần cập nhật khi có thay đổi.

---

## ✅ BƯỚC 5 — Chạy thử trên máy (chưa cần Facebook)

Trước khi nối Facebook, hãy thử nói chuyện với bot ngay trên máy:

```
python claude_bot.py
```

Gõ thử câu hỏi như: `nhung hươu tươi giá bao nhiêu?` và xem bot trả lời.
Gõ `thoat` để dừng.

➡️ Nếu bot trả lời hợp lý dựa trên file kiến thức → **bộ não đã hoạt động!**
Nếu báo lỗi về API key → kiểm tra lại Bước 3 và 4.

### Thử riêng tính năng trả lời COMMENT nhiều tầng

```
python test_comment.py
```

Lệnh này giả lập khách comment nhiều lần để bạn xem bot:
- Tầng 1-2: trả lời công khai, giấu giá, mời để lại SĐT/inbox.
- Tầng 3: chuyển sang nhắn tin riêng.
- Tự lưu khách để lại số điện thoại vào file `khach_hang.csv`.

---

## ✅ BƯỚC 6 — Đưa chatbot lên mạng (deploy miễn phí)

Facebook cần một địa chỉ web cố định để gửi tin nhắn tới. Ta dùng **Render.com**
(miễn phí). Cách dễ nhất:

1. Tạo tài khoản GitHub (https://github.com) và Render (https://render.com).
2. Đưa thư mục `nhung-huou-chatbot` lên GitHub (có thể nhờ hỗ trợ bước này).
3. Trên Render: **New** → **Web Service** → chọn repo GitHub của bạn.
4. Cấu hình:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Vào mục **Environment** trên Render, thêm 3 biến giống trong file `.env`:
   `ANTHROPIC_API_KEY`, `PAGE_ACCESS_TOKEN`, `VERIFY_TOKEN`.
6. Bấm **Deploy**. Khi xong, Render cho bạn 1 địa chỉ dạng
   `https://ten-cua-ban.onrender.com` → đây là địa chỉ webhook.

> 💡 Bước này hơi kỹ thuật. Nếu thấy khó, cứ dừng ở Bước 5 và nhắn lại,
> sẽ có người hướng dẫn chi tiết phần đưa lên GitHub + Render.

---

## ✅ BƯỚC 7 — Kết nối Fanpage Facebook

1. Vào https://developers.facebook.com → **My Apps** → **Create App**
   → chọn loại **Business** → đặt tên app.
2. Trong app, thêm sản phẩm **Messenger** → **Settings**.
3. Mục **Access Tokens**: chọn Fanpage của bạn → bấm **Generate Token**.
   Copy token này, dán vào `PAGE_ACCESS_TOKEN` (trong file `.env` và trên Render).
4. Mục **Webhooks** → **Add Callback URL**:
   - **Callback URL:** địa chỉ Render + `/webhook`
     (ví dụ `https://ten-cua-ban.onrender.com/webhook`)
   - **Verify Token:** dán đúng chuỗi `VERIFY_TOKEN` bạn đặt.
   - Bấm **Verify and Save**.
5. Mục **Webhook Fields**: tích chọn các mục sau:
   - **messages**, **messaging_postbacks** → để trả lời tin nhắn Messenger.
   - **feed** → để trả lời **comment** dưới bài đăng. ⬅️ QUAN TRỌNG cho tính năng comment.
6. Xong! Vào fanpage, dùng 1 tài khoản Facebook khác nhắn thử + comment thử → bot sẽ trả lời.

> ⚠️ Lúc đầu app ở chế độ "Development", chỉ admin/tester mới được bot trả lời.
> Khi chạy ổn, bạn cần gửi app để Facebook duyệt (App Review) với các quyền:
> - `pages_messaging` → gửi/nhận tin nhắn Messenger
> - `pages_read_engagement` → đọc comment của khách
> - `pages_manage_engagement` → trả lời/nhắn riêng từ comment
> Sau khi duyệt, mọi khách hàng mới được bot tự động trả lời.

---

## 💬 CHATBOT TRẢ LỜI COMMENT HOẠT ĐỘNG THẾ NÀO?

Bot hành xử như nhân viên thật, theo nhiều "tầng":

| Tầng | Khi nào | Bot làm gì |
|------|---------|-----------|
| **Tầng 1** | Khách comment lần đầu | Trả lời **công khai**, ngắn gọn. Nếu khách hỏi giá → mời để lại **SĐT** hoặc **inbox** (KHÔNG báo giá công khai). |
| **Tầng 2** | Khách comment tiếp | Trả lời công khai lần nữa, vẫn hướng khách về inbox/SĐT. |
| **Tầng 3 trở đi** | Khách vẫn comment | Bot **nhắn tin riêng (inbox)** tư vấn + xin SĐT, đồng thời để 1 dòng công khai báo "đã inbox". |

- Số tầng công khai chỉnh được qua `SO_TANG_CONG_KHAI` trong file `.env` (mặc định 2).
- **Vì sao giấu giá ở comment?** Đây là cách fanpage bán hàng chuyên nghiệp hay dùng:
  kéo khách về inbox để tư vấn kỹ, chốt đơn, và tránh đối thủ xem giá.
- Lưu ý kỹ thuật: Facebook chỉ cho nhắn tin riêng từ 1 comment **1 lần** và trong
  vòng **7 ngày** kể từ khi khách comment.

---

## 📋 KHÁCH HÀNG ĐỂ LẠI SỐ ĐIỆN THOẠI

Mỗi khi khách để lại số điện thoại (trong comment hoặc tin nhắn), bot **tự động
lưu** lại gồm: thời gian, tên, số điện thoại, **nguồn ("Chatbot FB - Comment" /
"Chatbot FB - Messenger")**, nội dung. Lưu vào 2 nơi:
1. **Google Sheet** (nếu đã cấu hình — xem bên dưới) — xem được mọi lúc trên điện thoại.
2. **File `khach_hang.csv`** (luôn có, mở bằng Excel) — bản dự phòng.

---

## 📊 CÀI GOOGLE SHEET ĐỂ LƯU KHÁCH (TÙY CHỌN)

Nếu muốn khách tự động chảy vào Google Sheet (tiện xem trên điện thoại, chia sẻ
cho nhân viên), làm theo các bước sau **một lần duy nhất**:

1. **Tạo Google Sheet mới** tại https://sheets.google.com → đặt tên ví dụ
   "Khách hàng Chatbot FB". Copy **ID** trong link:
   `docs.google.com/spreadsheets/d/`**`ID_Ở_ĐÂY`**`/edit`
2. Vào https://console.cloud.google.com → tạo 1 Project mới.
3. Vào **APIs & Services → Library** → bật **Google Sheets API**.
4. Vào **APIs & Services → Credentials → Create Credentials → Service account**.
   Tạo xong, bấm vào service account → tab **Keys → Add Key → JSON** → tải file về.
5. Đổi tên file JSON vừa tải thành **`google_credentials.json`**, đặt vào thư mục
   dự án (cùng chỗ với `app.py`).
6. Mở file JSON, copy giá trị **`client_email`** (dạng `...@...iam.gserviceaccount.com`).
   Quay lại Google Sheet → bấm **Share** → dán email đó vào → cấp quyền **Editor**.
7. Mở file `.env`, điền dòng: `GOOGLE_SHEET_ID=` + ID đã copy ở bước 1.

> Xong! Từ giờ mọi khách để lại SĐT sẽ tự động xuất hiện trong Google Sheet,
> ở tab "Khách Chatbot FB". Nếu chưa cấu hình, hệ thống vẫn lưu vào `khach_hang.csv`.

> ⚠️ Khi deploy lên Render (Bước 6): thêm nội dung file `google_credentials.json`
> vào Environment, hoặc nhắn để được hướng dẫn cách nạp credentials an toàn.

---

## 🌏 TRẢ LỜI ĐA NGÔN NGỮ (Việt / Trung / Hàn)

Bot tự nhận diện ngôn ngữ của khách:
- Khách nhắn TIẾNG TRUNG → bot trả lời bằng tiếng Trung.
- Khách nhắn TIẾNG HÀN → bot trả lời bằng tiếng Hàn.
- Còn lại → tiếng Việt (mặc định).

Áp dụng cho cả tin nhắn Messenger, comment, và tin theo đuổi. Mọi quy tắc khác
(không báo giá ở comment, báo giá đúng bước, mời liên hệ Ms. Hạnh...) giữ nguyên.
Tên riêng (Ms. Hạnh, Nhung Hươu Bổ Đà, website, hotline) luôn giữ nguyên.

---

## 🧠 BỘ NHỚ NGỮ CẢNH & 🔁 THEO ĐUỔI KHÁCH HÀNG

Bộ nhớ ngữ cảnh: Lịch sử trò chuyện của từng khách Messenger được lưu vào file
`khach_data.json`. Khách quay lại (kể cả sau nhiều ngày) bot vẫn nhớ đã trao đổi gì.

Theo đuổi tự động: Khách đã nhắn nhưng chưa phản hồi sau 24h, bot tự soạn 1 tin
nhẹ nhàng nhắc đúng chủ đề khách quan tâm và mời tư vấn tiếp.

Lệnh chạy:
  python theo_duoi.py test     (xem trước bot sẽ nhắn gì, KHÔNG gửi thật)
  python theo_duoi.py          (gửi thật cho khách quá 24h — cần đã nối Facebook)

CHO CHẠY TỰ ĐỘNG HÀNG NGÀY (Windows Task Scheduler):
1. Mở "Task Scheduler" (Bộ lập lịch tác vụ).
2. Create Basic Task → đặt tên "Theo duoi khach NHBD".
3. Trigger: Daily, chọn giờ (vd 9:00 sáng).
4. Action → Start a program:
   - Program/script: python
   - Add arguments: theo_duoi.py
   - Start in: (dán đường dẫn thư mục dự án này)
5. Finish.

Điều chỉnh trong file `.env`:
  FOLLOWUP_GIO_CHO=24   (số giờ chờ trước khi theo đuổi)
  FOLLOWUP_TOI_DA=3     (số lần theo đuổi tối đa/khách; để trống = không giới hạn)

⚠️ CHÍNH SÁCH FACEBOOK: Chỉ được nhắn tự do trong 24 GIỜ kể từ tin cuối của khách.
Sau 24h cần "message tag" (mã đã gắn sẵn tag HUMAN_AGENT — cho phép tới 7 ngày) hoặc
One-Time Notification. Theo đuổi quá dày hoặc sai chính sách có thể bị Facebook hạn chế
trang. Nên theo đuổi vừa phải (vd tối đa 3 lần, giãn cách hợp lý).

---

## 🔧 BẢO TRÌ & NÂNG CẤP

- **Sửa giá / sản phẩm / kịch bản bán hàng:** sửa file **`SYSTEM_PROMPT_NHBD_v1.md`**
  (chứa giá thật, sản phẩm, USP) — bot tự cập nhật, KHÔNG cần sửa code.
- **Sửa kiến thức chuyên sâu (y khoa, chăn nuôi):** sửa **`NHBD_KNOWLEDGE_BASE_COMPACT.md`**.
- **Bot trả lời thông minh hơn:** mở file `.env`, đổi dòng
  `CLAUDE_MODEL=claude-haiku-4-5-20251001` thành `CLAUDE_MODEL=claude-opus-4-8`
  (thông minh hơn nhưng tốn phí hơn một chút).
- **Chi phí Claude:** mỗi tin nhắn chỉ tốn vài chục đến vài trăm đồng (đã bật
  prompt caching để tiết kiệm). Theo dõi tại console.anthropic.com mục Usage.

---

## ❓ HAY GẶP LỖI

| Lỗi | Cách xử lý |
|-----|------------|
| `python` không nhận lệnh | Cài lại Python, nhớ tích "Add to PATH" (Bước 1) |
| `KeyError: ANTHROPIC_API_KEY` | Chưa tạo/điền file `.env` đúng (Bước 4) |
| `credit balance is too low` | Tài khoản Claude hết tiền → nạp credit tại console.anthropic.com mục Billing |
| Bot không trả lời trên FB | Kiểm tra Webhook đã Verify chưa, token còn đúng không |
| `pip` báo lỗi | Thử `python -m pip install -r requirements.txt` |
| Khách không vào Google Sheet | Kiểm tra đã Share sheet cho `client_email`, đã điền `GOOGLE_SHEET_ID` |

Chúc bạn thành công! 🦌
