#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""新浪财经API获取30只ETF数据，计算指标，判断入场信号"""

import requests
import json
import time
from datetime import datetime

ETF_LIST = [
    # 引擎A：跨境ETF趋势追踪（T+0）
    {"code": "513100", "name": "纳指ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "513500", "name": "标普500ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "513130", "name": "恒生科技ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "159920", "name": "恒生ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "513030", "name": "德国ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "513520", "name": "日经ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "513050", "name": "中概互联ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "513080", "name": "法国ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "513730", "name": "越南ETF", "engine": "A", "engine_name": "跨境T+0"},
    {"code": "513110", "name": "纳指科技ETF", "engine": "A", "engine_name": "跨境T+0"},
    # 引擎B：债券/货币ETF
    {"code": "511990", "name": "华宝添益", "engine": "B", "engine_name": "债券套利"},
    {"code": "511880", "name": "银华日利", "engine": "B", "engine_name": "债券套利"},
    {"code": "511620", "name": "海富通短融", "engine": "B", "engine_name": "债券套利"},
    {"code": "511520", "name": "政金债ETF", "engine": "B", "engine_name": "债券套利"},
    {"code": "511260", "name": "十年国债ETF", "engine": "B", "engine_name": "债券套利"},
    # 引擎C：黄金ETF
    {"code": "518880", "name": "华安黄金ETF", "engine": "C", "engine_name": "黄金宏观"},
    {"code": "159937", "name": "博时黄金ETF", "engine": "C", "engine_name": "黄金宏观"},
    {"code": "518800", "name": "黄金基金ETF", "engine": "C", "engine_name": "黄金宏观"},
    # 引擎D：宽基ETF网格
    {"code": "510300", "name": "沪深300ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "510500", "name": "中证500ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "159915", "name": "创业板ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "588000", "name": "科创50ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "510050", "name": "上证50ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "512100", "name": "中证1000ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "159901", "name": "深证100ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "510880", "name": "红利ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "560050", "name": "MSCI中国A50ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "159949", "name": "创业板50ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "510330", "name": "华夏沪深300ETF", "engine": "D", "engine_name": "宽基网格"},
    {"code": "159922", "name": "嘉实中证500ETF", "engine": "D", "engine_name": "宽基网格"},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn/',
}


def get_sina_symbol(code):
    """5/58开头=sh，15开头=sz"""
    if code.startswith('15') or code.startswith('16'):
        return f"sz{code}"
    return f"sh{code}"


def fetch_etf_data(code):
    symbol = get_sina_symbol(code)
    url = (f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
           f"CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen=30")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        data = json.loads(r.text)
        if not data or len(data) < 20:
            return None
        parsed = []
        for d in data:
            parsed.append({
                'date': d['day'],
                'open': float(d['open']),
                'close': float(d['close']),
                'high': float(d['high']),
                'low': float(d['low']),
                'volume': float(d['volume']),  # 股
            })
        return parsed
    except Exception as e:
        print(f"  [ERR] {code}: {e}")
        return None


def calc_indicators(data):
    if not data or len(data) < 20:
        return None
    closes = [d['close'] for d in data]
    volumes = [d['volume'] for d in data]

    latest_close = closes[-1]
    ma20 = sum(closes[-20:]) / 20
    ma5 = sum(closes[-5:]) / 5
    ma10 = sum(closes[-10:]) / 10

    latest_vol = volumes[-1]
    avg_vol_5 = sum(volumes[-6:-1]) / 5 if len(volumes) >= 6 else latest_vol
    vol_ratio = latest_vol / avg_vol_5 if avg_vol_5 > 0 else 1.0

    # 估算日均成交额（亿元）= 成交量(股) * 均价 / 1e8
    avg_amount_5y = 0
    for d in data[-5:]:
        avg_price = (d['high'] + d['low'] + d['close']) / 3
        avg_amount_5y += d['volume'] * avg_price / 1e8
    avg_amount_5y /= 5

    high_20 = max(closes[-20:])
    low_20 = min(closes[-20:])
    deviation = (latest_close - ma20) / ma20 * 100
    chg_5d = (latest_close - closes[-6]) / closes[-6] * 100 if len(closes) >= 6 else 0

    ma20_today = sum(closes[-20:]) / 20
    ma20_3ago = sum(closes[-22:-2]) / 20 if len(closes) >= 22 else ma20_today
    ma20_trend_up = ma20_today > ma20_3ago

    return {
        "latest_close": round(latest_close, 4),
        "ma20": round(ma20, 4),
        "ma5": round(ma5, 4),
        "ma10": round(ma10, 4),
        "vol_ratio": round(vol_ratio, 2),
        "avg_amount_5y": round(avg_amount_5y, 2),
        "high_20": round(high_20, 4),
        "low_20": round(low_20, 4),
        "deviation": round(deviation, 2),
        "chg_5d": round(chg_5d, 2),
        "ma20_trend_up": ma20_trend_up,
        "latest_date": data[-1]['date'],
        "above_ma20": latest_close >= ma20,
    }


