import requests
import chardet
import json
import pdfplumber
import os
import re

def process_single_pdf(file_path):
    output_folder = os.path.join(os.path.dirname(__file__), 'newtxt')
    try:
        filename = os.path.basename(file_path)
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        output_path = os.path.join(output_folder, txt_filename)

        content = []
        with open(os.path.join(os.path.dirname(__file__), 'base.txt'), 'r', encoding='utf-8') as f:
            file_content = f.read().strip()
            content.append(file_content)
        found_references = False
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # if found_references:
                #     break
                text = page.extract_text()
                if text:
                    content.append(text)
        
        if not content:
            print(f"跳过无文本内容文件: {filename}")
            return

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"成功转换: {filename} -> {txt_filename}")
        return output_path
    except Exception as e:
        print(f"处理文件 {filename} 时出错: {str(e)}")
