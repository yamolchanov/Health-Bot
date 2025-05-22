"""
TEST PLOTTING.PY
"""
import unittest
from unittest.mock import patch
from io import BytesIO
import datetime
import matplotlib.pyplot as plt
from telegram_tracker_bot.logic import plot_weekly_data


@patch('telegram_tracker_bot.logic.plotting.get_records_last_n_days')
@patch('telegram_tracker_bot.'
       'logic.plotting.format_timedelta', side_effect=lambda x: f"{x:.1f}h")
class TestPlotWeeklyData(unittest.TestCase):
    """"
    КЛАСС ТЕСТОВ
    """
    def setUp(self):
        self.user_id = 123
        self.today = datetime.date.today()
        self.dates_str = [(self.today - datetime.timedelta(days=i))
                          .strftime("%Y-%m-%d")
                          for i in range(6, -1, -1)]
        self.expected_dates = sorted([self.today - datetime.timedelta(days=i)
                                      for i in range(7)])

    def test_plot_with_all_data(self, _, mock_get_records):
        """ТЕСТ"""
        mock_get_records.side_effect = [
            [
                {"date": self.dates_str[0], "hours": 7.5},

                {"date": self.dates_str[2], "hours": 8.0},
                {"date": self.dates_str[6], "hours": 6.5},
            ],
            [
                {"date": self.dates_str[1], "amount": 2000},
                {"date": self.dates_str[3], "amount": 2200},
                {"date": self.dates_str[5], "amount": 1800},
            ],
            [
                {"date": self.dates_str[0], "duration_hours": 1.0},
                {"date": self.dates_str[4], "duration_hours": 1.5},
            ]
        ]

        buffer = plot_weekly_data(self.user_id)
        self.assertIsInstance(buffer, BytesIO)
        self.assertEqual(buffer.tell(), 0)
        mock_get_records.assert_any_call(self.user_id, "sleep", 7,
                                         'telegram_tracker_bot/'
                                         'db/tracker_data_base.db')
        mock_get_records.assert_any_call(self.user_id,
                                         "calories", 7,
                                         'telegram_tracker_bot'
                                         '/db/tracker_data_base.db')
        mock_get_records.assert_any_call(self.user_id,
                                         "workouts", 7,
                                         'telegram_tracker_bot'
                                         '/db/tracker_data_base.db')
        self.assertIsNotNone(plt.gcf())

    def test_plot_with_no_data(self, _, mock_get_records):
        """ТЕСТ"""
        mock_get_records.side_effect = [[], [], []]
        buffer = plot_weekly_data(self.user_id)
        self.assertIsNone(buffer)

    def test_plot_with_partial_data(
            self, _, mock_get_records):
        """ТЕСТ"""
        mock_get_records.side_effect = [
            [
                {"date": self.dates_str[0], "hours": 7.0},
                {"date": self.dates_str[6], "hours": 8.0},
            ],
            [
                {"date": self.dates_str[3], "amount": 2500},
                {"date": self.dates_str[5], "amount": 2100},
            ],
            []
        ]
        buffer = plot_weekly_data(self.user_id)
        self.assertIsInstance(buffer, BytesIO)
        self.assertEqual(buffer.tell(), 0)

    def test_plot_with_single_day_data(
            self, _, mock_get_records):
        """СНОВА ТЕСТ"""
        mock_get_records.side_effect = [
            [{"date": self.dates_str[0], "hours": 7.0}],
            [{"date": self.dates_str[0], "amount": 2000}],
            [{"date": self.dates_str[0], "duration_hours": 0.5}],
        ]
        buffer = plot_weekly_data(self.user_id)
        self.assertIsInstance(buffer, BytesIO)
        self.assertEqual(buffer.tell(), 0)

    def test_workout_duration_aggregation(
            self, _, mock_get_records):
        """Опять тест..."""
        mock_get_records.side_effect = [[], [], [
                {"date": self.dates_str[0], "duration_hours": 0.5},
                {"date": self.dates_str[0], "duration_hours": 0.75},
                {"date": self.dates_str[1], "duration_hours": 1.0},
            ]
        ]
        buffer = plot_weekly_data(self.user_id)
        self.assertIsInstance(buffer, BytesIO)
        self.assertEqual(buffer.tell(), 0)
