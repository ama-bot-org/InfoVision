import requests
import chardet
import json

import os

def process_single_file(file_path, filename):
    try:
        # 原文件处理逻辑移至此处
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            if not raw_data:
                print(f"跳过空文件: {filename}")
                return
            try:
                content = raw_data.decode('utf-8').strip()
            except UnicodeDecodeError:
                encoding = chardet.detect(raw_data)['encoding']
                content = raw_data.decode(encoding).strip()
        
        base_name = filename
        creatItem(content, base_name)
    
    except Exception as e:
        print(f"处理文件 {filename} 时出错: {str(e)}")


#依此读取内容中的<topic></topic>和><svg></svg>中的内容，每一组内容作为一个文件，保存到svgoutput文件夹中，文件名为topic中的内容
def creatItem(file_content, name):
    import re
    import os
    
    try:
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(__file__), 'static/svg/'+name)
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用正则表达式匹配所有topic-svg组合
        pattern = re.compile(r'<topic>(.*?)</topic>.*?<svg (.*?)</svg>', re.DOTALL)
        matches = pattern.findall(file_content)
        
        if not matches:
            print(f"未找到有效内容: {name}")
            return
        
        # 为每个匹配项生成文件
        for index, (topic, svg_content) in enumerate(matches, 1):
            # 清理topic内容作为文件名
            clean_topic = re.sub(r'[\\/*?:"<>|]', '', topic.strip())
            filename = f"{clean_topic}_{index}.svg" if len(matches) > 1 else f"{clean_topic}.svg"
            
            file_path = os.path.join(output_dir, filename)
            
            # 写入SVG内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f'<svg {svg_content.strip()}</svg>')
            
            print(f"成功生成: {filename}")
        
    except Exception as e:
        print(f"处理 {name} 时发生错误: {str(e)}")
