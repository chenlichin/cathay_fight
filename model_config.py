# 模型配置檔案
# 您可以在這裡設定要使用的 LLM 模型

# 預設模型設定（HuggingFace，本地可載入）
DEFAULT_MODEL = "gpt2"

# 可用的模型列表
AVAILABLE_MODELS = {
    # 較小的模型（載入速度快，適合測試）
    "gpt2": {
        "name": "GPT-2 (124M)",
        "description": "OpenAI 的 GPT-2 模型，較小但速度快",
        "size": "124M",
        "speed": "快"
    },
    
    "bigscience/bloom-560m": {
        "name": "BLOOM-560M",
        "description": "BigScience 的多語言模型，支援中文",
        "size": "560M",
        "speed": "中等"
    },
    
    "microsoft/DialoGPT-medium": {
        "name": "DialoGPT Medium",
        "description": "微軟的對話生成模型",
        "size": "345M",
        "speed": "中等"
    },
    
    "EleutherAI/gpt-neo-125M": {
        "name": "GPT-Neo 125M",
        "description": "EleutherAI 的開源 GPT 模型",
        "size": "125M",
        "speed": "快"
    },
    
    # 較大的模型（效果更好，但載入較慢）
    "gpt2-medium": {
        "name": "GPT-2 Medium (355M)",
        "description": "GPT-2 中型版本，效果更好",
        "size": "355M",
        "speed": "中等"
    },
    
    "bigscience/bloom-1b1": {
        "name": "BLOOM-1B1",
        "description": "BigScience 的 1.1B 參數模型",
        "size": "1.1B",
        "speed": "慢"
    }
}

# AWS Bedrock 模型（供 UI 選擇，實際呼叫可透過 bedrock_client）
AWS_MODELS = {
    "amazon.nova-micro-v1:0": {
        "name": "Amazon Nova Micro",
        "description": "輕量級模型，快速回應",
        "size": "-",
        "speed": "極快",
        "strategy": "aggressive",
        "region": "us-east-1"
    },
    "amazon.nova-lite-v1:0": {
        "name": "Amazon Nova Lite",
        "description": "平衡型模型，攻防兼備",
        "size": "-",
        "speed": "快",
        "strategy": "balanced",
        "region": "us-east-1"
    },
    "amazon.nova-pro-v1:0": {
        "name": "Amazon Nova Pro",
        "description": "高級模型，智能策略",
        "size": "-",
        "speed": "中等",
        "strategy": "defensive",
        "region": "us-east-1"
    },
    "anthropic.claude-3-haiku-20240307-v1:0": {
        "name": "Claude 3 Haiku",
        "description": "最強模型，全能型策略",
        "size": "-",
        "speed": "中等",
        "strategy": "balanced",
        "region": "us-east-1"
    }
}

# 模型載入設定
MODEL_SETTINGS = {
    "max_new_tokens": 50,  # 生成的最大 token 數量
    "temperature": 0.8,    # 生成溫度（控制隨機性）
    "do_sample": True,     # 是否使用採樣
    "top_p": 0.9,         # 核採樣參數
}

def get_model_info(model_name):
    """獲取模型資訊"""
    if model_name in AVAILABLE_MODELS:
        return AVAILABLE_MODELS[model_name]
    if model_name in AWS_MODELS:
        return AWS_MODELS[model_name]
    return None

def list_available_models():
    """列出所有可用模型"""
    print("📋 可用的 LLM 模型：")
    print("=" * 60)
    for model_id, info in AVAILABLE_MODELS.items():
        print(f"🔸 {model_id}")
        print(f"   名稱: {info['name']}")
        print(f"   描述: {info['description']}")
        print(f"   大小: {info['size']}")
        print(f"   速度: {info['speed']}")
        print()

def list_available_aws_models():
    """列出所有可用的 AWS 模型"""
    print("📋 可用的 AWS 模型：")
    print("=" * 60)
    for model_id, info in AWS_MODELS.items():
        print(f"🔸 {model_id}")
        print(f"   名稱: {info['name']}")
        print(f"   描述: {info['description']}")
        print(f"   策略: {info['strategy']}")
        print(f"   區域: {info['region']}")
        print()

def get_aws_models():
    """回傳 AWS 模型清單字典"""
    return AWS_MODELS

def get_recommended_model():
    """獲取推薦的模型（根據系統性能）"""
    import psutil
    
    # 檢查可用記憶體
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    if memory_gb >= 8:
        return "bigscience/bloom-560m"  # 8GB+ 記憶體
    elif memory_gb >= 4:
        return "gpt2-medium"  # 4GB+ 記憶體
    else:
        return "gpt2"  # 較小記憶體 