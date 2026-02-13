import os
import sys
import paddle
import pymupdf
import tempfile

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from graphs.node import get_ocr_instance

def test_paddleocr_v5_final():
    """最终测试PaddleOCR v5 (使用GPU0)"""
    print("=" * 60)
    print("最终测试PaddleOCR v5 (使用GPU0)")
    print("=" * 60)
    
    # 检查环境
    print("\n1. 检查环境:")
    print(f"   Python版本: {sys.version}")
    print(f"   Paddle版本: {paddle.__version__}")
    print(f"   CUDA可用: {paddle.is_compiled_with_cuda()}")
    
    if paddle.is_compiled_with_cuda():
        print(f"   GPU数量: {paddle.device.cuda.device_count()}")
        print(f"   当前设备: {paddle.device.get_device()}")
    
    # 检查环境变量
    print("\n2. 检查环境变量:")
    cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES', 'NOT SET')
    print(f"   CUDA_VISIBLE_DEVICES: {cuda_visible}")
    
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
    
    print(f"\n3. 找到 {len(pdf_files)} 个PDF文件:")
    for i, pdf_file in enumerate(pdf_files):
        print(f"   {i + 1}. {pdf_file}")
    
    # 使用第一个PDF文件
    pdf_path = pdf_files[0]
    print(f"\n4. 使用PDF文件: {pdf_path}")
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print("✓ PDF文件存在")
    
    # 打开PDF
    print("\n5. 打开PDF文件...")
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    print(f"✓ PDF打开成功，共 {total_pages} 页")
    
    # 只处理第一页
    page_num = 0
    print(f"\n6. 处理第 {page_num + 1} 页...")
    page = doc[page_num]
    
    # 转换为图片
    print("   1. 转换为图片...")
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
    print(f"   ✓ 图片尺寸: {pix.width} x {pix.height}")
    
    # 保存到临时文件
    print("   2. 保存到临时文件...")
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_image_path = temp_file.name
    
    pix.save(temp_image_path)
    print(f"   ✓ 图片已保存: {temp_image_path}")
    print(f"   ✓ 文件大小: {os.path.getsize(temp_image_path)} bytes")
    
    # 获取OCR实例
    print("\n7. 获取OCR实例...")
    ocr = get_ocr_instance()
    
    if ocr is None:
        print("❌ OCR引擎初始化失败")
        return
    
    print("✓ OCR引擎初始化成功")
    
    # OCR识别
    print(f"\n8. 开始OCR识别第 {page_num + 1} 页...")
    print("   (这可能需要一些时间，请耐心等待...)")
    
    try:
        # 使用PaddleOCR v5的predict方法
        result = ocr.predict(temp_image_path)
        print(f"\n✓ OCR识别完成")
        print(f"   结果类型: {type(result)}")
        print(f"   结果长度: {len(result) if result else 0}")
        
        if result and len(result) > 0:
            print(f"\n9. 处理识别结果...")
            page_content = ""
            for res in result:
                if isinstance(res, dict):
                    rec_texts = res.get('rec_texts', [])
                    rec_scores = res.get('rec_scores', [])
                    print(f"   检测到 {len(rec_texts)} 个文本区域")
                    for i, text in enumerate(rec_texts):
                        if text.strip():
                            confidence = rec_scores[i] if i < len(rec_scores) else 0.0
                            page_content += text + "\n"
                            if i < 5:  # 只打印前5个
                                print(f"   文本 {i + 1}: {text} (置信度: {confidence:.2f})")
            
            if page_content.strip():
                print(f"\n   ✓ 文本提取成功")
                print(f"   ✓ 内容长度: {len(page_content)}")
                print("\n10. 文本预览:")
                print("=" * 40)
                print(page_content[:500] + ("..." if len(page_content) > 500 else ""))
                print("=" * 40)
            else:
                print("❌ 提取的文本为空")
        else:
            print("❌ OCR识别返回空结果")
    except Exception as e:
        print(f"\n❌ OCR识别失败: {e}")
        import traceback
        print(f"\n详细错误信息:")
        print(traceback.format_exc())
    finally:
        # 清理临时文件
        if os.path.exists(temp_image_path):
            try:
                os.unlink(temp_image_path)
                print(f"\n✓ 临时文件已清理: {temp_image_path}")
            except:
                pass
    
    doc.close()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_paddleocr_v5_final()
