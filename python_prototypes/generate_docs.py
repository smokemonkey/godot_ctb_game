#!/usr/bin/env python3
"""
自动文档生成器 - 为game_time包生成API文档
"""

import os
import sys
import inspect
import importlib.util
from typing import Dict, List, Any


def analyze_module(module_path: str) -> Dict[str, Any]:
    """分析模块并提取信息"""
    try:
        # 从路径加载模块
        spec = importlib.util.spec_from_file_location("temp_module", module_path)
        if not spec or not spec.loader:
            return {}
        
        module = importlib.util.module_from_spec(spec)
        sys.modules["temp_module"] = module
        spec.loader.exec_module(module)
        
        module_name = os.path.basename(module_path).replace('.py', '')
        module_info = {
            'name': module_name,
            'path': module_path,
            'docstring': inspect.getdoc(module) or "无文档说明",
            'classes': [],
            'functions': [],
            'constants': []
        }
        
        # 获取类信息
        for name, obj in inspect.getmembers(module, predicate=inspect.isclass):
            if obj.__module__ == module.__name__:
                class_info = {
                    'name': obj.__name__,
                    'docstring': inspect.getdoc(obj) or "无文档说明",
                    'methods': []
                }
                
                # 获取方法信息
                for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                    if not method_name.startswith('_'):
                        method_info = {
                            'name': method_name,
                            'docstring': inspect.getdoc(method) or "无文档说明",
                            'signature': str(inspect.signature(method))
                        }
                        class_info['methods'].append(method_info)
                
                module_info['classes'].append(class_info)
        
        # 获取函数信息
        for name, obj in inspect.getmembers(module, predicate=inspect.isfunction):
            if obj.__module__ == module.__name__ and not name.startswith('_'):
                func_info = {
                    'name': obj.__name__,
                    'docstring': inspect.getdoc(obj) or "无文档说明",
                    'signature': str(inspect.signature(obj))
                }
                module_info['functions'].append(func_info)
        
        # 获取常量
        for name, obj in inspect.getmembers(module):
            if (not name.startswith('_') and 
                not inspect.isclass(obj) and 
                not inspect.isfunction(obj) and 
                not inspect.ismodule(obj) and
                name.isupper()):
                const_info = {
                    'name': name,
                    'value': repr(obj),
                    'type': type(obj).__name__
                }
                module_info['constants'].append(const_info)
        
        return module_info
    
    except Exception as e:
        print(f"分析模块 {module_path} 时出错: {e}")
        return {}


def generate_markdown_doc(modules_info: List[Dict[str, Any]]) -> str:
    """生成Markdown格式的文档"""
    doc = []
    doc.append("# Core System API 文档")
    doc.append("")
    doc.append("此文档由自动生成器创建，包含core包的完整API参考。")
    doc.append("")
    doc.append("## 目录")
    doc.append("")
    
    # 生成目录
    for module in modules_info:
        module_name = module['name']
        anchor = module_name.lower().replace('_', '-')
        doc.append(f"- [{module_name}](#{anchor})")
    doc.append("")
    
    # 生成详细文档
    for module in modules_info:
        module_name = module['name']
        doc.append(f"## {module_name}")
        doc.append("")
        doc.append(f"**文件路径**: `{module['path']}`")
        doc.append("")
        doc.append(f"**模块说明**: {module['docstring']}")
        doc.append("")
        
        # 常量
        if module['constants']:
            doc.append("### 常量")
            doc.append("")
            for const in module['constants']:
                doc.append(f"#### `{const['name']}`")
                doc.append(f"- **类型**: {const['type']}")
                doc.append(f"- **值**: {const['value']}")
                doc.append("")
        
        # 类
        if module['classes']:
            doc.append("### 类")
            doc.append("")
            for cls in module['classes']:
                doc.append(f"#### `{cls['name']}`")
                doc.append("")
                doc.append(f"{cls['docstring']}")
                doc.append("")
                
                # 类方法
                if cls['methods']:
                    doc.append("**方法**:")
                    doc.append("")
                    for method in cls['methods']:
                        doc.append(f"##### `{method['name']}{method['signature']}`")
                        doc.append("")
                        doc.append(f"{method['docstring']}")
                        doc.append("")
        
        # 函数
        if module['functions']:
            doc.append("### 函数")
            doc.append("")
            for func in module['functions']:
                doc.append(f"#### `{func['name']}{func['signature']}`")
                doc.append("")
                doc.append(f"{func['docstring']}")
                doc.append("")
        
        doc.append("---")
        doc.append("")
    
    return "\n".join(doc)


def main():
    """主函数"""
    # 扫描core包
    core_dir = "core"
    if not os.path.exists(core_dir):
        print("错误: 未找到core目录")
        return
    
    modules_info = []
    
    # 扫描Python文件和子目录
    for root, dirs, files in os.walk(core_dir):
        for filename in sorted(files):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_path = os.path.join(root, filename)
                print(f"分析模块: {module_path}")
                
                module_info = analyze_module(module_path)
                if module_info:
                    modules_info.append(module_info)
    
    # 生成文档
    if modules_info:
        doc_content = generate_markdown_doc(modules_info)
        
        # 写入文件
        doc_filename = "API_DOCS.md"
        with open(doc_filename, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"✅ API文档已生成: {doc_filename}")
        print(f"📄 共处理 {len(modules_info)} 个模块")
        
        # 显示模块摘要
        for module in modules_info:
            class_count = len(module['classes'])
            func_count = len(module['functions'])
            const_count = len(module['constants'])
            print(f"  - {module['name']}: {class_count}个类, {func_count}个函数, {const_count}个常量")
        
    else:
        print("❌ 未找到有效的模块")


if __name__ == "__main__":
    main() 