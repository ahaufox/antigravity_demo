#!/usr/bin/env python3
"""
测试进度报告生成脚本

功能：
1. 从 JSONL 文件加载测试数据
2. 计算统计信息
3. 生成 HTML 报告
"""
import json
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from datetime import datetime, timezone


# ==========================================
# 路径定义 (Step-by-step Path Definitions)
# ==========================================
current_file_path = os.path.abspath(__file__)
scripts_dir = os.path.dirname(current_file_path)               # .trae/skills/test-progress-manager/scripts
skill_dir = os.path.dirname(scripts_dir)                      # .trae/skills/test-progress-manager
skills_dir = os.path.dirname(skill_dir)                       # .trae/skills
trae_dir = os.path.dirname(skills_dir)                        # .trae
project_root = os.path.dirname(trae_dir)                      # mindseed (项目根目录)

PROJECT_ROOT = Path(project_root)
TEST_RESULTS_DIR = PROJECT_ROOT / "src/core/tests/test-results"
DEFAULT_DATA_DIR = TEST_RESULTS_DIR / "data"
DEFAULT_OUTPUT_DIR = TEST_RESULTS_DIR / "reports"
DEFAULT_TEMPLATES_DIR = TEST_RESULTS_DIR / "templates"
DEFAULT_ASSETS_PATH = "../assets"


def load_jsonl_file(jsonl_path: Path) -> list[dict]:
    """从 JSONL 文件加载测试数据"""
    tests = []
    if jsonl_path.exists():
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    tests.append(json.loads(line))
    return tests


def load_all_data(data_dir: Path, category: str | None = None) -> list[dict]:
    """加载所有或指定类别的测试数据"""
    all_tests = []
    
    if category:
        files = [f"{category}.jsonl"]
    else:
        files = ["backend.jsonl", "e2e.jsonl", "integration.jsonl", "frontend.jsonl"]
    
    for filename in files:
        file_path = data_dir / filename
        if file_path.exists():
            tests = load_jsonl_file(file_path)
            all_tests.extend(tests)
    
    return all_tests


def calculate_statistics(tests: list[dict]) -> dict:
    """计算测试统计信息"""
    total_tests = len(tests)
    passed_tests = sum(1 for t in tests if t.get("status") == "通过")
    failed_tests = sum(1 for t in tests if t.get("status") == "失败")
    not_tested_tests = sum(1 for t in tests if t.get("status") == "未测试")
    testing_tests = sum(1 for t in tests if t.get("status") == "测试中")
    blocked_tests = sum(1 for t in tests if t.get("status") == "阻塞")
    
    file_exists_count = sum(1 for t in tests if t.get("file_exists") == True)
    file_not_exists_count = sum(1 for t in tests if t.get("file_exists") == False)
    needs_retest_count = sum(1 for t in tests if t.get("needs_retest") == True)
    test_file_associated_count = sum(1 for t in tests if t.get("test_file_path"))
    
    completion_rate = 0
    if total_tests > 0:
        completion_rate = round((passed_tests / total_tests) * 100, 2)
    
    priority_counts = {
        "P0": {"total": 0, "passed": 0, "completion_rate": 0},
        "P1": {"total": 0, "passed": 0, "completion_rate": 0},
        "P2": {"total": 0, "passed": 0, "completion_rate": 0},
    }
    
    for test in tests:
        priority = test.get("priority", "P2")
        if priority in priority_counts:
            priority_counts[priority]["total"] += 1
            if test.get("status") == "通过":
                priority_counts[priority]["passed"] += 1
    
    for priority in priority_counts:
        if priority_counts[priority]["total"] > 0:
            priority_counts[priority]["completion_rate"] = round(
                (priority_counts[priority]["passed"] / priority_counts[priority]["total"]) * 100, 2
            )
    
    category_counts = {}
    for test in tests:
        cat = test.get("category", "未分类")
        if cat not in category_counts:
            category_counts[cat] = {"total": 0, "passed": 0}
        category_counts[cat]["total"] += 1
        if test.get("status") == "通过":
            category_counts[cat]["passed"] += 1
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "not_tested_tests": not_tested_tests,
        "testing_tests": testing_tests,
        "blocked_tests": blocked_tests,
        "completion_rate": completion_rate,
        "priority_counts": priority_counts,
        "category_counts": category_counts,
        "file_exists_count": file_exists_count,
        "file_not_exists_count": file_not_exists_count,
        "needs_retest_count": needs_retest_count,
        "test_file_associated_count": test_file_associated_count,
    }


import shutil

def load_template(template_name: str, templates_dir: Path):
    """不再需要加载 Jinja，保留接口以防报错，或直接忽略"""
    pass


def generate_html(
    tests: list[dict], 
    stats: dict, 
    output_dir: Path, 
    templates_dir: Path, 
    assets_path: str,
    category: str | None = None
) -> Path | None:
    """生成 HTML 测试进度报告（现在是纯静态单页应用）"""
    try:
        source_path = templates_dir / "test_progress_template.html"
        output_filename = "index.html"
        output_path = output_dir / output_filename
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 直接复制静态模板
        shutil.copy2(source_path, output_path)
        
        print(f"成功生成静态测试进度报告: {output_path}")
        print(f"请在浏览器中直接打开该文件即可查看所有类别的测试进度。")
        return output_path
    except Exception as e:
        import traceback
        print(f"错误：生成静态 HTML 反馈失败: {e}")
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description="生成测试进度管理 HTML 报告")
    
    parser.add_argument(
        "--input",
        default=str(DEFAULT_DATA_DIR),
        help="测试数据目录路径",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="HTML 报告输出目录",
    )
    parser.add_argument(
        "--templates",
        default=str(DEFAULT_TEMPLATES_DIR),
        help="模板目录路径",
    )
    parser.add_argument(
        "--assets",
        default=DEFAULT_ASSETS_PATH,
        help="静态资源相对路径",
    )
    parser.add_argument(
        "--category",
        choices=["backend", "e2e", "integration", "frontend"],
        help="指定测试类别",
    )
    
    args = parser.parse_args()
    
    data_dir = Path(args.input)
    output_dir = Path(args.output)
    templates_dir = Path(args.templates)
    
    tests = load_all_data(data_dir, args.category)
    if not tests:
        print("警告：没有加载到测试数据")
        return
    
    stats = calculate_statistics(tests)
    
    generate_html(
        tests, stats, output_dir, templates_dir, args.assets, args.category
    )
    
    print(f"\n统计信息:")
    print(f"  总测试数: {stats['total_tests']}")
    print(f"  通过: {stats['passed_tests']}")
    print(f"  失败: {stats['failed_tests']}")
    print(f"  未测试: {stats['not_tested_tests']}")
    print(f"  完成率: {stats['completion_rate']}%")
    print(f"  文件存在: {stats['file_exists_count']}")
    print(f"  文件不存在: {stats['file_not_exists_count']}")
    print(f"  需要重测: {stats['needs_retest_count']}")
    print(f"  关联测试脚本: {stats['test_file_associated_count']}")


if __name__ == "__main__":
    main()
