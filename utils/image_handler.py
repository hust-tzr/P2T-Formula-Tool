"""
Image handling and input module.
Supports loading from file, clipboard, and drag-drop operations.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io
import tempfile
import os

logger = logging.getLogger(__name__)

# 支持的图片格式
SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.tiff'}


class ImageHandler:
    """图片处理工具"""
    
    @staticmethod
    def load_from_file(file_path: str) -> Tuple[bool, Optional[Image.Image], Optional[str]]:
        """
        从文件加载图片
        
        Args:
            file_path: 文件路径
            
        Returns:
            (成功, 图片对象, 错误信息)
        """
        try:
            file_path = str(file_path)
            
            # 检查文件是否存在
            if not Path(file_path).exists():
                return False, None, f"文件不存在: {file_path}"
            
            # 检查文件格式
            suffix = Path(file_path).suffix.lower()
            if suffix not in SUPPORTED_FORMATS:
                return False, None, f"不支持的图片格式: {suffix}"
            
            # 打开图片
            image = Image.open(file_path)
            
            # 验证图片完整性
            image.verify()
            
            # 重新打开（verify()会关闭文件）
            image = Image.open(file_path)
            
            # 转换为RGB（确保兼容性）
            if image.mode not in ['RGB', 'RGBA']:
                image = image.convert('RGB')
            
            logger.info(f"图片加载成功: {file_path}")
            return True, image, None
        
        except Exception as e:
            error_msg = f"加载图片失败: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @staticmethod
    def load_from_clipboard() -> Tuple[bool, Optional[Image.Image], Optional[str]]:
        """
        从系统剪贴板读取图片
        
        Returns:
            (成功, 图片对象, 错误信息)
        """
        try:
            from PIL import ImageGrab
            
            # 尝试从剪贴板获取图片
            image = ImageGrab.grabclipboard()
            
            if image is None:
                return False, None, "剪贴板中没有图片"
            
            # 转换为RGB
            if image.mode not in ['RGB', 'RGBA']:
                image = image.convert('RGB')
            
            logger.info("从剪贴板加载图片成功")
            return True, image, None
        
        except ImportError:
            return False, None, "ImageGrab不可用（需要Windows系统或PIL的完整安装）"
        except Exception as e:
            error_msg = f"从剪贴板读取失败: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @staticmethod
    def save_temp_image(image: Image.Image) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        将PIL图片临时保存到磁盘
        
        这在从剪贴板或内存获得图片后用处理，因为识别器需要文件路径
        
        Returns:
            (成功, 临时文件路径, 错误信息)
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            # 保存image到临时文件
            image.save(tmp_path, 'PNG')
            
            logger.info(f"临时图片保存: {tmp_path}")
            return True, tmp_path, None
        
        except Exception as e:
            error_msg = f"保存临时图片失败: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @staticmethod
    def cleanup_temp_file(file_path: str):
        """清理临时文件"""
        try:
            if file_path and Path(file_path).exists():
                os.remove(file_path)
                logger.debug(f"删除临时文件: {file_path}")
        except Exception as e:
            logger.warning(f"删除临时文件失败: {e}")
    
    @staticmethod
    def get_image_info(image: Image.Image) -> dict:
        """获取图片信息"""
        return {
            'size': image.size,  # (width, height)
            'format': image.format,
            'mode': image.mode,
            'width': image.width,
            'height': image.height,
        }
    
    @staticmethod
    def resize_for_display(image: Image.Image, max_width: int = 400, max_height: int = 500) -> Image.Image:
        """
        缩放图片以适应显示区域
        
        Args:
            image: 原始图片
            max_width: 最大宽度
            max_height: 最大高度
            
        Returns:
            缩放后的图片
        """
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def convert_to_qpixmap(image: Image.Image):
        """
        将PIL Image转换为PyQt6 QPixmap
        
        Args:
            image: PIL Image对象
            
        Returns:
            QPixmap对象
        """
        try:
            from PyQt6.QtGui import QPixmap, QImage
            from PyQt6.QtCore import Qt
            
            # PIL Image转QImage
            if image.mode == 'RGBA':
                data = image.tobytes("raw", "RGBA")
                qimage = QImage(data, image.width, image.height, QImage.Format.Format_RGBA8888)
            else:
                # RGB
                rgb_image = image.convert('RGB')
                data = rgb_image.tobytes("raw", "RGB")
                qimage = QImage(data, rgb_image.width, rgb_image.height, QImage.Format.Format_RGB888)
            
            return QPixmap.fromImage(qimage)
        
        except ImportError:
            logger.error("PyQt6未安装")
            return None
