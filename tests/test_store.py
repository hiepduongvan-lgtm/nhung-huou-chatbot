"""
Tests for store.py — persistent conversation memory.

The `isolate_store` fixture in conftest.py redirects FILE_DATA to a tmp_path
file automatically, so every test starts with a clean slate.
"""

import json
from datetime import datetime, timedelta

import pytest
import store


def _write_raw(data: dict, tmp_path):
    """Helper: write raw dict to the temp store file."""
    store.FILE_DATA.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class TestLayKhach:
    def test_unknown_uid_returns_none(self):
        assert store.lay_khach("uid_unknown") is None

    def test_known_uid_returns_dict(self):
        store.ghi_tin_khach("u1", "Nguyễn A", "xin chào", "Dạ chào anh!")
        result = store.lay_khach("u1")
        assert result is not None
        assert result["ten"] == "Nguyễn A"

    def test_uid_coerced_to_string(self):
        store.ghi_tin_khach(123, "Khách số", "hi", "hi back")
        assert store.lay_khach("123") is not None
        assert store.lay_khach(123) is not None


class TestLayLichSu:
    def test_unknown_uid_returns_empty_list(self):
        assert store.lay_lich_su("nobody") == []

    def test_returns_conversation_history(self):
        store.ghi_tin_khach("u2", "", "hỏi 1", "trả lời 1")
        history = store.lay_lich_su("u2")
        assert len(history) == 2
        assert history[0] == {"role": "user", "content": "hỏi 1"}
        assert history[1] == {"role": "assistant", "content": "trả lời 1"}


class TestGhiTinKhach:
    def test_creates_new_customer_record(self):
        store.ghi_tin_khach("u3", "Trần B", "xin chào", "Dạ!")
        kh = store.lay_khach("u3")
        assert kh["ten"] == "Trần B"
        assert kh["so_lan_theo_duoi"] == 0
        assert kh["lan_cuoi_khach"] is not None

    def test_appends_messages(self):
        store.ghi_tin_khach("u4", "", "tin 1", "reply 1")
        store.ghi_tin_khach("u4", "", "tin 2", "reply 2")
        history = store.lay_lich_su("u4")
        assert len(history) == 4

    def test_truncates_history_at_limit(self):
        # Build a history of 38 messages already in the store
        msgs = []
        for i in range(19):
            msgs.append({"role": "user", "content": f"u{i}"})
            msgs.append({"role": "assistant", "content": f"a{i}"})
        _write_raw({"u5": {"ten": "", "lich_su": msgs, "so_lan_theo_duoi": 0,
                            "lan_cuoi_khach": None, "lan_theo_duoi_cuoi": None}},
                   None)
        # Adding 2 more messages (1 turn) pushes total to 40 — exactly the limit
        store.ghi_tin_khach("u5", "", "mới nhất", "trả lời mới")
        history = store.lay_lich_su("u5")
        assert len(history) == store.GIOI_HAN_LICH_SU

    def test_adding_beyond_limit_drops_oldest(self):
        msgs = []
        for i in range(20):
            msgs.append({"role": "user", "content": f"u{i}"})
            msgs.append({"role": "assistant", "content": f"a{i}"})
        _write_raw({"u6": {"ten": "", "lich_su": msgs, "so_lan_theo_duoi": 0,
                            "lan_cuoi_khach": None, "lan_theo_duoi_cuoi": None}},
                   None)
        store.ghi_tin_khach("u6", "", "mới nhất", "trả lời mới")
        history = store.lay_lich_su("u6")
        assert len(history) == store.GIOI_HAN_LICH_SU
        # The newest messages should be present
        assert history[-2]["content"] == "mới nhất"
        assert history[-1]["content"] == "trả lời mới"

    def test_resets_follow_up_counter(self):
        _write_raw({"u7": {"ten": "", "lich_su": [], "so_lan_theo_duoi": 3,
                            "lan_cuoi_khach": "2026-01-01T00:00:00",
                            "lan_theo_duoi_cuoi": "2026-01-02T00:00:00"}}, None)
        store.ghi_tin_khach("u7", "", "quay lại rồi", "Dạ!")
        kh = store.lay_khach("u7")
        assert kh["so_lan_theo_duoi"] == 0
        assert kh["lan_theo_duoi_cuoi"] is None

    def test_updates_ten_when_provided(self):
        store.ghi_tin_khach("u8", "Lê C", "hi", "hi")
        store.ghi_tin_khach("u8", "Lê Cường", "hi2", "hi2")
        assert store.lay_khach("u8")["ten"] == "Lê Cường"

    def test_preserves_ten_when_empty(self):
        store.ghi_tin_khach("u9", "Phạm D", "hi", "hi")
        store.ghi_tin_khach("u9", "", "hi2", "hi2")
        assert store.lay_khach("u9")["ten"] == "Phạm D"


