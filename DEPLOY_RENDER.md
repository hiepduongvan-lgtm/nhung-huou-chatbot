# 🚀 GIAI ĐOẠN 3 — ĐƯA CHATBOT LÊN MẠNG & KẾT NỐI FANPAGE

> Mục tiêu: chatbot chạy 24/7 trên Render.com (miễn phí) và trả lời khách thật
> trên Fanpage Facebook. Làm theo 4 phần A → B → C → D, từ trên xuống.
>
> ⚠️ KHÔNG chia sẻ file `.env`, `google_credentials.json` cho ai và KHÔNG đưa
> chúng lên mạng. Các thông tin bí mật sẽ nhập trực tiếp trên Render.

Tổng quan thứ tự:
- PHẦN A — Đưa code lên GitHub
- PHẦN B — Deploy lên Render.com (lấy địa chỉ web)
- PHẦN C — Tạo App Facebook + kết nối Webhook với Fanpage
- PHẦN D — Test với tài khoản phụ

---

## 📦 PHẦN A — ĐƯA CODE LÊN GITHUB

Render lấy code từ GitHub. Cách dễ nhất (không cần gõ lệnh) là dùng **GitHub Desktop**.
(Code của bạn đã được chuẩn bị sẵn thành một "kho git" — chỉ cần đẩy lên.)

1. Tạo tài khoản GitHub: vào https://github.com → Sign up (miễn phí).
2. Tải **GitHub Desktop**: https://desktop.github.com → cài đặt → đăng nhập tài khoản GitHub.
3. Trong GitHub Desktop: **File → Add local repository** →
   chọn thư mục dự án:
   `D:\Nhung hươu bổ đà\...\Projec Hihavitality\Dự án FB chatbot`
   → bấm **Add repository**.
4. Bấm nút **Publish repository** (góc trên bên phải).
   - **Name:** ví dụ `chatbot-nhung-huou`
   - ✅ TÍCH ô **"Keep this code private"** (để code riêng tư, người ngoài không xem được)
   - Bấm **Publish repository**.

✅ Xong! Code đã lên GitHub (riêng tư). Sau này mỗi khi sửa code, vào GitHub Desktop
bấm **Commit** rồi **Push** là cập nhật lên mạng.

> Lưu ý: file `.env` và `google_credentials.json` đã được cấu hình BỎ QUA tự động —
> chúng KHÔNG bị đưa lên GitHub. Yên tâm về bảo mật.

---

## ☁️ PHẦN B — DEPLOY LÊN RENDER.COM

1. Tạo tài khoản: https://render.com → **Get Started** → đăng nhập **bằng GitHub**
   (Sign in with GitHub) để Render kết nối được với kho code của bạn.
2. Trên Render bấm **New +** (góc trên phải) → chọn **Blueprint**.
   (Blueprint sẽ tự đọc file `render.yaml` có sẵn trong code và dựng mọi thứ.)
3. Chọn kho code `chatbot-nhung-huou` vừa publish → bấm **Connect**.
   - Nếu Render chưa thấy kho: bấm **Configure account** → cấp quyền cho Render
     truy cập kho riêng tư của bạn.
4. Render hiện ra dịch vụ tên `chatbot-nhung-huou-bo-da`. Nó sẽ hỏi bạn nhập
   các biến BÍ MẬT (vì `render.yaml` để trống chúng cho an toàn). Điền:
   - **ANTHROPIC_API_KEY** = API key Claude của bạn (lấy trong file `.env`)
   - **PAGE_ACCESS_TOKEN** = để TẠM TRỐNG (sẽ lấy ở PHẦN C, điền sau cũng được)
   - **VERIFY_TOKEN** = một chuỗi tự đặt, ví dụ `nhunghuouboda2026`
     (GHI NHỚ chuỗi này, lát cần dùng ở PHẦN C)
5. Bấm **Apply** / **Create**. Render bắt đầu dựng (mất 2–5 phút).
6. Khi xong, Render cho bạn một địa chỉ web dạng:
   **`https://chatbot-nhung-huou-bo-da.onrender.com`**
   👉 Mở thử địa chỉ này — nếu hiện dòng "Chatbot Nhung Huou Bo Da dang chay!"
   là **THÀNH CÔNG**. Ghi nhớ địa chỉ này (gọi là ĐỊA CHỈ RENDER).

> ⚠️ Gói miễn phí của Render sẽ "ngủ" sau ~15 phút không ai dùng. Khi có tin nhắn
> mới, nó "thức dậy" mất ~30–50 giây (tin nhắn đầu tiên có thể chậm). Muốn luôn
> chạy nhanh thì nâng gói trả phí ($7/tháng). Giai đoạn đầu cứ dùng miễn phí.

---

## 🔗 PHẦN C — TẠO APP FACEBOOK & KẾT NỐI WEBHOOK

