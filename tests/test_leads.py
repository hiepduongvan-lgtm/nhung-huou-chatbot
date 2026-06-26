"""
Tests for leads.py — phone/email detection and lead capture logic.
"""

import pytest
from leads import tim_so_dien_thoai, tim_email, xu_ly_lead


class TestTimSoDienThoai:
    def test_standard_10_digit(self):
        assert tim_so_dien_thoai("0987654321") == "0987654321"

    def test_dotted_format(self):
        assert tim_so_dien_thoai("098.765.4321") == "0987654321"

    def test_spaced_format(self):
        assert tim_so_dien_thoai("0987 654 321") == "0987654321"

    def test_plus84_prefix(self):
        assert tim_so_dien_thoai("+84912345678") == "0912345678"

    def test_84_prefix_11_chars(self):
        assert tim_so_dien_thoai("84912345678") == "0912345678"

    def test_number_embedded_in_sentence(self):
        assert tim_so_dien_thoai("gọi cho mình 0912345678 nhé shop") == "0912345678"

    def test_number_with_context(self):
        assert tim_so_dien_thoai("Shop ơi sđt mình 0977469988 nhé") == "0977469988"

    def test_9_digit_returns_none(self):
        assert tim_so_dien_thoai("098765432") is None

    def test_empty_string_returns_none(self):
        assert tim_so_dien_thoai("") is None

    def test_none_input_returns_none(self):
        assert tim_so_dien_thoai(None) is None

    def test_no_phone_in_text(self):
        assert tim_so_dien_thoai("xin chào shop ơi") is None

    def test_returns_first_number_when_multiple(self):
        result = tim_so_dien_thoai("0911111111 hoặc 0922222222")
        assert result == "0911111111"

    def test_hyphen_separated(self):
        assert tim_so_dien_thoai("098-765-4321") == "0987654321"


class TestTimEmail:
    def test_simple_gmail(self):
        assert tim_email("user@gmail.com") == "user@gmail.com"

    def test_normalised_to_lowercase(self):
        assert tim_email("User@Gmail.COM") == "user@gmail.com"

    def test_email_in_sentence(self):
        assert tim_email("mail mình là nguyenvana@gmail.com gửi báo giá nhé") == "nguyenvana@gmail.com"

    def test_subdomain_email(self):
        assert tim_email("b.tran@yahoo.com.vn") == "b.tran@yahoo.com.vn"

    def test_no_email_returns_none(self):
        assert tim_email("không có email nào ở đây") is None

    def test_empty_string_returns_none(self):
        assert tim_email("") is None

    def test_none_input_returns_none(self):
        assert tim_email(None) is None

    def test_returns_first_email_when_multiple(self):
        result = tim_email("a@foo.com và b@bar.com")
        assert result == "a@foo.com"

    def test_email_with_plus_sign(self):
        assert tim_email("user+tag@example.com") == "user+tag@example.com"


class TestXuLyLead:
    def test_phone_found_saves_and_returns(self, mocker):
        mock_luu = mocker.patch("leads.luu_khach_hang")
        sdt, email = xu_ly_lead("Khách A", "sđt 0912345678 nhé", "Messenger")
        assert sdt == "0912345678"
        assert email is None
        mock_luu.assert_called_once()

    def test_email_found_saves_and_returns(self, mocker):
        mock_luu = mocker.patch("leads.luu_khach_hang")
        sdt, email = xu_ly_lead("Khách B", "email a@b.com", "Comment")
        assert sdt is None
        assert email == "a@b.com"
        mock_luu.assert_called_once()

    def test_both_found_saves_and_returns(self, mocker):
        mock_luu = mocker.patch("leads.luu_khach_hang")
        sdt, email = xu_ly_lead("Khách C", "sđt 0912345678 email a@b.com", "Messenger")
        assert sdt == "0912345678"
        assert email == "a@b.com"
        mock_luu.assert_called_once()

    def test_neither_found_does_not_save(self, mocker):
        mock_luu = mocker.patch("leads.luu_khach_hang")
        sdt, email = xu_ly_lead("Khách D", "xin chào shop", "Messenger")
        assert sdt is None
        assert email is None
        mock_luu.assert_not_called()
