# 黃巧君 Fight ! - AI 格鬥遊戲
# Huang Qiao Jun Fight! - AI Fighting Game

[English](#english) | [繁體中文](#繁體中文)

---

## 🇹🇼 繁體中文

### 🎮 專案簡介
這是一個使用 PyGame 和大型語言模型 (LLMs) 的 AI 格鬥遊戲，兩個 AI 角色可以在聊天機器人競技場中對戰。專案結合了傳統格鬥遊戲的樂趣和現代 AI 技術的創新。

### ✨ 主要功能
- 🎯 **AI 對戰系統**：使用 Hugging Face 模型進行智能決策
- 🔊 **完整音效系統**：背景音樂、攻擊音效、選單音效
- 🎨 **自訂字體支援**：支援中文顯示和自訂字體
- 🧪 **模組化測試工具**：完整的測試套件
- 🖥️ **可調整視窗大小**：支援視窗化模式
- 🌏 **中文介面支援**：完整的繁體中文使用者介面
- ⚙️ **模型配置管理**：輕鬆切換不同的 AI 模型

### 🚀 安裝與執行

#### 前置需求
- Python 3.8+
- PyGame 2.5+
- 可選：Hugging Face Transformers (用於 LLM 功能)

#### 安裝步驟
1. **克隆專案**
   ```bash
   git clone https://github.com/chenlichin/cathay_fight.git
   cd cathay_fight
   ```

2. **安裝依賴**
   ```bash
   # 一般使用者
   pip install -r requirements.txt
   
   # 開發者（包含測試工具）
   pip install -r requirements-dev.txt
   ```

3. **執行程式**
   ```bash
   python main_game.py
   ```

> 📖 **詳細安裝說明請參考 [INSTALL.md](INSTALL.md)**

### 🎯 遊戲操作
- **主選單**：使用 ↑↓ 或 W/S 切換選項，Enter 確認
- **角色選擇**：選擇角色和 AI 策略
- **遊戲中**：觀看 AI 角色自動對戰
- **回合結束**：查看分數和選擇下一回合

### 📁 專案結構
```
cathay_fight/
├── main_game.py          # 主遊戲程式
├── menu.py               # 選單系統
├── llm_fighter.py        # AI 戰士邏輯
├── simple_ai.py          # 簡單 AI 備用系統
├── audio_manager.py      # 音效管理
├── font_manager.py       # 字體管理
├── model_config.py       # AI 模型配置
├── assets/               # 遊戲資源
│   ├── images/          # 圖片資源
│   └── music/           # 音效檔案
├── tests/                # 測試工具
├── requirements.txt      # 基本依賴
└── requirements-dev.txt  # 開發依賴
```

### 🔧 配置選項
- **AI 模型**：在 `model_config.py` 中修改模型設定
- **音效音量**：在遊戲中調整音效和音樂音量
- **視窗大小**：支援視窗化模式，可調整大小

### 🧪 測試工具
專案包含多個測試工具：
- `test_attack_sounds.py` - 攻擊音效測試
- `test_audio.py` - 音效系統測試
- `test_menu_audio.py` - 選單音效測試
- `test_character_selection.py` - 角色選擇測試

### 🤝 貢獻指南
歡迎提交 Issue 和 Pull Request！

---

## 🇺🇸 English

### 🎮 Project Description
This is an AI fighting game built with PyGame and Large Language Models (LLMs), where two AI characters can battle each other in a chatbot arena. The project combines the fun of traditional fighting games with the innovation of modern AI technology.

### ✨ Key Features
- 🎯 **AI Battle System**: Uses Hugging Face models for intelligent decision-making
- 🔊 **Complete Audio System**: Background music, attack sounds, menu sounds
- 🎨 **Custom Font Support**: Supports Chinese display and custom fonts
- 🧪 **Modular Testing Tools**: Comprehensive test suite
- 🖥️ **Resizable Window**: Supports windowed mode
- 🌏 **Chinese Interface**: Complete Traditional Chinese UI
- ⚙️ **Model Configuration**: Easy switching between different AI models

### 🚀 Installation & Usage

#### Prerequisites
- Python 3.8+
- PyGame 2.5+
- Optional: Hugging Face Transformers (for LLM features)

#### Installation Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/chenlichin/cathay_fight.git
   cd cathay_fight
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**
   ```bash
   python main_game.py
   ```

### 🎯 Game Controls
- **Main Menu**: Use ↑↓ or W/S to navigate, Enter to confirm
- **Character Selection**: Choose characters and AI strategies
- **In Game**: Watch AI characters battle automatically
- **Round End**: View scores and choose next round

### 📁 Project Structure
```
cathay_fight/
├── main_game.py          # Main game program
├── menu.py               # Menu system
├── llm_fighter.py        # AI fighter logic
├── simple_ai.py          # Simple AI fallback system
├── audio_manager.py      # Audio management
├── font_manager.py       # Font management
├── model_config.py       # AI model configuration
├── assets/               # Game resources
│   ├── images/          # Image resources
│   └── music/           # Audio files
└── tests/                # Testing tools
```

### 🔧 Configuration Options
- **AI Models**: Modify model settings in `model_config.py`
- **Audio Volume**: Adjust sound and music volume in game
- **Window Size**: Supports windowed mode with resizable window

### 🧪 Testing Tools
The project includes multiple testing tools:
- `test_attack_sounds.py` - Attack sound testing
- `test_audio.py` - Audio system testing
- `test_menu_audio.py` - Menu sound testing
- `test_character_selection.py` - Character selection testing

### 🤝 Contributing
Issues and Pull Requests are welcome!

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- PyGame community for the excellent game development framework
- Hugging Face for the transformer models
- All contributors and testers


