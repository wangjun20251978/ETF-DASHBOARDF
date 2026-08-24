# ETF四引擎轮动系统 - 实时信号看板

> 告别情绪博弈，构建你的系统化交易控制室

基于量化规则的ETF交易信号看板，覆盖跨境T+0、债券节假日套利、黄金宏观套利、宽基网格自动化四大引擎，实时监控30只主流ETF的入场信号。

## 功能特性

- **四引擎策略矩阵**：根据市场环境自动匹配最优交易引擎
- **30只ETF实时监控**：跨境ETF、债券/货币ETF、黄金ETF、宽基ETF全覆盖
- **量化入场条件**：基于20日均线、量比、波动率、流动性等多维度判断
- **市场状态判断**：基于沪深300与MA20关系自动判定趋势/震荡/下跌
- **重点标的卡片**：建议进场标的的详细指标展示
- **可筛选信号表**：按引擎类型或信号等级快速筛选
- **每日操作建议**：仓位配置、优先引擎、回避标的一目了然
- **三大纪律铁律**：流动性底线、均线铁律、系统纪律

## 四大引擎

| 引擎 | 适用环境 | 核心逻辑 | 标的类型 |
|------|---------|---------|---------|
| 跨境T+0套利 | 单边趋势 | MA20支撑+缩量回踩，2%止盈 | 纳指/标普/恒生/中概互联 |
| 债券节假日套利 | 法定长假前 | 节前买入享跨节息，节后卖出 | 货币/短债/政金债ETF |
| 黄金宏观套利 | 全球大宗共振 | 纽约金前置指标+MA20趋势 | 黄金ETF |
| 宽基网格自动化 | 长期横盘震荡 | 低估宽基+3%网格自动循环 | 沪深300/中证500/创业板等 |

## 信号说明

- 🟢 **建议进场/可开网格**：满足该引擎全部入场条件
- 🟡 **观望**：部分条件满足，等待更佳入场点
- 🔴 **不建议/流动性不足**：跌破均线或成交不活跃，回避

## 部署到 GitHub Pages

### 方法一：网页端操作（最简单）

1. 登录 GitHub，点击右上角 **+** → **New repository**
2. 仓库名填写 `etf-dashboard`（或任意名称），选择 **Public**，点击 **Create repository**
3. 在仓库页面点击 **uploading an existing file**
4. 把本文件夹里的 `index.html` 和 `poster.jpg` 拖进去，点击 **Commit changes**
5. 进入仓库 **Settings** → 左侧 **Pages**
6. **Source** 选择 `Deploy from a branch`，**Branch** 选择 `main` / `master`，文件夹选 `/ (root)`，点击 **Save**
7. 等待1-2分钟，页面上方会显示你的网址：`https://你的用户名.github.io/etf-dashboard/`

### 方法二：Git命令行

```bash
# 1. 初始化仓库
git init
git add index.html poster.jpg README.md
git commit -m "init: ETF四引擎轮动系统看板"

# 2. 关联远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/etf-dashboard.git
git branch -M main
git push -u origin main

# 3. 在 GitHub 仓库 Settings → Pages 中开启 Pages 即可
```

## 数据更新

当前页面为静态快照，如需更新数据：

1. 运行数据获取脚本（需Python环境）：
   ```bash
   pip install requests
   python fetch_sina.py    # 从新浪财经获取最新数据
   python gen_html.py      # 生成新的 index.html
   ```
2. 将新生成的 `index.html` 替换到仓库中，commit并push即可

## 项目结构

```
etf-dashboard/
├── index.html      # 主页面（GitHub Pages入口）
├── poster.jpg      # 顶部宣传海报
├── README.md       # 项目说明
├── fetch_sina.py   # 数据获取脚本（新浪财经）
└── gen_html.py     # HTML生成脚本
```

## 风险提示

⚠️ 本项目所有信号均基于量化规则自动生成，仅供学习参考，**不构成任何投资建议**。

- ETF交易存在风险，历史表现不代表未来收益
- 网格交易在单边暴跌行情中可能导致持续亏损
- 请务必选择低估宽基标的并严格控制仓位
- 市场有风险，投资需谨慎，盈亏自负

## 数据来源

新浪财经 API（历史K线数据）

---

*告别情绪博弈，从"散户"进化为"系统工厂长"*
