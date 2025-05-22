#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版本的Huggingface数据集搜索和下载工具
专门用于通过关键词搜索和下载数据集
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any

import datasets
from huggingface_hub import HfApi, hf_hub_download
from tqdm import tqdm
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)

def search_datasets(keyword, limit=20, show_file_count=False):
    """搜索数据集并返回结果"""
    print(f"{Fore.BLUE}正在搜索关键词 '{keyword}' 相关的数据集，请稍候...{Style.RESET_ALL}")
    
    api = HfApi()
    
    try:
        # 使用关键词搜索数据集
        datasets_list = list(api.list_datasets(search=keyword))
        
        if not datasets_list:
            print(f"{Fore.RED}没有找到与 '{keyword}' 相关的数据集{Style.RESET_ALL}")
            return []
        
        # 获取总数量
        total_count = len(datasets_list)
        
        # 按下载量排序
        datasets_list.sort(key=lambda x: x.downloads, reverse=True)
        
        # 显示总数和返回数量
        print(f"{Fore.GREEN}共找到 {total_count} 个相关数据集，显示下载量最高的 {min(limit, total_count)} 个:{Style.RESET_ALL}")
        
        # 限制结果数量
        if limit > 0:
            display_list = datasets_list[:limit]
        else:
            display_list = datasets_list
        
        # 是否获取文件数量
        if show_file_count:
            print(f"{Fore.BLUE}正在获取文件数量信息，这可能需要一些时间...{Style.RESET_ALL}")
        
        # 打印数据集信息
        for i, dataset in enumerate(display_list, 1):
            print(f"\n{Fore.YELLOW}{i}. {dataset.id}{Style.RESET_ALL}")
            print(f"   下载量: {dataset.downloads:,}")
            
            # 获取并显示文件数量
            if show_file_count:
                try:
                    files = api.list_repo_files(dataset.id, repo_type="dataset")
                    file_count = len(files)
                    
                    # 按文件类型分组
                    file_types = {}
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if not ext:
                            ext = "(无扩展名)"
                        if ext not in file_types:
                            file_types[ext] = 0
                        file_types[ext] += 1
                    
                    # 显示文件数量
                    type_info = ", ".join([f"{count}个{ext}" for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:3]])
                    if len(file_types) > 3:
                        type_info += f", 等{len(file_types)}种类型"
                    
                    print(f"   {Fore.CYAN}文件数量: {file_count} ({type_info}){Style.RESET_ALL}")
                except Exception as e:
                    print(f"   {Fore.RED}无法获取文件数量: {str(e)}{Style.RESET_ALL}")
            
            # 显示数据集的简短描述（如果有）
            if hasattr(dataset, 'description') and dataset.description:
                desc = dataset.description.split('\n')[0][:150] + ('...' if len(dataset.description) > 150 else '')
                print(f"   描述: {desc}")
            
            # 显示数据集的标签/类型（如果有）
            if hasattr(dataset, 'tags') and dataset.tags:
                tags = ', '.join(dataset.tags[:8]) + ('...' if len(dataset.tags) > 8 else '')
                print(f"   {Fore.GREEN}标签: {tags}{Style.RESET_ALL}")
        
        if total_count > limit:
            print(f"\n{Fore.BLUE}注意: 仅显示了 {limit} 个结果，实际共有 {total_count} 个匹配的数据集{Style.RESET_ALL}")
            print(f"{Fore.BLUE}如需查看更多结果，可以使用 --limit 参数增加显示数量{Style.RESET_ALL}")
            print(f"{Fore.BLUE}例如: python {sys.argv[0]} --search \"{keyword}\" --limit 50{Style.RESET_ALL}")
        
        return datasets_list
    
    except Exception as e:
        print(f"{Fore.RED}搜索时出错: {str(e)}{Style.RESET_ALL}")
        return []