def judge_signal(etf, indicators):
    if indicators is None:
        return {"signal": "数据不足", "signal_level": "none", "reason": "数据获取失败"}

    engine = etf["engine"]

    if engine == "A":
        cond1 = indicators["above_ma20"]
        cond2 = indicators["vol_ratio"] < 0.85
        cond3 = indicators["ma20_trend_up"]
        if cond1 and cond2 and cond3:
            return {"signal": "建议进场", "signal_level": "buy",
                    "reason": f"站上MA20，量比{indicators['vol_ratio']}缩量回踩，MA20向上，符合趋势狙击"}
        elif cond1 and cond3 and not cond2:
            return {"signal": "观望", "signal_level": "watch",
                    "reason": f"站上MA20且趋势向上，量比{indicators['vol_ratio']}未缩量，等缩量回踩点"}
        elif not cond1:
            return {"signal": "不建议", "signal_level": "avoid",
                    "reason": f"现价{indicators['latest_close']}低于MA20({indicators['ma20']})，偏离{indicators['deviation']}%，均线之下不抄底"}
        else:
            return {"signal": "观望", "signal_level": "watch", "reason": "部分条件满足，等待更佳点"}

    elif engine == "B":
        today = datetime.now()
        holiday_windows = [
            (datetime(today.year, 1, 15), datetime(today.year, 2, 15)),
            (datetime(today.year, 4, 20), datetime(today.year, 5, 5)),
            (datetime(today.year, 9, 20), datetime(today.year, 10, 10)),
        ]
        near_holiday = any(s <= today <= e for s, e in holiday_windows)
        if near_holiday:
            return {"signal": "建议进场", "signal_level": "buy",
                    "reason": "临近法定长假，节前倒数第2日买入，享跨节息+避险溢价"}
        else:
            return {"signal": "观望", "signal_level": "watch",
                    "reason": f"当前({today.strftime('%m-%d')})非长假窗口，作现金管理持有，长假前1周布局"}

    elif engine == "C":
        cond1 = indicators["above_ma20"]
        cond2 = indicators["ma20_trend_up"]
        cond3 = indicators["deviation"] < 8
        if cond1 and cond2 and cond3:
            return {"signal": "建议进场", "signal_level": "buy",
                    "reason": f"站上MA20({indicators['ma20']})，趋势向上，偏离{indicators['deviation']}%，可逢低布局"}
        elif cond1 and cond2 and not cond3:
            return {"signal": "观望", "signal_level": "watch",
                    "reason": f"趋势向上但偏离MA20达{indicators['deviation']}%，短期超买，等回调"}
        elif not cond1:
            return {"signal": "不建议", "signal_level": "avoid",
                    "reason": f"金价跌破MA20({indicators['ma20']})，趋势或拐头，不抄底"}
        else:
            return {"signal": "观望", "signal_level": "watch", "reason": "趋势未明确，等MA20方向确认"}

    elif engine == "D":
        price_range = indicators["high_20"] - indicators["low_20"]
        price_pos = (indicators["latest_close"] - indicators["low_20"]) / price_range * 100 if price_range > 0 else 50
        volatility = price_range / indicators["latest_close"] * 100 if indicators["latest_close"] > 0 else 0
        cond_vol = volatility > 4
        cond_pos = price_pos < 70
        cond_liq = indicators["avg_amount_5y"] > 1
        if cond_vol and cond_pos and cond_liq:
            return {"signal": "可开网格", "signal_level": "buy",
                    "reason": f"20日波动{volatility:.1f}%，价格处20日{price_pos:.0f}%分位，日均成交{indicators['avg_amount_5y']}亿，适合网格（需核实PE分位<30%）"}
        elif not cond_liq:
            return {"signal": "流动性不足", "signal_level": "avoid",
                    "reason": f"5日日均成交仅{indicators['avg_amount_5y']}亿，低于1亿底线"}
        elif cond_vol and not cond_pos:
            return {"signal": "观望", "signal_level": "watch",
                    "reason": f"波动充足但价格处20日{price_pos:.0f}%高位，等回调再开网格"}
        else:
            return {"signal": "暂不适合", "signal_level": "avoid",
                    "reason": f"20日波动仅{volatility:.1f}%，空间不足，网格收益有限"}

    return {"signal": "未知", "signal_level": "none", "reason": ""}


def main():
    print("=" * 60)
    print("新浪财经 - 获取30只ETF数据...")
    print("=" * 60)

    results = []
    success = 0

    for i, etf in enumerate(ETF_LIST, 1):
        print(f"[{i}/30] {etf['code']} {etf['name']}...", end=" ")
        data = fetch_etf_data(etf["code"])
        indicators = calc_indicators(data)
        signal = judge_signal(etf, indicators)
        result = {**etf, **(indicators or {}), **signal}
        results.append(result)

        if indicators:
            success += 1
            print(f"OK 价:{indicators['latest_close']} MA20:{indicators['ma20']} "
                  f"量比:{indicators['vol_ratio']} 成交:{indicators['avg_amount_5y']}亿 -> {signal['signal']}")
        else:
            print("FAIL")
        time.sleep(0.3)

    print(f"\n完成：成功{success}/30")

    output = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(results),
        "success": success,
        "etfs": results,
    }
    with open("etf_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    buy = sum(1 for r in results if r["signal_level"] == "buy")
    watch = sum(1 for r in results if r["signal_level"] == "watch")
    avoid = sum(1 for r in results if r["signal_level"] in ("avoid", "none"))
    print(f"信号：建议进场/可开网格 {buy} | 观望 {watch} | 不建议 {avoid}")
    print("已保存 etf_data.json")


if __name__ == "__main__":
    main()
