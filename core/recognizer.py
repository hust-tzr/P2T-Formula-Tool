"""
Pix2Text recognizer wrapper module.
Encapsulates pix2text recognition functionality with error handling and progress tracking.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path
from PIL import Image
import threading
import time

try:
    from pix2text import Pix2Text
except ImportError:
    raise ImportError("pix2text库未安装。请运行: pip install pix2text")


logger = logging.getLogger(__name__)


class RecognitionError(Exception):
    """识别错误基类"""
    pass


class ModelLoadError(RecognitionError):
    """模型加载错误"""
    pass


class FormulaRecognizer:
    """
    pix2text 公式识别器
    
    支持：
    - 单张图片识别
    - 批量图片识别
    - 识别进度回调
    - 错误处理和重试
    """
    
    _instance = None  # 单例
    _lock = threading.Lock()
    
    def __new__(cls):
        """确保全局只有一个pix2text模型实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化识别器"""
        if self._initialized:
            return
        
        self._initialized = True
        self.p2t = None
        self.is_loading = False
        self.load_failed = False
        self.load_error_msg = ""
    
    def ensure_loaded(self, on_progress=None):
        """
        确保模型已加载
        
        Args:
            on_progress: 进度回调，接收 (current, total, message) 的函数
            
        Raises:
            ModelLoadError: 模型加载失败
        """
        if self.p2t is not None:
            return  # 已加载
        
        if self.load_failed:
            raise ModelLoadError(f"模型加载失败: {self.load_error_msg}")
        
        if self.is_loading:
            # 等待另一个线程完成加载
            while self.is_loading and self.p2t is None:
                time.sleep(0.1)
            if self.p2t is None:
                raise ModelLoadError(f"模型加载失败: {self.load_error_msg}")
            return
        
        self.is_loading = True
        try:
            if on_progress:
                on_progress(1, 3, "正在加载pix2text模型...")
            
            logger.info("正在加载pix2text模型...")
            self.p2t = Pix2Text.from_config()
            
            if on_progress:
                on_progress(3, 3, "模型加载完成")
            
            logger.info("pix2text模型加载成功")
        
        except Exception as e:
            self.load_failed = True
            self.load_error_msg = str(e)
            logger.error(f"pix2text模型加载失败: {e}")
            raise ModelLoadError(f"模型加载失败: {e}")
        finally:
            self.is_loading = False
    
    def recognize_image(self, image_path: str, timeout: int = 120) -> Dict[str, Any]:
        """
        识别单张图片中的公式
        
        Args:
            image_path: 图片路径
            timeout: 超时时间（秒）
            
        Returns:
            {
                'success': bool,
                'text': str,  # LaTeX格式公式
                'error': str,  # 错误信息（如果失败）
                'raw_result': Any,  # 原始结果
            }
        """
        try:
            self.ensure_loaded()
            
            # 验证图片存在
            image_path = str(image_path)
            if not Path(image_path).exists():
                return {
                    'success': False,
                    'text': '',
                    'error': f'图片文件不存在: {image_path}',
                    'raw_result': None,
                }
            
            # 打开并验证图片
            try:
                image = Image.open(image_path)
                image.verify()  # 验证图片完整性
            except Exception as e:
                return {
                    'success': False,
                    'text': '',
                    'error': f'图片格式错误: {e}',
                    'raw_result': None,
                }
            
            logger.info(f"开始识别图片: {image_path}")
            
            # 执行识别
            try:
                # pix2text 1.1.x 没有 recognize_image，公式截图应走 recognize_formula
                result = self.p2t.recognize_formula(image_path, return_text=True) # type: ignore
                
                # 提取LaTeX文本
                latex_text = self._extract_latex(result)
                
                logger.info(f"图片识别成功: {image_path}")
                
                return {
                    'success': True,
                    'text': latex_text,
                    'error': '',
                    'raw_result': result,
                }
            
            except Exception as e:
                logger.error(f"识别过程出错: {e}")
                return {
                    'success': False,
                    'text': '',
                    'error': f'识别失败: {str(e)[:100]}',
                    'raw_result': None,
                }
        
        except ModelLoadError as e:
            return {
                'success': False,
                'text': '',
                'error': str(e),
                'raw_result': None,
            }
    
    def recognize_batch(self, image_paths: list, on_progress=None) -> list:
        """
        批量识别多张图片
        
        Args:
            image_paths: 图片路径列表
            on_progress: 进度回调 (current, total, current_file)
            
        Returns:
            结果列表，每项对应 recognize_image() 的返回值
        """
        results = []
        total = len(image_paths)
        
        for idx, path in enumerate(image_paths):
            if on_progress:
                on_progress(idx + 1, total, Path(path).name)
            
            result = self.recognize_image(path)
            results.append(result)
        
        return results
    
    def _extract_latex(self, result: Any) -> str:
        """
        从pix2text识别结果中提取LaTeX字符串
        
        pix2text 返回的结果格式可能有多种，这个方法尝试兼容多种格式
        """
        if result is None:
            return ""
        
        if isinstance(result, str):
            return result
        
        if isinstance(result, dict):
            # 尝试多个可能的字段名
            for key in ['text', 'latex', 'formula', 'content']:
                if key in result:
                    return str(result[key])
            
            # 如果都没找到，返回整个dict的字符串表示
            return str(result)
        
        if isinstance(result, list):
            # 如果是列表，连接所有元素
            texts = []
            for item in result:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict) and 'text' in item:
                    texts.append(item['text'])
            return " ".join(texts)
        
        return str(result)
    
    def reset(self):
        """重置识别器，卸载模型"""
        self.p2t = None
        self.is_loading = False
        self.load_failed = False
        self.load_error_msg = ""
        logger.info("识别器已重置")


def get_recognizer() -> FormulaRecognizer:
    """获取全局识别器实例（单例）"""
    return FormulaRecognizer()