def show_dataset_info(dataset_id):
    """显示数据集的详细信息"""
    print(f"{Fore.BLUE}正在获取数据集 '{dataset_id}' 的详细信息，请稍候...{Style.RESET_ALL}")
    
    api = HfApi()
    
    try:
        # 获取数据集信息
        dataset_info = api.dataset_info(dataset_id)
        
        print(f"\n{Fore.YELLOW}数据集: {dataset_info.id}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}作者: {dataset_info.author}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}下载量: {dataset_info.downloads:,}{Style.RESET_ALL}")
        
        if hasattr(dataset_info, 'citation') and dataset_info.citation:
            print(f"{Fore.CYAN}引用: {dataset_info.citation[:200]}...{Style.RESET_ALL}" if len(dataset_info.citation) > 200 else f"{Fore.CYAN}引用: {dataset_info.citation}{Style.RESET_ALL}")
        
        # 显示数据集的标签/类型（如果有）
        if hasattr(dataset_info, 'tags') and dataset_info.tags:
            print(f"{Fore.CYAN}标签: {', '.join(dataset_info.tags)}{Style.RESET_ALL}")
        
        # 显示完整描述
        if hasattr(dataset_info, 'description') and dataset_info.description:
            print(f"\n{Fore.GREEN}描述:{Style.RESET_ALL}")
            print(f"{dataset_info.description}")
        
        # 尝试获取数据集配置
        try:
            configs = datasets.get_dataset_config_names(dataset_id)
            if configs:
                print(f"\n{Fore.GREEN}可用配置:{Style.RESET_ALL}")
                for i, config in enumerate(configs, 1):
                    print(f"  {i}. {config}")
        except Exception as e:
            print(f"{Fore.YELLOW}无法获取数据集配置: {str(e)}{Style.RESET_ALL}")
        
        # 获取数据集文件列表
        try:
            # 获取仓库中的文件列表
            files = api.list_repo_files(dataset_id, repo_type="dataset")
            
            if files:
                print(f"\n{Fore.GREEN}数据集文件列表:{Style.RESET_ALL}")
                
                # 按文件类型分组显示
                file_groups = {}
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext not in file_groups:
                        file_groups[ext] = []
                    file_groups[ext].append(file)
                
                # 显示分组后的文件
                for ext, file_list in file_groups.items():
                    print(f"\n  {Fore.CYAN}{ext if ext else '其他文件'} ({len(file_list)}个):{Style.RESET_ALL}")
                    for i, file in enumerate(sorted(file_list)[:10], 1):
                        file_url = f"https://huggingface.co/datasets/{dataset_id}/resolve/main/{file}"
                        print(f"    {i}. {file}")
                    
                    if len(file_list) > 10:
                        print(f"    ... 等共 {len(file_list)} 个文件")
                
                print(f"\n{Fore.BLUE}查看完整文件列表: https://huggingface.co/datasets/{dataset_id}/tree/main{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}未找到数据集文件{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.YELLOW}获取文件列表时出错: {str(e)}{Style.RESET_ALL}")
        
        # 显示下载指令
        print(f"\n{Fore.GREEN}使用以下命令下载此数据集:{Style.RESET_ALL}")
        print(f"python {sys.argv[0]} --download {dataset_id}")
        print(f"\n{Fore.GREEN}也可以在Python代码中使用以下方式加载:{Style.RESET_ALL}")
        print(f"```python")
        print(f"from datasets import load_dataset")
        print(f"dataset = load_dataset('{dataset_id}')")
        print(f"```")
        
        # 显示浏览器链接
        print(f"\n{Fore.GREEN}在浏览器中查看: https://huggingface.co/datasets/{dataset_id}{Style.RESET_ALL}")
        
        return True
    
    except Exception as e:
        print(f"{Fore.RED}获取数据集信息时出错: {str(e)}{Style.RESET_ALL}")
        return False

