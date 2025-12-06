from flask import Flask, render_template, request, jsonify, redirect, url_for
import yaml
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog

app = Flask(__name__)
YAML_PATH = os.path.join(os.path.dirname(__file__), 'projects.yaml')

def load_projects():
    with open(YAML_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_projects(data):
    with open(YAML_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

def get_git_info(folder_path):
    """프로젝트의 Git 정보를 가져옴"""
    git_info = {
        'is_git': False,
        'branch': '',
        'last_commit': '',
        'last_commit_date': '',
        'has_changes': False,
        'remote_url': ''
    }

    git_dir = os.path.join(folder_path, '.git')
    if not os.path.isdir(git_dir):
        return git_info

    git_info['is_git'] = True

    try:
        # 현재 브랜치
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=folder_path, capture_output=True, timeout=5,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout:
            git_info['branch'] = result.stdout.strip()

        # 마지막 커밋 메시지
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%s'],
            cwd=folder_path, capture_output=True, timeout=5,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout:
            git_info['last_commit'] = result.stdout.strip()[:50]

        # 마지막 커밋 날짜
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%cr'],
            cwd=folder_path, capture_output=True, timeout=5,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout:
            git_info['last_commit_date'] = result.stdout.strip()

        # 변경사항 여부
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=folder_path, capture_output=True, timeout=5,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout:
            git_info['has_changes'] = len(result.stdout.strip()) > 0

        # 원격 URL
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            cwd=folder_path, capture_output=True, timeout=5,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout:
            git_info['remote_url'] = result.stdout.strip()

    except Exception as e:
        print(f"Git info error: {e}")

    return git_info

def get_git_history(folder_path, limit=20):
    """프로젝트의 Git 커밋 히스토리를 가져옴"""
    history = []

    git_dir = os.path.join(folder_path, '.git')
    if not os.path.isdir(git_dir):
        return history

    try:
        # 커밋 히스토리 가져오기 (해시, 메시지, 작성자, 날짜)
        result = subprocess.run(
            ['git', 'log', f'-{limit}', '--pretty=format:%h|%s|%an|%cr'],
            cwd=folder_path, capture_output=True, timeout=10,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                parts = line.split('|')
                if len(parts) >= 4:
                    history.append({
                        'hash': parts[0],
                        'message': parts[1][:80],  # 메시지 80자 제한
                        'author': parts[2],
                        'date': parts[3],
                    })
    except Exception as e:
        print(f"Git history error: {e}")

    return history

def detect_tech_stack(folder_path):
    """프로젝트 폴더에서 기술 스택 감지"""
    tech_stack = []

    tech_indicators = {
        # 언어
        'package.json': 'JavaScript/Node.js',
        'tsconfig.json': 'TypeScript',
        'requirements.txt': 'Python',
        'setup.py': 'Python',
        'pyproject.toml': 'Python',
        'Pipfile': 'Python',
        'go.mod': 'Go',
        'Cargo.toml': 'Rust',
        'pom.xml': 'Java/Maven',
        'build.gradle': 'Java/Gradle',
        'composer.json': 'PHP',
        'Gemfile': 'Ruby',
        '*.csproj': 'C#/.NET',
        'CMakeLists.txt': 'C/C++',
        # 프레임워크
        'next.config.js': 'Next.js',
        'nuxt.config.js': 'Nuxt.js',
        'vue.config.js': 'Vue.js',
        'angular.json': 'Angular',
        'svelte.config.js': 'Svelte',
        'vite.config.js': 'Vite',
        'vite.config.ts': 'Vite',
        'webpack.config.js': 'Webpack',
        'tailwind.config.js': 'Tailwind CSS',
        'manage.py': 'Django',
        'platformio.ini': 'PlatformIO/ESP32',
        # 기타
        'Dockerfile': 'Docker',
        'docker-compose.yml': 'Docker Compose',
        'docker-compose.yaml': 'Docker Compose',
        '.github': 'GitHub Actions',
        'vercel.json': 'Vercel',
        'netlify.toml': 'Netlify',
    }

    try:
        items = os.listdir(folder_path)
        for indicator, tech in tech_indicators.items():
            if indicator.startswith('*.'):
                ext = indicator[1:]
                if any(f.endswith(ext) for f in items):
                    tech_stack.append(tech)
            elif indicator in items:
                tech_stack.append(tech)

        # package.json에서 추가 정보 추출
        pkg_path = os.path.join(folder_path, 'package.json')
        if os.path.exists(pkg_path):
            import json
            with open(pkg_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                if 'react' in deps:
                    tech_stack.append('React')
                if 'vue' in deps:
                    tech_stack.append('Vue.js')
                if 'express' in deps:
                    tech_stack.append('Express')
                if 'electron' in deps:
                    tech_stack.append('Electron')

        # requirements.txt에서 Flask/FastAPI 감지
        req_path = os.path.join(folder_path, 'requirements.txt')
        if os.path.exists(req_path):
            with open(req_path, 'r', encoding='utf-8') as f:
                reqs = f.read().lower()
                if 'flask' in reqs:
                    tech_stack.append('Flask')
                if 'fastapi' in reqs:
                    tech_stack.append('FastAPI')
                if 'django' in reqs:
                    tech_stack.append('Django')
    except Exception as e:
        print(f"Tech stack detection error: {e}")

    return list(set(tech_stack))

@app.route('/')
def index():
    data = load_projects()
    projects = data.get('projects', [])
    groups = data.get('groups', [])

    # 각 프로젝트에 기술 스택 및 Git 정보 추가
    for p in projects:
        path = p.get('path', '')
        if path and os.path.isdir(path):
            p['tech_stack'] = detect_tech_stack(path)
            p['git_info'] = get_git_info(path)
        else:
            p['tech_stack'] = []
            p['git_info'] = {'is_git': False}

    # 필터링
    category = request.args.get('category', 'all')
    status = request.args.get('status', 'all')
    group_filter = request.args.get('group', 'all')
    search = request.args.get('search', '').lower()

    filtered = projects
    if category != 'all':
        filtered = [p for p in filtered if p.get('category') == category]
    if status != 'all':
        filtered = [p for p in filtered if p.get('status') == status]
    if group_filter != 'all':
        filtered = [p for p in filtered if p.get('group') == group_filter]
    if search:
        filtered = [p for p in filtered if search in p.get('name', '').lower()
                    or search in p.get('description', '').lower()
                    or any(search in tag.lower() for tag in p.get('tags', []))]

    # 그룹별로 프로젝트 정리
    grouped_projects = {}
    ungrouped = []
    for p in filtered:
        g = p.get('group', '')
        if g:
            if g not in grouped_projects:
                grouped_projects[g] = []
            grouped_projects[g].append(p)
        else:
            ungrouped.append(p)

    # 통계
    stats = {
        'total': len(projects),
        'active': len([p for p in projects if p.get('status') == 'active']),
        'paused': len([p for p in projects if p.get('status') == 'paused']),
        'done': len([p for p in projects if p.get('status') == 'done']),
    }

    categories = list(set(p.get('category', 'other') for p in projects))

    return render_template('index.html',
                         projects=filtered,
                         grouped_projects=grouped_projects,
                         ungrouped=ungrouped,
                         groups=groups,
                         stats=stats,
                         categories=categories,
                         current_category=category,
                         current_status=status,
                         current_group=group_filter,
                         search=search)

@app.route('/add', methods=['POST'])
def add_project():
    data = load_projects()
    new_project = {
        'name': request.form.get('name'),
        'path': request.form.get('path'),
        'category': request.form.get('category', 'personal'),
        'status': request.form.get('status', 'active'),
        'group': request.form.get('group', ''),
        'tags': [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
        'description': request.form.get('description', ''),
        'git_url': request.form.get('git_url', ''),
    }
    data['projects'].append(new_project)
    save_projects(data)
    return redirect(url_for('index'))

@app.route('/update/<name>', methods=['POST'])
def update_project(name):
    data = load_projects()
    for p in data['projects']:
        if p['name'] == name:
            p['status'] = request.form.get('status', p['status'])
            p['category'] = request.form.get('category', p['category'])
            p['group'] = request.form.get('group', p.get('group', ''))
            p['description'] = request.form.get('description', p['description'])
            p['git_url'] = request.form.get('git_url', p.get('git_url', ''))
            tags_str = request.form.get('tags', '')
            if tags_str:
                p['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]
            break
    save_projects(data)
    return redirect(url_for('index'))

@app.route('/project/<name>')
def project_detail(name):
    data = load_projects()
    groups = data.get('groups', [])
    project = next((p for p in data['projects'] if p['name'] == name), None)

    if not project:
        return redirect(url_for('index'))

    path = project.get('path', '')
    if path and os.path.isdir(path):
        project['tech_stack'] = detect_tech_stack(path)
        project['git_info'] = get_git_info(path)
        project['git_history'] = get_git_history(path)
    else:
        project['tech_stack'] = []
        project['git_info'] = {'is_git': False}
        project['git_history'] = []

    return render_template('detail.html', project=project, groups=groups)

@app.route('/delete/<name>', methods=['POST'])
def delete_project(name):
    data = load_projects()
    data['projects'] = [p for p in data['projects'] if p['name'] != name]
    save_projects(data)
    return redirect(url_for('index'))

@app.route('/add-group', methods=['POST'])
def add_group():
    data = load_projects()
    if 'groups' not in data:
        data['groups'] = []
    group_name = request.form.get('group_name', '').strip()
    if group_name and group_name not in data['groups']:
        data['groups'].append(group_name)
        save_projects(data)
    return redirect(url_for('index'))

@app.route('/delete-group/<group_name>', methods=['POST'])
def delete_group(group_name):
    data = load_projects()
    if 'groups' in data and group_name in data['groups']:
        data['groups'].remove(group_name)
        # 해당 그룹의 프로젝트들은 그룹 해제
        for p in data['projects']:
            if p.get('group') == group_name:
                p['group'] = ''
        save_projects(data)
    return redirect(url_for('index'))

@app.route('/browse-folder')
def browse_folder():
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        folder_path = filedialog.askdirectory(parent=root)
        root.destroy()

        if folder_path:
            folder_path = os.path.normpath(folder_path)
            folder_name = os.path.basename(folder_path)
            tech_stack = detect_tech_stack(folder_path)
            return jsonify({
                'path': folder_path,
                'name': folder_name,
                'tech_stack': tech_stack
            })
    except Exception as e:
        print(f"Browse folder error: {e}")
    return jsonify({'path': '', 'name': '', 'tech_stack': []})

@app.route('/open/<name>/<action>')
def open_project(name, action):
    data = load_projects()
    project = next((p for p in data['projects'] if p['name'] == name), None)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    path = project['path']
    
    if sys.platform == 'win32':
        if action == 'vscode':
            subprocess.Popen(['code', path], shell=True)
        elif action == 'terminal':
            subprocess.Popen(f'start cmd /K "cd /d {path}"', shell=True)
        elif action == 'explorer':
            subprocess.Popen(f'explorer "{path}"', shell=True)
        elif action == 'claude':
            subprocess.Popen(f'start cmd /K "cd /d {path} && claude"', shell=True)
    else:
        if action == 'vscode':
            subprocess.Popen(['code', path])
        elif action == 'terminal':
            subprocess.Popen(['gnome-terminal', f'--working-directory={path}'])
        elif action == 'claude':
            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'cd "{path}" && claude; exec bash'])
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
