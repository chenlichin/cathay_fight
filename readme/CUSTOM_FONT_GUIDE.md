# 客製化字體使用指南

## 如何使用客製化字體

### 1. 準備字體檔案
將您的字體檔案（.ttf 或 .otf 格式）放入 `assets/fonts/` 資料夾中。

### 2. 修改字體設定

#### 在 `menu.py` 中：
```python
# 使用客製化字體
self.title_font = font_manager.get_font("your_font.ttf", 80)
self.menu_font = font_manager.get_font("your_font.ttf", 40)
self.subtitle_font = font_manager.get_font("your_font.ttf", 30)

# 或使用系統字體（預設）
self.title_font = font_manager.get_font(size=80)
self.menu_font = font_manager.get_font(size=40)
self.subtitle_font = font_manager.get_font(size=30)
```

#### 在 `main_game.py` 中：
```python
# 使用客製化字體
count_font = font_manager.get_font("your_font.ttf", 80)
score_font = font_manager.get_font("your_font.ttf", 30)
game_over_font = font_manager.get_font("your_font.ttf", 60)
option_font = font_manager.get_font("your_font.ttf", 40)

# 或使用系統字體（預設）
count_font = font_manager.get_font(size=80)
score_font = font_manager.get_font(size=30)
game_over_font = font_manager.get_font(size=60)
option_font = font_manager.get_font(size=40)
```

### 3. 字體檔案格式支援
- **TrueType (.ttf)**
- **OpenType (.otf)**
- **其他 Pygame 支援的字體格式**

### 4. 字體回退機制
如果客製化字體載入失敗，系統會自動回退到以下字體：
1. microsoftyahei (微軟雅黑)
2. simhei (黑體)
3. simsun (宋體)
4. kaiti (楷體)
5. 系統預設字體

### 5. 範例：使用現有的 turok.ttf 字體

如果您想使用專案中現有的 `turok.ttf` 字體：

```python
# 在 menu.py 中
self.title_font = font_manager.get_font("turok.ttf", 80)
self.menu_font = font_manager.get_font("turok.ttf", 40)

# 在 main_game.py 中
count_font = font_manager.get_font("turok.ttf", 80)
score_font = font_manager.get_font("turok.ttf", 30)
```

**注意**：`turok.ttf` 可能不支援中文字符，建議使用支援中文的字體檔案。

### 6. 推薦的中文字體
- **思源黑體** (Source Han Sans)
- **思源宋體** (Source Han Serif)
- **文泉驛微米黑**
- **Noto Sans CJK**

### 7. 字體快取
字體管理器會自動快取已載入的字體，提高效能。如果您更換字體檔案，請重新啟動遊戲。

### 8. 除錯
如果字體載入有問題，請檢查：
- 字體檔案是否在正確的資料夾中
- 字體檔案名稱是否正確
- 字體檔案是否損壞
- 控制台輸出的錯誤訊息 