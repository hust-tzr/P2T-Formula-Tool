"""
LaTeX to Markdown formatter module.
Converts LaTeX formulas to Markdown format with configurable inline/block style.
"""

import re
from enum import Enum
from typing import Tuple


class FormulaStyle(Enum):
    """公式输出样式"""
    INLINE = "inline"           # $...$
    BLOCK = "block"             # $$...$$
    AUTO = "auto"               # 自动选择（复杂的用块级）
    WORD = "word"               # Word 公式（不包裹 $, 直接粘贴到Word公式框）


class MarkdownFormatter:
    """
    将LaTeX公式转换为Markdown格式
    """
    
    def __init__(self, style: FormulaStyle = FormulaStyle.AUTO):
        self.style = style
    
    def format_formula(self, latex: str) -> str:
        """
        将LaTeX公式转换为Markdown格式
        
        Args:
            latex: LaTeX 公式字符串（可能包含 $ 或 $$ 分隔符）
            
        Returns:
            Markdown 格式的公式
        """
        if not latex:
            return ""
        
        # 移除外层的 $ 或 $$
        formula = self._clean_formula(latex)
        
        if self.style == FormulaStyle.INLINE:
            return f"${formula}$"
        elif self.style == FormulaStyle.BLOCK:
            return f"$${formula}$$"
        elif self.style == FormulaStyle.WORD:
            return self._word_format(formula)
        else:  # AUTO
            return self._auto_format(formula)
    
    def _clean_formula(self, latex: str) -> str:
        """删除LaTeX公式周围的 $ 和 $$ 分隔符"""
        latex = latex.strip()
        
        # 移除外层 $$...$$
        if latex.startswith("$$") and latex.endswith("$$"):
            latex = latex[2:-2].strip()
        # 移除外层 $...$
        elif latex.startswith("$") and latex.endswith("$"):
            latex = latex[1:-1].strip()
        
        return latex
    
    def _auto_format(self, formula: str) -> str:
        """
        自动选择行内或块级格式
        
        逻辑：
        - 如果包含 \\\\（换行符）或展开的运算符 \\sum \\int 等，使用块级
        - 否则使用行内
        """
        # 判断是否复杂（包含换行或大型运算符）
        complex_patterns = [
            r'\\\\',           # 换行符
            r'\\sum',          # 求和
            r'\\prod',         # 求积
            r'\\int',          # 积分
            r'\\lim',          # 极限
            r'\\frac',         # 分数
            r'\\begin{',       # 环境开始
        ]
        
        is_complex = any(re.search(p, formula) for p in complex_patterns)
        
        if is_complex:
            return f"$${formula}$$"
        else:
            return f"${formula}$"

    def _word_format(self, formula: str) -> str:
        """
        转为适合 Word 公式输入框的 LaTeX 文本。

        说明：
        - 不添加 $/$$ 包裹
        - 清理 OCR 引入的空格与 {} 噪声
        - 尽量输出紧凑形式（接近 Word 最易识别的写法）
        """
        s = " ".join(formula.split())

        # 去掉常见噪声块
        s = s.replace("{}", "")
        s = s.replace("{ }", "")

        # 命令与大括号之间不要有空格: \frac {a}{b} -> \frac{a}{b}
        s = re.sub(r"(\\[A-Za-z]+)\s+\{", r"\1{", s)

        # 变量/右括号 后接命令时去空格: x \ddot{y} -> x\ddot{y}
        s = re.sub(r"([A-Za-z0-9}\]])\s+(\\[A-Za-z]+)", r"\1\2", s)

        # 紧凑括号和上下标: v _ {a r e a} -> v_{area}
        s = re.sub(r"\s*([_^{}()])\s*", r"\1", s)

        # 操作符两侧去空格（aligned中常见）
        s = re.sub(r"\s*([=+\-*/&])\s*", r"\1", s)

        # 仅由字母/数字/空格组成的大括号内容，移除内部空格: {a r e a}->{area}, {d t}->{dt}
        def _compact_brace(match):
            content = match.group(1)
            if re.fullmatch(r"[A-Za-z0-9 ]+", content):
                return "{" + content.replace(" ", "") + "}"
            return "{" + content + "}"

        for _ in range(4):
            new_s = re.sub(r"\{([^{}]*)\}", _compact_brace, s)
            if new_s == s:
                break
            s = new_s

        # aligned 环境做额外清洗：把 {expr}&{expr} 噪声恢复为 expr&expr
        s = self._cleanup_aligned_for_word(s)

        # Word 公式框更适合纯紧凑表达：去掉所有空白字符
        s = re.sub(r"\s+", "", s)
        return s

    def _cleanup_aligned_for_word(self, formula: str) -> str:
        """清理 aligned 环境中OCR引入的冗余花括号。"""
        m = re.search(r"\\begin\{aligned\}(.*)\\end\{aligned\}", formula)
        if not m:
            return formula

        body = m.group(1)
        lines = [part.strip() for part in re.split(r"\\\\", body)]
        cleaned_lines = []

        for line in lines:
            if not line:
                continue

            line = line.replace("{}", "").strip()

            if "&" in line:
                lhs, rhs = line.split("&", 1)
                lhs = self._strip_outer_braces(lhs.strip())
                rhs = self._strip_outer_braces(rhs.strip())
                line = f"{lhs}&{rhs}" if lhs else f"&{rhs}"
            else:
                line = self._strip_outer_braces(line)

            cleaned_lines.append(line)

        if not cleaned_lines:
            return formula

        return "\\begin{aligned}" + "\\\\".join(cleaned_lines) + "\\end{aligned}"

    def _strip_outer_braces(self, text: str) -> str:
        """如果字符串整体被一对最外层大括号包裹，则剥离该层。"""
        text = text.strip()
        while text.startswith("{") and text.endswith("}") and self._is_outer_braced(text):
            text = text[1:-1].strip()
        return text

    def _is_outer_braced(self, text: str) -> bool:
        """判断文本是否由一对最外层大括号完整包裹。"""
        depth = 0
        for idx, ch in enumerate(text):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and idx != len(text) - 1:
                    return False
            if depth < 0:
                return False
        return depth == 0
    
    def format_batch(self, formulas: list) -> list:
        """批量转换多个公式"""
        return [self.format_formula(f) for f in formulas]
    
    def validate_latex(self, latex: str) -> Tuple[bool, str]:
        """
        验证LaTeX语法（基础检查）
        
        Returns:
            (是否有效, 错误信息)
        """
        formula = self._clean_formula(latex)
        
        # 检查括号匹配
        if not self._check_brackets(formula):
            return False, "括号不匹配"
        
        # 检查是否为空
        if not formula.strip():
            return False, "公式为空"
        
        return True, ""
    
    def _check_brackets(self, formula: str) -> bool:
        """检查各类括号是否匹配"""
        brackets = {"(": ")", "{": "}", "[": "]"}
        stack = []
        
        for char in formula:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return False
                if brackets[stack.pop()] != char:
                    return False
        
        return len(stack) == 0


