"""
claude_bot.py
-------------
"Bộ não" của chatbot Nhung Hươu Bổ Đà (HiHa Vitality).

Kiến thức được nạp từ 2 file thật:
  - SYSTEM_PROMPT_NHBD_v1.md       -> tính cách, quy tắc, sản phẩm, GIÁ thật
  - NHBD_KNOWLEDGE_BASE_COMPACT.md -> kiến thức chuyên sâu (y khoa, chăn nuôi)

Muốn đổi giá / sản phẩm / kịch bản -> sửa 2 file .md trên, KHÔNG cần sửa file này.
"""

import os
import re
import sys
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Đảm bảo in tiếng Việt ra màn hình Windows không bị lỗi mã hoá
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Model dùng để trả lời. Haiku rẻ + nhanh, hợp cho chatbot fanpage.
# Muốn câu trả lời "cao cấp" hơn -> đổi thành "claude-opus-4-8".
MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

_DIR = Path(__file__).parent


def _doc_file(ten: str) -> str:
    """Đọc nội dung 1 file kiến thức trong thư mục dự án (nếu có)."""
    f = _DIR / ten
    return f.read_text(encoding="utf-8") if f.exists() else ""


# Nạp kiến thức thật khi khởi động
_SYSTEM_PROMPT_NHBD = _doc_file("SYSTEM_PROMPT_NHBD_v1.md")
_KNOWLEDGE_COMPACT = _doc_file("NHBD_KNOWLEDGE_BASE_COMPACT.md")

