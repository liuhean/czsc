# -*- coding: utf-8 -*-
"""
author: xielei
email: 781353528@qq.com
create_dt: 2024/3/17 15:30
describe: 多信号观察页面
"""

import os

from czsc.objects import Signal

os.environ["czsc_max_bi_num"] = "20"
os.environ["czsc_research_cache"] = r"D:\CZSC投研数据"
import czsc
import numpy as np
import pandas as pd
import streamlit as st
from datetime import timedelta
from czsc.utils import sorted_freqs
from czsc.connectors.research import get_raw_bars, get_symbols

st.set_page_config(layout="wide")

signals_module = st.sidebar.text_input("信号模块名称：", value="czsc.signals")
parser = czsc.SignalsParser(signals_module=signals_module)

st.title("多信号观察")

with st.sidebar:
    st.header("信号配置")
    with st.form("my_form"):
        # # 定义多个文本框，并为它们设定标签
        text_box1_label = "信号 1"
        text_box2_label = "信号 2"
        # # 创建第一个文本框
        text_box1 = st.text_area(text_box1_label, placeholder="在此输入信号...")

        # # 创建第二个文本框
        text_box2 = st.text_area(text_box2_label, placeholder="在此输入信号...")
        # conf = st.text_input("请输入信号：", value="60分钟_D0停顿分型_BE辅助V230106_看多_强_任意_0")
        symbol = st.selectbox("请选择股票：", get_symbols("ALL"), index=0)
        freqs = st.multiselect("请选择周期：", sorted_freqs, default=["30分钟", "日线", "周线"])
        freqs = czsc.freqs_sorted(freqs)
        sdt = st.date_input("开始日期：", value=pd.to_datetime("2022-01-01"))
        edt = st.date_input("结束日期：", value=pd.to_datetime("2023-01-01"))
        submit_button = st.form_submit_button(label="提交")

if submit_button:
    signal1 = text_box1
    signal2 = text_box2

    # 获取K线，计算信号
    bars = get_raw_bars(symbol, freqs[0], pd.to_datetime(sdt) - timedelta(days=365 * 3), edt)

    signal_confs = [text_box1, text_box2]
    # 将当前的信号列表转换为Signal对象列表，然后封装到一个signals_all Factor中
    # 计算信号
    signals_config = czsc.get_signals_config(signal_confs, signals_module=signals_module)
    sigs = czsc.generate_czsc_signals(bars, signals_config, df=True, sdt=sdt)  # type: ignore
    columns = [x for x in sigs.columns if len(x.split("_")) == 3]  # type: ignore
    signals = [Signal(x) for x in signal_confs]
    sigs["match"] = sigs.apply(czsc.Factor(signals_all=signals).is_match, axis=1)

    # 在图中绘制指定需要观察的信号
    chart = czsc.KlineChart(n_rows=3, height=800)
    chart.add_kline(sigs, freqs[0])  # type: ignore
    # 可以参考这里的代码，绘制其他自定义指标
    chart.add_sma(sigs, row=1, ma_seq=(5, 10, 20), visible=True)
    chart.add_vol(sigs, row=2)
    chart.add_macd(sigs, row=3)
    df1 = sigs[sigs["match"] == True][["dt", "close", "low"]].copy()  # type: ignore
    chart.add_scatter_indicator(
        x=df1["dt"],
        y=df1["low"],
        row=1,
        name="信号",
        mode="markers",
        marker_size=20,
        marker_color="red",
        marker_symbol="triangle-up",
    )
    st.plotly_chart(
        chart.fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "toggleSpikelines",
                "select2d",
                "zoomIn2d",
                "zoomOut2d",
                "lasso2d",
                "autoScale2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
            ],
        },
    )
