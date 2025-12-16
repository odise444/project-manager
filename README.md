# Project Manager

로컬 개발 프로젝트들을 한눈에 관리하는 웹 대시보드.

## 기능

- 프로젝트 CRUD (YAML 저장)
- 프로젝트 그룹핑 및 필터링
- 기술 스택 자동 감지 (package.json, requirements.txt 등)
- Git 정보 표시 (브랜치, 커밋, 변경사항)
- 상세 페이지에서 커밋 히스토리 확인
- VS Code, Terminal, Explorer, Claude 바로가기
- 다크/라이트 테마
- 드래그 앤 드롭으로 프로젝트 정렬

## 실행

```bash
# 가상환경 생성 (최초 1회)
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 의존성 설치
pip install flask pyyaml

# 실행
python app.py
```

http://localhost:5000 접속

## 구조

```
proj-manager/
├── app.py              # Flask 백엔드
├── projects.yaml       # 프로젝트 데이터
├── templates/
│   ├── index.html      # 메인 페이지
│   ├── detail.html     # 상세 페이지
│   └── _project_card.html
└── static/
    └── style.css
```

## 스크린샷

(추후 추가)
