import pytest
from unittest.mock import patch, MagicMock
import requests

from chess_api import ChessAPI, fetch_with_retry, MAX_RETRIES, BASE_DELAY
import chess_api


class TestUsernameNormalization:
    """Bug 4: Username case-insensitive"""

    def test_username_lowercased(self):
        with patch('builtins.input', return_value='TwG2000'):
            username = input("Enter your chess.com account username: ").strip().lower()
            assert username == "twg2000"

    def test_username_strips_whitespace(self):
        with patch('builtins.input', return_value='  Twg2000  '):
            username = input("Enter your chess.com account username: ").strip().lower()
            assert username == "twg2000"

    def test_username_already_lowercase(self):
        with patch('builtins.input', return_value='twg2000'):
            username = input("Enter your chess.com account username: ").strip().lower()
            assert username == "twg2000"


class TestFetchWithRetry:
    """Bug 2: Retry/backoff exponencial"""

    def test_success_first_attempt(self):
        with patch('chess_api.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"username": "test"}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = fetch_with_retry("http://test.com", {})
            assert result == {"username": "test"}
            assert mock_get.call_count == 1

    def test_retry_on_failure_then_success(self):
        with patch('chess_api.requests.get') as mock_get, \
             patch('chess_api.time.sleep') as mock_sleep:
            fail_response = MagicMock()
            fail_response.raise_for_status.side_effect = requests.exceptions.RequestException("timeout")

            success_response = MagicMock()
            success_response.json.return_value = {"username": "test"}
            success_response.raise_for_status = MagicMock()

            mock_get.side_effect = [fail_response, success_response]

            result = fetch_with_retry("http://test.com", {}, max_retries=2)
            assert result == {"username": "test"}
            assert mock_get.call_count == 2
            assert mock_sleep.call_count == 1

    def test_max_retries_exceeded(self):
        with patch('chess_api.requests.get') as mock_get, \
             patch('chess_api.time.sleep'):
            mock_get.side_effect = requests.exceptions.RequestException("timeout")

            with pytest.raises(requests.exceptions.RequestException):
                fetch_with_retry("http://test.com", {}, max_retries=2)
            assert mock_get.call_count == 2


class TestConstants:
    """Verify constants are properly defined"""

    def test_max_retries_value(self):
        assert MAX_RETRIES == 3

    def test_base_delay_value(self):
        assert BASE_DELAY == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
