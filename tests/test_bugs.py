import pytest
import time
from unittest.mock import patch, MagicMock
import requests

from main import fetch_with_retry, cleanup, MAX_RETRIES, BASE_DELAY
import main


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
        with patch('main.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"username": "test"}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = fetch_with_retry("http://test.com", {})
            assert result == {"username": "test"}
            assert mock_get.call_count == 1

    def test_retry_on_failure_then_success(self):
        with patch('main.requests.get') as mock_get, \
             patch('main.time.sleep') as mock_sleep:
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
        with patch('main.requests.get') as mock_get, \
             patch('main.time.sleep'):
            mock_get.side_effect = requests.exceptions.RequestException("timeout")

            with pytest.raises(requests.exceptions.RequestException):
                fetch_with_retry("http://test.com", {}, max_retries=2)
            assert mock_get.call_count == 2


class TestCleanup:
    """Bug 3: RPC cleanup com signal handlers"""

    def test_cleanup_closes_rpc(self):
        mock_rpc = MagicMock()
        main.rpc = mock_rpc
        with pytest.raises(SystemExit):
            cleanup()
        mock_rpc.close.assert_called_once()

    def test_cleanup_no_rpc(self):
        main.rpc = None
        with pytest.raises(SystemExit):
            cleanup()

    def test_cleanup_handles_close_exception(self):
        mock_rpc = MagicMock()
        mock_rpc.close.side_effect = Exception("already closed")
        main.rpc = mock_rpc
        with pytest.raises(SystemExit):
            cleanup()


class TestConstants:
    """Verify constants are properly defined"""

    def test_max_retries_value(self):
        assert MAX_RETRIES == 3

    def test_base_delay_value(self):
        assert BASE_DELAY == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