def download_dataset(dataset_id, config=None, force_direct_download=False):
    """下载指定的数据集"""
    print(f"{Fore.BLUE}正在准备下载数据集: {dataset_id}{Style.RESET_ALL}")
    
    # 创建保存数据集的目录
    save_dir = os.path.join("datasets", dataset_id.replace("/", "_"))
    os.makedirs(save_dir, exist_ok=True)
    
    # 如果强制使用直接下载方法
    if force_direct_download:
        return direct_download_dataset(dataset_id, save_dir)
    
    try:
        if config:
            # 下载特定配置
            print(f"{Fore.GREEN}下载配置: {config}{Style.RESET_ALL}")
            ds = datasets.load_dataset(dataset_id, config, cache_dir=save_dir)
            
            # 保存数据集信息
            config_info_path = os.path.join(save_dir, f"{config}_info.json")
            with open(config_info_path, 'w', encoding='utf-8') as f:
                info = {
                    "dataset_id": dataset_id,
                    "config": config,
                    "splits": list(ds.keys()),
                    "features": str(next(iter(ds.values())).features),
                }
                json.dump(info, f, indent=2, ensure_ascii=False)
        else:
            # 尝试获取数据集配置
            try:
                dataset_configs = datasets.get_dataset_config_names(dataset_id)
                
                if dataset_configs:
                    print(f"{Fore.CYAN}数据集包含以下配置:{Style.RESET_ALL}")
                    for i, cfg in enumerate(dataset_configs, 1):
                        print(f"  {i}. {cfg}")
                    
                    # 下载第一个配置
                    config = dataset_configs[0]
                    print(f"{Fore.GREEN}自动选择第一个配置: {config}{Style.RESET_ALL}")
                    
                    ds = datasets.load_dataset(dataset_id, config, cache_dir=save_dir)
                    
                    # 保存数据集信息
                    config_info_path = os.path.join(save_dir, f"{config}_info.json")
                    with open(config_info_path, 'w', encoding='utf-8') as f:
                        info = {
                            "dataset_id": dataset_id,
                            "config": config,
                            "splits": list(ds.keys()),
                            "features": str(next(iter(ds.values())).features),
                        }
                        json.dump(info, f, indent=2, ensure_ascii=False)
                else:
                    # 数据集没有特定配置
                    ds = datasets.load_dataset(dataset_id, cache_dir=save_dir)
                    
                    # 保存数据集信息
                    info_path = os.path.join(save_dir, "dataset_info.json")
                    with open(info_path, 'w', encoding='utf-8') as f:
                        info = {
                            "dataset_id": dataset_id,
                            "splits": list(ds.keys()),
                            "features": str(next(iter(ds.values())).features),
                        }
                        json.dump(info, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"{Fore.YELLOW}使用datasets库加载数据集失败: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}此数据集可能不使用标准格式或需要特殊处理{Style.RESET_ALL}")
                
                # 询问用户是否尝试直接下载
                print(f"\n{Fore.CYAN}是否尝试直接从仓库下载原始文件? [y/n]:{Style.RESET_ALL} ", end="")
                try:
                    choice = input().strip().lower()
                    if choice in ['y', 'yes']:
                        return direct_download_dataset(dataset_id, save_dir)
                    else:
                        print(f"{Fore.YELLOW}取消下载{Style.RESET_ALL}")
                        print(f"\n{Fore.CYAN}提示: 您也可以使用以下命令直接下载原始文件:{Style.RESET_ALL}")
                        print(f"python {sys.argv[0]} --download {dataset_id} --force-direct")
                        print(f"\n{Fore.CYAN}或者先查看数据集详细信息:{Style.RESET_ALL}")
                        print(f"python {sys.argv[0]} --info {dataset_id}")
                        return False
                except EOFError:
                    print(f"\n{Fore.YELLOW}检测到非交互式环境，自动尝试直接下载{Style.RESET_ALL}")
                    return direct_download_dataset(dataset_id, save_dir)
                
                return False
        
        # 打印数据集结构
        print(f"\n{Fore.CYAN}数据集结构:{Style.RESET_ALL}")
        for split, split_ds in ds.items():
            print(f"  {split}: {len(split_ds)} 样本")
        
        print(f"{Fore.GREEN}数据集已保存到: {os.path.abspath(save_dir)}{Style.RESET_ALL}")
        return True
    
    except Exception as e:
        print(f"{Fore.RED}下载数据集时出错: {str(e)}{Style.RESET_ALL}")
        
        # 询问用户是否尝试直接下载
        print(f"\n{Fore.CYAN}是否尝试直接从仓库下载原始文件? [y/n]:{Style.RESET_ALL} ", end="")
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes']:
                return direct_download_dataset(dataset_id, save_dir)
            else:
                print(f"{Fore.YELLOW}取消下载{Style.RESET_ALL}")
                print(f"\n{Fore.CYAN}提示: 您也可以使用以下命令直接下载原始文件:{Style.RESET_ALL}")
                print(f"python {sys.argv[0]} --download {dataset_id} --force-direct")
                print(f"\n{Fore.CYAN}或者先查看数据集详细信息:{Style.RESET_ALL}")
                print(f"python {sys.argv[0]} --info {dataset_id}")
                return False
        except EOFError:
            print(f"\n{Fore.YELLOW}检测到非交互式环境，自动尝试直接下载{Style.RESET_ALL}")
            return direct_download_dataset(dataset_id, save_dir)
        
        return False