# System prompt nền cho bot. Gộp prompt chính + kiến thức chuyên sâu.
SYSTEM_BASE = f"""{_SYSTEM_PROMPT_NHBD}

=== KIẾN THỨC CHUYÊN SÂU (dùng khi khách hỏi sâu về khoa học/chăn nuôi) ===
{_KNOWLEDGE_COMPACT}
=== HẾT KIẾN THỨC ===

=== PHONG CÁCH & QUY TẮC TRẢ LỜI (BẮT BUỘC — ƯU TIÊN CAO NHẤT, GHI ĐÈ phần trên) ===

0. XƯNG DANH — LÀ TƯ VẤN VIÊN, KHÔNG PHẢI BOT: Luôn hành xử và xưng hô như một
   TƯ VẤN VIÊN (nhân viên tư vấn) thật của Nhung Hươu Bổ Đà, xưng "em" - gọi
   "anh/chị". KHÔNG nêu tên riêng cá nhân. TUYỆT ĐỐI KHÔNG bao giờ tự gọi mình là
   "bot", "chatbot", "trợ lý ảo", "trợ lý AI", "AI", "trí tuệ nhân tạo", "máy",
   "hệ thống". Nếu khách hỏi "có phải bot/máy/AI không?", hãy trả lời tự nhiên,
   khéo léo: "Dạ em là tư vấn viên của bên Nhung Hươu Bổ Đà, luôn sẵn sàng hỗ trợ
   anh/chị ạ" — KHÔNG xác nhận mình là máy/AI. Câu mở đầu nên là "Em là tư vấn
   viên của Nhung Hươu Bổ Đà..." (KHÔNG dùng "trợ lý").

1. CỰC NGẮN GỌN & BÁM SÁT Ý: Tập trung đúng trọng tâm câu khách hỏi, tối đa 2-3
   câu ngắn (~40-60 từ). KHÔNG lan man, KHÔNG nói sang chuyện khách không hỏi,
   KHÔNG liệt kê dài. Mỗi tin chỉ 1 ý chính + 1 câu hỏi dẫn dắt. Thà ngắn rồi
   hỏi thêm, không nói dài. KHÔNG mở đầu câu trả lời bằng những nhãn như "Trả lời
   thẳng:", "Em xin trả lời:"... — đi thẳng vào nội dung một cách tự nhiên.

2. VĂN PHONG: Mềm mại, nghiêm túc, chuẩn mực, lịch sự. KHÔNG bông đùa, KHÔNG
   suồng sã. Xưng "em" - gọi "anh/chị". Emoji rất hạn chế (nhiều nhất 1, hoặc
   không dùng). KHÔNG dùng từ thô/chợ búa ("luộc", "xay", "chặt", "hàng",
   "ship"...); nếu tài liệu có thì diễn đạt lại thanh thoát ("luộc"→"sơ chế ở
   nhiệt độ thấp", "xay"→"nghiền mịn", "giao/ship"→"giao hàng tận nơi").

3. KHÔNG MARKDOWN: Viết văn bản thuần. KHÔNG dùng **in đậm**, #, bảng |, hay
   gạch đầu dòng "- ". Cần tách ý thì chỉ xuống dòng đơn giản.

4. TUÂN THỦ QUẢNG CÁO (THEO LUẬT VIỆT NAM — BẮT BUỘC):
   - Sản phẩm là THỰC PHẨM BỔ TRỢ / BỒI BỔ SỨC KHỎE, KHÔNG phải là thuốc và
     KHÔNG có tác dụng thay thế thuốc chữa bệnh.
   - TUYỆT ĐỐI KHÔNG cam kết, KHÔNG hứa hẹn hiệu quả. KHÔNG dùng: "chữa khỏi",
     "trị", "đặc trị", "hết bệnh", "100%", "cam kết hiệu quả", "đảm bảo khỏi".
     Chỉ dùng: "hỗ trợ", "góp phần", "giúp bồi bổ", "tăng cường".
   - Khi khách hỏi về bệnh lý, nói có chừng mực và khuyên tham khảo ý kiến bác sĩ
     nếu có bệnh nền hoặc đang dùng thuốc.

5. TẠO NIỀM TIN (nhắc khéo, tự nhiên, KHÔNG lặp ở mọi tin): Khi giới thiệu sản
   phẩm / khách còn băn khoăn / kết thúc tư vấn, có thể nhắc: sản phẩm đạt chứng
   nhận OCOP 3 sao, an toàn vệ sinh thực phẩm (ATVSTP), đầy đủ giấy chứng nhận;
   và mời khách tham khảo thêm tại website samnhungviet.com.vn.

6. BÁO GIÁ ĐÚNG THỜI ĐIỂM (quy tắc quan trọng): KHÔNG báo giá ngay khi khách vừa
   hỏi. Phải đi qua các bước tư vấn trước (xác định đối tượng → phân tích nhu cầu
   → gợi ý sản phẩm), CHỈ báo giá ở BƯỚC CUỐI cùng sau khi đã hiểu nhu cầu và đã
   gợi ý sản phẩm phù hợp. Nếu khách hỏi giá quá sớm, khéo léo hỏi nhu cầu trước
   (vd: "Để em tư vấn đúng sản phẩm và mức giá phù hợp nhất, cho em hỏi mình mua
   cho ai và cần hỗ trợ điều gì ạ?").

7. KỊCH BẢN TƯ VẤN (bám sát từng bước, mỗi tin chỉ đi 1 bước, không dồn):
   (1) Chào hỏi thân thiện, ngắn gọn.
   (2) Xác định đối tượng: mua cho ai, độ tuổi, tình trạng sức khỏe.
   (3) Phân tích nhu cầu chính của khách.
   (4) Gợi ý sản phẩm phù hợp (mô tả công dụng).
   (5) BƯỚC CUỐI — BÁO GIÁ: nêu giá sản phẩm đã gợi ý, ĐỒNG THỜI thông báo: liên hệ
       Ms. Hạnh 0977 469 988 để được tư vấn thêm và nhận NHIỀU ƯU ĐÃI hấp dẫn cho
       khách hàng; mời khách để lại SỐ ĐIỆN THOẠI hoặc EMAIL để được chăm sóc/đặt hàng.
   Mục tiêu: tư vấn đúng nhu cầu, báo giá ở bước cuối, và khách để lại SĐT/email.
   Dẫn dắt nhẹ nhàng, không thúc ép.

8. Luôn trả lời bằng tiếng Việt.
"""


def _lam_sach_markdown(text: str) -> str:
    """Lọc bỏ ký hiệu markdown để câu trả lời hiển thị sạch trên Messenger/comment
    (Facebook hiển thị nguyên ký tự markdown nên cần loại bỏ)."""
    # Bỏ ký hiệu tiêu đề đầu dòng: #, ##, ###...
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
    # Bỏ in đậm/nghiêng: **x** , __x__ , *x*
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"\*([^*\n]+)\*", r"\1", text)
    # Đổi gạch đầu dòng "- " hoặc "* " thành "• " cho thanh thoát
    text = re.sub(r"(?m)^\s*[-*]\s+", "• ", text)
    # Bỏ dấu gạch ngang ngăn cách kiểu markdown (--- hoặc ===)
    text = re.sub(r"(?m)^\s*([-=]{3,})\s*$", "", text)
    # Gọn các dòng trống thừa
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ====== NHẬN DIỆN NGÔN NGỮ (Việt / Trung / Hàn) ======
_RE_HANGUL = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏]")   # chữ Hàn
_RE_HAN = re.compile(r"[一-鿿㐀-䶿]")                    # chữ Hán (Trung)


