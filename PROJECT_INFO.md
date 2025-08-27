# 專案資訊 / Project Information

## 📊 專案統計 / Project Statistics

- **版本 / Version**: 1.0.0
- **最後更新 / Last Updated**: 2025年1月 / January 2025
- **Python 版本 / Python Version**: 3.8+
- **主要依賴 / Main Dependencies**: PyGame 2.5+, Transformers 4.30+
- **授權 / License**: MIT License

## 🎯 開發目標 / Development Goals

### 已完成 / Completed ✅
- [x] 基礎遊戲引擎 / Basic game engine
- [x] AI 對戰系統 / AI battle system
- [x] 音效系統 / Audio system
- [x] 字體管理 / Font management
- [x] 測試工具 / Testing tools
- [x] 模型配置 / Model configuration

### 計劃中 / Planned 📋
- [ ] 效能優化 / Performance optimization
- [ ] 錯誤處理改進 / Error handling improvement
- [ ] 配置管理系統 / Configuration management system

## 🏗️ 技術架構 / Technical Architecture

### 核心模組 / Core Modules
- `main_game.py` - 主遊戲循環 / Main game loop
- `llm_fighter.py` - AI 戰士邏輯 / AI fighter logic
- `menu.py` - 使用者介面 / User interface
- `audio_manager.py` - 音效管理 / Audio management
- `font_manager.py` - 字體管理 / Font management
- `model_config.py` - 模型配置 / Model configuration

### 支援模組 / Support Modules
- `simple_ai.py` - 簡單 AI 備用 / Simple AI fallback
- `switch_model.py` - 模型切換工具 / Model switching tool

### 配置檔案 / Configuration Files
- `requirements.txt` - 基本依賴
- `requirements-dev.txt` - 開發依賴

## 🧪 測試覆蓋 / Test Coverage

專案包含完整的測試工具套件，涵蓋：
- 音效系統測試 / Audio system testing
- 選單功能測試 / Menu functionality testing
- 角色選擇測試 / Character selection testing
- 勝利畫面測試 / Victory screen testing

## 🔧 配置選項 / Configuration Options

- **AI 模型**：在 `model_config.py` 中修改模型設定
- **音效音量**：在遊戲中調整音效和音樂音量
- **視窗大小**：支援視窗化模式，可調整大小

## 🚀 安裝說明 / Installation Guide

### 一般使用者 / General Users
```bash
pip install -r requirements.txt
```

### 開發者 / Developers
```bash
pip install -r requirements-dev.txt
```

## 📞 聯絡資訊 / Contact Information

- **GitHub**: [@chenlichin](https://github.com/chenlichin)
- **專案頁面**: [cathay_fight](https://github.com/chenlichin/cathay_fight)
- **問題回報**: [Issues](https://github.com/chenlichin/cathay_fight/issues)

## 🙏 致謝 / Acknowledgments

- PyGame 社群提供優秀的遊戲開發框架
- Hugging Face 提供變換器模型
- 所有貢獻者和測試者
