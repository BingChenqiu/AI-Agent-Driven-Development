#!/usr/bin/env python3
"""
ADD Transformer - Context Generator
生成 .ai-context.md 和项目级知识库
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from analyze_project import analyze_project, count_lines, get_file_type


def generate_module_context(module_path: Path, analysis: dict = None) -> str:
    """生成模块级上下文文件"""
    
    # 分析模块
    code_extensions = {'.ts', '.tsx', '.js', '.jsx', '.py', '.rs', '.go', '.java', '.kt', '.swift', '.rb', '.php', '.cs', '.cpp', '.c'}
    
    files_info = []
    total_lines = 0
    
    for dirpath, dirnames, filenames in os.walk(module_path):
        excluded_dirs = {'node_modules', '.git', '__pycache__', 'dist', 'build', 'vendor', '.venv', 'venv', 'test', 'tests', '__tests__'}
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        
        for f in filenames:
            file_path = Path(dirpath) / f
            ext = file_path.suffix.lower()
            
            if ext in code_extensions:
                lines = count_lines(file_path)
                total_lines += lines
                files_info.append({
                    'name': f,
                    'path': str(file_path.relative_to(module_path)),
                    'type': get_file_type(file_path),
                    'lines': lines,
                })
    
    # 推断模块职责（基于文件名和目录名）
    module_name = module_path.name
    inferred_purpose = infer_module_purpose(module_name, files_info)
    
    # 生成上下文
    content = f"""# {module_name} 模块上下文

> generated_by: add-transformer
> verified_at: {datetime.now().strftime('%Y-%m-%d')}
> provenance: code-analyzed

## 职责

{inferred_purpose['responsibilities']}

## 核心文件

| 文件 | 类型 | 行数 |
|------|------|------|
"""
    
    for f in sorted(files_info, key=lambda x: x['lines'], reverse=True)[:10]:
        content += f"| `{f['path']}` | {f['type']} | {f['lines']} |\n"
    
    content += f"""
## 设计决策

{inferred_purpose['decisions']}

## 约束条件

{inferred_purpose['constraints']}

## Evidence Gaps

- [ ] 模块间的依赖关系需要人工确认
- [ ] 核心业务逻辑需要补充详细说明
"""
    
    return content


def infer_module_purpose(module_name: str, files_info: list) -> dict:
    """推断模块职责"""
    
    # 基于模块名的启发式推断
    name_lower = module_name.lower()
    
    purpose_map = {
        'user': {'responsibilities': '- 用户相关业务逻辑\n- 用户认证与授权', 'decisions': '- [待补充]', 'constraints': '- [待补充]'},
        'auth': {'responsibilities': '- 认证与授权\n- 会话管理', 'decisions': '- [待补充]', 'constraints': '- 禁止在日志中打印敏感信息'},
        'api': {'responsibilities': '- API 接口定义\n- 请求处理', 'decisions': '- [待补充]', 'constraints': '- 所有输入必须验证'},
        'db': {'responsibilities': '- 数据库操作\n- 数据访问层', 'decisions': '- [待补充]', 'constraints': '- 所有查询必须参数化'},
        'util': {'responsibilities': '- 通用工具函数\n- 辅助方法', 'decisions': '- [待补充]', 'constraints': '- 保持无状态'},
        'core': {'responsibilities': '- 核心业务逻辑\n- 主要功能实现', 'decisions': '- [待补充]', 'constraints': '- [待补充]'},
        'service': {'responsibilities': '- 业务服务层\n- 业务逻辑封装', 'decisions': '- [待补充]', 'constraints': '- [待补充]'},
        'handler': {'responsibilities': '- 请求处理器\n- 控制器逻辑', 'decisions': '- [待补充]', 'constraints': '- [待补充]'},
        'model': {'responsibilities': '- 数据模型定义\n- 实体类', 'decisions': '- [待补充]', 'constraints': '- [待补充]'},
    }
    
    # 查找匹配的模式
    for key, value in purpose_map.items():
        if key in name_lower:
            return value
    
    # 默认模板
    return {
        'responsibilities': f'- {module_name} 相关业务逻辑\n- [待补充详细职责]',
        'decisions': '- [待补充设计决策]',
        'constraints': '- [待补充约束条件]',
    }


def generate_project_index(project_path: Path, analysis: dict) -> str:
    """生成项目级 INDEX.md"""
    
    files = analysis.get('files', {})
    stats = files.get('file_stats', {})
    modules = analysis.get('modules', {})
    ai_context = analysis.get('ai_context', {})
    
    # 获取入口点
    entry_points = modules.get('entry_points', [])
    entry_info = ""
    if entry_points:
        entry_info = f"- 入口：`{entry_points[0]}`\n"
    else:
        entry_info = "- 入口：[待确认]\n"
    
    # 获取主要模块
    module_list = modules.get('modules', [])
    modules_info = ""
    if module_list:
        modules_info = "- 主要模块：" + " / ".join([m['name'] for m in module_list[:5]]) + "\n"
    else:
        modules_info = "- 主要模块：[待识别]\n"
    
    content = f"""# {project_path.name} - AI 快速上下文

> generated_by: add-transformer
> verified_at: {datetime.now().strftime('%Y-%m-%d')}
> provenance: code-analyzed

## 核心架构

{entry_info}{modules_info}

## 关键约定