class TestGhiTheoDuoi:
    def test_increments_counter(self):
        store.ghi_tin_khach("u10", "", "ban đầu", "ok")
        store.ghi_theo_duoi("u10", "Anh/chị còn cần tư vấn không ạ?")
        assert store.lay_khach("u10")["so_lan_theo_duoi"] == 1

    def test_appends_assistant_message(self):
        store.ghi_tin_khach("u11", "", "hi", "hi")
        store.ghi_theo_duoi("u11", "Tin theo đuổi")
        history = store.lay_lich_su("u11")
        assert history[-1] == {"role": "assistant", "content": "Tin theo đuổi"}

    def test_sets_lan_theo_duoi_cuoi(self):
        store.ghi_tin_khach("u12", "", "hi", "hi")
        store.ghi_theo_duoi("u12", "Theo đuổi")
        assert store.lay_khach("u12")["lan_theo_duoi_cuoi"] is not None

    def test_noop_for_unknown_uid(self):
        store.ghi_theo_duoi("uid_nonexistent", "ignored")
        assert store.lay_khach("uid_nonexistent") is None

    def test_multiple_follow_ups_accumulate(self):
        store.ghi_tin_khach("u13", "", "hi", "hi")
        store.ghi_theo_duoi("u13", "lần 1")
        store.ghi_theo_duoi("u13", "lần 2")
        assert store.lay_khach("u13")["so_lan_theo_duoi"] == 2


class TestDanhSachCanTheoDuoi:
    def _past(self, hours: float) -> str:
        return (datetime.now() - timedelta(hours=hours)).isoformat(timespec="seconds")

    def test_returns_overdue_customer(self):
        _write_raw({"u14": {"ten": "Khách", "lich_su": [{"role": "user", "content": "hi"}],
                             "so_lan_theo_duoi": 0,
                             "lan_cuoi_khach": self._past(25),
                             "lan_theo_duoi_cuoi": None}}, None)
        result = store.danh_sach_can_theo_duoi(gio_cho=24)
        assert any(uid == "u14" for uid, _ in result)

    def test_excludes_recent_customer(self):
        _write_raw({"u15": {"ten": "Mới", "lich_su": [{"role": "user", "content": "hi"}],
                             "so_lan_theo_duoi": 0,
                             "lan_cuoi_khach": self._past(2),
                             "lan_theo_duoi_cuoi": None}}, None)
        result = store.danh_sach_can_theo_duoi(gio_cho=24)
        assert not any(uid == "u15" for uid, _ in result)

    def test_respects_toi_da_limit(self):
        _write_raw({"u16": {"ten": "Max", "lich_su": [{"role": "user", "content": "hi"}],
                             "so_lan_theo_duoi": 3,
                             "lan_cuoi_khach": self._past(30),
                             "lan_theo_duoi_cuoi": None}}, None)
        result = store.danh_sach_can_theo_duoi(gio_cho=24, toi_da=3)
        assert not any(uid == "u16" for uid, _ in result)

    def test_includes_when_under_toi_da(self):
        _write_raw({"u17": {"ten": "Under", "lich_su": [{"role": "user", "content": "hi"}],
                             "so_lan_theo_duoi": 2,
                             "lan_cuoi_khach": self._past(30),
                             "lan_theo_duoi_cuoi": None}}, None)
        result = store.danh_sach_can_theo_duoi(gio_cho=24, toi_da=3)
        assert any(uid == "u17" for uid, _ in result)

    def test_uses_lan_theo_duoi_cuoi_as_reference(self):
        # lan_theo_duoi_cuoi is recent (1h ago), so should NOT be overdue despite
        # lan_cuoi_khach being 48h ago
        _write_raw({"u18": {"ten": "Follow", "lich_su": [{"role": "user", "content": "hi"}],
                             "so_lan_theo_duoi": 1,
                             "lan_cuoi_khach": self._past(48),
                             "lan_theo_duoi_cuoi": self._past(1)}}, None)
        result = store.danh_sach_can_theo_duoi(gio_cho=24)
        assert not any(uid == "u18" for uid, _ in result)

    def test_excludes_customer_with_no_timestamp(self):
        _write_raw({"u19": {"ten": "NoTime", "lich_su": [],
                             "so_lan_theo_duoi": 0,
                             "lan_cuoi_khach": None,
                             "lan_theo_duoi_cuoi": None}}, None)
        result = store.danh_sach_can_theo_duoi(gio_cho=0)
        assert not any(uid == "u19" for uid, _ in result)


class TestXoaKhach:
    def test_removes_existing_customer(self):
        store.ghi_tin_khach("u20", "", "hi", "hi")
        assert store.lay_khach("u20") is not None
        store.xoa_khach("u20")
        assert store.lay_khach("u20") is None

    def test_noop_for_unknown_uid(self):
        store.xoa_khach("nobody")  # should not raise
