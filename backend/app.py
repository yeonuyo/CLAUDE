from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_next_id(tasks):
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

def parse_task_from_text(text):
    """자연어 텍스트에서 과제 정보를 추출합니다."""
    result = {
        'title': '',
        'description': text,
        'date': '',
        'time': '',
        'priority': 'medium',
        'points': '',
        'submission_location': ''
    }
    
    # 과제명 추출 (제목, 과제명, 레포트 등의 키워드 활용)
    title_patterns = [
        r'과제\s*[:：]\s*(.+?)(?=\n|\r|$)',
        r'제목\s*[:：]\s*(.+?)(?=\n|\r|$)',
        r'과제명\s*[:：]\s*(.+?)(?=\n|\r|$)',
        r'레포트\s*[:：]\s*(.+?)(?=\n|\r|$)',
        r'과제\s*[1-9]\s*[:：]\s*(.+?)(?=\n|\r|$)',
        r'(\w+\s*과제)',
        r'(\w+\s*레포트)',
        r'(\w+\s*프로젝트)'
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['title'] = match.group(1).strip()
            break
    
    # 마감일 추출 (다양한 날짜 형식 지원)
    date_patterns = [
        r'마감일?\s*[:：]\s*(\d{4})[.\-/년]\s*(\d{1,2})[.\-/월]\s*(\d{1,2})[일]?',
        r'제출일?\s*[:：]\s*(\d{4})[.\-/년]\s*(\d{1,2})[.\-/월]\s*(\d{1,2})[일]?',
        r'due\s*[:：]?\s*(\d{4})[.\-/]\s*(\d{1,2})[.\-/]\s*(\d{1,2})',
        r'(\d{4})[.\-/]\s*(\d{1,2})[.\-/]\s*(\d{1,2})\s*까지',
        r'(\d{1,2})[.\-/월]\s*(\d{1,2})[일]\s*까지',
        r'(\d{1,2})[월]\s*(\d{1,2})[일]'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) >= 3:
                year, month, day = groups[0], groups[1], groups[2]
                result['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            elif len(groups) == 2:
                month, day = groups[0], groups[1]
                current_year = datetime.now().year
                result['date'] = f"{current_year}-{month.zfill(2)}-{day.zfill(2)}"
            break
    
    # 시간 추출
    time_patterns = [
        r'(\d{1,2})\s*[:：시]\s*(\d{2})\s*분?까지',
        r'(\d{1,2})\s*[:：시]\s*(\d{2})',
        r'오후\s*(\d{1,2})\s*[:：시]',
        r'오전\s*(\d{1,2})\s*[:：시]',
        r'(\d{1,2})\s*시\s*까지'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                hour, minute = groups[0], groups[1]
                result['time'] = f"{hour.zfill(2)}:{minute.zfill(2)}"
            elif len(groups) == 1:
                hour = groups[0]
                result['time'] = f"{hour.zfill(2)}:00"
            break
    
    # 배점 추출
    points_patterns = [
        r'배점\s*[:：]\s*(\d+)\s*점',
        r'점수\s*[:：]\s*(\d+)\s*점',
        r'(\d+)\s*점\s*만점',
        r'총\s*(\d+)\s*점'
    ]
    
    for pattern in points_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['points'] = match.group(1) + '점'
            break
    
    # 제출장소 추출
    location_patterns = [
        r'제출\s*장소\s*[:：]\s*(.+?)(?=\n|\r|$)',
        r'제출\s*방법\s*[:：]\s*(.+?)(?=\n|\r|$)',
        r'제출처\s*[:：]\s*(.+?)(?=\n|\r|$)',
        r'이메일\s*[:：]\s*([\w\.-]+@[\w\.-]+)',
        r'LMS\s*제출',
        r'오프라인\s*제출',
        r'온라인\s*제출'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) > 0:
                result['submission_location'] = match.group(1).strip()
            else:
                result['submission_location'] = match.group(0).strip()
            break
    
    # 우선순위 결정 (키워드 기반)
    high_priority_keywords = ['중요', '시험', '발표', '프로젝트', '최종']
    low_priority_keywords = ['선택', '추가', '보너스']
    
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in high_priority_keywords):
        result['priority'] = 'high'
    elif any(keyword in text_lower for keyword in low_priority_keywords):
        result['priority'] = 'low'
    
    return result

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data.get('title') or not data.get('date'):
        return jsonify({'error': '제목과 날짜는 필수입니다.'}), 400
    
    tasks = load_tasks()
    new_task = {
        'id': get_next_id(tasks),
        'title': data['title'],
        'description': data.get('description', ''),
        'date': data['date'],
        'time': data.get('time', ''),
        'priority': data.get('priority', 'medium'),
        'points': data.get('points', ''),
        'submission_location': data.get('submission_location', ''),
        'completed': False,
        'notifications_enabled': data.get('notifications_enabled', True),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    tasks = load_tasks()
    
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({'error': '과제를 찾을 수 없습니다.'}), 404
    
    task.update({
        'title': data.get('title', task['title']),
        'description': data.get('description', task['description']),
        'date': data.get('date', task['date']),
        'time': data.get('time', task['time']),
        'priority': data.get('priority', task['priority']),
        'points': data.get('points', task.get('points', '')),
        'submission_location': data.get('submission_location', task.get('submission_location', '')),
        'completed': data.get('completed', task['completed']),
        'notifications_enabled': data.get('notifications_enabled', task.get('notifications_enabled', True))
    })
    
    save_tasks(tasks)
    return jsonify(task)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return '', 204

@app.route('/api/tasks/<int:task_id>/toggle', methods=['PUT'])
def toggle_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': '과제를 찾을 수 없습니다.'}), 404
    
    task['completed'] = not task['completed']
    save_tasks(tasks)
    return jsonify(task)

@app.route('/api/tasks/date/<date>')
def get_tasks_by_date(date):
    tasks = load_tasks()
    filtered_tasks = [task for task in tasks if task['date'] == date]
    return jsonify(filtered_tasks)

@app.route('/api/chatbot/parse', methods=['POST'])
def parse_assignment_text():
    data = request.get_json()
    
    if not data.get('text'):
        return jsonify({'error': '텍스트가 필요합니다.'}), 400
    
    parsed_data = parse_task_from_text(data['text'])
    
    # 필수 정보가 누락된 경우 처리
    if not parsed_data['title']:
        parsed_data['title'] = '제목을 입력해주세요'
    
    if not parsed_data['date']:
        # 기본값으로 오늘 날짜 설정
        parsed_data['date'] = datetime.now().strftime('%Y-%m-%d')
    
    return jsonify({
        'success': True,
        'parsed_data': parsed_data,
        'message': '과제 정보를 성공적으로 추출했습니다.'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)