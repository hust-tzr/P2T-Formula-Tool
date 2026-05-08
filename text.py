from pix2text import Pix2Text

img_fp = 'D:\个人资料及学科资料\myself\简历\唐卓然-个人简历.pdf'
p2t = Pix2Text.from_config()
doc = p2t.recognize_pdf(img_fp, page_numbers=[0, 1])
doc.to_markdown('D:\个人资料及学科资料\myself\简历')  # 导出的 Markdown 信息保存在 output-md 目录中
