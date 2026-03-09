const { Project, SyntaxKind } = require('ts-morph');
const { resolve } = require('path');

const project = new Project();

function extractInfo(filePath) {
    const sourceFile = project.addSourceFileAtPath(filePath);
    const points = [];

    // 1. 提取导出的函数
    sourceFile.getFunctions().forEach(func => {
        if (func.isExported()) {
            points.push({
                function_name: func.getName(),
                line_number: func.getStartLineNumber(),
                function_type: func.getName()?.[0] === func.getName()?.[0]?.toUpperCase() ? 'component' : 'function',
                description: func.getJsDocs()[0]?.getDescription().trim() || ""
            });
        }
    });

    // 2. 提取导出的类
    sourceFile.getClasses().forEach(cls => {
        if (cls.isExported()) {
            points.push({
                function_name: cls.getName(),
                line_number: cls.getStartLineNumber(),
                function_type: 'class',
                description: cls.getJsDocs()[0]?.getDescription().trim() || ""
            });
        }
    });

    // 3. 提取变量声明 (箭头函数组件/Hooks)
    sourceFile.getVariableStatements().forEach(stmt => {
        if (stmt.isExported()) {
            stmt.getDeclarations().forEach(decl => {
                const name = decl.getName();
                const initializer = decl.getInitializer();

                if (initializer && (initializer.getKind() === SyntaxKind.ArrowFunction || initializer.getKind() === SyntaxKind.FunctionExpression)) {
                    let typeLabel = 'function';
                    if (name.startsWith('use')) {
                        typeLabel = 'hook';
                    } else if (name[0] === name[0].toUpperCase()) {
                        typeLabel = 'component';
                    }

                    points.push({
                        function_name: name,
                        line_number: decl.getStartLineNumber(),
                        function_type: typeLabel,
                        description: stmt.getJsDocs()[0]?.getDescription().trim() || ""
                    });
                }
            });
        }
    });

    return points;
}

const targetPath = process.argv[2];
if (!targetPath) {
    console.error("Usage: node ts-parser-helper.js <file-path>");
    process.exit(1);
}

try {
    const results = extractInfo(resolve(targetPath));
    process.stdout.write(JSON.stringify(results, null, 2));
} catch (e) {
    console.error(`Error parsing ${targetPath}: ${e.message}`);
    process.exit(1);
}
