#!/usr/bin/env python3
"""
ADD Transformer - Project Analyzer
分析项目结构，识别需要改造的地方
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from collections import defaultdict


def count_lines(file_path: Path) -> int:
    """统计文件行数"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0


def get_file_type(file_path: Path) -> str:
    """获取文件类型"""
    suffix = file_path.suffix.lower()
    type_map = {
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.py': 'Python',
        '.rs': 'Rust',
        '.go': 'Go',
        '.java': 'Java',
        '.kt': 'Kotlin',
        '.swift': 'Swift',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.cs': 'C#',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'Header',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.sql': 'SQL',
    }
    return type_map.get(suffix, suffix.upper() if suffix else 'Unknown')


def analyze_directory_structure(root: Path, max_depth: int = 10) -> dict:
    """分析目录结构"""
    result = {
        'max_depth': 0,
        'deep_paths': [],
        'file_count_by_dir': defaultdict(int),
        'dirs': [],
    }
    
    for dirpath, dirnames, filenames in os.walk(root):
        rel_path = Path(dirpath).relative_to(root)
        depth = len(rel_path.parts) - 1 if rel_path.parts != ('.',) else 0
        
        if depth > result['max_depth']:
            result['max_depth'] = depth
        
        if depth > 3:
            result['deep_paths'].append(str(rel_path))
        
        # 排除常见的不重要目录
        excluded_dirs = {'node_modules', '.git', '__pycache__', 'dist', 'build', 'vendor', '.venv', 'venv'}
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        
        file_count = len([f for f in filenames if not f.startswith('.')])
        result['file_count_by_dir'][str(rel_path)] = file_count
        result['dirs'].append({
            'path': str(rel_path),
            'depth': depth,
            'file_count': file_count,
        })
    
    return result


def analyze_file_sizes(root: Path, thresholds: dict = None) -> dict:
    """分析文件大小"""
    if thresholds is None:
        thresholds = {
            'warning': 500,  # 警告阈值
            'critical': 1000,  # 严重阈值
        }
    
    result = {
        'large_files': [],
        'file_stats': {
            'total_files': 0,
            'total_lines': 0,
            'avg_lines': 0,
            'by_type': defaultdict(lambda: {'count': 0, 'lines': 0}),
        },
        'thresholds': thresholds,
    }
    
    code_extensions = {'.ts', '.tsx', '.js', '.jsx', '.py', '.rs', '.go', '.java', '.kt', '.swift', '.rb', '.php', '.cs', '.cpp', '.c'}
    
    for dirpath, dirnames, filenames in os.walk(root):
        excluded_dirs = {'node_modules', '.git', '__pycache__', 'dist', 'build', 'vendor', '.venv', 'venv', 'test', 'tests', '__tests__'}
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        
        for filename in filenames:
            file_path = Path(dirpath) / filename
            ext = file_path.suffix.lower()
            
            if ext not in code_extensions:
                continue
            
            lines = count_lines(file_path)
            rel_path = file_path.relative_to(root)
            file_type = get_file_type(file_path)
            
            result['file_stats']['total_files'] += 1
            result['file_stats']['total_lines'] += lines
            result['file_stats']['by_type'][file_type]['count'] += 1
            result['file_stats']['by_type'][file_type]['lines'] += lines
            
            if lines > thresholds['warning']:
                severity = 'critical' if lines > thresholds['critical'] else 'warning'
                result['large_files'].append({
                    'path': str(rel_path),
                    'lines': lines,
                    'type': file_type,
                    'severity': severity,
                })
    
    if result['file_stats']['total_files'] > 0:
        result['file_stats']['avg_lines'] = result['file_stats']['total_lines'] / result['file_stats']['total_files']
    
    result['large_files'].sort(key=lambda x: x['lines'], reverse=True)
    return result


def analyze_git_hotspots(root: Path, days: int = 30, top_n: int = 20) -> dict:
    """分析 Git 热点文件"""
    result = {
        'hotspots': [],
        'has_git': False,
    }
    
    git_dir = root / '.git'
    if not git_dir.exists():
        return result
    
    result['has_git'] = True
    
    try:
        # 获取最近 N 天的提交统计
        cmd = [
            'git', '-C', str(root),
            'log', f'--since={days} days ago',
            '--pretty=format:', '--name-only',
        ]
        result_proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result_proc.returncode == 0:
            file_counts = defaultdict(int)
            for line in result_proc.stdout.strip().split('\n'):
                line = line.strip()
                if line:
                    file_counts[line] += 1
            
            sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
            result['hotspots'] = [
                {'path': path, 'changes': count}
                for path, count in sorted_files
            ]
    except Exception as e:
        result['error'] = str(e)
    
    return result


def infer_modules(root: Path) -> dict:
    """推断模块边界"""
    result = {
        'modules': [],
        'entry_points': [],
    }
    
    # 常见的入口文件
    entry_patterns = ['main', 'index', 'app', 'server', '__init__']
    # 常见的模块目录名
    module_indicators = ['src', 'lib', 'app', 'core', 'modules', 'services', 'handlers', 'controllers']
    
    for dirpath, dirnames, filenames in os.walk(root):
        rel_path = Path(dirpath).relative_to(root)
        depth = len(rel_path.parts)
        
        if depth > 2:
            continue
        
        # 检查入口文件
        for f in filenames:
            name = Path(f).stem.lower()
            ext = Path(f).suffix.lower()
            if name in entry_patterns and ext in {'.ts', '.js', '.py', '.go', '.rs'}:
                result['entry_points'].append(str(rel_path / f))
        
        # 检查模块目录
        for d in dirnames:
            if d.lower() in module_indicators:
                result['modules'].append({
                    'name': d,
                    'path': str(rel_path / d),
                    'type': 'inferred',
                })
    
    return result


