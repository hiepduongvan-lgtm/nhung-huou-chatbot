# 🚀 HƯỚNG DẪN APP REVIEW — CHATBOT NHUNG HƯƠU BỔ ĐÀ

> Mục tiêu: Để bot phục vụ MỌI khách hàng (không chỉ admin/tester) và bật trả lời
> comment công khai. Facebook duyệt thường 3-7 ngày.

---

## ✅ CHUẨN BỊ TRƯỚC KHI NỘP (checklist)

1. [ ] **Privacy Policy URL** — đăng file PRIVACY_POLICY.md lên website, lấy link công khai.
   Điền vào: App → Settings → Basic → **Privacy Policy URL**.
2. [ ] **App Icon** — logo 1024×1024 px (dùng logo Nhung Hươu Bổ Đà).
   Điền vào: App → Settings → Basic → App Icon.
3. [ ] **Category** — chọn "Messaging" hoặc "Business".
4. [ ] **Xác minh** — App → Settings → cuộn xuống **Business/Individual Verification**.
   Cá nhân: làm **Individual Verification** (cần CMND/CCCD). (Một số quyền có thể yêu cầu
   Business Verification — nếu Facebook đòi, làm theo hướng dẫn của họ.)
5. [ ] **Data Handling** — App Review → trả lời bảng câu hỏi xử lý dữ liệu (Data Use Checkup).
6. [ ] **Video demo** — quay theo kịch bản bên dưới, tải lên YouTube (chế độ Unlisted) hoặc
   tải trực tiếp khi nộp.

---

## 📝 LỜI MÔ TẢ TỪNG QUYỀN (copy y nguyên, tiếng Anh cho người duyệt)

### 1) pages_messaging
**How your app uses this permission:**
> Our chatbot provides customer service for our Facebook Page "Nhung Huou Bo Da", a
> business selling deer velvet health supplements. When a customer sends a message to
> our Page, the bot reads the message and replies with product consultation, answers
> questions, and helps the customer leave their phone number or email for follow-up by
> our staff. We only message users who have first messaged our Page, within Facebook's
> standard messaging window.

### 2) pages_read_engagement
**How your app uses this permission:**
> Used to read the content of incoming messages and basic Page engagement so the chatbot
> can understand customer inquiries and respond with relevant product information.

### 3) pages_manage_metadata
**How your app uses this permission:**
> Used to subscribe our app to the Page's webhook events (messages and feed) so the bot
> receives customer messages and comments in real time and can respond promptly.

### 4) pages_manage_engagement
**How your app uses this permission:**
> Used to reply to customer comments on our Page's posts. The bot posts a helpful public
> reply and invites the customer to continue in a private message for detailed consultation.

### 5) pages_read_user_content
**How your app uses this permission:**
> Used to read the text of customer comments on our Page's posts so the bot can understand
> the comment and provide a relevant reply or send a private message to assist the customer.

---

## 🎬 KỊCH BẢN VIDEO DEMO (quay màn hình ~2-3 phút)

Quay rõ ràng, có thể vừa quay vừa nói (hoặc phụ đề). Trình tự:

1. **Mở đầu:** Quay màn hình hiện Fanpage "Nhung Hươu Bổ Đà" và nói: "This is our business
   Page selling deer velvet products. Our chatbot provides customer service."

2. **Demo tin nhắn (pages_messaging, pages_read_engagement):**
   - Dùng 1 tài khoản khác (hoặc điện thoại) nhắn cho Fanpage: "Cho hỏi nhung hươu mật ong".
   - Quay cảnh bot trả lời tư vấn.
   - Nhắn tiếp để lại số điện thoại → quay cảnh bot ghi nhận.

3. **Demo comment (pages_manage_engagement, pages_read_user_content, pages_manage_metadata):**
   - Dùng tài khoản khác comment dưới 1 bài đăng: "giá bao nhiêu shop".
   - Quay cảnh bot trả lời comment / nhắn tin riêng cho người comment.

4. **Kết:** Nói rõ "The bot only assists customers who contact our Page, and we respect
   user privacy per our Privacy Policy."

> 💡 Mẹo: Trong lúc quay, NÊN đang ở chế độ Development với tài khoản tester để bot trả lời
> được (chứng minh tính năng hoạt động).

---

## 📤 CÁC BƯỚC NỘP

1. App Dashboard → **App Review → Permissions and Features**.
2. Với từng quyền ở trên, bấm **Request Advanced Access**.
3. Điền **lời mô tả** (mục trên) + **hướng dẫn cho người duyệt** (tóm tắt kịch bản video)
   + **tải video demo**.
4. Hoàn tất **Verification** + **Privacy Policy URL** + **Data Use Checkup**.
5. Bấm **Submit for Review**.
6. Chờ Facebook duyệt (3-7 ngày). Có thể bị hỏi thêm — trả lời rõ ràng, hợp tác.

---

## ✅ SAU KHI ĐƯỢC DUYỆT

1. Chuyển App sang chế độ **Live** (gạt công tắc ở đầu trang App Dashboard).
2. Bot tự động phục vụ **mọi khách hàng** (không chỉ admin/tester).
3. Bật comment công khai: trên Render, thêm biến môi trường **COMMENT_CONG_KHAI=1**
   → bot trả lời comment công khai 3 lần rồi mời inbox (như đã code sẵn).

🎉 Lúc đó chatbot chính thức "lên sóng" hoàn toàn!
