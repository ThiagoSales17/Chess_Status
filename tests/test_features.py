import pytest
from unittest.mock import patch, MagicMock
import requests

from models import ChessPlayer, GameStats, GameRecord, PlayerProfile, LiveGame, COUNTRY_FLAGS
from utils import (
    format_rating_change, format_win_rate, get_country_flag,
    format_followers, build_presence_stats, build_leaderboard, RatingTracker
)
from config import Config
from chess_api import ChessAPI


class TestModels:
    def test_game_record_total(self):
        r = GameRecord(wins=5, losses=3, draws=2)
        assert r.total == 10

    def test_game_record_win_rate(self):
        r = GameRecord(wins=7, losses=3, draws=0)
        assert r.win_rate == 70.0

    def test_game_record_win_rate_empty(self):
        r = GameRecord()
        assert r.win_rate == 0.0

    def test_game_record_win_rate_str(self):
        r = GameRecord(wins=1, losses=1, draws=0)
        assert r.win_rate_str == "50.0%"

    def test_chess_player_get_stats(self):
        p = ChessPlayer(rapid=GameStats(rating=1500))
        assert p.get_stats("rapid").rating == 1500
        assert p.get_stats("blitz") is None

    def test_chess_player_best_rating(self):
        p = ChessPlayer(
            rapid=GameStats(rating=1200),
            blitz=GameStats(rating=1800),
        )
        mode, rating = p.get_best_rating()
        assert mode == "blitz"
        assert rating == 1800

    def test_live_game(self):
        lg = LiveGame(is_live=True, opponent="magnus", color="white")
        assert lg.is_live
        assert lg.opponent == "magnus"


class TestUtils:
    def test_format_rating_change_positive(self):
        assert "📈" in format_rating_change(1500, 1520)
        assert "+20" in format_rating_change(1500, 1520)

    def test_format_rating_change_negative(self):
        assert "📉" in format_rating_change(1500, 1480)
        assert "-20" in format_rating_change(1500, 1480)

    def test_format_rating_change_zero(self):
        assert "➡️" in format_rating_change(1500, 1500)

    def test_format_win_rate(self):
        assert format_win_rate(7, 3, 0) == "70.0%"

    def test_format_win_rate_zero(self):
        assert format_win_rate(0, 0, 0) == "N/A"

    def test_country_flag_brazil(self):
        assert get_country_flag("BR") == "🇧🇷"

    def test_country_flag_unknown(self):
        assert "🏁" in get_country_flag("ZZ")

    def test_country_flag_none(self):
        assert get_country_flag(None) == ""

    def test_format_followers_thousands(self):
        assert format_followers(1500) == "1.5K"

    def test_format_followers_millions(self):
        assert format_followers(2_000_000) == "2.0M"

    def test_format_followers_small(self):
        assert format_followers(42) == "42"

    def test_build_presence_stats(self):
        player = ChessPlayer(
            profile=PlayerProfile(username="test", league="Silver"),
            rapid=GameStats(rating=1200, record=GameRecord(wins=10, losses=5, draws=3)),
        )
        result = build_presence_stats(player, "rapid")
        assert "details" in result
        assert "state" in result
        assert "1200" in result["state"]

    def test_build_leaderboard(self):
        players = [
            ChessPlayer(profile=PlayerProfile(username="alice"), rapid=GameStats(rating=1500, record=GameRecord(wins=5, losses=5))),
            ChessPlayer(profile=PlayerProfile(username="bob"), rapid=GameStats(rating=1800, record=GameRecord(wins=8, losses=2))),
        ]
        lb = build_leaderboard(players, "rapid")
        assert "bob" in lb
        assert "alice" in lb
        assert "1800" in lb


class TestRatingTracker:
    def test_first_rating(self):
        t = RatingTracker()
        result = t.update("user1", "rapid", 1500)
        assert result is None

    def test_rating_change(self):
        t = RatingTracker()
        t.update("user1", "rapid", 1500)
        result = t.update("user1", "rapid", 1520)
        assert result == (1500, 1520)

    def test_no_change(self):
        t = RatingTracker()
        t.update("user1", "rapid", 1500)
        result = t.update("user1", "rapid", 1500)
        assert result is None

    def test_history(self):
        t = RatingTracker()
        t.update("user1", "rapid", 1500)
        t.update("user1", "rapid", 1520)
        t.update("user1", "rapid", 1510)
        assert t.get_history("user1", "rapid") == [1500, 1520, 1510]


class TestConfig:
    def test_validate_missing(self):
        cfg = Config.__new__(Config)
        cfg.username = ""
        cfg.app_id = ""
        errors = cfg.validate()
        assert len(errors) == 2

    def test_validate_ok(self):
        cfg = Config.__new__(Config)
        cfg.username = "testuser"
        cfg.app_id = "123456"
        errors = cfg.validate()
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
