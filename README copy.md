# PDF2SVG 转换器

一个基于Flask的Web应用，用于将PDF文件转换为SVG格式并提供在线预览功能。

## 功能特性

- PDF文件上传和转换
- SVG格式在线预览
- 支持流式数据处理
- 轮播图展示多页SVG
- 文件下载功能
- API访问频率限制

## 安装说明

1. 克隆项目到本地

2. 安装依赖包：
```bash
pip install flask PyPDF2 pdfplumber requests
```

3. 创建必要的目录：
- uploads/：用于存储上传的PDF文件
- static/svg/：用于存储生成的SVG文件
- newtxt/：用于存储中间文本文件
- svgtxt/：用于存储处理后的文本

## 使用方法

1. 启动服务器：
```bash
python app.py
```

2. 访问Web界面：
- 打开浏览器访问 `http://127.0.0.1:8000`
- 选择PDF文件并上传
- 等待转换完成后即可在线预览SVG

## API接口

### 流式数据处理
- 端点：`/streamupload`
- 方法：POST
- 参数：file（PDF文件）
- 返回：SSE流式数据

## 注意事项

- 支持的最大文件大小为16MB
- API访问有频率限制（2次/分钟）
- 仅支持PDF格式文件上传

## 演示资源

### 演示视频
<video width="100%" controls>
  <source src="static/演示视频.mp4" type="video/mp4">
  您的浏览器不支持视频标签。
</video>

### 演示SVG
以下是一些示例SVG文件的预览：

<div style="display: flex; flex-wrap: wrap; gap: 20px;">
  <object data="Meta Agent Search 算法工作流程_2.svg" type="image/svg+xml" style="width: 45%; min-width: 300px;"></object>
  <object data="static/实验结果与跨域迁移能力_3.svg" type="image/svg+xml" style="width: 45%; min-width: 300px;"></object>
</div>