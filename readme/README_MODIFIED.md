# 黃巧君 Fight ! - 修改版 AI 格鬥遊戲

## 專案說明

這是基於原始 PyGame Model Brawl League 專案的修改版本，增加了完整的遊戲選單系統和更豐富的遊戲體驗。

## 新增功能

### 1. 遊戲登入畫面
- 快打旋風風格的主標題「黃巧君 Fight !」
- 選單選項：進入遊戲、結束遊戲
- 選項閃爍效果和鍵盤導航

### 2. 角色選取畫面
- 兩個玩家分別選擇角色（戰士/法師）
- 模型策略選擇（防禦型/攻擊型）
- 角色預覽和詳細說明
- 完整的鍵盤控制

### 3. 擴展的主遊戲畫面
- 兩側顯示 AI 策略和動作資訊
- 即時顯示模型執行狀態
- 血量和狀態監控
- Game Over 畫面和選項

### 4. 智能模型載入
- 支援 Hugging Face 模型（可自行替換）
- 網路連線失敗時自動使用簡化 AI
- 保留原始模型載入邏輯

## 安裝和執行

### 1. 安裝依賴
```bash
# 基本依賴
sudo pip3 install pygame

# 如果要使用 Hugging Face 模型
sudo pip3 install transformers torch
```

### 2. 啟動遊戲
```bash
python3 main_game.py
```

## 模型自定義

### 更換 Hugging Face 模型
在 `main_game.py` 中修改以下行：
```python
MODEL_NAME = "your-model-name"  # 替換為您想要的模型
```

支援的模型類型：
- 任何支援 text-generation 的 Hugging Face 模型
- 建議使用較小的模型（如 0.5B-1B 參數）以確保流暢運行

### 備用 AI 系統
當無法載入 Hugging Face 模型時，系統會自動使用 `simple_ai.py` 中的簡化 AI：
- 防禦型：更多移動和防守動作
- 攻擊型：更多攻擊和進逼動作

## 遊戲控制

### 主選單
- ↑↓ 或 W/S：選擇選項
- Enter 或 Space：確認

### 角色選擇
- ←→ 或 A/D：選擇角色/模型
- ↑↓ 或 W/S：切換選擇類型
- Enter/Space：確認選擇
- ESC：返回主選單

### Game Over 畫面
- ↑↓ 或 W/S：選擇選項
- Enter 或 Space：確認

## 檔案結構

```
bedrock_brawler/
├── main_game.py          # 主遊戲檔案（修改版）
├── menu.py               # 選單系統
├── simple_ai.py          # 簡化 AI 模擬器
├── llm_fighter.py        # AI 戰士類別
├── fighter.py            # 原始戰士類別
├── assets/               # 遊戲資源
│   ├── fonts/           # 字體檔案
│   └── images/          # 圖片資源
└── requirements.txt      # 原始依賴清單
```

## 技術特色

1. **模組化設計**：選單系統、AI 邏輯、遊戲邏輯分離
2. **容錯機制**：網路問題時自動切換到備用 AI
3. **可擴展性**：易於添加新角色、新模型、新功能
4. **用戶友好**：完整的 UI 和清晰的操作指引

## 開發說明

### 添加新角色
1. 在 `assets/images/` 中添加角色圖片
2. 在 `menu.py` 的 `CharacterSelectMenu` 中更新角色列表
3. 在 `main_game.py` 中添加對應的動畫步驟

### 添加新 AI 策略
1. 在 `simple_ai.py` 中添加新的策略邏輯
2. 在 `menu.py` 中更新模型選項
3. 在 `main_game.py` 中添加對應的 prompt

## 授權

基於原始專案的授權條款。

