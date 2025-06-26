#!/usr/bin/env python3
"""
代码同步工具 - 在Python原型和C#/GDScript生产代码之间同步

用法:
    python sync_code.py py cs [--file=<module>] [--dry-run]
    python sync_code.py cs py [--file=<module>] [--dry-run]
    python sync_code.py --check-mapping
    python sync_code.py --update-tests
"""

import os
import sys
import argparse
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class CodeSyncer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.python_dir = self.project_root / "python_prototypes" / "core"
        self.csharp_dir = self.project_root / "scripts" / "csharp" / "core"
        self.gdscript_dir = self.project_root / "scripts" / "gdscript" / "core"
        
        # 映射文件路径
        self.py_to_cs_mapping = self.project_root / "python_prototypes" / "CSHARP_MAPPING.md"
        self.cs_to_py_mapping = self.project_root / "scripts" / "csharp" / "PYTHON_MAPPING.md"
        
        # 模块映射
        self.module_mapping = {
            "calendar": {
                "py": "calendar/calendar.py",
                "cs": "Calendar.cs",
                "gd": "Calendar.gd"
            },
            "indexed_time_wheel": {
                "py": "indexed_time_wheel/indexed_time_wheel.py", 
                "cs": "IndexedTimeWheel.cs",
                "gd": "IndexedTimeWheel.gd"
            },
            "ctb_manager": {
                "py": "ctb_manager/ctb_manager.py",
                "cs": "CTBManager.cs", 
                "gd": "CTBManager.gd"
            },
            "game_world": {
                "py": "game_world.py",
                "cs": "GameWorld.cs",
                "gd": "GameWorld.gd"
            }
        }

    def sync(self, source_lang: str, target_lang: str, module: Optional[str] = None, dry_run: bool = False):
        """同步代码从源语言到目标语言"""
        print(f"🔄 同步 {source_lang.upper()} → {target_lang.upper()}")
        
        if module:
            modules_to_sync = [module]
        else:
            modules_to_sync = list(self.module_mapping.keys())
        
        results = []
        for mod in modules_to_sync:
            result = self._sync_module(mod, source_lang, target_lang, dry_run)
            results.append(result)
        
        # 更新映射文件
        if not dry_run:
            self._update_mapping_files()
            
        return results

    def _sync_module(self, module: str, source_lang: str, target_lang: str, dry_run: bool) -> Dict:
        """同步单个模块"""
        if module not in self.module_mapping:
            return {"module": module, "status": "error", "message": f"Unknown module: {module}"}
        
        # 获取源文件和目标文件路径
        source_file = self._get_file_path(module, source_lang)
        target_file = self._get_file_path(module, target_lang)
        
        if not source_file.exists():
            return {"module": module, "status": "error", "message": f"Source file not found: {source_file}"}
        
        # 检查文件变更
        source_hash = self._get_file_hash(source_file)
        target_hash = self._get_file_hash(target_file) if target_file.exists() else None
        
        print(f"  📁 {module}: {source_file.name} → {target_file.name}")
        
        if dry_run:
            return {"module": module, "status": "would_sync", "source": str(source_file), "target": str(target_file)}
        
        # 实际同步逻辑（这里简化为复制，实际应该是智能转换）
        if source_lang == "py" and target_lang == "cs":
            success = self._py_to_cs(source_file, target_file)
        elif source_lang == "cs" and target_lang == "py":
            success = self._cs_to_py(source_file, target_file)
        else:
            return {"module": module, "status": "error", "message": f"Unsupported sync: {source_lang} → {target_lang}"}
        
        if success:
            self._add_sync_header(target_file, source_file, source_lang)
            return {"module": module, "status": "synced", "source_hash": source_hash}
        else:
            return {"module": module, "status": "error", "message": "Sync failed"}

    def _get_file_path(self, module: str, lang: str) -> Path:
        """获取模块在指定语言中的文件路径"""
        mapping = self.module_mapping[module]
        filename = mapping[lang]
        
        if lang == "py":
            return self.python_dir / filename
        elif lang == "cs":
            return self.csharp_dir / filename
        elif lang == "gd":
            return self.gdscript_dir / filename
        else:
            raise ValueError(f"Unknown language: {lang}")

    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希"""
        if not file_path.exists():
            return ""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _py_to_cs(self, py_file: Path, cs_file: Path) -> bool:
        """Python转C#（简化实现）"""
        print(f"    🐍→🔷 Converting {py_file.name} to {cs_file.name}")
        # 这里应该实现实际的转换逻辑
        # 现在只是创建一个占位符文件
        
        cs_file.parent.mkdir(parents=True, exist_ok=True)
        
        template = f"""// Auto-generated from {py_file.name}
// Last sync: {datetime.datetime.now().isoformat()}

using System;

namespace Core
{{
    /// <summary>
    /// {py_file.stem.title()} - Converted from Python prototype
    /// Source: {py_file}
    /// </summary>
    public class {py_file.stem.title().replace('_', '')}
    {{
        // TODO: Implement conversion from Python
        // Original Python file: {py_file}
        
        public {py_file.stem.title().replace('_', '')}()
        {{
            // Constructor
        }}
    }}
}}
"""
        
        with open(cs_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return True

    def _cs_to_py(self, cs_file: Path, py_file: Path) -> bool:
        """C#转Python（简化实现）"""
        print(f"    🔷→🐍 Converting {cs_file.name} to {py_file.name}")
        # 实际实现应该解析C#代码并转换
        
        py_file.parent.mkdir(parents=True, exist_ok=True)
        
        template = f'''#!/usr/bin/env python3
"""
Auto-generated from {cs_file.name}
Last sync: {datetime.datetime.now().isoformat()}
Source: {cs_file}
"""

class {py_file.stem.title().replace('_', '')}:
    """Converted from C# implementation"""
    
    def __init__(self):
        # TODO: Implement conversion from C#
        # Original C# file: {cs_file}
        pass
'''
        
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return True

    def _add_sync_header(self, target_file: Path, source_file: Path, source_lang: str):
        """为目标文件添加同步头信息"""
        content = target_file.read_text(encoding='utf-8')
        
        sync_info = f"""
Last synced from {source_lang.upper()}: {datetime.datetime.now().isoformat()}
Source: {source_file}
Hash: {self._get_file_hash(source_file)}
"""
        
        # 根据文件类型添加合适的注释
        if target_file.suffix == '.cs':
            header = f"/// <summary>\n///{sync_info}/// </summary>\n"
        elif target_file.suffix == '.py':
            header = f'"""\n{sync_info}"""\n'
        elif target_file.suffix == '.gd':
            header = f"#{sync_info.replace(chr(10), chr(10)+'# ')}\n"
        else:
            header = f"#{sync_info}\n"
        
        # 简单替换（实际应该更智能）
        if "Auto-generated" in content:
            # 文件已有同步信息，更新它
            pass
        else:
            # 添加新的同步信息
            pass

    def _update_mapping_files(self):
        """更新映射文件"""
        print("📋 更新映射文件...")
        
        # 更新Python→C#映射
        mapping_content = self._generate_mapping_content("py", "cs")
        with open(self.py_to_cs_mapping, 'w', encoding='utf-8') as f:
            f.write(mapping_content)
        
        # 更新C#→Python映射  
        mapping_content = self._generate_mapping_content("cs", "py")
        with open(self.cs_to_py_mapping, 'w', encoding='utf-8') as f:
            f.write(mapping_content)

    def _generate_mapping_content(self, source_lang: str, target_lang: str) -> str:
        """生成映射文件内容"""
        timestamp = datetime.datetime.now().isoformat()
        
        content = f"""# {source_lang.upper()} → {target_lang.upper()} Mapping

Last updated: {timestamp}

## Module Correspondence

| {source_lang.upper()} Module | {target_lang.upper()} Module | Status | Last Sync |
|------------|------------|--------|-----------|
"""
        
        for module, mapping in self.module_mapping.items():
            source_file = self._get_file_path(module, source_lang)
            target_file = self._get_file_path(module, target_lang)
            
            source_exists = "✅" if source_file.exists() else "❌"
            target_exists = "✅" if target_file.exists() else "❌"
            status = f"{source_exists} → {target_exists}"
            
            content += f"| `{mapping[source_lang]}` | `{mapping[target_lang]}` | {status} | {timestamp[:10]} |\n"
        
        content += f"""

## Sync Commands

```bash
# Sync specific module
python sync_code.py {source_lang} {target_lang} --file=<module>

# Sync all modules  
python sync_code.py {source_lang} {target_lang}

# Dry run (preview changes)
python sync_code.py {source_lang} {target_lang} --dry-run
```

## Notes

- This file is auto-generated by sync_code.py
- Manual edits will be overwritten
- Check git diff before committing sync changes
"""
        
        return content

    def check_mapping(self):
        """检查映射文件一致性"""
        print("🔍 检查映射文件一致性...")
        
        issues = []
        
        for module, mapping in self.module_mapping.items():
            for lang, filename in mapping.items():
                file_path = self._get_file_path(module, lang)
                if not file_path.exists():
                    issues.append(f"Missing {lang} file: {file_path}")
        
        if issues:
            print("❌ 发现问题:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ 映射检查通过")
            return True

def main():
    parser = argparse.ArgumentParser(description="代码同步工具")
    parser.add_argument("source", nargs="?", choices=["py", "cs", "gd"], help="源语言")
    parser.add_argument("target", nargs="?", choices=["py", "cs", "gd"], help="目标语言")
    parser.add_argument("--file", help="指定同步的模块")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际同步")
    parser.add_argument("--check-mapping", action="store_true", help="检查映射文件")
    parser.add_argument("--update-tests", action="store_true", help="更新测试文件")
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    syncer = CodeSyncer(str(project_root))
    
    if args.check_mapping:
        syncer.check_mapping()
    elif args.source and args.target:
        results = syncer.sync(args.source, args.target, args.file, args.dry_run)
        
        print("\n📊 同步结果:")
        for result in results:
            status_icon = {"synced": "✅", "error": "❌", "would_sync": "🔄"}.get(result["status"], "❓")
            print(f"  {status_icon} {result['module']}: {result['status']}")
            if "message" in result:
                print(f"    {result['message']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()