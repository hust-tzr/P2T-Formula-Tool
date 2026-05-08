"""
Formula Recognition Application
Extracts mathematical formulas from images and converts them to Markdown format.
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('formula_recognition.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    try:
        # 创建应用
        app = QApplication(sys.argv)
        
        logger.info("=" * 50)
        logger.info("应用启动")
        logger.info("=" * 50)
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        logger.info("主窗口已显示")
        
        # 运行应用
        sys.exit(app.exec())
    
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有必要的依赖:")
        print("  pip install PyQt6 pix2text Pillow markdown2 python-docx reportlab")
        sys.exit(1)
    
    except Exception as e:
        logger.exception("应用启动失败")
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
