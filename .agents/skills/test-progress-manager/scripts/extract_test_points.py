#!/usr/bin/env python3
"""
待测试功能点提取脚本

功能：
1. 扫描项目代码文件
2. 解析代码结构（支持 Python AST, TSX/TS Regex)
3. 支持外部配置文件定义路径和排除规则
4. 生成 need_*.jsonl 文件并保留原有 ID 和优先级
"""
import ast
import re
import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


# ==========================================
# 路径定义 (Step-by-step Path Definitions)
# ==========================================
current_file_path = os.path.abspath(__file__)
scripts_dir = os.path.dirname(current_file_path)               # .agents/skills/test-progress-manager/scripts
skill_dir = os.path.dirname(scripts_dir)                      # .agents/skills/test-progress-manager
skills_dir = os.path.dirname(skill_dir)                       # .agents/skills
project_root = os.path.dirname(os.path.dirname(os.path.dirname(skill_dir))) # mindseed (项目根目录)

PROJECT_ROOT = Path(project_root)
TEST_RESULTS_DIR = PROJECT_ROOT / "src/core/tests/test-results"
CONFIG_FILE = TEST_RESULTS_DIR / "config/extract_config.json"
DEFAULT_OUTPUT_DIR = TEST_RESULTS_DIR / "data"

# 默认配置 (如果配置文件不存在)
DEFAULT_CONFIG = {
    "backend": {
        "patterns": ["src/core/backend/services/**/*.py", "src/core/backend/routers/**/*.py"],
        "output": "need_backend.jsonl",
        "category": "后端服务"
    },
    "exclude": ["**/node_modules/**", "**/__pycache__/**"]
}


