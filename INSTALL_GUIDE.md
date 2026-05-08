# 环境配置和安装指南

## 概述

本指南详细说明如何配置 Python 环境、安装项目依赖，以及在本地运行 **公式识别工具**。

---

## 📋 系统要求

### 最低配置
- **操作系统**：Windows 7+ / macOS 10.14+ / Linux (Ubuntu 18.04+)
- **Python 版本**：3.10 或更高 (建议 3.10.x)
- **内存**：4GB RAM (建议 8GB 及以上)
- **磁盘空间**：2-3GB (用于模型文件缓存)
- **网络**：首次启动需要下载深度学习模型 (~500MB)

### 推荐配置
- Windows 10/11 或 Ubuntu 20.04 LTS 及以上
- Python 3.10.x
- 8GB+ RAM
- SSD 硬盘

---

## 🔧 安装步骤

### 第1步：安装 Anaconda 或 Miniconda

#### Windows 用户

1. 访问 [Anaconda 官网](https://www.anaconda.com/download) 或 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. 下载 **Python 3.10 版本**的安装程序（建议下载 Miniconda，更轻量）
3. 双击安装程序，按提示完成安装
4. **重要**：勾选 "Add Anaconda to PATH" (在 Windows 用户中添加到系统 PATH)
5. 安装完成后，重启计算机

**验证安装**：
```bash
# 打开 PowerShell 或 CMD，运行：
conda --version
python --version
```

#### macOS 用户

```bash
# 使用 Homebrew 安装 Miniconda
brew install miniconda

# 初始化 conda
conda init zsh  # 如果使用 zsh shell
conda init bash # 如果使用 bash shell

# 重启终端使配置生效
```

#### Linux 用户 (Ubuntu/Debian)

```bash
# 下载安装脚本
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 运行安装脚本
bash Miniconda3-latest-Linux-x86_64.sh

# 按提示完成安装，选择默认路径即可

# 初始化 conda
conda init

# 重启终端
```

---

### 第2步：创建 Python 虚拟环境

#### Windows 用户（使用 PowerShell 或 CMD）

```bash
# 打开 PowerShell / CMD，运行：

# 创建名为 p2t 的虚拟环境，Python 版本为 3.10
conda create -n p2t python=3.10 -y

# 激活虚拟环境
conda activate p2t

# 验证 Python 版本
python --version
```

#### macOS / Linux 用户

```bash
# 创建虚拟环境
conda create -n p2t python=3.10 -y

# 激活虚拟环境
conda activate p2t

# 验证 Python 版本
python --version
```

---

### 第3步：下载项目代码

#### 使用 Git 克隆（推荐）

```bash
# 确保已安装 Git，或从 https://git-scm.com 下载安装

# 克隆项目
git clone https://github.com/your-username/pix2text.git

# 进入项目目录
cd pix2text
```

#### 或手动下载

1. 在 GitHub 上点击 "Code" → "Download ZIP"
2. 解压到本地目录
3. 打开终端，进入解压后的项目目录

---

### 第4步：安装项目依赖

进入项目目录后，激活虚拟环境并安装依赖：

```bash
# 确保已激活 p2t 环境
conda activate p2t

# 进入项目目录（如未进入）
cd path/to/pix2text

# 使用 pip 安装依赖（推荐方式）
pip install -r requirements.txt

# 或手动安装各个包
pip install PyQt6==6.11.0
pip install pix2text==1.1.6
pip install Pillow==12.2.0
pip install markdown2==2.4.9
pip install python-docx==0.8.11
pip install reportlab==4.0.9
pip install latex2mathml==3.81.0
```

**国内用户加速**（可选）：如果 pip 下载速度慢，可以使用清华大学镜像：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

---

### 第5步：验证安装

运行以下命令验证所有依赖都已正确安装：

```bash
# 激活环境
conda activate p2t

# 进入项目目录
cd path/to/pix2text

# 运行验证脚本
python -c "
import sys
print('Python 版本:', sys.version)
try:
    import PyQt6; print('✓ PyQt6 已安装')
except: print('✗ PyQt6 未安装')
try:
    import pix2text; print('✓ pix2text 已安装')
except: print('✗ pix2text 未安装')
try:
    import PIL; print('✓ Pillow 已安装')
except: print('✗ Pillow 未安装')
try:
    import latex2mathml; print('✓ latex2mathml 已安装')
except: print('✗ latex2mathml 未安装')
print('所有依赖检查完毕！')
"
```

如果所有项都显示 ✓，说明环境配置成功。

---

## 🚀 运行应用

### 方式1：使用启动脚本（Windows 推荐）

```bash
# 项目目录下，双击 run.bat 文件
# 或在 PowerShell 中运行：
.\run.bat
```

### 方式2：使用命令行

```bash
# 激活虚拟环境
conda activate p2t

# 进入项目目录
cd path/to/pix2text

# 运行应用
python app.py
```

### 方式3：使用 VS Code 运行

1. 打开 VS Code
2. 打开项目文件夹（File → Open Folder）
3. 在 Python 扩展中选择解释器为 `p2t` 环境
4. 打开 `app.py` 文件
5. 点击右上角的 "运行" 按钮，或按 `Ctrl+F5`

---

## 📦 依赖说明

项目使用以下主要依赖库：

| 包名 | 版本 | 用途 |
|-----|------|------|
| **PyQt6** | 6.11.0+ | GUI 框架 - 用户界面 |
| **pix2text** | 1.1.6+ | 公式识别 - 基于深度学习的 OCR 引擎 |
| **Pillow** | 12.2.0+ | 图像处理 - 加载和处理图片 |
| **markdown2** | 2.4.9+ | Markdown 生成 - 转换为 Markdown 格式 |
| **python-docx** | 0.8.11+ | Word 文档处理 - 导出到 Word (未来功能) |
| **reportlab** | 4.0.9+ | PDF 生成 - 导出到 PDF (未来功能) |
| **latex2mathml** | 3.81.0+ | 公式转换 - 将 LaTeX 转为 MathML |

### 依赖关系图

```
公式识别工具
├── PyQt6         (GUI)
├── pix2text      (核心识别)
│   └── torch, numpy, opencv 等深度学习库
├── Pillow        (图像处理)
├── latex2mathml  (公式转换)
├── markdown2     (输出格式)
├── python-docx   (Word 导出)
└── reportlab     (PDF 导出)
```

---

## 🔄 更新或重新安装依赖

### 升级所有依赖到最新版本

```bash
conda activate p2t
pip install --upgrade -r requirements.txt
```

### 清理并重新安装

```bash
# 激活环境
conda activate p2t

# 卸载所有依赖
pip uninstall -r requirements.txt -y

# 重新安装
pip install -r requirements.txt
```

### 删除虚拟环境（如需要重新开始）

```bash
# 先停用环境
conda deactivate

# 删除环境
conda env remove -n p2t
```

---

## 🐛 常见问题排查

### Q1：激活虚拟环境时出现 "无法加载文件" 错误

**Windows PowerShell 错误**：
```
PowerShell 因为在此系统上禁用了脚本的执行... activate.ps1 无法加载
```

**解决方案**：
```bash
# 打开 PowerShell（以管理员身份），运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后再运行激活命令
conda activate p2t
```

---

### Q2：pip 安装包时超时或很慢

**原因**：网络连接问题或默认镜像源速度慢

**解决方案**：
```bash
# 方式1：使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package-name

# 方式2：永久配置（创建或修改 ~/.pip/pip.conf）
# Windows: %APPDATA%\pip\pip.ini
# Linux/Mac: ~/.pip/pip.conf

[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```

---

### Q3：启动应用时出现 "ModuleNotFoundError"

**原因**：未正确激活虚拟环境，或依赖未安装

**解决方案**：
```bash
# 1. 确保激活了正确的环境
conda activate p2t

# 2. 检查缺失的模块
pip list | grep package-name

# 3. 重新安装缺失的依赖
pip install --upgrade package-name
```

---

### Q4：首次运行时应用卡顿或长时间加载

**原因**：pix2text 模型需要从网络下载 (~500MB)，第一次启动需要 30-120 秒

**解决方案**：
- 耐心等待，不要关闭应用
- 确保网络连接稳定
- 查看日志文件 `formula_recognition.log` 了解加载进度
- 后续启动会快得多（模型已缓存到本地）

**手动预下载模型**（可选）：
```bash
python -c "from pix2text import Pix2Text; Pix2Text.from_config()"
```

---

### Q5：粘贴截图功能在 Linux/Mac 上不工作

**原因**：Pillow 在 Linux/Mac 上需要额外配置

**解决方案（Linux - Ubuntu/Debian）**：
```bash
# 安装系统依赖
sudo apt-get install libxcb-xfixes0-dev libxcb-shape0-dev

# 重新安装 Pillow
pip install --upgrade --force-reinstall Pillow
```

**解决方案（macOS）**：
```bash
# 使用 Homebrew 安装依赖
brew install libxcb

# 重新安装 Pillow
pip install --upgrade --force-reinstall Pillow
```

---

### Q6：VSCode 中 Python 扩展报错或找不到环境

**解决方案**：
1. 打开命令面板（Ctrl+Shift+P）
2. 输入 "Python: Select Interpreter"
3. 选择 `./p2t/bin/python` (Linux/Mac) 或 `.\p2t\Scripts\python.exe` (Windows)
4. 重启 VSCode

---

### Q7：生成 MathML 时出现错误

**原因**：`latex2mathml` 不支持某些 LaTeX 命令或环境

**解决方案**：
- 使用"原始识别"而不是"格式化结果"作为转换源
- 某些复杂的 LaTeX 命令可能不被支持，手动简化公式或查看 [latex2mathml 文档](https://github.com/roniemartinez/latex2mathml)

---

## 💡 性能优化建议

### 1. 使用 SSD 硬盘

如果项目在 HDD（机械硬盘）上运行，首次模型加载会比较慢。建议将项目和模型缓存移到 SSD。

### 2. 增加可用内存

关闭不必要的后台程序，为应用腾出至少 2GB 内存。

### 3. GPU 加速（可选）

如果拥有 NVIDIA GPU，可以安装 CUDA 版本的 PyTorch 以加速识别：

```bash
conda activate p2t

# 安装 CUDA 支持（需要有 NVIDIA GPU）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 🔗 有用的资源

- **Python 官方文档**：https://docs.python.org/3.10/
- **Conda 使用指南**：https://docs.conda.io/projects/conda/en/latest/
- **PyQt6 文档**：https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **pix2text 项目**：https://github.com/breezedeus/pix2text
- **LaTeX 在线编辑器**：https://www.overleaf.com/

---

## 📝 开发环境设置（可选）

如果想为项目做开发贡献，建议额外安装以下工具：

```bash
conda activate p2t

# 代码检查工具
pip install pylint flake8 black

# 测试框架
pip install pytest

# 调试工具
pip install ipython ipdb
```

---

## ✅ 环境配置检查清单

完成以下步骤后，项目应该可以正常运行：

- [ ] 安装了 Anaconda 或 Miniconda
- [ ] 创建了名为 `p2t` 的虚拟环境（Python 3.10）
- [ ] 下载了项目代码
- [ ] 安装了 `requirements.txt` 中的所有依赖
- [ ] 运行验证脚本确认所有依赖已安装
- [ ] 成功启动应用（可能需要等待模型下载）
- [ ] 能够加载图片并识别公式

---

## 🆘 获取帮助

如果遇到问题：

1. 查看本指南的"常见问题排查"部分
2. 检查 `formula_recognition.log` 日志文件
3. 在 GitHub Issues 中搜索相似问题
4. 提交新的 Issue 并附上错误信息和日志内容

---

## 📄 许可证

详见项目根目录的 `LICENSE` 文件。

---

**最后更新**：2026-05-08  
**文档版本**：1.0
