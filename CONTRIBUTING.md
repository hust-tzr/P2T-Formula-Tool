# 📝 贡献指南

感谢你对本项目的关注！本指南说明如何为项目做贡献。

---

## 🤝 贡献方式

### 1. 报告 Bug（问题）

如果你发现应用有 Bug，请：

1. 检查 [Issues](../../issues) 中是否已有相同报告
2. 如没有，请创建新 Issue，包含以下信息：
   - **标题**：简洁描述问题（例如："粘贴截图时应用崩溃"）
   - **描述**：详细说明问题发生的步骤
   - **预期**：应该发生什么
   - **实际**：实际发生了什么
   - **环境**：操作系统、Python 版本、pix2text 版本等
   - **日志**：附上 `formula_recognition.log` 中的相关错误信息

### 2. 提出建议（Feature Request）

如果你有改进建议：

1. 创建新 Issue，标题以 `[Feature]` 开头
2. 清晰描述：
   - 功能是什么
   - 为什么需要这个功能
   - 大致的实现思路（可选）

### 3. 改进代码（Pull Request）

我们欢迎代码贡献！按以下步骤进行：

#### 步骤 1：Fork 项目

在 GitHub 上点击 "Fork" 按钮，创建项目的个人副本。

#### 步骤 2：克隆你的 Fork

```bash
git clone https://github.com/your-username/pix2text.git
cd pix2text
```

#### 步骤 3：创建特性分支

```bash
# 确保在 main/master 分支
git checkout main

# 创建新分支（分支名应清晰描述改动内容）
git checkout -b fix/bug-in-recognizer
# 或
git checkout -b feature/add-batch-recognition
```

#### 步骤 4：进行改动

编辑代码进行修改。建议：

- 遵循现有代码风格
- 添加注释说明复杂逻辑
- 对新功能添加基本的异常处理

#### 步骤 5：测试你的改动

```bash
# 激活虚拟环境
conda activate p2t

# 运行应用，手动测试功能
python app.py

# 或运行自动化测试（如有）
pytest tests/
```

#### 步骤 6：提交改动

```bash
# 查看改动的文件
git status

# 将改动添加到暂存区
git add .

# 提交改动（清晰的提交信息）
git commit -m "Fix: 修复识别失败时的崩溃问题

- 添加了异常捕获
- 改进了错误提示信息
- 添加了日志记录

Fixes #123"
```

**提交信息规范**：
- 使用英文或中文，保持一致
- 第一行：简洁总结（50字以内）
- 空行
- 第二部分：详细说明（可选）
- 如果解决了某个 Issue，在末尾添加 `Fixes #issue-number`

#### 步骤 7：推送到你的 Fork

```bash
git push origin fix/bug-in-recognizer
```

#### 步骤 8：创建 Pull Request

1. 在 GitHub 上访问你的 Fork
2. 点击 "Pull Request" 按钮
3. 确保基准分支是原项目的 `main`，头部分支是你的特性分支
4. 填写 PR 信息：
   - **标题**：清晰描述改动（例如："修复：粘贴截图时的内存泄漏"）
   - **描述**：
     - 改动的目的
     - 改动了什么
     - 如何测试这些改动
     - 相关的 Issue 号码（如有）
5. 点击 "Create Pull Request"

---

## 📋 代码规范

为了保持代码一致性，请遵循以下规范：

### Python 代码规范

1. **遵循 PEP 8**
   ```bash
   # 检查代码风格
   pip install flake8
   flake8 core/ ui/ utils/
   ```

2. **使用类型提示**
   ```python
   def recognize_image(self, image_path: str, timeout: int = 120) -> Dict[str, Any]:
       """识别单张图片中的公式"""
       ...
   ```

3. **添加文档字符串**
   ```python
   def format_formula(self, latex: str) -> str:
       """
       将LaTeX公式转换为Markdown格式
       
       Args:
           latex: LaTeX 公式字符串
           
       Returns:
           Markdown 格式的公式
       """
       ...
   ```

4. **命名规范**
   - 模块/文件：`lowercase_with_underscores`
   - 类名：`PascalCase`
   - 函数/方法：`lowercase_with_underscores`
   - 常量：`UPPERCASE_WITH_UNDERSCORES`

### UI 代码规范

1. **控件命名**
   ```python
   # 按类型前缀命名
   self.btn_recognize = QPushButton(...)    # 按钮
   self.txt_input = QTextEdit(...)          # 文本框
   self.lbl_status = QLabel(...)            # 标签
   self.combo_style = QComboBox(...)        # 下拉框
   ```

2. **信号和槽**
   ```python
   # 槽函数以 _on_ 前缀命名
   def _on_recognize(self):
       """识别公式"""
       ...
   ```

### 注释规范

```python
# 单行注释
result = self.recognizer.recognize_image(path)  # 执行识别

# 多行注释或重要说明
"""
这个算法使用正则表达式清理 OCR 结果中的噪声。
支持以下操作：
1. 移除空格
2. 压缩花括号
3. 修复下标/上标
"""
```

---

## 🏗️ 项目架构

### 核心模块（core/）

| 文件 | 职责 |
|-----|------|
| `recognizer.py` | pix2text 识别引擎的封装，单例模式 |
| `formatter.py` | LaTeX 格式转换，支持多种输出格式 |

### UI 模块（ui/）

| 文件 | 职责 |
|-----|------|
| `main_window.py` | 主窗口，包含所有 UI 控件和事件处理 |

### 工具模块（utils/）

| 文件 | 职责 |
|-----|------|
| `image_handler.py` | 图片加载、格式转换、剪贴板操作 |

### 入口

| 文件 | 职责 |
|-----|------|
| `app.py` | 应用主程序入口 |

---

## 🧪 测试

目前项目缺少自动化测试。如果你想添加测试：

### 创建测试文件

```bash
# 创建 tests 目录
mkdir tests
touch tests/__init__.py
touch tests/test_formatter.py
touch tests/test_recognizer.py
```

### 编写测试

```python
# tests/test_formatter.py
import pytest
from core.formatter import MarkdownFormatter, FormulaStyle

def test_word_format_with_aligned():
    """测试 aligned 环境的 Word 格式化"""
    formatter = MarkdownFormatter(FormulaStyle.WORD)
    latex = r"\begin{aligned}x&=1\\&=2\end{aligned}"
    result = formatter.format_formula(latex)
    assert r"\begin{aligned}" in result
    assert r"\end{aligned}" in result
```

### 运行测试

```bash
pip install pytest
pytest tests/
```

---

## 📦 发布新版本（维护者）

1. 更新版本号：
   - `README.md` 中的版本号
   - `app.py` 中的版本号

2. 更新 `CHANGELOG.md`（如有）

3. 创建 Git 标签：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

---

## 💬 交流方式

- **Issue**：报告 Bug 或提出建议
- **Pull Request**：提交代码改动
- **Discussions**（如启用）：自由讨论

---

## ✅ 检查清单

提交 PR 前，请确保：

- [ ] 代码遵循 PEP 8 规范
- [ ] 添加了必要的注释和文档字符串
- [ ] 在本地测试过改动
- [ ] 所有改动都与 Issue 或特性相关
- [ ] 提交信息清晰且详细
- [ ] 没有提交无关的文件（如 `__pycache__/`、`.pyc` 等）

---

## 📚 参考资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub Flow 指南](https://guides.github.com/introduction/flow/)
- [PEP 8 Python 代码规范](https://www.python.org/dev/peps/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 🙏 致谢

感谢所有为项目做出贡献的人！

---

**最后更新**：2026-05-08
