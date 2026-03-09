#!/usr/bin/env python3
"""
测试进度数据生成与合并脚本 (并发优化版)

功能：
1. 以 file_path 为唯一标识合并测试数据
2. 使用 ThreadPoolExecutor 并发检查文件存在性和修改时间
3. 计算是否需要重新测试
4. 支持按类别拆分数据文件
"""
import json
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor


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
DEFAULT_DATA_DIR = TEST_RESULTS_DIR / "data"
TESTS_ROOT = PROJECT_ROOT / "src/core/tests"

# 全局缓存：文件名 -> 相对路径列表 (针对重名文件)
_TEST_FILE_CACHE: Dict[str, List[str]] = {}

def _init_test_cache():
    """初始化测试文件缓存"""
    global _TEST_FILE_CACHE
    if _TEST_FILE_CACHE:
        return
    
    if not TESTS_ROOT.exists():
        return

    for root, dirs, files in os.walk(TESTS_ROOT):
        for f in files:
            if f.endswith(".py") or f.endswith(".ts") or f.endswith(".tsx"):
                rel_path = os.path.relpath(os.path.join(root, f), PROJECT_ROOT)
                if f not in _TEST_FILE_CACHE:
                    _TEST_FILE_CACHE[f] = []
                _TEST_FILE_CACHE[f].append(rel_path)


def get_file_status(file_path: str, project_root: Path = PROJECT_ROOT) -> Dict[str, Any]:
    """获取单个文件的状态（存在性、修改时间）"""
    full_path = project_root / file_path
    exists = full_path.exists()
    mtime = None
    if exists:
        try:
            mtime_ts = full_path.stat().st_mtime
            mtime = datetime.fromtimestamp(mtime_ts, tz=timezone.utc).isoformat()
        except Exception:
            pass
    return {"file_exists": exists, "file_mtime": mtime}


def check_needs_retest(
    file_mtime: Optional[str], 
    last_test_mtime: Optional[str], 
    status: str
) -> bool:
    """判断是否需要重新测试的逻辑"""
    if not file_mtime or status != "通过":
        return False
    if not last_test_mtime:
        return True
    return file_mtime > last_test_mtime


def load_jsonl_file(jsonl_path: Path) -> List[Dict[str, Any]]:
    """加载 JSONL 数据文件"""
    tests = []
    if jsonl_path.exists():
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    tests.append(json.loads(line))
    return tests


def save_jsonl_file(tests: List[Dict[str, Any]], jsonl_path: Path):
    """保存数据到 JSONL"""
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for test in tests:
            json.dump(test, f, ensure_ascii=False)
            f.write("\n")


