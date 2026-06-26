"""
Tests for pure helper functions in claude_bot.py.
None of these tests touch the Anthropic API.
"""

import pytest

# Import only the pure functions — the module-level Anthropic client is
# initialised with ANTHROPIC_API_KEY="test-key" set in conftest.py.
from claude_bot import (
    _lam_sach_markdown,
    _phat_hien_ngon_ngu,
    _an_gia,
    _huong_dan_ngon_ngu,
)


class TestLamSachMarkdown:
    def test_strips_h1_heading(self):
        assert _lam_sach_markdown("# Tiêu đề") == "Tiêu đề"

    def test_strips_h2_heading(self):
        assert _lam_sach_markdown("## Mục lớn") == "Mục lớn"

    def test_strips_h3_heading(self):
        assert _lam_sach_markdown("### Mục nhỏ") == "Mục nhỏ"

    def test_strips_bold_double_asterisk(self):
        assert _lam_sach_markdown("**in đậm**") == "in đậm"

    def test_strips_bold_double_underscore(self):
        assert _lam_sach_markdown("__in đậm__") == "in đậm"

    def test_strips_italic_single_asterisk(self):
        assert _lam_sach_markdown("*in nghiêng*") == "in nghiêng"

    def test_converts_dash_bullet_to_circle(self):
        result = _lam_sach_markdown("- mục một")
        assert result == "• mục một"

    def test_converts_asterisk_bullet_to_circle(self):
        result = _lam_sach_markdown("* mục hai")
        assert result == "• mục hai"

    def test_strips_horizontal_rule_dashes(self):
        result = _lam_sach_markdown("trước\n---\nsau")
        assert "---" not in result

    def test_strips_horizontal_rule_equals(self):
        result = _lam_sach_markdown("trước\n===\nsau")
        assert "===" not in result

    def test_collapses_excess_blank_lines(self):
        result = _lam_sach_markdown("dòng 1\n\n\n\ndòng 2")
        assert "\n\n\n" not in result

    def test_plain_text_unchanged(self):
        text = "Dạ em là tư vấn viên của Nhung Hươu Bổ Đà"
        assert _lam_sach_markdown(text) == text

    def test_mixed_content(self):
        md = "## Sản phẩm\n\n**Nhung Hươu** rất tốt\n\n- Công dụng 1\n- Công dụng 2"
        result = _lam_sach_markdown(md)
        assert "##" not in result
        assert "**" not in result
        assert "• Công dụng 1" in result


class TestPhatHienNgonNgu:
    def test_korean_characters(self):
        assert _phat_hien_ngon_ngu("안녕하세요") == "ko"

    def test_chinese_characters(self):
        assert _phat_hien_ngon_ngu("你好") == "zh"

    def test_vietnamese_text(self):
        assert _phat_hien_ngon_ngu("Xin chào shop") == "vi"

    def test_latin_text(self):
        assert _phat_hien_ngon_ngu("Hello shop") == "vi"

    def test_empty_string(self):
        assert _phat_hien_ngon_ngu("") == "vi"

    def test_mixed_korean_and_latin(self):
        assert _phat_hien_ngon_ngu("Hello 안녕") == "ko"

    def test_mixed_chinese_and_latin(self):
        assert _phat_hien_ngon_ngu("Hello 你好") == "zh"


class TestAnGia:
    def test_hides_standard_vnd_price(self):
        result = _an_gia("Giá sản phẩm là 850.000 VNĐ ạ", "vi")
        assert "850.000" not in result

    def test_hides_vnd_per_unit(self):
        result = _an_gia("Giá 1.800.000 VNĐ/lạng", "vi")
        assert "1.800.000" not in result

    def test_hides_k_shorthand(self):
        result = _an_gia("khoảng 850k thôi ạ", "vi")
        assert "850k" not in result

    def test_hides_M_shorthand(self):
        result = _an_gia("chỉ 1.2M ạ", "vi")
        assert "1.2M" not in result

    def test_hides_trieu(self):
        result = _an_gia("giá 14 triệu nhé", "vi")
        assert "14 triệu" not in result

    def test_text_without_price_unchanged(self):
        text = "Dạ sản phẩm rất tốt cho sức khỏe ạ"
        assert _an_gia(text, "vi") == text

    def test_empty_string_unchanged(self):
        assert _an_gia("", "vi") == ""

    def test_uses_vietnamese_placeholder(self):
        result = _an_gia("Giá 850.000 VNĐ", "vi")
        from claude_bot import _THAY_GIA
        assert _THAY_GIA["vi"] in result

    def test_uses_chinese_placeholder(self):
        result = _an_gia("价格 850.000 VNĐ", "zh")
        from claude_bot import _THAY_GIA
        assert _THAY_GIA["zh"] in result

    def test_uses_korean_placeholder(self):
        result = _an_gia("가격 850.000 VNĐ", "ko")
        from claude_bot import _THAY_GIA
        assert _THAY_GIA["ko"] in result

    def test_unknown_lang_falls_back_to_vi(self):
        result = _an_gia("Giá 850.000 VNĐ", "en")
        from claude_bot import _THAY_GIA
        assert _THAY_GIA["vi"] in result


class TestHuongDanNgonNgu:
    def test_chinese_returns_nonempty_instruction(self):
        result = _huong_dan_ngon_ngu("zh")
        assert "TIẾNG TRUNG" in result

    def test_korean_returns_nonempty_instruction(self):
        result = _huong_dan_ngon_ngu("ko")
        assert "TIẾNG HÀN" in result

    def test_vietnamese_returns_empty_string(self):
        assert _huong_dan_ngon_ngu("vi") == ""

    def test_unknown_lang_returns_empty_string(self):
        assert _huong_dan_ngon_ngu("en") == ""

    def test_chinese_instruction_preserves_brand_names(self):
        result = _huong_dan_ngon_ngu("zh")
        assert "Ms. Hạnh" in result
        assert "Nhung Hươu Bổ Đà" in result

    def test_korean_instruction_preserves_brand_names(self):
        result = _huong_dan_ngon_ngu("ko")
        assert "Ms. Hạnh" in result
        assert "Nhung Hươu Bổ Đà" in result
