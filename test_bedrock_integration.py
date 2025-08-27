#!/usr/bin/env python3
"""
測試 AWS Bedrock 整合
Test AWS Bedrock integration
"""

import asyncio
from bedrock_client import BedrockClient

async def test_bedrock_integration():
    """測試 Bedrock 整合"""
    print("=== 測試 AWS Bedrock 整合 ===")
    
    # 創建 Bedrock 客戶端
    client = BedrockClient()
    
    # 檢查可用性
    print(f"Bedrock 可用性: {client.available}")
    
    if not client.available:
        print("❌ Bedrock 不可用，無法進行測試")
        return
    
    # 獲取可用模型
    models = client.get_available_models()
    print(f"✅ 可用模型數量: {len(models)}")
    
    # 測試每個模型
    for model_id, model_info in models.items():
        print(f"\n--- 測試模型: {model_info['name']} ---")
        print(f"策略: {model_info['strategy']}")
        print(f"區域: {model_info['region']}")
        
        # 測試模型呼叫
        try:
            system_prompt = f"You are a {model_info['strategy']} player in a fighting game."
            context_prompt = "You are in a fighting game. Consider your position and health."
            
            print("🔄 呼叫 Bedrock 模型...")
            actions = await client.invoke_model(
                model_id,
                system_prompt,
                context_prompt,
                1
            )
            
            if actions:
                print(f"✅ 成功獲取動作: {actions}")
            else:
                print("❌ 無法獲取動作")
                
        except Exception as e:
            print(f"❌ 模型呼叫失敗: {e}")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    asyncio.run(test_bedrock_integration())
