import requests
import json
import os

def streamoutput(file_path):
        # 读取配置文件
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as config_file:
        config = json.load(config_file)
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read().strip()
    # 添加响应头信息
    yield 'data: {"type": "start"}\n\n'
    url = config['api_url']
    payload = json.dumps({
    "model": config['model'],
    "messages": [
        {
            "role": "user",
            "content": file_content
        }
    ],
    "stream": True
    })
    headers = {
    'Authorization': f'Bearer {config["api_key"]}',
    'Content-Type': 'application/json'
    }
    filename = os.path.basename(file_path)
    response = requests.request("POST", url, headers=headers, data=payload, stream=True)
    if response.status_code != 200:
        print("Error:", response.status_code)
        return
    output_file = os.path.join(os.path.dirname(__file__), 'svgtxt/' + filename)
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_data = decoded_line[6:]
                    try:
                        data = json.loads(json_data)
                        if 'choices' in data and len(data['choices']) > 0:
                            content = data['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                # 格式化为SSE数据格式
                                yield f'data: {json.dumps({"content": content})}\n\n'
                                f.write(content)
                    except json.JSONDecodeError:
                        print("Error decoding JSON:", json_data)
                        yield f'data: {json.dumps({"content": "Done"})}\n\n'
                    except Exception as e:
                        print(f"Error processing JSON: {str(e)}")
                        continue
