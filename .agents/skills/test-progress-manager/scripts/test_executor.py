import subprocess
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

def run_single_test_file(file_rel_path: str, data_dir: Path, project_root: Path) -> Dict[str, Any]:
    """执行单个测试文件并返回结果摘要"""
    full_path = project_root / file_rel_path
    if not full_path.exists():
        return {"status": "error", "message": f"测试文件不存在: {file_rel_path}"}

    print(f"▶️ 正在执行单文件测试: {file_rel_path}")
    
    # 确定测试类型
    is_pytest = file_rel_path.endswith(".py")
    is_playwright = ".spec." in file_rel_path
    is_vitest = ".test.ts" in file_rel_path or ".test.tsx" in file_rel_path

    # 确定报告存储根目录（改用 /tmp 以防止 Vitest 清理核心数据目录）
    temp_report_dir = Path("/tmp/mindseed_test_reports")
    temp_report_dir.mkdir(parents=True, exist_ok=True)

    success = False
    try:
        if is_pytest:
            xml_path = temp_report_dir / f"single_pytest_{int(time.time())}.xml"
            cmd = ["pytest", str(full_path), f"--junitxml={str(xml_path)}"]
            result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
            # 同步结果
            from update_from_results import update_jsonl_from_results
            update_jsonl_from_results(data_dir, pytest_xml=xml_path)
            success = result.returncode == 0
        elif is_playwright:
            json_path = temp_report_dir / f"single_pw_{int(time.time())}.json"
            # 必须指定配置文件，否则 Playwright 会默认清理执行目录下的 test-results 文件夹
            config_path = "tests/e2e/playwright.config.ts"
            cmd = ["npx", "playwright", "test", str(full_path), "--reporter=json", f"--config={config_path}"]
            with open(json_path, "w") as f:
                result = subprocess.run(cmd, cwd=project_root / "src/core", stdout=f, stderr=subprocess.PIPE)
            # 同步结果
            from update_from_results import update_jsonl_from_results
            update_jsonl_from_results(data_dir, playwright_json=json_path)
            success = result.returncode == 0
        elif is_vitest:
            xml_path = temp_report_dir / f"single_vitest_{int(time.time())}.xml"
            # Vitest 在 frontend 目录下运行
            frontend_dir = project_root / "src/core/frontend"
            rel_to_frontend = full_path.relative_to(frontend_dir)
            cmd = ["npx", "vitest", "run", str(rel_to_frontend), "--reporter=junit", "--outputFile", str(xml_path)]
            result = subprocess.run(cmd, cwd=frontend_dir, capture_output=True, text=True)
            # 同步结果 (Vitest 的 JUnit XML 与 Pytest 兼容)
            from update_from_results import update_jsonl_from_results
            update_jsonl_from_results(data_dir, pytest_xml=xml_path)
            success = result.returncode == 0
        else:
            return {"status": "error", "message": "不支持的测试文件类型"}
            
        return {"status": "success", "pass": success}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_smart_tests(data_dir: Path, project_root: Path, force_all: bool = False):
    """根据 JSONL 状态执行按需测试"""
    from generate_test_data import load_jsonl_file
    
    all_test_files = set()
    categories = ["backend", "frontend", "e2e", "integration"]
    
    # 1. 收集需要测试的文件路径
    for cat in categories:
        jsonl_path = data_dir / f"{cat}.jsonl"
        if not jsonl_path.exists():
            continue
            
        tests = load_jsonl_file(jsonl_path)
        for t in tests:
            if force_all or t.get("needs_retest") or t.get("status") == "未测试":
                path = t.get("test_file_path")
                if path and os.path.exists(os.path.join(project_root, path)):
                    all_test_files.add(path)
    
    if not all_test_files:
        print("💡 当前无建议测试项 (所有功能点均已通过且代码未变动)。使用 --all 强制全量运行。")
        return

    print(f"🚀 准备执行 {len(all_test_files)} 个关联测试脚本...")
    
    # 2. 分类执行
    pytest_files = [f for f in all_test_files if f.endswith(".py")]
    playwright_files = [f for f in all_test_files if ".spec." in f]
    vitest_files = [f for f in all_test_files if ".test.ts" in f or ".test.tsx" in f]

    # 报告存储目录
    temp_report_dir = Path("/tmp/mindseed_test_reports")
    temp_report_dir.mkdir(parents=True, exist_ok=True)

    # 执行 Pytest
    if pytest_files:
        print(f"▶️ 正在运行 Pytest ({len(pytest_files)} 个文件)...")
        report_path = temp_report_dir / "pytest_report.xml"
        # 使用 importlib 模式防止 conftest.py 冲突
        cmd = ["pytest", "--import-mode=importlib"] + pytest_files + [f"--junitxml={report_path}"]
        subprocess.run(cmd, cwd=project_root)
        
    # 执行 Playwright
    if playwright_files:
        print(f"▶️ 正在运行 Playwright ({len(playwright_files)} 个文件)...")
        report_path = temp_report_dir / "playwright_report.json"
        # 必须指定配置文件，否则 Playwright 会默认清理执行目录下的 test-results 文件夹
        config_path = "tests/e2e/playwright.config.ts"
        cmd = ["npx", "playwright", "test"] + playwright_files + ["--reporter=json", f"--config={config_path}"]
        with open(report_path, "w") as f:
            subprocess.run(cmd, cwd=project_root / "src/core", stdout=f)

    # 执行 Vitest
    if vitest_files:
        print(f"▶️ 正在运行 Vitest ({len(vitest_files)} 个文件)...")
        report_path = temp_report_dir / "vitest_report.xml"
        # 运行目录设为 src/core 以匹配 vitest.config.ts 位置
        vitest_cwd = project_root / "src/core"
        # 转换为相对于 src/core 的路径
        rel_vitest_files = []
        for f in vitest_files:
            try:
                rel_vitest_files.append(str((project_root / f).relative_to(vitest_cwd)))
            except ValueError:
                # 如果不在 src/core 下（例如在 src/core/tests/unit/frontend），也需要正确处理
                # vitest_files 存储的是相对于项目根目录的路径
                rel_vitest_files.append(f)
                
        cmd = ["npx", "vitest", "run"] + rel_vitest_files + ["--reporter=junit", "--outputFile", str(report_path)]
        subprocess.run(cmd, cwd=vitest_cwd)

    # 3. 自动同步结果
    print("\n🔄 正在自动同步测试结果至进度管理系统...")
    from update_from_results import update_jsonl_from_results
    
    # 确保收集所有生成的报告
    xml_reports = []
    pytest_xml = None
    vitest_xml = None
    playwright_json = None

    temp_report_dir = Path("/tmp/mindseed_test_reports")
    
    if pytest_files:
        pytest_xml = temp_report_dir / "pytest_report.xml"
        if pytest_xml.exists():
            xml_reports.append(pytest_xml)
    if vitest_files:
        vitest_xml = temp_report_dir / "vitest_report.xml"
        if vitest_xml.exists():
            xml_reports.append(vitest_xml)
    
    playwright_json = temp_report_dir / "playwright_report.json"
    if not playwright_json.exists():
        playwright_json = None
        
    update_jsonl_from_results(
        data_dir, 
        pytest_xml=pytest_xml if not xml_reports else None, # 兼容单参数
        pytest_xml_list=xml_reports if xml_reports else None,
        playwright_json=playwright_json
    )