def _phat_hien_ngon_ngu(text: str) -> str:
    """Trả về 'ko' (Hàn), 'zh' (Trung), hoặc 'vi' (Việt - mặc định)."""
    if not text:
        return "vi"
    if _RE_HANGUL.search(text):
        return "ko"
    if _RE_HAN.search(text):
        return "zh"
    return "vi"


def _huong_dan_ngon_ngu(lang: str) -> str:
    """Chỉ thị cho bot trả lời đúng ngôn ngữ của khách (ghi đè 'trả lời tiếng Việt')."""
    # Tên riêng PHẢI giữ nguyên, không dịch / không phiên âm
    giu_nguyen = ("Giữ NGUYÊN VĂN (không dịch, không phiên âm) các tên riêng: "
                  "'Ms. Hạnh', 'Nhung Hươu Bổ Đà', 'HiHa Vitality', 'Vân Hà, Bắc Ninh', "
                  "website 'samnhungviet.com.vn', số hotline '0977 469 988'.")
    if lang == "zh":
        return (
            "\n\n=== NGÔN NGỮ TRẢ LỜI (BẮT BUỘC) ===\n"
            "Khách đang nhắn bằng TIẾNG TRUNG. Hãy trả lời HOÀN TOÀN bằng tiếng Trung, "
            "dùng đúng kiểu chữ khách dùng (giản thể 简体 hoặc phồn thể 繁體). Vẫn giữ "
            "đúng thông tin sản phẩm, quy tắc tư vấn và quy tắc báo giá. " + giu_nguyen
        )
    if lang == "ko":
        return (
            "\n\n=== NGÔN NGỮ TRẢ LỜI (BẮT BUỘC) ===\n"
            "Khách đang nhắn bằng TIẾNG HÀN. Hãy trả lời HOÀN TOÀN bằng tiếng Hàn "
            "(한국어), lịch sự trang trọng. Vẫn giữ đúng thông tin sản phẩm, quy tắc tư "
            "vấn và quy tắc báo giá. " + giu_nguyen
        )
    return ""


# Lời thay thế khi ẩn giá — theo từng ngôn ngữ
_THAY_GIA = {
    "vi": "(em xin phép tư vấn kỹ rồi báo giá sau ạ)",
    "zh": "(稍后为您详细咨询并报价)",
    "ko": "(자세한 상담 후 가격을 안내해 드리겠습니다)",
}


def _an_gia(text: str, lang: str = "vi") -> str:
    """Ẩn con số giá (dùng cho GIAI ĐOẠN ĐẦU / comment công khai — khi chưa được
    phép báo giá). Thay con số bằng lời mời tư vấn (theo ngôn ngữ khách)."""
    if not text:
        return text
    thay = _THAY_GIA.get(lang, _THAY_GIA["vi"])
    # 850.000 VNĐ/hũ , 1.800.000 VNĐ/lạng ...
    text = re.sub(r"\d{1,3}(?:\.\d{3})+\s*(?:VNĐ|VND|đ)?(?:\s*/\s*\w+)?", thay, text)
    # 850k , 1.2M , 14 triệu ...
    text = re.sub(r"\b\d+(?:[.,]\d+)?\s*(?:k|K|M|triệu|nghìn)\b(?:\s*/\s*\w+)?", thay, text)
    return text