def load_config() -> Dict[str, Any]:
    """从文件加载配置"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"警告：读取配置文件失败 ({e})，使用默认配置")
    return DEFAULT_CONFIG


def is_excluded(file_path: Path, exclude_patterns: List[str]) -> bool:
    """检查文件是否应被排除"""
    for pattern in exclude_patterns:
        if file_path.match(pattern):
            return True
    return False


def extract_python_functions(file_path: Path) -> List[Dict[str, Any]]:
    """使用 AST 从 Python 文件提取功能点"""
    points = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            # 提取函数
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 忽略私有方法或内置方法（除非是重要的逻辑）
                if node.name.startswith("__") and node.name.endswith("__"):
                    continue
                
                docstring = ast.get_docstring(node) or ""
                points.append({
                    "function_name": node.name,
                    "line_number": node.lineno,
                    "function_type": "function",
                    "description": docstring.split("\n")[0] if docstring else "",
                })
            # 提取类
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node) or ""
                points.append({
                    "function_name": node.name,
                    "line_number": node.lineno,
                    "function_type": "class",
                    "description": docstring.split("\n")[0] if docstring else "",
                })
    except Exception as e:
        print(f"解析 Python {file_path} 失败: {e}")
    
    return points


def extract_typescript_functions(file_path: Path) -> List[Dict[str, Any]]:
    """使用外部 Node.js AST 工具从 TypeScript/TSX 文件提取功能点"""
    helper_script = Path(__file__).parent / "ts-parser-helper.js"
    node_path = PROJECT_ROOT / "src/core/frontend/node_modules"
    
    try:
        env = os.environ.copy()
        env["NODE_PATH"] = str(node_path)
        
        result = subprocess.run(
            ["node", str(helper_script), str(file_path)],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )
        
        points = json.loads(result.stdout)
        
        # 处理 E2E 测试用例 (保留正则扫描，因为它们通常很简单且不总是导出的)
        if file_path.suffix == ".ts" and (".spec" in file_path.name or ".test" in file_path.name):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            test_pattern = r"(?:test|it|describe)\s*\(\s*['\"`]([^'\"`]+)['\"`]"
            for match in re.finditer(test_pattern, content):
                line_num = content[:match.start()].count("\n") + 1
                points.append({
                    "function_name": match.group(1),
                    "line_number": line_num,
                    "function_type": "test",
                    "description": "",
                })
        
        return points
    except Exception as e:
        print(f"AST 解析 TS {file_path} 失败: {e}")
        # 退回到正则（可选，此处不退回以确保质量）
        return []


def extract_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """根据文件扩展名分流处理"""
    suffix = file_path.suffix.lower()
    if suffix == ".py":
        return extract_python_functions(file_path)
    elif suffix in (".ts", ".tsx"):
        return extract_typescript_functions(file_path)
    return []


def generate_point_id(category: str, index: int) -> str:
    """生成具备分类辨识度的功能点 ID"""
    prefix_map = {
        "backend": "BP",
        "e2e": "EP",
        "integration": "IP",
        "frontend": "FP",
    }
    prefix = prefix_map.get(category, "XP")
    return f"{prefix}-{index:04d}"


def extract_test_points(target: str, output_dir: Path, config: Dict[str, Any]) -> int:
    """提取核心逻辑：扫描、解析、合并、写入"""
    if target not in config:
        print(f"跳过未知类别: {target}")
        return 0
    
    target_config = config[target]
    exclude_patterns = config.get("exclude", [])
    all_points = []
    
    # 扫描匹配的文件
    for pattern in target_config["patterns"]:
        for file_path in PROJECT_ROOT.glob(pattern):
            if file_path.is_file() and not is_excluded(file_path, exclude_patterns):
                points = extract_from_file(file_path)
                for point in points:
                    point["file_path"] = str(file_path.relative_to(PROJECT_ROOT))
                    point["category"] = target_config["category"]
                    all_points.append(point)
    
    output_path = output_dir / target_config["output"]
    
    # 加载现有数据以保留手动修改的优先级和 ID
    existing_points = []
    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        existing_points.append(json.loads(line))
        except (json.JSONDecodeError, IOError):
            pass
    
    # 构建快速查找图（基于文件路径和函数名）
    existing_lookup = {(p["file_path"], p["function_name"]): p for p in existing_points}
    
    final_points = []
    for i, point in enumerate(all_points, 1):
        lookup_key = (point["file_path"], point["function_name"])
        
        if lookup_key in existing_lookup:
            existing = existing_lookup[lookup_key]
            point["point_id"] = existing.get("point_id", generate_point_id(target, i))
            point["priority"] = existing.get("priority", "P2")
            point["source"] = existing.get("source", "extracted")
        else:
            point["point_id"] = generate_point_id(target, i)
            point["priority"] = "P2"
            point["source"] = "extracted"
        
        point["extracted_at"] = datetime.now(tz=timezone.utc).isoformat()
        final_points.append(point)
    
    # 写入 JSONL
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for point in final_points:
            json.dump(point, f, ensure_ascii=False)
            f.write("\n")
    
    print(f"成功同步 {len(final_points)} 个 {target_config['category']} 功能点 -> {output_path.relative_to(PROJECT_ROOT)}")
    return len(final_points)


def extract_all(output_dir: Path, config: Dict[str, Any] = None) -> int:
    """提取所有配置的类别"""
    if config is None:
        config = load_config()
    total = 0
    for cat in config.keys():
        if isinstance(config[cat], dict) and "patterns" in config[cat]:
            total += extract_test_points(cat, output_dir, config)
    return total


def main():
    parser = argparse.ArgumentParser(description="项目功能点自动化提取工具")
    parser.add_argument("--target", choices=["backend", "e2e", "integration", "frontend"], help="指定目标类别")
    parser.add_argument("--all", action="store_true", help="提取所有配置的类别")
    parser.add_argument("--output", help="自定义输出目录")
    
    args = parser.parse_args()
    config = load_config()
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    
    if args.all:
        total = 0
        for cat in config.keys():
            if isinstance(config[cat], dict) and "patterns" in config[cat]:
                total += extract_test_points(cat, output_dir, config)
        print(f"\n✅ 提取完成，共计 {total} 个功能点。")
    elif args.target:
        extract_test_points(args.target, output_dir, config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