- [待补充：API 响应格式]
- [待补充：错误处理方式]
- [待补充：命名约定]

## 代码统计

- 总文件数：{stats.get('total_files', 0)}
- 总行数：{stats.get('total_lines', 0):,}
- 平均文件行数：{stats.get('avg_lines', 0):.1f}

## Evidence Gaps

- [ ] 系统边界需要人工确认
- [ ] 模块间依赖关系需要梳理
- [ ] 核心业务流程需要补充文档

## 快速导航

"""
    
    # 添加目录结构概览
    content += "```\n"
    content += f"{project_path.name}/\n"
    
    # 遍历第一级目录
    for item in sorted(project_path.iterdir()):
        if item.is_dir() and not item.name.startswith('.') and item.name not in {'node_modules', '__pycache__', 'dist', 'build'}:
            content += f"├── {item.name}/\n"
    
    content += "```\n"
    
    return content


def generate_systems_doc(project_path: Path, analysis: dict) -> str:
    """生成 systems.md"""
    
    modules = analysis.get('modules', {})
    entry_points = modules.get('entry_points', [])
    module_list = modules.get('modules', [])
    
    content = f"""# 系统边界

> generated_by: add-transformer
> verified_at: {datetime.now().strftime('%Y-%m-%d')}
> provenance: code-analyzed

## 入口点

"""
    
    if entry_points:
        for ep in entry_points:
            content += f"- `{ep}`\n"
    else:
        content += "- [待识别]\n"
    
    content += """
## 模块划分

| 模块名 | 路径 | 状态 |
|--------|------|------|
"""
    
    for m in module_list:
        status = "✅ 已识别"
        content += f"| {m['name']} | `{m['path']}` | {status} |\n"
    
    content += """
## 系统边界说明

[待补充：各模块的职责边界和交互关系]
"""
    
    return content


def generate_dependencies_doc(project_path: Path, analysis: dict) -> str:
    """生成 dependencies.md"""
    
    modules = analysis.get('modules', {})
    module_list = modules.get('modules', [])
    
    content = f"""# 依赖关系图

> generated_by: add-transformer
> verified_at: {datetime.now().strftime('%Y-%m-%d')}
> provenance: code-analyzed

## 模块依赖

```mermaid
graph TD
"""
    
    # 添加节点
    for m in module_list[:10]:
        content += f"    {m['name']}[{m['name']}]\n"
    
    content += """```

## 依赖说明

[待补充：模块间的依赖关系需要通过 import 分析确认]

## Evidence Gaps

- [ ] 需要通过 AST 分析确认精确的依赖关系
- [ ] 需要识别循环依赖
"""
    
    return content


def generate_concept_model(project_path: Path, analysis: dict) -> str:
    """生成 concept_model.json"""
    
    modules = analysis.get('modules', {})
    files = analysis.get('files', {})
    
    model = {
        "project": project_path.name,
        "generated_at": datetime.now().isoformat(),
        "provenance": "code-analyzed",
        "statistics": {
            "total_files": files.get('file_stats', {}).get('total_files', 0),
            "total_lines": files.get('file_stats', {}).get('total_lines', 0),
        },
        "modules": modules.get('modules', []),
        "entry_points": modules.get('entry_points', []),
        "evidence_gaps": [
            "Module dependencies require AST analysis",
            "Core business logic needs manual documentation",
        ]
    }
    
    return json.dumps(model, indent=2, ensure_ascii=False)


def create_knowledge_base(project_path: Path, analysis: dict, output_path: Path = None):
    """创建完整的知识库目录结构"""
    
    if output_path is None:
        output_path = project_path / '.ai-context'
    else:
        output_path = Path(output_path)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成各个文件
    files_to_create = {
        'INDEX.md': generate_project_index(project_path, analysis),
        'systems.md': generate_systems_doc(project_path, analysis),
        'dependencies.md': generate_dependencies_doc(project_path, analysis),
        'concept_model.json': generate_concept_model(project_path, analysis),
    }
    
    created_files = []
    for filename, content in files_to_create.items():
        file_path = output_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        created_files.append(str(file_path))
        print(f"  ✅ 创建: {file_path.relative_to(project_path)}")
    
    return created_files


def main():
    parser = argparse.ArgumentParser(description='ADD 上下文生成器')
    parser.add_argument('path', help='模块或项目路径')
    parser.add_argument('--type', '-t', choices=['module', 'project'], default='module',
                        help='生成类型：module (模块级) 或 project (项目级)')
    parser.add_argument('--output', '-o', help='输出路径')
    
    args = parser.parse_args()
    
    target_path = Path(args.path).resolve()
    
    if not target_path.exists():
        print(f"错误: 路径不存在 {target_path}")
        return
    
    if args.type == 'module':
        # 生成模块级上下文
        content = generate_module_context(target_path)
        
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = target_path / '.ai-context.md'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 生成模块上下文: {output_path}")
    
    elif args.type == 'project':
        # 生成项目级知识库
        print(f"分析项目: {target_path}")
        analysis = analyze_project(target_path)
        
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = target_path / '.ai-context'
        
        print(f"创建知识库: {output_path}")
        created = create_knowledge_base(target_path, analysis, output_path)
        print(f"\n✅ 知识库创建完成，共 {len(created)} 个文件")


if __name__ == '__main__':
    main()