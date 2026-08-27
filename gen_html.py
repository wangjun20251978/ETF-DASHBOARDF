#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""读取ETF数据JSON，生成完整HTML网页"""

import json
from datetime import datetime

# 读取数据
with open("etf_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

etfs = data["etfs"]
update_time = data["update_time"]

# 统计
buy_list = [e for e in etfs if e["signal_level"] == "buy"]
watch_list = [e for e in etfs if e["signal_level"] == "watch"]
avoid_list = [e for e in etfs if e["signal_level"] in ("avoid", "none")]

# 按引擎分组
engines = {
    "A": {"name": "跨境T+0套利", "desc": "主动趋势追踪", "color": "#f59e0b", "icon": "📈"},
    "B": {"name": "债券节假日套利", "desc": "事件驱动停泊", "color": "#06b6d4", "icon": "🏦"},
    "C": {"name": "黄金宏观套利", "desc": "全球宏观共振", "color": "#eab308", "icon": "🥇"},
    "D": {"name": "宽基网格自动化", "desc": "被动震荡收割", "color": "#ec4899", "icon": "🔄"},
}

# 生成ETF表格行
def generate_rows(etf_list):
    rows = ""
    for e in etf_list:
        level_class = {
            "buy": "signal-buy",
            "watch": "signal-watch",
            "avoid": "signal-avoid",
            "none": "signal-none"
        }.get(e.get("signal_level", "none"), "signal-none")

        level_text = {
            "buy": "建议进场",
            "watch": "观望",
            "avoid": "不建议",
            "none": "数据不足"
        }.get(e.get("signal_level", "none"), "未知")

        # 对于网格引擎，buy显示"可开网格"
        if e.get("engine") == "D" and e.get("signal_level") == "buy":
            level_text = "可开网格"

        ma20_status = "✓ 站上" if e.get("above_ma20") else "✗ 跌破"
        vol_status = "缩量" if e.get("vol_ratio", 1) < 0.85 else ("放量" if e.get("vol_ratio", 1) > 1.2 else "平量")

        rows += f"""
        <tr class="etf-row" data-engine="{e.get('engine','')}" data-level="{e.get('signal_level','')}">
            <td class="code">{e.get('code','')}</td>
            <td class="name">{e.get('name','')}</td>
            <td class="engine-tag" style="color:{engines.get(e.get('engine','A'),{}).get('color','#999')}">{engines.get(e.get('engine','A'),{}).get('name','')}</td>
            <td class="price">{e.get('latest_close','-')}</td>
            <td class="ma20">{e.get('ma20','-')}</td>
            <td class="deviation {'pos' if e.get('deviation',0)>=0 else 'neg'}">{e.get('deviation',0):+.2f}%</td>
            <td class="volratio">{e.get('vol_ratio','-')} <span class="vol-tag">{vol_status}</span></td>
            <td class="amount">{e.get('avg_amount_5y','-')}亿</td>
            <td class="ma20-status {'up' if e.get('above_ma20') else 'down'}">{ma20_status}</td>
            <td class="signal {level_class}">{level_text}</td>
            <td class="reason">{e.get('reason','')}</td>
        </tr>"""
    return rows

all_rows = generate_rows(etfs)

# 生成建议进场的重点卡片
def generate_buy_cards():
    cards = ""
    for e in buy_list:
        eng = engines.get(e.get("engine", "A"), {})
        signal_text = "可开网格" if e.get("engine") == "D" else "建议进场"
        cards += f"""
        <div class="focus-card">
            <div class="focus-header" style="border-left:4px solid {eng.get('color','#999')}">
                <div class="focus-title">
                    <span class="focus-code">{e.get('code','')}</span>
                    <span class="focus-name">{e.get('name','')}</span>
                </div>
                <span class="focus-signal">{signal_text}</span>
            </div>
            <div class="focus-body">
                <div class="focus-metric"><span>现价</span><b>{e.get('latest_close','-')}</b></div>
                <div class="focus-metric"><span>MA20</span><b>{e.get('ma20','-')}</b></div>
                <div class="focus-metric"><span>偏离</span><b class="{ 'pos' if e.get('deviation',0)>=0 else 'neg'}">{e.get('deviation',0):+.2f}%</b></div>
                <div class="focus-metric"><span>量比</span><b>{e.get('vol_ratio','-')}</b></div>
                <div class="focus-metric"><span>日均成交</span><b>{e.get('avg_amount_5y','-')}亿</b></div>
                <div class="focus-metric"><span>5日涨跌</span><b class="{ 'pos' if e.get('chg_5d',0)>=0 else 'neg'}">{e.get('chg_5d',0):+.2f}%</b></div>
            </div>
            <div class="focus-reason">{e.get('reason','')}</div>
        </div>"""
    return cards

buy_cards = generate_buy_cards()

# 市场状态判断（基于沪深300ETF 510300）
hs300 = next((e for e in etfs if e["code"] == "510300"), None)
if hs300:
    if hs300.get("above_ma20") and hs300.get("ma20_trend_up"):
        market_state = "上涨趋势"
        market_desc = "沪深300站上MA20且均线向上，趋势偏多，可侧重跨境T+0和黄金引擎"
        market_color = "#10b981"
    elif hs300.get("above_ma20") and not hs300.get("ma20_trend_up"):
        market_state = "震荡偏强"
        market_desc = "沪深300在MA20上方但均线走平，震荡市为主，网格引擎优先"
        market_color = "#f59e0b"
    elif not hs300.get("above_ma20") and hs300.get("ma20_trend_up"):
        market_state = "回调中"
        market_desc = "沪深300跌破MA20但均线仍向上，短期回调，观望为主等待企稳"
        market_color = "#f97316"
    else:
        market_state = "下跌趋势"
        market_desc = "沪深300跌破MA20且均线向下，防守为主，降低仓位，关注货币ETF"
        market_color = "#ef4444"
else:
    market_state = "未知"
    market_desc = ""
    market_color = "#6b7280"

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ETF四引擎轮动系统 - 实时信号看板</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #0a0e1a;
    color: #e2e8f0;
    line-height: 1.6;
}}
.container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}

