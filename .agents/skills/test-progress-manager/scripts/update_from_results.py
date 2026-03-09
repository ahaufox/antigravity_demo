import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

def parse_pytest_xml(xml_path: Path) -> List[Dict[str, Any]]:
    """解析 Pytest 生成的 JUnit XML 报告"""
    if not xml_path.exists():
        return []
    
    results = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for testcase in root.findall(".//testcase"):
            classname = testcase.get("classname", "")
            name = testcase.get("name", "")
            file_path = testcase.get("file", "")
            
            # 状态判定
            status = "通过"
            if testcase.find("failure") is not None:
                status = "失败"
            elif testcase.find("error") is not None:
                status = "失败"
            elif testcase.find("skipped") is not None:
                continue # 跳过不计入状态更新
                
            results.append({
                "function_name": name,
                "classname": classname,
                "file_path": file_path,
                "status": status
            })
    except Exception as e:
        print(f"Error parsing Pytest XML: {e}")
        
    return results

def parse_playwright_json(json_path: Path) -> List[Dict[str, Any]]:
    """解析 Playwright 生成的 JSON 报告"""
    if not json_path.exists():
        return []
        
    results = []
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for suite in data.get("suites", []):
            for file_suite in suite.get("suites", []): # 文件级
                file_path = file_suite.get("title", "")
                for test_suite in file_suite.get("suites", []): # Describe 级
                    for spec in test_suite.get("specs", []):
                        name = spec.get("title", "")
                        # 检查结果
                        results_list = spec.get("tests", [{}])[0].get("results", [])
                        status = "通过" if results_list and results_list[0].get("status") == "passed" else "失败"
                        
                        results.append({
                            "function_name": name,
                            "file_path": file_path,
                            "status": status
                        })
    except Exception as e:
        print(f"Error parsing Playwright JSON: {e}")
        
    return results

def update_jsonl_from_results(data_dir: Path, pytest_xml: Path = None, playwright_json: Path = None, pytest_xml_list: List[Path] = None):
    """根据测试报告更新 JSONL 数据"""
    from generate_test_data import load_jsonl_file, save_jsonl_file
    
    # 汇总结果集
    all_results = []
    
    # 处理单个 pytest_xml
    if pytest_xml:
        all_results.extend(parse_pytest_xml(pytest_xml))
        
    # 处理多个 pytest_xml (如来自不同的执行器)
    if pytest_xml_list:
        for xml_path in pytest_xml_list:
            all_results.extend(parse_pytest_xml(xml_path))
            
    if playwright_json:
        all_results.extend(parse_playwright_json(playwright_json))
        
    if not all_results:
        print("未发现有效的测试结果。")
        return

    # 分类处理每一个 JSONL
    for cat in ["backend", "frontend", "e2e", "integration"]:
        file_path = data_dir / f"{cat}.jsonl"
        if not file_path.exists():
            continue
            
        tests = load_jsonl_file(file_path)
        updated_count = 0
        
        for test in tests:
            # 策略：通过 function_name 或关联的 test_file_path 进行匹配
            match = None
            for res in all_results:
                # 1. 优先通过函数名匹配 (Pytest 常见)
                if res["function_name"] == test.get("function_name"):
                    match = res
                    break
                # 2. 备选：如果 JSONL 已经有关联脚本路径，检查报告中的文件名是否包含于此
                if test.get("test_file_path") and res["file_path"] in test["test_file_path"]:
                    match = res
                    break
            
            if match:
                test["status"] = match["status"]
                test["updated_at"] = datetime.now(tz=timezone.utc).isoformat()
                test["test_execution_time"] = test["updated_at"]
                # 同步 mtime 防止误判重测
                if match["status"] == "通过":
                    test["last_test_mtime"] = test.get("file_mtime")
                test["needs_retest"] = False
                updated_count += 1
                
        if updated_count > 0:
            save_jsonl_file(tests, file_path)
            print(f"✅ {cat}: 自动同步了 {updated_count} 项测试结果")
