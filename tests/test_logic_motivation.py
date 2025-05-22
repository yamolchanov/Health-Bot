# test_motivation.py
import unittest
from telegram_tracker_bot.logic import get_random_motivation
from telegram_tracker_bot.logic.motivation import MESSAGES

class TestGetRandomMotivation(unittest.TestCase):
    def test_returns_string(self):
        message = get_random_motivation()
        self.assertIsInstance(message, str)

    def test_returns_message_from_list(self):
        message = get_random_motivation()
        self.assertIn(message, MESSAGES)

    def test_randomness_over_multiple_calls(self):
        results = {get_random_motivation() for _ in range(100)}
        self.assertGreater(len(results), 1)
