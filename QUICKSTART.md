# ⚡ 快速开始指南

适合想快速上手的用户。详细安装说明请参考 [INSTALL_GUIDE.md](INSTALL_GUIDE.md)。

---

## 🎯 一分钟快速开始

### 前置条件
- 已安装 Anaconda / Miniconda（Python 3.10+）
- 已下载/克隆本项目代码

### 快速安装

**Windows 用户（PowerShell）：**
```bash
# 1. 创建虚拟环境
conda create -n p2t python=3.10 -y
conda activate p2t

# 2. 进入项目目录
cd path\to\pix2text

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
python app.py
```

**Mac / Linux 用户：**
```bash
# 1. 创建虚拟环境
conda create -n p2t python=3.10 -y
conda activate p2t

# 2. 进入项目目录
cd path/to/pix2text

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
python app.py
```

---

## 📖 基本使用

1. **加载图片**
   - 点击"📁 打开文件"选择图片，或
   - 点击"📋 粘贴截图"，或
   - 直接拖放图片到预览区

2. **识别公式**
   - 点击"🔍 识别公式"按钮
   - 首次运行会加载模型，需要等待 30-60 秒

3. **复制或保存**
   - 点击"📋 复制结果"复制到剪贴板，或
   - 点击"💾 保存为Markdown"保存到文件

4. **生成 MathML**
   - 点击"📐 生成 MathML"将公式转为 MathML 代码
   - 选择"格式化结果"或"原始识别"作为转换源

---

## 🐛 常见问题

**Q: 应用启动很慢？**
A: 首次启动时需要下载模型文件 (~500MB)，耐心等待。后续启动会很快。

**Q: 粘贴截图不工作？**
A: 确保你的图片已复制到剪贴板（通常用 Win+Shift+S 截图后自动复制）。

**Q: 识别结果不准确？**
A: 识别准确度取决于输入图片质量。使用清晰的黑白公式图片效果最好。

**更多问题？** → 查看 [INSTALL_GUIDE.md 的故障排除部分](INSTALL_GUIDE.md#-常见问题排查)

---

## 📁 项目目录

```
pix2text/
├── app.py                 # 主程序
├── run.bat               # Windows 启动脚本（双击运行）
├── requirements.txt      # 依赖列表
├── README.md            # 项目说明
├── INSTALL_GUIDE.md     # 详细安装指南
├── QUICKSTART.md        # 本文件
│
├── core/                # 核心模块
│   ├── recognizer.py    # 识别引擎封装
│   └── formatter.py     # LaTeX 格式转换
│
├── ui/                  # 用户界面
│   └── main_window.py   # 主窗口
│
└── utils/               # 工具
    └── image_handler.py # 图像处理
```

---

## 🚀 后续步骤

完成以上步骤后，你可以：

1. **定制应用**
   - 修改 `core/formatter.py` 调整输出格式
   - 修改 `ui/main_window.py` 定制界面

2. **贡献代码**
   - Fork 项目
   - 修改代码
   - 提交 Pull Request

3. **打包分发**
   - 使用 PyInstaller 打包为 EXE
   - 创建安装程序分发给他人

---

## 📚 更多资源

- [详细安装指南](INSTALL_GUIDE.md)
- [项目 README](README.md)
- [pix2text 官方项目](https://github.com/breezedeus/pix2text)
- [PyQt6 文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

---

**遇到问题？** 查看 [INSTALL_GUIDE.md](INSTALL_GUIDE.md) 获得帮助，或在 GitHub Issues 中提问。

**版本**：1.0 | **最后更新**：2026-05-08