def add_new_fields(tests: List[Dict[str, Any]], project_root: Path = PROJECT_ROOT) -> List[Dict[str, Any]]:
    """使用线程池并发更新文件状态字段"""
    if not tests: return []

    def update_single_test(test):
        file_path = test.get("file_path", "")
        if not file_path: return test
        
        status_info = get_file_status(file_path, project_root)
        file_exists = status_info["file_exists"]
        file_mtime = status_info["file_mtime"]
        
        last_test_mtime = test.get("last_test_mtime")
        status = test.get("status", "未测试")
        
        test["file_exists"] = file_exists
        test["file_mtime"] = file_mtime
        if "last_test_mtime" not in test:
            test["last_test_mtime"] = None
            
        test["needs_retest"] = check_needs_retest(file_mtime, last_test_mtime, status)
        test["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
        return test

    # 使用并发提升数百个文件的 IO 检查速度
    with ThreadPoolExecutor(max_workers=10) as executor:
        return list(executor.map(update_single_test, tests))


def guess_test_file(file_path: str, function_name: str = "") -> str:
    """推断对应代码的测试文件路径 (评分制增强版)"""
    if not file_path: return ""
    
    _init_test_cache()
    
    # 1. 如果本身就在 tests 目录下，直接返回
    if "tests/" in file_path and (file_path.endswith(".py") or file_path.endswith(".ts") or file_path.endswith(".tsx")):
        return file_path

    mirror_rules = [
        {
            "src_prefix": "src/core/frontend/src/",
            "test_prefix": "src/core/frontend/src/__tests__/",
            "test_exts": [".test.tsx", ".test.ts", ".spec.tsx", ".spec.ts"],
            "test_file_prefix": ""
        },
        {
            "src_prefix": "src/core/frontend/src/",
            "test_prefix": "src/core/tests/unit/frontend/",
            "test_exts": [".test.tsx", ".test.ts"],
            "test_file_prefix": ""
        },
        {
            "src_prefix": "src/core/backend/",
            "test_prefix": "src/core/tests/unit/backend/",
            "test_exts": [".py"],
            "test_file_prefix": "test_"
        }
    ]

    # 1. 精确规则匹配
    for rule in mirror_rules:
        if file_path.startswith(rule["src_prefix"]):
            rel_path = file_path[len(rule["src_prefix"]):]
            dir_name = os.path.dirname(rel_path)
            base_name = os.path.basename(rel_path)
            pure_name = os.path.splitext(base_name)[0]
            
            for ext in rule.get("test_exts", [rule.get("test_ext", "")]):
                test_file_name = f"{rule['test_file_prefix']}{pure_name}{ext}"
                standard_test = os.path.join(rule["test_prefix"], dir_name, test_file_name)
                
                if (PROJECT_ROOT / standard_test).exists():
                    return standard_test

    # 3. 评分制搜索 (全局)
    best_score = -1
    best_match = ""
    
    base_name = os.path.basename(file_path)
    pure_name = os.path.splitext(base_name)[0]
    dir_parts = [p for p in os.path.dirname(file_path).split(os.sep) if p]
    
    # 核心关键词提取
    ignore_words = {"service", "router", "crud", "api", "utils", "business", "management", "gateway", "routers", "src", "core", "components", "hooks"}
    src_keywords = set(pure_name.split("_")) | set(dir_parts)
    src_keywords = {k for k in src_keywords if k.lower() and k.lower() not in ignore_words}
    
    for t_fname, t_paths in _TEST_FILE_CACHE.items():
        # 清理测试文件名以获取纯关键词
        t_pure_name = t_fname.replace("test_", "").replace("_test", "").replace(".test", "").replace(".spec", "")
        t_pure_name = os.path.splitext(t_pure_name)[0]
        t_keywords = set(t_pure_name.split("_")) | set(t_pure_name.split("."))
        
        # 基础分：文件名关键词重复度
        common_keys = src_keywords & t_keywords
        score = len(common_keys) * 10
        
        # 加分项：路径相似度
        for t_path in t_paths:
            current_score = score
            t_dir_parts = set(os.path.dirname(t_path).split(os.sep))
            path_matches = len(t_dir_parts & set(dir_parts))
            current_score += path_matches * 5
            
            # 加分项：精确匹配优先
            if t_pure_name == pure_name:
                current_score += 30
                
            # 加分项：函数名核实
            if function_name and check_function_in_test(PROJECT_ROOT / t_path, function_name):
                current_score += 50
            
            if current_score > best_score and current_score >= 15:
                best_score = current_score
                best_match = t_path
                
    return best_match

def check_function_in_test(test_file: Path, target_func: str) -> bool:
    """粗略扫描测试文件是否包含目标功能的测试"""
    if not test_file.exists():
        return False
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单字符串匹配：查找包含 test_xxx 或者 原函数名 的内容
            if f"test_{target_func}" in content or target_func in content:
                return True
    except Exception:
        pass
    return False

def sync_test_files(output_dir: Path, category: Optional[str] = None):
    """扫描现有测试文件，关联并更新 JSONL 状态"""
    cats = [category] if category else ["backend", "e2e", "integration", "frontend"]
    for cat in cats:
        jsonl_path = output_dir / f"{cat}.jsonl"
        if not jsonl_path.exists():
            continue
            
        tests = load_jsonl_file(jsonl_path)
        updated_count = 0
        for t in tests:
            file_path = t.get("file_path", "")
            if not file_path:
                continue

            # 优先规则：file_path 本身就是测试脚本（E2E / spec 文件）
            # 此时 test_file_path 直接等于 file_path，无需再猜测
            is_self_test = (
                "tests/" in file_path and (
                    file_path.endswith(".py")
                    or file_path.endswith(".ts")
                    or file_path.endswith(".tsx")
                )
            ) or ".spec." in file_path
            
            if is_self_test and not t.get("test_file_path"):
                t["test_file_path"] = file_path
                t["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
                updated_count += 1
                continue
                
            # 通用规则：通过 guess_test_file 推断测试文件路径
            test_file = guess_test_file(file_path, t.get("function_name", ""))
            if test_file:
                full_test_path = PROJECT_ROOT / test_file
                if full_test_path.exists():
                    t["test_file_path"] = test_file
                    t["file_exists"] = True
                    
                    # 检查是否包含具体的测试函数
                    is_tested = check_function_in_test(full_test_path, t.get("function_name", ""))
                    if is_tested and t.get("status") in ["未测试", "测试中"]:
                        t["status"] = "通过"
                        t["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
                        updated_count += 1
                        
        save_jsonl_file(tests, jsonl_path)
        print(f"✅ 已同步 {cat} 测试脚本关联，自动更新了 {updated_count} 条记录")



def generate_test_data(
    output_dir: Path, 
    category: Optional[str] = None, 
    merge: bool = True
):
    """生成或合并测试数据的核心入口"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cats = [category] if category else ["backend", "e2e", "integration", "frontend"]
    
    for cat in cats:
        output_path = output_dir / f"{cat}.jsonl"
        need_path = output_dir / f"need_{cat}.jsonl"
        
        existing_tests = load_jsonl_file(output_path)
        existing_by_key = {(t["file_path"], t["function_name"]): t for t in existing_tests}
        
        if merge and need_path.exists():
            # 1. 加载新提取的功能点
            new_points = load_jsonl_file(need_path)
            final_tests = []
            new_file_and_funcs = set()

            # 2. 以新提取的点为基准（同步最新的代码结构）
            for p in new_points:
                key = (p["file_path"], p["function_name"])
                new_file_and_funcs.add(key)
                
                if key in existing_by_key:
                    # 保留历史测试状态
                    ext = existing_by_key[key]
                    p.update({
                        "test_id": ext.get("point_id", ext.get("test_id")),
                        "status": ext.get("status", "未测试"),
                        "test_execution_time": ext.get("test_execution_time"),
                        "notes": ext.get("notes"),
                        "last_test_mtime": ext.get("last_test_mtime"),
                        "priority": ext.get("priority", p.get("priority", "P2"))
                    })
                else:
                    # 新增点
                    p["test_id"] = p.get("point_id")
                    p["status"] = "未测试"
                
                final_tests.append(p)

            # 3. 处理那些在代码中已删除但在数据中存在的记录（标记文件不存在）
            for key, ext in existing_by_key.items():
                if key not in new_file_and_funcs:
                    ext["file_exists"] = False
                    final_tests.append(ext)

            # 4. 并发更新文件状态与重测标记
            updated_tests = add_new_fields(final_tests)
            save_jsonl_file(updated_tests, output_path)
            print(f"✅ 已同步 {cat} 数据：现有 {len(existing_tests)} -> 最终 {len(updated_tests)}")
        
        elif merge and output_path.exists():
            # 仅刷新现有状态
            updated_tests = add_new_fields(existing_tests)
            save_jsonl_file(updated_tests, output_path)
            print(f"✅ 已并发同步 {cat} 状态，共 {len(updated_tests)} 条记录")
        
        else:
            if not output_path.exists():
                save_jsonl_file([], output_path)
                print(f"📦 已初始化 {cat} 数据容器")


def main():
    parser = argparse.ArgumentParser(description="测试进度数据同步与并发检查工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # Merge
    p_mrg = subparsers.add_parser("merge", help="合并并检查状态")
    p_mrg.add_argument("--output", default=str(DEFAULT_DATA_DIR), help="输出目录")
    p_mrg.add_argument("--category", help="指定细分类别")
    
    # Update Status (Atomic)
    p_upd = subparsers.add_parser("update", help="强制刷新文件状态")
    p_upd.add_argument("--input", default=str(DEFAULT_DATA_DIR))
    p_upd.add_argument("--category")
    
    # Sync Test Files
    p_sync = subparsers.add_parser("sync", help="关联已有测试文件并更新状态")
    p_sync.add_argument("--output", default=str(DEFAULT_DATA_DIR), help="输出目录")
    p_sync.add_argument("--category")
    
    args = parser.parse_args()
    
    if args.command == "merge" or args.command == "update":
        generate_test_data(
            Path(p_mrg.get_default("output") if args.command == "merge" else args.input),
            getattr(args, "category", None),
            merge=True
        )
    elif args.command == "sync":
        sync_test_files(
            Path(p_sync.get_default("output")),
            getattr(args, "category", None)
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
