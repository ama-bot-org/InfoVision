import os
import json
from flask import Flask, request, render_template, jsonify, Response
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import subprocess
import re
from pdfparse import process_single_pdf
from getsvg import process_single_file
from stream import streamoutput


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SVG_FOLDER'] = './static/svg/'  # make sure all os works
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# 确保上传目录存在
for folder in [app.config['UPLOAD_FOLDER'], app.config['SVG_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

#根据文档名称获取输出目录下对应文档名称文件夹下的所有svg
def convert_pdf_to_svg(doc_name, output_dir):
    # 从PDF文件路径中提取文件名（不含扩展名）作为子目录名
    base_name = os.path.splitext(os.path.basename(doc_name))[0]
    print(base_name)
    # 在输出目录下创建以文档名命名的子目录
    current_dir = os.getcwd()
    print(current_dir)
    doc_output_dir = os.path.join(current_dir+output_dir, base_name)
    print(doc_output_dir)
    os.makedirs(doc_output_dir, exist_ok=True)
    
    # 获取该目录下所有的SVG文件.
    
    svg_files = []
    if os.path.exists(doc_output_dir):
        for file in os.listdir(doc_output_dir):
            if file.lower().endswith('.svg'):
                # 构建相对于static目录的路径，这样前端可以直接使用
                relative_path = os.path.join('svg', base_name, file)
                svg_files.append(relative_path)
    return sorted(svg_files)  # 按文件名排序返回
   

@app.route('/')
def index():
    return render_template('index.html')

    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
        
    try:
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        # 解析pdf
        output_path = process_single_pdf(pdf_path)
        # 获取大模型数据
        #llm_output = os.path.join(os.path.dirname(__file__), 'svgtxt/' + base_name + '.txt')
        llm_output = llm_process_files(output_path)
        # 获取svg
        process_single_file(llm_output,base_name)
        svg_files = convert_pdf_to_svg(pdf_path, app.config['SVG_FOLDER'])
        print(svg_files)
        if not svg_files:
            return jsonify({'error': 'PDF转换失败'}), 500
            
        return jsonify({'success': True, 'files': svg_files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/streamupload', methods=['POST'])
def stream_upload():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
        
    try:
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        # 解析pdf
        output_path = process_single_pdf(pdf_path)
        # 获取大模型数据
        def generate():
            for content in streamoutput(output_path):
                print(content)
                yield content
        
        response = Response(generate(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        response.headers['X-Accel-Buffering'] = 'no'
        return response
        
    except Exception as e:
        #这边需要记录日志
        return jsonify({'error': str(e)}), 500



@app.route('/updateconfig', methods=['POST'])
def updateconfig():
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
            
        # 验证必要字段
        required_fields = ['api_url', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
                
        # 验证字段格式
        if not isinstance(data['api_url'], str) or not data['api_url'].startswith('http'):
            return jsonify({'error': 'api_url格式不正确'}), 400
        if not isinstance(data['api_key'], str) or not data['api_key'].startswith('sk-'):
            return jsonify({'error': 'api_key格式不正确'}), 400
            
        # 更新配置文件
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)