def convert_pix2text_to_markdown(pix2text_result: dict, style: FormulaStyle = FormulaStyle.AUTO) -> str:
    """
    将pix2text识别结果转换为Markdown
    
    Args:
        pix2text_result: pix2text.recognize_image() 返回的字典
        style: 公式样式
        
    Returns:
        Markdown 格式的字符串
    """
    formatter = MarkdownFormatter(style)
    result_lines = []
    
    # 如果结果包含LaTeX公式
    if isinstance(pix2text_result, str):
        # 直接是LaTeX字符串
        return formatter.format_formula(pix2text_result)
    
    if isinstance(pix2text_result, dict):
        # 假设结果结构中有 'text' 或 'latex' 字段
        if 'latex' in pix2text_result:
            return formatter.format_formula(pix2text_result['latex'])
        elif 'text' in pix2text_result:
            return formatter.format_formula(pix2text_result['text'])
    
    # 如果是列表则遍历处理
    if isinstance(pix2text_result, list):
        for item in pix2text_result:
            if isinstance(item, str):
                result_lines.append(formatter.format_formula(item))
            elif isinstance(item, dict) and 'latex' in item:
                result_lines.append(formatter.format_formula(item['latex']))
    
    return "\n\n".join(result_lines) if result_lines else str(pix2text_result)
