import os
import sys
import paddle
import pymupdf
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from graphs.node import get_ocr_instance

def test_paddleocr_v5_result_structure():
    """测试PaddleOCR v5返回结构"""
    print("=" * 60)
    print("测试PaddleOCR v5返回结构")
    print("=" * 60)
    
    # 查找测试PDF文件
    pdf_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pdf') and not file.startswith('~'):
                pdf_path = os.path.join(root, file)
                pdf_files.append(pdf_path)
    
    if not pdf_files:
        print("\n❌ 未找到PDF文件")
        return
    
    # 使用第一个PDF文件
    pdf_path = pdf_files[0]
    print(f"\n使用PDF文件: {pdf_path}")
    
    # 打开PDF
    doc = pymupdf.open(pdf_path)
    page = doc[0]
    
    # 转换为图片
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_image_path = temp_file.name
    
    pix.save(temp_image_path)
    print(f"图片已保存: {temp_image_path}")
    
    # 获取OCR实例
    ocr = get_ocr_instance()
    
    if ocr is None:
        print("❌ OCR引擎初始化失败")
        return
    
    print("✓ OCR引擎初始化成功")
    
    # OCR识别
    print("\n开始OCR识别...")
    try:
        result = ocr.predict(temp_image_path)
        print(f"\n✓ OCR识别完成")
        print(f"结果类型: {type(result)}")
        print(f"结果长度: {len(result) if result else 0}")
        
        if result and len(result) > 0:
            print(f"\n第一个结果:")
            print(f"  类型: {type(result[0])}")
            print(f"  内容: {result[0]}")
            
            if isinstance(result[0], dict):
                print(f"\n字典键: {result[0].keys()}")
                if 'results' in result[0]:
                    print(f"results长度: {len(result[0]['results'])}")
                    if len(result[0]['results']) > 0:
                        print(f"第一个result: {result[0]['results'][0]}")
        else:
            print("❌ OCR识别返回空结果")
    except Exception as e:
        print(f"❌ OCR识别失败: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        # 清理临时文件
        if os.path.exists(temp_image_path):
            try:
                os.unlink(temp_image_path)
            except:
                pass
    
    doc.close()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_paddleocr_v5_result_structure()
