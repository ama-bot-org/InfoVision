import requests
import chardet
import json

import os
from concurrent.futures import ThreadPoolExecutor

def process_files():
    folder_path = os.path.join(os.path.dirname(__file__), 'newtxt')
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isfile(file_path):
                executor.submit(process_single_file, file_path, filename)

def process_single_file(file_path, filename):
    try:
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
        
        base_name = os.path.splitext(filename)[0]
        creatItem(content, base_name)
    
    except Exception as e:
        print(f"处理文件 {filename} 时出错: {str(e)}")





def creatItem(file_content,name):
    url ="https://chatapi.littlewheat.com/v1/chat/completions"
    payload = json.dumps({
    "model": "claude-3-7-sonnet-20250219",
    "messages": [
        {
            "role": "user",
            "content": file_content  # 替换为读取的文件内容
        }
    ],
    "stream": True
    })
    headers = {
    'Authorization': 'Bearer sk-ZZJsHTgmYPGyIxNrO2Z11lbDZ0q7P3T6MTVoQM0v4kbMOZqK',
    'Content-Type': 'application/json'
    }
    #4.56
    response = requests.request("POST", url, headers=headers, data=payload, stream=True)
    full_response = ''
    output_path = os.path.join(os.path.dirname(__file__), 'svgtxt/' + name + '.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in response.iter_lines():
            print(line)
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_data = decoded_line[6:]
                    try:
                        data = json.loads(json_data)
                        content = data['choices'][0]['delta'].get('content', '')
                        print(content, end='', flush=True)
                        full_response += content
                        f.write(content)
                    except json.JSONDecodeError:
                        print("Error decoding JSON:", json_data)
                        pass
                    except KeyError:
                        print("Error KeyError JSON:", KeyError)
                        pass