def check_ai_context_files(root: Path) -> dict:
    """检查现有的 AI 上下文文件"""
    result = {
        'project_context': None,
        'module_contexts': [],
        'knowledge_base': None,
    }
    
    # 检查项目级上下文
    project_context_names = ['.ai-context.md', 'AGENTS.md', 'CLAUDE.md', '.cursor.md']
    for name in project_context_names:
        path = root / name
        if path.exists():
            result['project_context'] = name
            break
    
    # 检查模块级上下文
    for dirpath, dirnames, filenames in os.walk(root):
        if '.ai-context.md' in filenames:
            rel_path = Path(dirpath).relative_to(root)
            result['module_contexts'].append(str(rel_path))
    
    # 检查知识库
    knowledge_base_path = root / '.ai-context'
    if knowledge_base_path.exists() and knowledge_base_path.is_dir():
        result['knowledge_base'] = {
            'path': '.ai-context',
            'files': list(f.name for f in knowledge_base_path.iterdir() if f.is_file()),
        }
    
    return result


def analyze_project(project_path: Path) -> dict:
    """完整分析项目"""
    root = Path(project_path).resolve()
    
    if not root.exists():
        return {'error': f'Path does not exist: {root}'}
    
    print(f"分析项目: {root}")
    print("=" * 60)
    
    results = {
        'project_path': str(root),
        'structure': analyze_directory_structure(root),
        'files': analyze_file_sizes(root),
        'git': analyze_git_hotspots(root),
        'modules': infer_modules(root),
        'ai_context': check_ai_context_files(root),
    }
    
    return results


def print_report(results: dict):
    """打印分析报告"""
    print("\n" + "=" * 60)
    print("ADD 改造分析报告")
    print("=" * 60)
    
    # 文件大小分析
    files = results.get('files', {})
    large_files = files.get('large_files', [])
    stats = files.get('file_stats', {})
    
    print(f"\n📊 文件统计:")
    print(f"   总文件数: {stats.get('total_files', 0)}")
    print(f"   总行数: {stats.get('total_lines', 0):,}")
    print(f"   平均行数: {stats.get('avg_lines', 0):.1f}")
    
    if large_files:
        critical = [f for f in large_files if f['severity'] == 'critical']
        warning = [f for f in large_files if f['severity'] == 'warning']
        print(f"\n⚠️  大文件警告:")
        print(f"   严重 (>1000行): {len(critical)} 个")
        print(f"   警告 (>500行): {len(warning)} 个")
        
        if critical:
            print("\n   需要拆分的文件:")
            for f in critical[:10]:
                print(f"   ❌ {f['path']} ({f['lines']} 行)")
    
    # 目录结构分析
    structure = results.get('structure', {})
    deep_paths = structure.get('deep_paths', [])
    
    if deep_paths:
        print(f"\n📁 目录嵌套过深 (>3层):")
        for p in deep_paths[:10]:
            print(f"   {p}")
    
    # Git 热点
    git = results.get('git', {})
    if git.get('has_git') and git.get('hotspots'):
        print(f"\n🔥 最近修改热点文件:")
        for h in git['hotspots'][:10]:
            print(f"   {h['path']} ({h['changes']} 次修改)")
    
    # AI 上下文检查
    ai = results.get('ai_context', {})
    print(f"\n🤖 AI 上下文状态:")
    print(f"   项目级上下文: {'✅ ' + ai['project_context'] if ai.get('project_context') else '❌ 缺失'}")
    print(f"   模块级上下文: {len(ai.get('module_contexts', []))} 个")
    print(f"   知识库: {'✅ 存在' if ai.get('knowledge_base') else '❌ 缺失'}")
    
    # 改造建议
    print("\n" + "=" * 60)
    print("📋 改造建议优先级:")
    print("=" * 60)
    
    has_critical = any(f['severity'] == 'critical' for f in large_files)
    has_deep = len(deep_paths) > 0
    missing_project_context = not ai.get('project_context')
    missing_knowledge_base = not ai.get('knowledge_base')
    
    priority = []
    
    if has_critical:
        priority.append(('P0', '拆分 >1000 行的大文件'))
    
    if missing_project_context:
        priority.append(('P0', '创建项目级 .ai-context.md'))
    
    if missing_knowledge_base:
        priority.append(('P1', '创建 .ai-context/ 知识库'))
    
    if has_deep:
        priority.append(('P1', '扁平化过深的目录结构'))
    
    if not priority:
        print("   ✅ 项目结构良好，无需紧急改造")
    else:
        for p, desc in priority:
            print(f"   [{p}] {desc}")


def main():
    parser = argparse.ArgumentParser(description='ADD 项目分析器')
    parser.add_argument('project_path', help='项目路径')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    results = analyze_project(args.project_path)
    
    if args.json:
        output = json.dumps(results, indent=2, ensure_ascii=False, default=str)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
    else:
        print_report(results)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n详细结果已保存到: {args.output}")


if __name__ == '__main__':
    main()