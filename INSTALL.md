# 安裝指南 / Installation Guide

## 🚀 快速開始 / Quick Start

### 一般使用者 / General Users
如果你只想玩遊戲，執行以下命令：

```bash
# 1. 克隆專案
git clone https://github.com/chenlichin/cathay_fight.git
cd cathay_fight

# 2. 安裝基本依賴
pip install -r requirements.txt

# 3. 執行程式
python main_game.py
```

### 開發者 / Developers
如果你要開發或貢獻程式碼，執行以下命令：

```bash
# 1. 克隆專案
git clone https://github.com/chenlichin/cathay_fight.git
cd cathay_fight

# 2. 安裝完整開發工具鏈
pip install -r requirements-dev.txt

# 3. 執行程式
python main_game.py

# 4. 運行測試
pytest tests/
```

## 📋 依賴說明 / Dependencies Explanation

### requirements.txt
- **pygame**: 遊戲引擎
- **transformers**: AI 模型支援（可選）
- **torch**: PyTorch 深度學習框架（可選）

### requirements-dev.txt
- **pytest**: 測試框架
- **black**: 程式碼格式化
- **flake8**: 程式碼品質檢查
- **其他開發工具**

## ❓ 常見問題 / FAQ

**Q: 我只需要玩遊戲，需要安裝 requirements-dev.txt 嗎？**
A: 不需要！只需要 `pip install -r requirements.txt`

**Q: 安裝 transformers 失敗怎麼辦？**
A: 可以跳過，遊戲會使用簡單的 AI 備用系統

**Q: 如何更新到最新版本？**
A: `git pull` 然後重新安裝依賴

## 🔧 故障排除 / Troubleshooting

### 音效問題
- 確保系統音效驅動正常
- 檢查音量設定

### 字體問題
- 確保系統支援中文字體
- 或使用自訂字體檔案

### AI 模型問題
- 如果 transformers 安裝失敗，遊戲仍可正常運行
- 會自動切換到簡單 AI 模式
