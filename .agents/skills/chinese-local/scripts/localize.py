import os
import re
import sys
import argparse

# --- 配置 (Configuration) ---
TARGET_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript-react',
    '.jsx': 'javascript-react',
    '.css': 'css',
    '.scss': 'scss',
    '.html': 'html',
    '.md': 'markdown'
}

# 模式定义 (Patterns)
PATTERNS = {
    'python_comment': r'#.*$',
    'python_docstring': r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')',
    'c_style_comment': r'//.*$',
    'multiline_comment': r'/\*[\s\S]*?\*/',
    'html_comment': r'<!--[\s\S]*?-->'
}

def is_sql(text):
    """判断内容是否为 SQL 语句"""
    # 基础 SQL 关键词
    sql_keywords = r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH|FROM|WHERE|JOIN|UNION|VALUES|SET|INTO|TABLE)\b'
    matches = re.findall(sql_keywords, text, re.IGNORECASE)
    
    # 如果包含多个 SQL 关键词，很可能是 SQL
    if len(set(m.upper() for m in matches)) >= 2:
        return True
    
    # 检查特定的 SQL 模式
    patterns = [
        r'SELECT\s+.*\s+FROM',
        r'INSERT\s+INTO\s+.*\s+VALUES',
        r'UPDATE\s+.*\s+SET',
        r'DELETE\s+FROM',
        r'CREATE\s+TABLE',
        r'ALTER\s+TABLE',
        r'WHERE\s+.*\s*(=|LIKE|IN|IS)',
        r'\$\d+', # PostgreSQL 占位符 $1, $2
        r':\w+',  # 参数化查询 :param
        r'RETURNING\s+\*',
        r'ON\s+CONFLICT',
        r'GROUP\s+BY',
        r'ORDER\s+BY'
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            return True
            
    return False

def is_code_like(text):
    """判断内容是否看起来像代码而非自然语言描述"""
    # 如果是明显的 Python 属性访问或函数调用
    if re.search(r'\w+\.\w+\(', text):
        return True
    # 如果包含大量代码常用符号且没有空格分隔的单词
    if re.search(r'[\[\]\{\}\(\)_=<>]', text) and not re.search(r'\b\w+\b\s+\b\w+\b', text):
        return True
    return False

def is_english(text, min_length=3):
    """判断内容是否包含足够比例的英文字符（简单的启发式方法）"""
    # 如果是 SQL 或看起来像代码，直接返回 False (排除)
    if is_sql(text) or is_code_like(text):
        return False
    # 移除符号和数字
    clean_text = re.sub(r'[^a-zA-Z\s]', '', text).strip()
    if len(clean_text) < min_length:
        return False
    # 判断是否包含中文字符
    if re.search(r'[\u4e00-\u9fff]', text):
        return False
    return True

def analyze_file(file_path, min_length=3):
    ext = os.path.splitext(file_path)[1]
    if ext not in TARGET_EXTENSIONS:
        return []

    lang = TARGET_EXTENSIONS[ext]
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    results = []

    # 按行处理，或者全文匹配文档字符串
    if lang == 'python':
        # 1. 文档字符串
        for match in re.finditer(PATTERNS['python_docstring'], content):
            text = match.group(0)
            if is_english(text, min_length):
                line_no = content.count('\n', 0, match.start()) + 1
                results.append({'type': 'docstring', 'line': line_no, 'content': text.strip()})
        
        # 2. 注释 (排除在字符串内的 #)
        for i, line in enumerate(content.splitlines(), 1):
            if '#' in line:
                # 简单处理：如果 # 不是在引号内
                # (更严谨的做法是解析 AST，这里使用简单正则)
                comment_match = re.search(PATTERNS['python_comment'], line)
                if comment_match:
                    text = comment_match.group(0)
                    if is_english(text, min_length):
                        results.append({'type': 'comment', 'line': i, 'content': text.strip()})

    elif lang in ['javascript', 'typescript', 'typescript-react', 'javascript-react', 'css', 'scss']:
        # 1. 多行注释
        for match in re.finditer(PATTERNS['multiline_comment'], content):
            text = match.group(0)
            if is_english(text, min_length):
                line_no = content.count('\n', 0, match.start()) + 1
                results.append({'type': 'multiline-comment', 'line': line_no, 'content': text.strip()})
        
        # 2. 单行注释
        for i, line in enumerate(content.splitlines(), 1):
            if '//' in line:
                comment_match = re.search(PATTERNS['c_style_comment'], line)
                if comment_match:
                    text = comment_match.group(0)
                    if is_english(text, min_length):
                        results.append({'type': 'comment', 'line': i, 'content': text.strip()})

    elif lang in ['html', 'markdown']:
        for match in re.finditer(PATTERNS['html_comment'], content):
            text = match.group(0)
            if is_english(text, min_length):
                line_no = content.count('\n', 0, match.start()) + 1
                results.append({'type': 'html-comment', 'line': line_no, 'content': text.strip()})

    return results

def main():
    parser = argparse.ArgumentParser(description="扫描代码中的英文注释以进行中文本地化。")
    parser.add_argument("target", help="文件或目录路径")
    parser.add_argument("--min-length", "-l", type=int, default=50, help="最小英文字符长度 (默认: 50)")
    args = parser.parse_args()

    if os.path.isfile(args.target):
        targets = [args.target]
    elif os.path.isdir(args.target):
        targets = []
        for root, dirs, files in os.walk(args.target):
            # 排除常见目录
            if any(p in root for p in ['.git', '__pycache__', 'node_modules', '.next']):
                continue
            for f in files:
                targets.append(os.path.join(root, f))
    else:
        print(f"错误: 找不到目标 {args.target}")
        sys.exit(1)

    print(f"🔍 正在扫描: {args.target} (最小长度: {args.min_length})")
    total_found = 0
    for target in targets:
        findings = analyze_file(target, args.min_length)
        if findings:
            print(f"\n📄 文件: {target}")
            for item in findings:
                print(f"  [{item['line']:>4}] ({item['type']}): {item['content']}")
                total_found += 1

    print(f"\n✨ 扫描完成。共发现 {total_found} 处待处理的英文内容。")

if __name__ == "__main__":
    main()
