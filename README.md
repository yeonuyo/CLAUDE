# React 기반 과제 일정 관리 캘린더 시스템

Flask API 백엔드와 React 프론트엔드로 구성된 웹 기반 과제 일정 관리 캘린더 시스템입니다.

## 기능

- 📅 월별 캘린더 뷰
- ➕ 과제 추가/수정/삭제
- ✅ 과제 완료 상태 토글
- 🎯 우선순위 설정 (높음/보통/낮음)
- ⏰ 시간 설정
- 📱 반응형 디자인

## 프로젝트 구조

```
CLAUDE/
├── backend/
│   ├── app.py              # Flask API 서버
│   ├── requirements.txt    # Python 의존성
│   └── tasks.json         # 데이터 파일 (자동 생성)
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Calendar.js    # 캘린더 컴포넌트
│   │   │   ├── TaskList.js    # 과제 목록 컴포넌트
│   │   │   ├── TaskModal.js   # 과제 추가/수정 모달
│   │   │   └── *.css         # 각 컴포넌트 스타일
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
└── README.md
```

## 설치 및 실행

### 백엔드 (Flask API)

1. 백엔드 디렉토리로 이동:
```bash
cd backend
```

2. 가상환경 생성 및 활성화 (권장):
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. Flask 서버 실행:
```bash
python app.py
```

백엔드 서버가 http://localhost:5000 에서 실행됩니다.

### 프론트엔드 (React)

1. 새 터미널에서 프론트엔드 디렉토리로 이동:
```bash
cd frontend
```

2. 의존성 설치:
```bash
npm install
```

3. React 개발 서버 실행:
```bash
npm start
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

## 사용법

1. 브라우저에서 http://localhost:3000 접속
2. 캘린더에서 날짜를 클릭하여 해당 날짜 선택
3. "새 과제 추가" 버튼을 클릭하여 과제 추가
4. 캘린더에서 과제가 있는 날짜에는 색상 표시됩니다
5. 우측 패널에서 선택된 날짜의 과제 목록을 확인하고 관리할 수 있습니다

## API 엔드포인트

- `GET /api/tasks` - 모든 과제 조회
- `POST /api/tasks` - 새 과제 생성
- `PUT /api/tasks/<id>` - 과제 수정
- `DELETE /api/tasks/<id>` - 과제 삭제
- `PUT /api/tasks/<id>/toggle` - 과제 완료 상태 토글
- `GET /api/tasks/date/<date>` - 특정 날짜의 과제 조회

## 데이터 저장

모든 과제 데이터는 `backend/tasks.json` 파일에 JSON 형식으로 저장됩니다.