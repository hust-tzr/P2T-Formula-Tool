"""
Main window UI for the formula recognition application.
"""

import logging
import os
from pathlib import Path
from typing import Optional
from threading import Thread

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QScrollArea, QFileDialog, QMessageBox, QProgressBar,
    QProgressDialog, QSplitter, QComboBox, QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QMimeData, QUrl
from PyQt6.QtGui import QDropEvent, QDragEnterEvent

from core.recognizer import get_recognizer, RecognitionError
from core.formatter import MarkdownFormatter, FormulaStyle
from utils.image_handler import ImageHandler

logger = logging.getLogger(__name__)


class RecognitionSignals(QObject):
    """识别线程信号 - 用于线程间安全通信"""
    progress = pyqtSignal(int, int, str)       # (current, total, message)
    success = pyqtSignal(int, str)             # (image_index, latex_text)
    error = pyqtSignal(str, str)               # (error_msg, error_type: 'warning'|'critical')
    finished = pyqtSignal()                    # 完成信号


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("公式识别工具 v1.0")
        self.setGeometry(120, 120, 980, 650)
        
        # 初始化状态
        self.current_image: Optional[QPixmap] = None
        self.current_image_path: Optional[str] = None
        self.temp_image_path: Optional[str] = None
        self.recognizer = get_recognizer()
        self.formatter = MarkdownFormatter(FormulaStyle.WORD)
        self.is_recognizing = False
        self.last_latex_text: Optional[str] = None
        self.current_recognizing_index: Optional[int] = None

        # 多图片状态：每项包含 path/is_temp/latex/result
        self.image_items = []
        
        # 线程信号
        self.recognition_signals = RecognitionSignals()
        
        # 初始化UI
        self._init_ui()
        self._setup_styles()
        self._setup_drag_drop()
        self._setup_shortcuts()
        self._connect_signals()
        
        logger.info("主窗口初始化完成")
    
    def _init_ui(self):
        """初始化用户界面"""
        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout()
        
        # ===== 左侧：图片展示和加载区域 =====
        left_layout = QVBoxLayout()
        
        # 标签
        image_label = QLabel("图片预览区域")
        image_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(image_label)
        
        # 图片显示区域
        self.image_display = QLabel()
        self.image_display.setMinimumSize(300, 220)
        self.image_display.setMaximumHeight(260)
        self.image_display.setStyleSheet("border: 2px dashed #ccc; background-color: #f5f5f5;")
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setText("拖放图片到此 或 点击下面按钮\n支持PNG、JPG、BMP等格式")
        left_layout.addWidget(self.image_display)

        # 图片列表
        image_list_label = QLabel("图片列表（可多张，点击切换）")
        image_list_label.setFont(QFont("Arial", 9))
        left_layout.addWidget(image_list_label)

        self.image_list = QListWidget()
        self.image_list.currentRowChanged.connect(self._on_image_selected)
        self.image_list.setMaximumHeight(180)
        left_layout.addWidget(self.image_list)
        
        # 按钮行
        button_layout = QVBoxLayout()
        
        self.btn_open = QPushButton("📁 打开文件")
        self.btn_open.clicked.connect(self._on_open_file)
        button_layout.addWidget(self.btn_open)
        
        self.btn_paste = QPushButton("📋 粘贴截图")
        self.btn_paste.clicked.connect(self._on_paste_image)
        button_layout.addWidget(self.btn_paste)
        
        self.btn_clear = QPushButton("🗑️ 清除")
        self.btn_clear.clicked.connect(self._on_clear_image)
        button_layout.addWidget(self.btn_clear)
        
        left_layout.addLayout(button_layout)
        
        # ===== 右侧：识别结果和导出区域 =====
        right_layout = QVBoxLayout()
        
        # 标签
        result_label = QLabel("识别结果（Markdown格式）")
        result_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addWidget(result_label)
        
        # 结果文本框
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("识别结果将显示在这里...")
        right_layout.addWidget(self.result_text)

        # 原始识别文本（Raw LaTeX） - 供对比用
        raw_label = QLabel("原始识别（Raw LaTeX）")
        raw_label.setFont(QFont("Arial", 9))
        right_layout.addWidget(raw_label)

        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        self.raw_text.setPlaceholderText("识别得到的原始LaTeX文本将显示在这里，供对比使用...")
        self.raw_text.setMaximumHeight(120)
        right_layout.addWidget(self.raw_text)
        
        # 导出按钮行
        export_layout = QVBoxLayout()
        
        # 公式样式选择
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("公式格式:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "自动选择",
            "行内公式 $...$",
            "块级公式 $$...$$",
            "Word公式（直接粘贴到Word公式框）",
        ])
        self.style_combo.setCurrentIndex(3)
        self.style_combo.currentIndexChanged.connect(self._on_style_changed)
        style_layout.addWidget(self.style_combo)
        export_layout.addLayout(style_layout)
        
        # 导出按钮
        self.btn_recognize = QPushButton("🔍 识别公式")
        self.btn_recognize.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_recognize.clicked.connect(self._on_recognize)
        export_layout.addWidget(self.btn_recognize)
        
        self.btn_copy = QPushButton("📋 复制结果")
        self.btn_copy.clicked.connect(self._on_copy_result)
        export_layout.addWidget(self.btn_copy)
        
        self.btn_save = QPushButton("💾 保存为Markdown")
        self.btn_save.clicked.connect(self._on_save_markdown)
        export_layout.addWidget(self.btn_save)

        # MathML 输出来源选择与生成按钮
        mathml_src_layout = QHBoxLayout()
        mathml_src_layout.addWidget(QLabel("MathML 来源:"))
        self.mathml_source_combo = QComboBox()
        self.mathml_source_combo.addItems(["格式化结果", "原始识别"])
        mathml_src_layout.addWidget(self.mathml_source_combo)
        export_layout.addLayout(mathml_src_layout)

        self.btn_mathml = QPushButton("📐 生成 MathML")
        self.btn_mathml.clicked.connect(self._on_generate_mathml)
        export_layout.addWidget(self.btn_mathml)
        
        right_layout.addLayout(export_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 10px;")
        right_layout.addWidget(self.status_label)
        
        # ===== 组合左右布局 =====
        # 使用QSplitter以支持可调整大小的面板
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
    
    def _setup_styles(self):
        """设置样式表"""
        stylesheet = """
        QPushButton {
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid #ddd;
            background-color: #f0f0f0;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        QTextEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            font-family: "Courier New";
            font-size: 10px;
        }
        QLabel {
            color: #333;
        }
        """
        self.setStyleSheet(stylesheet)
    
    def _setup_drag_drop(self):
        """启用拖放功能"""
        self.setAcceptDrops(True)

    def _setup_shortcuts(self):
        """快捷键设置"""
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.paste_shortcut.activated.connect(self._on_paste_shortcut)
    
    def _connect_signals(self):
        """连接识别线程信号到主线程槽"""
        self.recognition_signals.progress.connect(self._on_recognition_progress)
        self.recognition_signals.success.connect(self._on_recognition_success)
        self.recognition_signals.error.connect(self._on_recognition_error)
        self.recognition_signals.finished.connect(self._on_recognition_finished)

    def _on_paste_shortcut(self):
        """Ctrl+V 时优先粘贴剪贴板图片"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data and mime_data.hasImage():
            self._on_paste_image()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖入时处理"""
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            # 检查是否包含图片文件
            for url in mime_data.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if Path(path).suffix.lower() in {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}:
                        event.acceptProposedAction()
                        return
    
    def dropEvent(self, event: QDropEvent):
        """放开时处理"""
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    self._load_image_path(path)
                    break
    
    def _on_open_file(self):
        """打开文件对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*)"
        )
        if file_path:
            self._load_image_path(file_path)
    
    def _on_paste_image(self):
        """从剪贴板粘贴图片"""
        self._update_status("正在从剪贴板读取图片...", True)
        
        success, image, error = ImageHandler.load_from_clipboard()
        if success:
            # 保存临时文件
            tmp_success, tmp_path, tmp_error = ImageHandler.save_temp_image(image)
            if tmp_success:
                self._add_image_item(tmp_path, image, is_temp=True)
                self._update_status(f"已从剪贴板加载图片", False)
            else:
                self._update_status(f"错误: {tmp_error}", False)
                QMessageBox.warning(self, "错误", tmp_error)
        else:
            self._update_status(f"错误: {error}", False)
            QMessageBox.warning(self, "错误", error)
    
    def _on_clear_image(self):
        """清除当前图片"""
        index = self.image_list.currentRow()
        if index < 0 or index >= len(self.image_items):
            QMessageBox.information(self, "提示", "当前没有可清除的图片")
            return

        item = self.image_items.pop(index)
        if item.get('is_temp'):
            ImageHandler.cleanup_temp_file(item.get('path'))

        self.image_list.takeItem(index)

        if self.image_items:
            self.image_list.setCurrentRow(min(index, len(self.image_items) - 1))
        else:
            self.current_image = None
            self.current_image_path = None
            self.last_latex_text = None
            self.image_display.clear()
            self.image_display.setText("拖放图片到此 或 点击下面按钮\n支持PNG、JPG、BMP等格式")
            self.result_text.clear()

        self._update_status("已清除当前图片", False)
    
    def _on_recognize(self):
        """开始识别"""
        index = self.image_list.currentRow()
        if index < 0 or index >= len(self.image_items):
            QMessageBox.warning(self, "警告", "请先加载一张图片")
            return

        image_path = self.image_items[index]['path']
        
        self.is_recognizing = True
        self.current_recognizing_index = index
        self._update_status("正在加载模型和识别公式...", True)
        self.btn_recognize.setEnabled(False)
        
        # 在独立线程中执行识别
        thread = Thread(target=self._recognize_worker, daemon=True)
        thread.start()
    
    def _recognize_worker(self):
        """识别工作线程 - 在后台线程中执行，通过信号与主线程通信"""
        try:
            # 确保模型已加载
            self.recognizer.ensure_loaded(on_progress=self._on_worker_progress)
            
            # 执行识别
            self.recognition_signals.progress.emit(2, 3, "正在识别公式...")
            index = self.current_recognizing_index
            if index is None or index < 0 or index >= len(self.image_items):
                self.recognition_signals.error.emit("当前图片索引无效", 'warning')
                return

            result = self.recognizer.recognize_image(self.image_items[index]['path'])
            
            if result['success']:
                latex_text = result['text']
                self.recognition_signals.success.emit(index, latex_text)
            else:
                error_msg = result['error']
                self.recognition_signals.error.emit(error_msg, 'warning')
        
        except RecognitionError as e:
            error_msg = str(e)
            self.recognition_signals.error.emit(error_msg, 'critical')
        
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.exception("识别过程异常")
            self.recognition_signals.error.emit(error_msg, 'critical')
        
        finally:
            self.recognition_signals.finished.emit()
    
    def _on_worker_progress(self, current, total, message):
        """后台线程的进度回调 - 在线程中调用，发出信号到主线程"""
        self.recognition_signals.progress.emit(current, total, message)
    
    def _on_recognition_progress(self, current, total, message):
        """进度槽 - 在主线程中执行"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self._update_status(message, True)
    
    def _on_recognition_success(self, image_index, latex_text):
        """识别成功槽 - 在主线程中执行"""
        self.last_latex_text = latex_text
        if 0 <= image_index < len(self.image_items):
            self.image_items[image_index]['latex'] = latex_text
            self.image_items[image_index]['result'] = self.formatter.format_formula(latex_text)
            if image_index == self.image_list.currentRow():
                self.result_text.setText(self.image_items[image_index]['result'])
                # 同步显示原始识别文本，便于比较
                self.raw_text.setText(latex_text)
        self._update_status(f"识别成功！公式: {latex_text[:50]}...", False)
    
    def _on_recognition_error(self, error_msg, error_type):
        """识别错误槽 - 在主线程中执行"""
        self.result_text.setText(f"错误: {error_msg}")
        # 出错时清空原始文本显示
        try:
            self.raw_text.clear()
        except Exception:
            pass
        self._update_status(f"错误: {error_msg}", False)
        if error_type == 'warning':
            QMessageBox.warning(self, "识别失败", error_msg)
        else:
            QMessageBox.critical(self, "识别失败", error_msg)
    
    def _on_recognition_finished(self):
        """识别完成槽 - 在主线程中执行"""
        self.is_recognizing = False
        self.current_recognizing_index = None
        self.btn_recognize.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def _on_style_changed(self, index):
        """公式样式改变"""
        style_map = {
            0: FormulaStyle.AUTO,
            1: FormulaStyle.INLINE,
            2: FormulaStyle.BLOCK,
            3: FormulaStyle.WORD,
        }
        self.formatter = MarkdownFormatter(style_map[index])

        selected = self.image_list.currentRow()
        if 0 <= selected < len(self.image_items):
            latex_text = self.image_items[selected].get('latex')
            if latex_text:
                rendered = self.formatter.format_formula(latex_text)
                self.image_items[selected]['result'] = rendered
                self.result_text.setText(rendered)
                # 保持原始识别文本显示
                self.raw_text.setText(latex_text)
        # 更新 MathML 来源选择（保持当前选择，不自动改变）
    
    def _on_copy_result(self):
        """复制结果到剪贴板"""
        selected = self.image_list.currentRow()
        if 0 <= selected < len(self.image_items) and self.image_items[selected].get('latex'):
            text = MarkdownFormatter(FormulaStyle.WORD).format_formula(self.image_items[selected]['latex'])
        else:
            text = self.result_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "没有结果可复制")
            return
        
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self._update_status("已复制到剪贴板", False)

    def _on_generate_mathml(self):
        """生成 MathML 并展示/复制/保存"""
        selected = self.image_list.currentRow()
        # 选择来源：0-格式化结果，1-原始识别
        src_index = self.mathml_source_combo.currentIndex()

        if src_index == 0:
            # 格式化结果可能包含 $/$$(strip)
            if 0 <= selected < len(self.image_items):
                latex = self.image_items[selected].get('result') or ''
            else:
                latex = ''
            # 去除行内或块级包裹
            if latex.startswith('$$') and latex.endswith('$$'):
                latex_in = latex[2:-2].strip()
            elif latex.startswith('$') and latex.endswith('$'):
                latex_in = latex[1:-1].strip()
            else:
                latex_in = latex
        else:
            latex_in = self.raw_text.toPlainText()

        if not latex_in.strip():
            QMessageBox.warning(self, "提示", "没有可用的 LaTeX 文本用于生成 MathML")
            return

        try:
            from latex2mathml.converter import convert
        except Exception:
            QMessageBox.information(self, "缺少依赖", "生成 MathML 需要安装 `latex2mathml` 包。\n请在终端运行:\n\npip install latex2mathml")
            return

        try:
            mathml = convert(latex_in)
        except Exception as e:
            QMessageBox.critical(self, "转换失败", f"LaTeX 转 MathML 失败: {e}")
            return

        self._show_mathml_dialog(mathml)

    def _show_mathml_dialog(self, mathml: str):
        """弹窗显示生成的 MathML，支持复制与保存"""
        dlg = QDialog(self)
        dlg.setWindowTitle("生成的 MathML")
        dlg_layout = QVBoxLayout()

        te = QTextEdit()
        te.setReadOnly(True)
        te.setPlainText(mathml)
        dlg_layout.addWidget(te)

        btn_layout = QHBoxLayout()
        copy_btn = QPushButton("复制到剪贴板")
        def on_copy():
            QApplication.clipboard().setText(mathml)
            QMessageBox.information(self, "已复制", "MathML 已复制到剪贴板")
        copy_btn.clicked.connect(on_copy)
        btn_layout.addWidget(copy_btn)

        save_btn = QPushButton("保存为文件")
        def on_save():
            file_path, _ = QFileDialog.getSaveFileName(self, "保存 MathML", "", "XML 文件 (*.xml);;所有文件 (*)")
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(mathml)
                    QMessageBox.information(self, "已保存", f"已保存到: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "保存失败", str(e))
        save_btn.clicked.connect(on_save)
        btn_layout.addWidget(save_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(close_btn)

        dlg_layout.addLayout(btn_layout)
        dlg.setLayout(dlg_layout)
        dlg.resize(700, 400)
        dlg.exec()
    
    def _on_save_markdown(self):
        """保存为Markdown文件"""
        text = self.result_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "警告", "没有内容可保存")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存为Markdown",
            "",
            "Markdown文件 (*.md);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self._update_status(f"已保存: {file_path}", False)
                QMessageBox.information(self, "成功", f"文件已保存到:\n{file_path}")
            except Exception as e:
                error_msg = f"保存失败: {str(e)}"
                self._update_status(error_msg, False)
                QMessageBox.critical(self, "保存失败", error_msg)
    
    def _load_image_path(self, image_path: str):
        """加载本地图片文件"""
        success, image, error = ImageHandler.load_from_file(image_path)
        if success:
            self._add_image_item(image_path, image, is_temp=False)
            self._update_status(f"已加载: {Path(image_path).name}", False)
        else:
            self._update_status(f"错误: {error}", False)
            QMessageBox.warning(self, "加载失败", error)

    def _add_image_item(self, image_path: str, image, is_temp: bool):
        """添加图片到列表并选中"""
        display_name = Path(image_path).name
        item_data = {
            'path': image_path,
            'is_temp': is_temp,
            'latex': None,
            'result': '',
            'image': image,
        }
        self.image_items.append(item_data)
        self.image_list.addItem(QListWidgetItem(display_name))
        self.image_list.setCurrentRow(len(self.image_items) - 1)

    def _on_image_selected(self, index: int):
        """选择不同图片时更新预览和结果"""
        if index < 0 or index >= len(self.image_items):
            return

        item = self.image_items[index]
        self.current_image_path = item['path']
        self.last_latex_text = item.get('latex')
        self._display_image(item['image'])
        self.result_text.setText(item.get('result', ''))
        # 显示原始识别文本
        self.raw_text.setText(item.get('latex') or '')
    
    def _display_image(self, image):
        """在上窗口中显示图片"""
        self.current_image = image
        
        # 缩放用于显示
        display_image = image.copy()
        display_image.thumbnail((300, 240))
        
        # 转换为QPixmap
        qpixmap = ImageHandler.convert_to_qpixmap(display_image)
        if qpixmap:
            self.image_display.setPixmap(qpixmap)
        
        # 结果区由 _on_image_selected / _on_recognition_success 负责设置
    
    def _update_status(self, message: str, is_busy: bool = False):
        """更新状态标签"""
        prefix = "⏳ " if is_busy else "✓ "
        self.status_label.setText(f"{prefix}{message}")
    
    def closeEvent(self, event):
        """窗口关闭时处理"""
        # 清理所有临时文件
        for item in self.image_items:
            if item.get('is_temp'):
                ImageHandler.cleanup_temp_file(item.get('path'))
        event.accept()