### C1. Tạo App và lấy Page Access Token
1. Vào https://developers.facebook.com → **My Apps** → **Create App**.
2. Chọn loại **Business** → đặt tên app (vd "Chatbot NHBD") → tạo.
3. Trong app, tìm mục **Messenger** → bấm **Set up**.
4. Kéo xuống **Access Tokens** → bấm **Add or remove Pages** → chọn **Fanpage
   Nhung Hươu Bổ Đà** → cấp quyền đầy đủ.
5. Sau khi thêm, bấm **Generate Token** cạnh tên Fanpage → **COPY** chuỗi token.
6. Quay lại **Render** → dịch vụ của bạn → tab **Environment** → sửa biến
   **PAGE_ACCESS_TOKEN** = dán token vừa copy → **Save Changes**
   (Render sẽ tự khởi động lại dịch vụ).

### C2. Cấu hình Webhook
1. Vẫn trong Messenger settings, kéo tới mục **Webhooks** → bấm
   **Add Callback URL** (hoặc **Edit Callback URL**).
   - **Callback URL:** ĐỊA CHỈ RENDER + `/webhook`
     ví dụ: `https://chatbot-nhung-huou-bo-da.onrender.com/webhook`
   - **Verify Token:** dán đúng chuỗi `VERIFY_TOKEN` đã đặt ở PHẦN B (bước 4).
   - Bấm **Verify and Save**.
   > Nếu báo lỗi xác minh: mở ĐỊA CHỈ RENDER một lần cho dịch vụ "thức dậy",
   > đợi 1 phút rồi thử lại.
2. Sau khi lưu, ở mục Webhooks bấm **Add subscriptions** cho Fanpage và TÍCH chọn:
   - ✅ **messages**
   - ✅ **messaging_postbacks**
   - ✅ **feed**  ⬅️ (để bot trả lời cả COMMENT dưới bài đăng)

### C3. Xin quyền (App Review) để chạy với mọi khách
- Lúc đầu app ở chế độ **Development** — chỉ người có vai trò trong app mới được
  bot trả lời (đủ để TEST ở PHẦN D).
- Để mọi khách hàng được trả lời, vào **App Review → Permissions and Features**,
  xin duyệt 3 quyền: `pages_messaging`, `pages_read_engagement`,
  `pages_manage_engagement`. Sau khi được duyệt, chuyển app sang **Live**.

---

## 🧪 PHẦN D — TEST VỚI TÀI KHOẢN PHỤ

Vì app đang ở chế độ Development, cần thêm tài khoản phụ làm "Người kiểm thử":

1. Trong app Facebook → **App Roles / Roles → Roles** → **Add People** →
   **Testers** → nhập tên/tài khoản phụ của bạn → gửi lời mời.
2. Đăng nhập tài khoản phụ → vào https://developers.facebook.com → chấp nhận lời mời.
3. Dùng tài khoản phụ:
   - Mở **Fanpage Nhung Hươu Bổ Đà** → nhắn tin (Messenger) thử → bot phải trả lời.
   - Vào một **bài đăng** → để lại **comment** thử → bot phải trả lời comment.
4. Kiểm tra:
   - Bot trả lời đúng giọng tư vấn viên, đúng quy tắc báo giá.
   - Để lại thử số điện thoại/email trong tin nhắn → kiểm tra có lưu vào
     Google Sheet / file khách hàng không.

✅ Nếu các bước trên chạy đúng → chatbot đã LÊN SÓNG thành công!

---

## ⚠️ MẤY LƯU Ý QUAN TRỌNG SAU KHI DEPLOY

- **Lưu khách hàng:** Trên Render miễn phí, file `khach_hang.csv` và `khach_data.json`
  sẽ bị xóa mỗi khi dịch vụ khởi động lại. Vì vậy NÊN bật **Google Sheet** (xem
  HUONG_DAN.md mục 📊) để lưu khách bền vững. Với Google Sheet, thêm biến môi trường
  trên Render: `GOOGLE_SHEET_ID` và nội dung file credentials (nhắn để được hướng dẫn
  cách nạp credentials an toàn lên Render).
- **Bộ nhớ ngữ cảnh:** cũng lưu trong file nên sẽ reset khi dịch vụ khởi động lại
  (gói miễn phí). Cần nhớ lâu dài bền vững thì dùng Render Disk (trả phí) hoặc
  database — khi cần nhắn để nâng cấp.
- **Tính năng theo đuổi khách (`theo_duoi.py`):** cần chạy định kỳ. Render miễn phí
  không có sẵn lịch chạy; có thể dùng Render **Cron Job** (trả phí) hoặc một dịch vụ
  gọi định kỳ. Trước mắt vẫn chạy được thủ công trên máy bạn: `python theo_duoi.py`.
- **Cập nhật code sau này:** sửa file trên máy → mở GitHub Desktop → **Commit** →
  **Push**. Render tự động deploy lại bản mới sau ~2–3 phút.
