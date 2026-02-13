import json
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 读取配置文件
with open('config/workflow_input.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

try:
    # 直接导入并使用GraphService
    from main import service
    import asyncio
    
    # 运行工作流
    result = asyncio.run(service.run(data))
    
    # 打印结果（使用UTF-8编码）
    print("final_pdf_path:")
    print(result.get('final_pdf_path', ''))
    print("\nanalysis_report:")
    print(result.get('analysis_report', ''))
    
except Exception as e:
    print(f"运行失败: {e}")
    import traceback
    traceback.print_exc()