def _goi_claude(system_text: str, messages: list, max_tokens: int = 350) -> str:
    """Gọi Claude API với prompt caching để tiết kiệm chi phí."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=[{
            "type": "text",
            "text": system_text,
            "cache_control": {"type": "ephemeral"},  # cache để các lần sau rẻ hơn
        }],
        messages=messages,
    )
    # Lọc markdown để hiển thị sạch trên Messenger/comment
    return _lam_sach_markdown(response.content[0].text)


# Số lượt đầu (của khách) CHƯA được phép báo giá — phải tư vấn trước đã.
SO_LUOT_CHUA_BAO_GIA = 2


def tra_loi(tin_nhan_khach: str, lich_su: list | None = None) -> str:
    """
    Trả lời tin nhắn Messenger theo GIAI ĐOẠN:
    - 2 lượt đầu: chưa báo giá, tập trung xác định đối tượng + phân tích nhu cầu.
    - Từ lượt 3 (đã tư vấn đủ): được báo giá ở bước cuối + ưu đãi Ms. Hạnh.
    """
    lich_su = lich_su or []
    luot = len(lich_su) // 2 + 1  # đây là lượt thứ mấy của khách

    if luot <= SO_LUOT_CHUA_BAO_GIA:
        giai_doan = (
            "\n\n=== GIAI ĐOẠN HIỆN TẠI: ĐẦU CUỘC TRÒ CHUYỆN — CHƯA BÁO GIÁ ===\n"
            "Đây mới là lượt đầu, TUYỆT ĐỐI CHƯA nêu giá hay con số tiền nào. Hãy "
            "chào hỏi, xác định đối tượng (mua cho ai, độ tuổi, tình trạng) và phân "
            "tích nhu cầu. Nếu khách hỏi giá, khéo léo xin thông tin nhu cầu trước "
            "rồi hứa sẽ tư vấn sản phẩm và mức giá phù hợp nhất."
        )
    else:
        giai_doan = (
            "\n\n=== GIAI ĐOẠN HIỆN TẠI: ĐÃ TƯ VẤN ĐỦ — ĐƯỢC BÁO GIÁ ===\n"
            "Đã hiểu nhu cầu khách. Bây giờ hãy gợi ý sản phẩm phù hợp và BÁO GIÁ sản "
            "phẩm đó. Khi báo giá, thông báo khách liên hệ Ms. Hạnh 0977 469 988 để "
            "nhận thêm nhiều ưu đãi, và mời khách để lại SỐ ĐIỆN THOẠI hoặc EMAIL."
        )

    # Nhận diện ngôn ngữ khách (Việt / Trung / Hàn) để trả lời đúng ngôn ngữ
    lang = _phat_hien_ngon_ngu(tin_nhan_khach)
    system = SYSTEM_BASE + giai_doan + _huong_dan_ngon_ngu(lang)

    messages = list(lich_su)
    messages.append({"role": "user", "content": tin_nhan_khach})
    try:
        reply = _goi_claude(system, messages)
        # Giai đoạn đầu: chặn giá lần cuối phòng khi model lỡ nêu
        if luot <= SO_LUOT_CHUA_BAO_GIA:
            reply = _an_gia(reply, lang)
        return reply
    except Exception as e:
        print(f"[LỖI Claude API] {e}")
        return ("Dạ shop xin lỗi, hệ thống đang bận một chút ạ. Anh/chị nhắn lại "
                "giúp em sau ít phút, hoặc để lại số điện thoại để bên em gọi tư vấn nhé! "
                "Hotline Ms. Hạnh: 0977 469 988 🦌")


def tra_loi_comment(noi_dung_comment: str, tang: int = 1, ten_khach: str = "") -> str:
    """
    Tạo câu trả lời cho COMMENT dưới bài đăng (hành xử như nhân viên thật).

    tang 1-2 -> trả lời CÔNG KHAI: ngắn, tự nhiên, KHÔNG báo giá công khai,
                mời khách để lại SĐT hoặc nhắn tin (inbox) để được tư vấn & báo giá.
    tang >=3 -> NHẮN TIN RIÊNG (inbox): tư vấn đầy đủ, có thể báo giá, xin SĐT.
    """
    chao = f"Khách bình luận tên là: {ten_khach}.\n" if ten_khach else ""

    if tang >= 3:
        tinh_huong = (
            f"{chao}Bạn vừa chuyển sang NHẮN TIN RIÊNG (Messenger) với khách sau khi "
            "đã trả lời comment công khai vài lần. Hãy chào thân mật (kèm tên nếu có), "
            "cảm ơn khách đã quan tâm và mời khách tiếp tục trao đổi tại đây để được "
            "tư vấn kỹ. KHÔNG nêu giá trong tin này — hãy bắt đầu bằng việc hỏi nhu "
            "cầu (mua cho ai, cần hỗ trợ điều gì). Có thể mời khách để lại SỐ ĐIỆN "
            "THOẠI hoặc EMAIL."
        )
    else:
        tinh_huong = (
            f"{chao}Bạn đang TRẢ LỜI COMMENT CÔNG KHAI dưới bài đăng (lần thứ {tang}).\n\n"
            "⚠️ QUY TẮC BẮT BUỘC — ƯU TIÊN CAO NHẤT:\n"
            "1. TUYỆT ĐỐI KHÔNG nêu BẤT KỲ con số giá nào, không khoảng giá, không "
            "khuyến mãi cụ thể.\n"
            "2. Trả lời THẬT NGẮN (1-2 câu), tự nhiên, ấm áp, đúng trọng tâm khách hỏi.\n"
            "3. Đến đoạn khách hỏi giá hoặc muốn mua: lịch sự MỜI KHÁCH NHẮN TIN "
            "(inbox/IB) cho shop để được tư vấn chi tiết và báo giá. Có thể kèm hotline "
            "Ms. Hạnh 0977 469 988.\n"
            "4. Có thể nói ngắn gọn về công dụng sản phẩm, nhưng KHÔNG nói giá."
        )

    lang = _phat_hien_ngon_ngu(noi_dung_comment)
    system = (SYSTEM_BASE + "\n\n=== TÌNH HUỐNG HIỆN TẠI ===\n" + tinh_huong
              + _huong_dan_ngon_ngu(lang))
    try:
        reply = _goi_claude(system, [{"role": "user", "content": noi_dung_comment}], max_tokens=300)
        # COMMENT (mọi tầng): TUYỆT ĐỐI không để lộ giá — giá chỉ báo trong Messenger
        return _an_gia(reply, lang)
    except Exception as e:
        print(f"[LỖI Claude API - comment] {e}")
        return "Dạ anh/chị nhắn tin (inbox) cho shop để được tư vấn chi tiết giúp em nhé ạ! 🦌"


def tao_tin_theo_duoi(lich_su: list, lan_thu: int = 1) -> str:
    """Soạn 1 tin nhắn THEO ĐUỔI khách dựa trên hội thoại trước (khách chưa phản hồi).
    lan_thu: lần theo đuổi thứ mấy (càng về sau giọng càng nhẹ nhàng)."""
    if not lich_su:
        return ""
    huong = (
        "\n\n=== NHIỆM VỤ: SOẠN TIN THEO ĐUỔI KHÁCH (PROACTIVE) ===\n"
        f"Khách đã nhắn tin trước đây nhưng đã một thời gian chưa phản hồi (đây là "
        f"lần theo đuổi thứ {lan_thu}). Dựa vào hội thoại phía trên, hãy soạn MỘT tin "
        "nhắn NGẮN (1-2 câu), nhẹ nhàng, lịch sự, chủ động hỏi thăm: NHẮC ĐÚNG chủ đề "
        "hoặc sản phẩm mà khách đã quan tâm, hỏi anh/chị còn cần em hỗ trợ thêm gì "
        "không, và mời để lại số điện thoại nếu tiện để bên em tư vấn. KHÔNG thúc ép, "
        "KHÔNG báo giá. Nếu là lần theo đuổi thứ 2 trở đi, giọng càng nhẹ nhàng, tôn "
        "trọng, tránh làm phiền khách."
    )
    # Theo đuổi bằng đúng ngôn ngữ khách đã dùng (tin gần nhất của khách)
    tin_khach = next((m["content"] for m in reversed(lich_su) if m.get("role") == "user"), "")
    lang = _phat_hien_ngon_ngu(tin_khach)

    messages = list(lich_su)
    messages.append({"role": "user",
                     "content": "[Hệ thống: khách chưa phản hồi, hãy chủ động soạn tin theo đuổi như hướng dẫn.]"})
    try:
        return _goi_claude(SYSTEM_BASE + huong + _huong_dan_ngon_ngu(lang), messages, max_tokens=200)
    except Exception as e:
        print(f"[LỖI tạo tin theo đuổi] {e}")
        return ""


# Chạy thử nhanh từ terminal: python claude_bot.py
if __name__ == "__main__":
    print("=== Thử nghiệm chatbot Nhung Hươu Bổ Đà (gõ 'thoat' để dừng) ===")
    history = []
    while True:
        cau_hoi = input("\nKhách: ")
        if cau_hoi.strip().lower() in ("thoat", "thoát", "exit", "quit"):
            break
        tl = tra_loi(cau_hoi, history)
        print(f"Bot: {tl}")
        history.append({"role": "user", "content": cau_hoi})
        history.append({"role": "assistant", "content": tl})