def direct_download_dataset(dataset_id, save_dir):
    """直接从仓库下载数据集文件"""
    print(f"{Fore.YELLOW}尝试直接从仓库下载文件...{Style.RESET_ALL}")
    
    # 从仓库下载文件
    api = HfApi()
    try:
        files = api.list_repo_files(dataset_id, repo_type="dataset")
        if not files:
            print(f"{Fore.RED}未找到任何文件{Style.RESET_ALL}")
            return False
        
        total_files = len(files)
        print(f"{Fore.GREEN}找到 {total_files} 个文件{Style.RESET_ALL}")
        
        # 确认下载
        if total_files > 100:
            print(f"{Fore.YELLOW}注意: 数据集包含大量文件 ({total_files}个)，下载可能需要较长时间{Style.RESET_ALL}")
            print(f"{Fore.CYAN}是否继续下载? [y/n]:{Style.RESET_ALL} ", end="")
            try:
                choice = input().strip().lower()
                if choice not in ['y', 'yes']:
                    print(f"{Fore.YELLOW}已取消下载{Style.RESET_ALL}")
                    return False
            except EOFError:
                print(f"\n{Fore.YELLOW}检测到非交互式环境，继续下载{Style.RESET_ALL}")
        
        # 开始下载
        success_count = 0
        error_files = []
        
        for file in tqdm(files, desc="下载文件"):
            try:
                file_path = os.path.join(save_dir, file)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                hf_hub_download(
                    repo_id=dataset_id,
                    filename=file,
                    repo_type="dataset",
                    local_dir=save_dir,
                    local_dir_use_symlinks=False
                )
                success_count += 1
            except Exception as file_e:
                print(f"{Fore.RED}下载文件 {file} 失败: {str(file_e)}{Style.RESET_ALL}")
                error_files.append(file)
        
        if success_count == total_files:
            print(f"{Fore.GREEN}已成功下载所有 {total_files} 个文件到: {os.path.abspath(save_dir)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}已下载 {success_count}/{total_files} 个文件，{len(error_files)} 个文件下载失败{Style.RESET_ALL}")
            if error_files:
                print(f"{Fore.YELLOW}下载失败的文件:{Style.RESET_ALL}")
                for i, file in enumerate(error_files[:10], 1):
                    print(f"  {i}. {file}")
                if len(error_files) > 10:
                    print(f"  ... 等 {len(error_files)} 个文件")
        
        return success_count > 0
    except Exception as repo_e:
        print(f"{Fore.RED}无法从仓库下载文件: {str(repo_e)}{Style.RESET_ALL}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Huggingface数据集搜索和下载工具")
    parser.add_argument("--search", help="要搜索的关键词")
    parser.add_argument("--download", help="要下载的数据集ID")
    parser.add_argument("--info", help="查看指定数据集的详细信息")
    parser.add_argument("--config", help="要下载的数据集配置名称")
    parser.add_argument("--limit", type=int, default=30, help="显示的搜索结果数量限制")
    parser.add_argument("--force-direct", action="store_true", help="强制使用直接下载方法")
    parser.add_argument("--show-files", action="store_true", help="显示数据集文件数量和类型统计")
    args = parser.parse_args()
    
    # 显示欢迎信息
    print(f"{Fore.CYAN}======================================{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  Huggingface数据集搜索下载工具  {Style.RESET_ALL}")
    print(f"{Fore.CYAN}======================================{Style.RESET_ALL}")
    
    # 查看数据集详细信息
    if args.info:
        show_dataset_info(args.info)
        return
    
    # 下载指定的数据集
    elif args.download:
        download_dataset(args.download, args.config, args.force_direct)
        return
    
    # 搜索数据集
    elif args.search:
        datasets_list = search_datasets(args.search, args.limit, args.show_files)
        
        if datasets_list:
            print(f"\n{Fore.CYAN}如需查看数据集详细信息，请使用命令:{Style.RESET_ALL}")
            print(f"python {sys.argv[0]} --info 数据集ID")
            print(f"\n{Fore.CYAN}如需下载数据集，请使用命令:{Style.RESET_ALL}")
            print(f"python {sys.argv[0]} --download 数据集ID [--config 配置名称]")
            print(f"\n{Fore.CYAN}例如:{Style.RESET_ALL}")
            print(f"python {sys.argv[0]} --info {datasets_list[0].id}")
            print(f"python {sys.argv[0]} --download {datasets_list[0].id}")
        return
    
    # 如果没有提供任何参数，进入交互模式
    print(f"{Fore.CYAN}请输入要搜索的关键词 (例如 'time series', 'chinese', 'nlp'):{Style.RESET_ALL}")
    keyword = input().strip()
    
    if not keyword:
        print(f"{Fore.RED}搜索关键词不能为空{Style.RESET_ALL}")
        return
    
    # 询问是否显示文件数量
    show_files = False
    print(f"{Fore.CYAN}是否显示数据集文件数量统计? (y/n, 默认n):{Style.RESET_ALL} ", end="")
    try:
        choice = input().strip().lower()
        if choice in ['y', 'yes']:
            show_files = True
    except EOFError:
        pass
    
    # 搜索数据集
    datasets_list = search_datasets(keyword, args.limit, show_files)
    
    if datasets_list:
        print(f"\n{Fore.CYAN}请选择操作: [1] 查看详细信息 [2] 下载数据集 [0] 退出{Style.RESET_ALL}")
        try:
            action = int(input().strip())
            
            if action == 0:
                print(f"{Fore.YELLOW}已退出{Style.RESET_ALL}")
                return
            
            elif action == 1:
                # 查看详细信息
                print(f"{Fore.CYAN}请输入要查看的数据集编号:{Style.RESET_ALL}")
                choice = int(input().strip())
                
                if 1 <= choice <= len(datasets_list):
                    selected_dataset = datasets_list[choice-1]
                    show_dataset_info(selected_dataset.id)
                else:
                    print(f"{Fore.RED}无效的数据集编号{Style.RESET_ALL}")
            
            elif action == 2:
                # 下载数据集
                print(f"{Fore.CYAN}请输入要下载的数据集编号:{Style.RESET_ALL}")
                choice = int(input().strip())
                
                if 1 <= choice <= len(datasets_list):
                    selected_dataset = datasets_list[choice-1]
                    download_dataset(selected_dataset.id, args.config, args.force_direct)
                else:
                    print(f"{Fore.RED}无效的数据集编号{Style.RESET_ALL}")
            
            else:
                print(f"{Fore.RED}无效的选择{Style.RESET_ALL}")
        
        except ValueError:
            print(f"{Fore.RED}请输入有效的数字{Style.RESET_ALL}")
        except EOFError:
            print(f"{Fore.RED}检测到输入错误，退出程序{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 