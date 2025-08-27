# LLM 模型使用指南

## 概述

現在您的 AI 格鬥遊戲支援真正的 LLM 模型來控制角色動作！系統會根據您的選擇使用真實的語言模型或簡化的 AI 模擬器。

## 快速開始

### 1. 使用預設模型
直接執行遊戲，系統會使用 `model_config.py` 中設定的預設模型：
```bash
python main_game.py
```

### 2. 切換模型
使用模型切換工具：
```bash
python switch_model.py
```

### 3. 手動修改模型
編輯 `model_config.py` 檔案，修改 `DEFAULT_MODEL` 變數：
```python
DEFAULT_MODEL = "gpt2"  # 改為您想要的模型
```

## 可用模型

### 🚀 快速模型（適合測試）
- **gpt2** (124M) - OpenAI 的 GPT-2 模型，載入快速
- **EleutherAI/gpt-neo-125M** (125M) - 開源 GPT 模型

### ⚖️ 平衡模型（推薦）
- **bigscience/bloom-560m** (560M) - 多語言模型，支援中文
- **microsoft/DialoGPT-medium** (345M) - 對話生成模型
- **gpt2-medium** (355M) - GPT-2 中型版本

### 🧠 大型模型（效果最佳）
- **bigscience/bloom-1b1** (1.1B) - 大型多語言模型

## 模型設定

### 生成參數
在 `model_config.py` 中可以調整：
```python
MODEL_SETTINGS = {
    "max_new_tokens": 50,  # 生成的最大 token 數量
    "temperature": 0.8,    # 生成溫度（0.1-1.0，越高越隨機）
    "do_sample": True,     # 是否使用採樣
    "top_p": 0.9,         # 核採樣參數
}
```

### 策略提示詞
在 `main_game.py` 中可以修改策略提示詞：
```python
model_prompts = [
    "You are a very aggressive player",  # 攻擊型
    "You are a very defensive player"    # 防禦型
]
```

## 故障排除

### 模型載入失敗
如果看到「使用簡化 AI 模擬器」訊息：

1. **檢查網路連線**：確保能連接到 Hugging Face
2. **檢查記憶體**：大型模型需要足夠的 RAM
3. **嘗試較小模型**：使用 `gpt2` 或 `EleutherAI/gpt-neo-125M`
4. **檢查 transformers 安裝**：`pip install transformers torch`

### 性能問題
- **載入慢**：使用較小的模型
- **回應慢**：調整 `max_new_tokens` 參數
- **記憶體不足**：關閉其他程式或使用較小模型

## 自定義模型

### 添加新模型
在 `model_config.py` 的 `AVAILABLE_MODELS` 中添加：
```python
"your-model-name": {
    "name": "您的模型名稱",
    "description": "模型描述",
    "size": "模型大小",
    "speed": "載入速度"
}
```

### 使用本地模型
將模型檔案放在本地，然後指定路徑：
```python
DEFAULT_MODEL = "./models/your-local-model"
```

## 模型行為調試

### 查看模型回應
遊戲執行時會在控制台顯示模型的回應，格式如下：
```
bigscience/bloom-560m response:
- MOVE_CLOSER
- HIGH_ATTACK
- JUMP
- LOW_ATTACK
```

### 調整策略
修改 `llm_fighter.py` 中的提示詞來改變 AI 行為：
```python
prompt = f"{full_system_prompt}\nYour next moves are:"
```

## 推薦設定

### 初次使用
```python
DEFAULT_MODEL = "gpt2"  # 快速載入，適合測試
```

### 正式遊戲
```python
DEFAULT_MODEL = "bigscience/bloom-560m"  # 支援中文，效果較好
```

### 高性能系統
```python
DEFAULT_MODEL = "bigscience/bloom-1b1"  # 最佳效果，需要更多資源
```

## 注意事項

1. **首次載入**：模型需要下載，可能需要幾分鐘
2. **記憶體使用**：大型模型會佔用較多 RAM
3. **網路依賴**：需要網路連線來下載模型
4. **模型快取**：下載後的模型會快取在本地

現在您可以享受真正的 AI 對戰體驗了！🎮 