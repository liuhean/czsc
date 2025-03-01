# -*- coding: utf-8 -*-
"""
author: liuhean
create_dt: 20250223 19:45
describe: 5分钟BS1
"""
import czsc

from pathlib import Path
from loguru import logger

from czsc.connectors import qmt_connector as qmc
from czsc import Event, Position


def create_bs1_V250502223(symbol, **kwargs):
    """5分钟BS1

    使用的信号函数：

    https://czsc.readthedocs.io/en/latest/api/czsc.signals.zdy_macd_bs1_V230422.html
    """
    base_freq = kwargs.get("base_freq", "5分钟")
    opens = [
        {
            "operate": "开多",
            "signals_all": [],
            "signals_any": [],
            "signals_not": [],
            "factors": [
                {
                    "signals_all": [f"{base_freq}_D1T50MACD_BS1辅助V230422_看多_下跌7笔_任意_0"],
                    "signals_any": [],
                    "signals_not": [],
                }
            ],
        },
        {
            "operate": "开空",
            "signals_all": [],
            "signals_any": [],
            "signals_not": [],
            "factors": [
                {
                    "signals_all": [f"{base_freq}_D1T50MACD_BS1辅助V230422_看空_上涨5笔_任意_0"],
                    "signals_any": [],
                    "signals_not": [],
                }
            ],
        },
    ]

    exits = []

    pos = Position(
        name=f"{base_freq}BS1",
        symbol=symbol,
        opens=[Event.load(x) for x in opens],
        exits=[Event.load(x) for x in exits],
        interval=60 * 5,
        timeout=16 * 30,
        stop_loss=500,
    )
    return pos


class Strategy(czsc.CzscStrategyBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_stocks = kwargs.get("is_stocks", True)

    @property
    def positions(self):
        pos_list = [create_bs1_V250502223(self.symbol)]
        return pos_list


if __name__ == "__main__":
    # results_path = Path(r"D:\策略研究\5分钟BS1")
    # logger.add(results_path / "czsc.log", rotation="1 week", encoding="utf-8")
    # results_path.mkdir(exist_ok=True, parents=True)

    symbols = qmc.get_symbols("train")[:30]
    symbol = symbols[0]
    # symbol = "000016.SH"
    tactic = Strategy(symbol=symbol, is_stocks=True)

    # 使用 logger 记录策略的基本信息
    logger.info(f"K线周期列表：{tactic.freqs}")
    logger.info(f"信号函数配置列表：{tactic.signals_config}")

    # replay 查看策略的编写是否正确，执行过程是否符合预期
    # print("tactic:", tactic)
    # print("tactic.base_freq:", tactic.base_freq)
    bars = qmc.get_raw_bars(symbol, freq=tactic.base_freq, sdt="20240811", edt="20241210")
    # print("qmc.get_raw_bars:bars", bars)

    # trader = tactic.replay(bars, sdt="20210101", res_path=results_path / "replay", refresh=True)

    # 当策略执行过程符合预期后，将持仓策略保存到本地 json 文件中
    # tactic.save_positions(results_path / "positions")
