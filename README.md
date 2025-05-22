# Huggingface数据集下载工具

这是一个用于从Huggingface自动下载数据集的工具，支持按类型筛选和浏览数据集。

## 功能特点

- 支持按类型浏览和下载Huggingface数据集
- 按下载量排序显示数据集
- 支持分页浏览数据集列表
- 显示数据集详细信息和配置
- 支持下载数据集的特定配置或全部配置
- 彩色命令行界面，提供友好的用户体验

## 安装依赖

首先，安装必要的依赖包：

```bash
pip install -r requirements.txt
```

## 使用方法

### 交互式使用

直接运行脚本，按照提示操作：

```bash
python download_huggingface_datasets.py
```

程序会提示您选择数据集类型，然后显示符合条件的数据集列表供您选择。

### 命令行参数

您也可以使用命令行参数直接指定要下载的数据集类型或特定数据集：

```bash
# 指定数据集类型
python download_huggingface_datasets.py --type "text-classification"

# 直接指定数据集ID
python download_huggingface_datasets.py --dataset "glue"
```

## 可用的数据集类型

本工具支持以下几类数据集：

### 文本类数据集
- text-classification
- sentiment-analysis
- question-answering
- summarization
- translation
- text-generation
- language-modeling

### 图像类数据集
- image-classification
- object-detection
- image-segmentation
- image-to-text

### 音频类数据集
- audio-classification
- automatic-speech-recognition
- text-to-speech

### 多模态数据集
- visual-question-answering
- document-question-answering
- image-to-text

### 表格类数据集
- tabular-classification
- tabular-regression

## 数据保存位置

下载的数据集将保存在当前目录下的`datasets`文件夹中，每个数据集会创建一个单独的子文件夹。

## 注意事项

- 下载大型数据集可能需要较长时间，请耐心等待
- 首次使用时会自动创建缓存，之后下载相同数据集会更快
- 如果遇到网络问题，请确保您的网络可以正常访问Huggingface网站 