/* 顶部海报 */
.hero {{
    width: 100%;
    border-radius: 0 0 20px 20px;
    overflow: hidden;
    margin-bottom: 30px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}}
.hero img {{ width: 100%; display: block; }}

/* 更新时间 */
.update-bar {{
    text-align: center;
    padding: 12px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.15), transparent);
    border-radius: 10px;
    margin-bottom: 30px;
    font-size: 14px;
    color: #94a3b8;
}}
.update-bar b {{ color: #60a5fa; }}

/* 市场状态 */
.market-state {{
    background: linear-gradient(135deg, #1a1f2e, #0f1420);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px 30px;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    gap: 24px;
}}
.market-indicator {{
    width: 80px; height: 80px;
    border-radius: 50%;
    background: {market_color};
    display: flex; align-items: center; justify-content: center;
    font-size: 28px;
    box-shadow: 0 0 30px {market_color}55;
    flex-shrink: 0;
}}
.market-info h2 {{ font-size: 22px; margin-bottom: 6px; color: {market_color}; }}
.market-info p {{ font-size: 14px; color: #94a3b8; }}

/* 统计卡片 */
.stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 30px;
}}
.stat-card {{
    background: linear-gradient(135deg, #1a1f2e, #0f1420);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}}
.stat-card .num {{ font-size: 36px; font-weight: 700; margin-bottom: 4px; }}
.stat-card .label {{ font-size: 13px; color: #94a3b8; }}
.stat-buy .num {{ color: #10b981; }}
.stat-watch .num {{ color: #f59e0b; }}
.stat-avoid .num {{ color: #ef4444; }}
.stat-total .num {{ color: #60a5fa; }}

/* 区块标题 */
.section-title {{
    font-size: 20px;
    font-weight: 700;
    margin: 40px 0 20px;
    padding-left: 14px;
    border-left: 4px solid #3b82f6;
    color: #f1f5f9;
}}

/* 四引擎策略说明 */
.engines-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-bottom: 30px;
}}
.engine-card {{
    background: linear-gradient(135deg, #1a1f2e, #0f1420);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 22px;
    border-top: 3px solid var(--ec);
}}
.engine-card h3 {{ font-size: 17px; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }}
.engine-card .engine-desc {{ font-size: 13px; color: #94a3b8; margin-bottom: 14px; }}
.engine-card .rules {{ font-size: 13px; color: #cbd5e1; }}
.engine-card .rules li {{ margin-bottom: 6px; padding-left: 4px; list-style: none; }}
.engine-card .rules li::before {{ content: "▸ "; color: var(--ec); }}

/* 筛选栏 */
.filter-bar {{
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}}
.filter-btn {{
    padding: 8px 18px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.15);
    background: transparent;
    color: #94a3b8;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
}}
.filter-btn:hover {{ border-color: #3b82f6; color: #e2e8f0; }}
.filter-btn.active {{ background: #3b82f6; color: #fff; border-color: #3b82f6; }}

/* 表格 */
.table-wrap {{
    overflow-x: auto;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 40px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    min-width: 900px;
}}
thead th {{
    background: #1a1f2e;
    padding: 14px 12px;
    text-align: left;
    font-weight: 600;
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    position: sticky;
    top: 0;
    white-space: nowrap;
}}
tbody td {{
    padding: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    white-space: nowrap;
}}
tbody tr:hover {{ background: rgba(59,130,246,0.06); }}
.code {{ font-family: monospace; color: #60a5fa; font-weight: 600; }}
.name {{ font-weight: 500; }}
.price {{ font-weight: 600; }}
.deviation.pos {{ color: #ef4444; }}
.deviation.neg {{ color: #10b981; }}
.pos {{ color: #ef4444; }}
.neg {{ color: #10b981; }}
.vol-tag {{ font-size: 11px; color: #94a3b8; }}
.ma20-status.up {{ color: #10b981; }}
.ma20-status.down {{ color: #ef4444; }}
.signal {{ font-weight: 700; text-align: center; padding: 6px 10px; border-radius: 6px; font-size: 12px; }}
.signal-buy {{ background: rgba(16,185,129,0.15); color: #10b981; }}
.signal-watch {{ background: rgba(245,158,11,0.15); color: #f59e0b; }}
.signal-avoid {{ background: rgba(239,68,68,0.15); color: #ef4444; }}
.signal-none {{ background: rgba(107,114,128,0.15); color: #6b7280; }}
.reason {{ font-size: 12px; color: #94a3b8; white-space: normal; min-width: 200px; max-width: 300px; }}

/* 重点关注卡片 */
.focus-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 16px;
    margin-bottom: 40px;
}}
.focus-card {{
    background: linear-gradient(135deg, #1a1f2e, #0f1420);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    overflow: hidden;
}}
.focus-header {{
    padding: 14px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255,255,255,0.02);
}}
.focus-code {{ font-family: monospace; color: #60a5fa; font-weight: 700; margin-right: 8px; }}
.focus-name {{ font-weight: 600; }}
.focus-signal {{
    background: rgba(16,185,129,0.15);
    color: #10b981;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}}
.focus-body {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    padding: 16px 18px;
}}
.focus-metric {{ text-align: center; }}
.focus-metric span {{ display: block; font-size: 11px; color: #64748b; margin-bottom: 2px; }}
.focus-metric b {{ font-size: 15px; }}
.focus-reason {{
    padding: 12px 18px;
    font-size: 12px;
    color: #94a3b8;
    border-top: 1px solid rgba(255,255,255,0.05);
    line-height: 1.5;
}}

/* 操作建议 */
.advice-box {{
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 16px;
    padding: 28px 30px;
    margin-bottom: 30px;
}}
.advice-box h3 {{ color: #60a5fa; margin-bottom: 16px; font-size: 18px; }}
.advice-box ul {{ list-style: none; }}
.advice-box li {{
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 14px;
    color: #cbd5e1;
}}
.advice-box li:last-child {{ border-bottom: none; }}
.advice-box li::before {{ content: "⚡ "; }}

/* 纪律铁律 */
.discipline {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 40px;
}}
.disc-card {{
    background: linear-gradient(135deg, #1a1f2e, #0f1420);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 22px;
    text-align: center;
}}
.disc-card .lock {{ font-size: 32px; margin-bottom: 10px; }}
.disc-card h4 {{ font-size: 15px; margin-bottom: 8px; color: #f1f5f9; }}
.disc-card p {{ font-size: 12px; color: #94a3b8; line-height: 1.6; }}

/* 风险提示 */
.risk-warning {{
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 40px;
    font-size: 13px;
    color: #fca5a5;
    line-height: 1.8;
}}
.risk-warning b {{ color: #ef4444; }}

footer {{
    text-align: center;
    padding: 30px 0;
    color: #475569;
    font-size: 12px;
    border-top: 1px solid rgba(255,255,255,0.05);
}}

@media (max-width: 768px) {{
    .stats {{ grid-template-columns: repeat(2, 1fr); }}
    .engines-grid {{ grid-template-columns: 1fr; }}
    .discipline {{ grid-template-columns: 1fr; }}
    .focus-grid {{ grid-template-columns: 1fr; }}
    .market-state {{ flex-direction: column; text-align: center; }}
}}
</style>
</head>
<body>

<!-- 顶部海报 -->
<div class="hero">
    <img src="poster.jpg" alt="ETF四引擎轮动系统">
</div>

<div class="container">

<!-- 更新时间 -->
<div class="update-bar">
    数据更新时间：<b>{update_time}</b> ｜ 数据来源：新浪财经 ｜ 共监控 <b>30</b> 只ETF
</div>

<!-- 市场状态 -->
<div class="market-state">
    <div class="market-indicator">{'📈' if '涨' in market_state or '强' in market_state else '📉' if '跌' in market_state else '⚖️'}</div>
    <div class="market-info">
        <h2>当前市场状态：{market_state}</h2>
        <p>{market_desc}</p>
    </div>
</div>

<!-- 统计 -->
<div class="stats">
    <div class="stat-card stat-total"><div class="num">{len(etfs)}</div><div class="label">监控总数</div></div>
    <div class="stat-card stat-buy"><div class="num">{len(buy_list)}</div><div class="label">建议进场/可开网格</div></div>
    <div class="stat-card stat-watch"><div class="num">{len(watch_list)}</div><div class="label">观望</div></div>
    <div class="stat-card stat-avoid"><div class="num">{len(avoid_list)}</div><div class="label">不建议/流动性不足</div></div>
</div>

<!-- 四引擎策略条件 -->
<h2 class="section-title">四引擎入场条件</h2>
<div class="engines-grid">
    <div class="engine-card" style="--ec:#f59e0b">
        <h3>📈 跨境T+0套利</h3>
        <div class="engine-desc">主动趋势追踪 ｜ 适用：单边趋势</div>
        <ul class="rules">
            <li>价格回踩后站上20日均线</li>
            <li>当日成交量较前5日均量萎缩（量比&lt;0.85）</li>
            <li>MA20趋势向上（右侧确认）</li>
            <li>止盈≥2%，跌破MA20下方1.5%止损</li>
            <li>标的：纳指/标普/恒生科技/中概互联等跨境ETF</li>
        </ul>
    </div>
    <div class="engine-card" style="--ec:#06b6d4">
        <h3>🏦 债券节假日套利</h3>
        <div class="engine-desc">事件驱动停泊 ｜ 适用：法定长假前</div>
        <ul class="rules">
            <li>节前倒数第2个交易日买入货币/短债ETF</li>
            <li>享受跨节假日息计提+资金避险溢价</li>
            <li>节后开盘首日卖出，完成资金闭环</li>
            <li>单次预期0.3%-0.8%，年化增厚2%-3%</li>
            <li>标的：华宝添益/银华日利/政金债ETF等</li>
        </ul>
    </div>
    <div class="engine-card" style="--ec:#eab308">
        <h3>🥇 黄金宏观套利</h3>
        <div class="engine-desc">全球宏观共振 ｜ 适用：全球大宗共振</div>
        <ul class="rules">
            <li>纽约金期货站上MA20（前置指标）</li>
            <li>国内黄金ETF同步站稳MA20</li>
            <li>MA20趋势向上，偏离度&lt;8%（未超买）</li>
            <li>止盈5%减半/8%清仓，跌破MA20止损</li>
            <li>标的：华安黄金/博时黄金ETF</li>
        </ul>
    </div>
    <div class="engine-card" style="--ec:#ec4899">
        <h3>🔄 宽基网格自动化</h3>
        <div class="engine-desc">被动震荡收割 ｜ 适用：长期横盘震荡</div>
        <ul class="rules">
            <li>必须选宽基ETF，指数PE分位值&lt;30%</li>
            <li>日均成交额&gt;1亿（流动性底线）</li>
            <li>20日波动&gt;4%（有收割空间）</li>
            <li>每涨跌3%触发一次买卖，自动循环</li>
            <li>严禁高估值行业ETF开网格，防"网破鱼死"</li>
        </ul>
    </div>
</div>

<!-- 重点关注 -->
<h2 class="section-title">🔥 当前建议进场标的（{len(buy_list)}只）</h2>
<div class="focus-grid">
{buy_cards}
</div>

<!-- 全量信号表 -->
<h2 class="section-title">📊 30只ETF全量信号</h2>
<div class="filter-bar">
    <button class="filter-btn active" onclick="filterTable('all', this)">全部</button>
    <button class="filter-btn" onclick="filterTable('A', this)">跨境T+0</button>
    <button class="filter-btn" onclick="filterTable('B', this)">债券套利</button>
    <button class="filter-btn" onclick="filterTable('C', this)">黄金宏观</button>
    <button class="filter-btn" onclick="filterTable('D', this)">宽基网格</button>
    <button class="filter-btn" onclick="filterTable('buy', this)">仅看建议进场</button>
</div>
<div class="table-wrap">
<table>
<thead>
<tr>
    <th>代码</th>
    <th>名称</th>
    <th>引擎</th>
    <th>现价</th>
    <th>MA20</th>
    <th>偏离度</th>
    <th>量比</th>
    <th>日均成交</th>
    <th>MA20状态</th>
    <th>信号</th>
    <th>判断理由</th>
</tr>
</thead>
<tbody>
{all_rows}
</tbody>
</table>
</div>

<!-- 操作建议 -->
<h2 class="section-title">💡 今日操作建议</h2>
<div class="advice-box">
    <h3>基于当前市场状态（{market_state}）的配置建议</h3>
    <ul>
        <li><b>市场判断：</b>{market_desc}</li>
        <li><b>优先引擎：</b>{'跨境T+0 + 黄金宏观' if '涨' in market_state else '宽基网格自动化' if '震' in market_state else '债券/货币ETF防守'}</li>
        <li><b>仓位建议：</b>{'趋势仓60%，网格仓30%，现金10%' if '涨' in market_state else '网格仓50%，趋势仓20%，现金30%' if '震' in market_state else '货币/债券仓60%，网格仓20%，现金20%'}</li>
        <li><b>重点关注：</b>{'、'.join([e['name'] for e in buy_list[:5]])} 等{len(buy_list)}只标的符合入场条件</li>
        <li><b>回避标的：</b>跌破MA20的跨境ETF（如{ '、'.join([e['name'] for e in avoid_list if e.get('engine')=='A'][:3]) }），均线之下不抄底</li>
        <li><b>网格提示：</b>当前{sum(1 for e in etfs if e.get('engine')=='D' and e.get('signal_level')=='buy')}只宽基ETF满足网格条件，但需自行核实对应指数PE分位是否&lt;30%</li>
        <li><b>纪律提醒：</b>条件单设定后绝不因盘中情绪手动干预，跌破止损位无条件执行</li>
    </ul>
</div>

<!-- 三大铁律 -->
<h2 class="section-title">🔒 三大纪律铁律</h2>
<div class="discipline">
    <div class="disc-card">
        <div class="lock">🚪</div>
        <h4>流动性底线</h4>
        <p>绝不碰日成交额低于1亿的冷门ETF，防止滑点过大导致套利失败</p>
    </div>
    <div class="disc-card">
        <div class="lock">📏</div>
        <h4>均线铁律</h4>
        <p>跌破20日均线坚决不买，右侧趋势未确立前绝不盲目抄底</p>
    </div>
    <div class="disc-card">
        <div class="lock">🤖</div>
        <h4>尊重系统</h4>
        <p>条件单一旦设定运行，绝不因盘中情绪波动手动干预</p>
    </div>
</div>

<!-- 风险提示 -->
<div class="risk-warning">
    <b>⚠️ 风险提示：</b>本页面所有信号均基于量化规则自动生成，仅供学习参考，不构成任何投资建议。
    ETF交易存在风险，历史表现不代表未来收益。市场有风险，投资需谨慎，盈亏自负。
    网格交易在单边暴跌行情中可能导致持续亏损，请务必选择低估宽基标的并控制仓位。
</div>

<footer>
    ETF四引擎轮动系统 ｜ 数据来源：新浪财经 ｜ 生成时间：{update_time}<br>
    告别情绪博弈，构建你的系统化交易控制室
</footer>

</div>

<script>
function filterTable(type, btn) {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.etf-row').forEach(row => {{
        if (type === 'all') {{
            row.style.display = '';
        }} else if (type === 'buy') {{
            row.style.display = row.dataset.level === 'buy' ? '' : 'none';
        }} else {{
            row.style.display = row.dataset.engine === type ? '' : 'none';
        }}
    }});
}}
</script>

</body>
</html>"""

# 写入HTML
output_path = "index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML已生成: {output_path}")
print(f"文件大小: {len(html)} 字节")
print(f"建议进场: {len(buy_list)}只 | 观望: {len(watch_list)}只 | 不建议: {len(avoid_list)}只")
