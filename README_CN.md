# Huggingface数据集搜索下载工具

这是一个强大的命令行工具，用于搜索、浏览和下载Huggingface上的数据集。通过简单的命令，您可以快速找到所需的数据集，查看详细信息，并下载到本地使用。

## 功能特点

- 按关键词搜索Huggingface数据集
- 显示数据集的文件数量和类型统计
- 查看数据集的详细信息（描述、标签、文件列表等）
- 以标准格式或直接下载方式获取数据集
- 交互式操作界面，易于使用
- 彩色输出，信息展示清晰

## 安装依赖

使用前，请确保已安装以下依赖：

```bash
pip install datasets huggingface_hub tqdm colorama
```

或者直接安装requirements.txt中的依赖：

```bash
pip install -r requirements.txt
```

## 命令行参数

```
python search_huggingface.py [参数]
```

### 主要参数

| 参数 | 说明 |
|------|------|
| `--search KEYWORD` | 按关键词搜索数据集 |
| `--info DATASET_ID` | 查看指定数据集的详细信息 |
| `--download DATASET_ID` | 下载指定的数据集 |
| `--force-direct` | 强制使用直接下载方式（下载所有原始文件） |
| `--config CONFIG` | 指定要下载的数据集配置 |
| `--limit NUMBER` | 限制显示的搜索结果数量（默认30） |
| `--show-files` | 显示数据集的文件数量和类型统计 |

## 使用示例

### 1. 搜索数据集

```bash
# 基本搜索
python search_huggingface.py --search "time series"

# 显示更多结果
python search_huggingface.py --search "time series" --limit 50

# 同时显示文件数量统计
python search_huggingface.py --search "time series" --show-files
```

### 2. 查看数据集详情

```bash
# 查看特定数据集的详细信息
python search_huggingface.py --info "netop/Beam-Level-Traffic-Timeseries-Dataset"
```

### 3. 下载数据集

```bash
# 使用标准方式下载数据集
python search_huggingface.py --download "netop/Beam-Level-Traffic-Timeseries-Dataset"

# 直接下载所有原始文件（不经过datasets库处理）
python search_huggingface.py --download "netop/Beam-Level-Traffic-Timeseries-Dataset" --force-direct

# 指定特定配置下载
python search_huggingface.py --download "glue" --config "sst2"
```

### 4. 交互式使用

直接运行脚本而不带任何参数，进入交互模式：

```bash
python search_huggingface.py
```

然后按照提示输入关键词、选择操作等。

## 数据集下载方式说明

本工具提供两种下载方式：

1. **标准下载方式**：使用Huggingface的datasets库加载数据集，便于直接在代码中使用。但有些数据集可能不支持此方式。

2. **直接下载方式**：直接从Huggingface仓库下载所有原始文件，保持原始目录结构。适用于所有数据集，特别是那些没有使用标准格式的数据集。

如果标准下载方式失败，工具会提示您是否尝试直接下载方式。您也可以通过`--force-direct`参数强制使用直接下载方式。

## 下载位置

所有下载的数据集将保存在当前目录下的`datasets`文件夹中，每个数据集会创建一个单独的子文件夹。例如：

```
datasets/
  └── netop_Beam-Level-Traffic-Timeseries-Dataset/
      ├── data/
      │   ├── train/
      │   │   └── ...
      │   ├── test-1/
      │   │   └── ...
      │   └── test-2/
      │       └── ...
      ├── images/
      │   └── ...
      └── README.md
```

## 常见问题

**Q: 为什么有些数据集无法下载?**  
A: 有些数据集可能没有使用标准格式，此时可以使用`--force-direct`参数强制直接下载原始文件。

**Q: 如何知道数据集有多大?**  
A: 使用`--info`参数查看数据集详情，或者在搜索时添加`--show-files`参数显示文件统计信息。

**Q: 数据集下载后如何使用?**  
A: 标准下载的数据集可以直接通过datasets库加载：
```python
from datasets import load_dataset
dataset = load_dataset("数据集ID", cache_dir="./datasets/数据集目录")
```
直接下载的原始文件可以根据文件格式选择合适的方式加载，如CSV文件可以用pandas读取。 