# coding:utf-8
import datetime
import unittest
from unittest import mock

from easytrader.xq_follower import XueQiuFollower


class TestXueQiuTrader(unittest.TestCase):
    def test_adjust_sell_amount_without_enable(self):
        follower = XueQiuFollower()

        mock_user = mock.MagicMock()
        follower._users = [mock_user]

        follower._adjust_sell = False
        amount = follower._adjust_sell_amount("169101", 1000)
        self.assertEqual(amount, amount)

    def test_adjust_sell_amount(self):
        follower = XueQiuFollower()

        mock_user = mock.MagicMock()
        follower._users = [mock_user]
        mock_user.position = TEST_POSITION

        follower._adjust_sell = True
        test_cases = [
            ("169101", 600, 600),
            ("169101", 700, 600),
            ("000000", 100, 100),
            ("sh169101", 700, 600),
        ]
        for stock_code, sell_amount, excepted_amount in test_cases:
            amount = follower._adjust_sell_amount(stock_code, sell_amount)
            self.assertEqual(amount, excepted_amount)

    def test_slippage_with_default(self):
        follower = XueQiuFollower()
        mock_user = mock.MagicMock()

        # test default no slippage
        test_price = 1.0
        test_trade_cmd = {
            "strategy": "test_strategy",
            "strategy_name": "test_strategy",
            "action": "buy",
            "stock_code": "162411",
            "amount": 100,
            "price": 1.0,
            "datetime": datetime.datetime.now(),
        }
        follower._execute_trade_cmd(
            trade_cmd=test_trade_cmd,
            users=[mock_user],
            expire_seconds=10,
            entrust_prop="limit",
            send_interval=10,
        )
        _, kwargs = getattr(mock_user, test_trade_cmd["action"]).call_args
        self.assertAlmostEqual(kwargs["price"], test_price)

    def test_slippage(self):
        follower = XueQiuFollower()
        mock_user = mock.MagicMock()

        test_price = 1.0
        follower.slippage = 0.05

        # test buy
        test_trade_cmd = {
            "strategy": "test_strategy",
            "strategy_name": "test_strategy",
            "action": "buy",
            "stock_code": "162411",
            "amount": 100,
            "price": 1.0,
            "datetime": datetime.datetime.now(),
        }
        follower._execute_trade_cmd(
            trade_cmd=test_trade_cmd,
            users=[mock_user],
            expire_seconds=10,
            entrust_prop="limit",
            send_interval=10,
        )
        excepted_price = test_price * (1 + follower.slippage)
        _, kwargs = getattr(mock_user, test_trade_cmd["action"]).call_args
        self.assertAlmostEqual(kwargs["price"], excepted_price)

        # test sell
        test_trade_cmd["action"] = "sell"
        follower._execute_trade_cmd(
            trade_cmd=test_trade_cmd,
            users=[mock_user],
            expire_seconds=10,
            entrust_prop="limit",
            send_interval=10,
        )
        excepted_price = test_price * (1 - follower.slippage)
        _, kwargs = getattr(mock_user, test_trade_cmd["action"]).call_args
        self.assertAlmostEqual(kwargs["price"], excepted_price)


TEST_POSITION = [
    {
        "Unnamed: 14": "",
        "买入冻结": 0,
        "交易市场": "深Ａ",
        "卖出冻结": 0,
        "参考市价": 1.464,
        "参考市值": 919.39,
        "参考成本价": 1.534,
        "参考盈亏": -43.77,
        "可用余额": 628,
        "当前持仓": 628,
        "盈亏比例(%)": -4.544,
        "股东代码": "0000000000",
        "股份余额": 628,
        "证券代码": "169101",
    }
]
