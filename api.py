"""
영어 발음 분석 REST API (Flask)
모바일 앱, 웹 앱에서 호출 가능한 API 엔드포인트
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import os
import uuid
from datetime import datetime
from pronunciation_analyzer import PronunciationAnalyzer
from interview.interview_analyzer import InterviewAnalyzer, load_questions, get_random_question

app = Flask(__name__)
CORS(app)  # CORS 허용 (프론트엔드 연결용)

# 글로벌 분석기 인스턴스
analyzer = PronunciationAnalyzer(model_size="base")
interview_analyzer = InterviewAnalyzer(pronunciation_analyzer=analyzer)

# 면접 세션 저장소 (메모리 기반 - 프로덕션에서는 데이터베이스 사용)
interview_sessions = {}


@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'service': 'pronunciation-analyzer',
        'version': '1.0.0'
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_pronunciation():
    """
    발음 분석 API
    
    Request:
        - audio: 오디오 파일 (multipart/form-data)
        - reference_text: 참조 텍스트 (string)
        - analyze_prosody: 운율 분석 여부 (boolean, optional)
    
    Response:
        - spoken_text: 인식된 텍스트
        - pronunciation: 발음 분석 결과
        - prosody: 운율 분석 결과 (옵션)
        - feedback: AI 피드백
    """
    try:
        # 파라미터 검증
        if 'audio' not in request.files:
            return jsonify({
                'error': 'audio file is required',
                'code': 'MISSING_AUDIO'
            }), 400
        
        if 'reference_text' not in request.form:
            return jsonify({
                'error': 'reference_text is required',
                'code': 'MISSING_REFERENCE'
            }), 400
        
        audio_file = request.files['audio']
        reference_text = request.form['reference_text']
        analyze_prosody_flag = request.form.get('analyze_prosody', 'true').lower() == 'true'
        
        # 오디오 파일을 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # 전체 분석 실행
            result = analyzer.full_analysis(tmp_path, reference_text)
            
            # 운율 분석 제외 옵션
            if not analyze_prosody_flag:
                result['prosody'] = None
            
            return jsonify({
                'success': True,
                'data': result
            }), 200
        
        finally:
            # 임시 파일 삭제
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ANALYSIS_FAILED'
        }), 500


@app.route('/api/transcribe', methods=['POST'])
def transcribe_only():
    """
    음성을 텍스트로만 변환 (STT only)
    
    Request:
        - audio: 오디오 파일
    
    Response:
        - text: 변환된 텍스트
    """
    try:
        if 'audio' not in request.files:
            return jsonify({
                'error': 'audio file is required',
                'code': 'MISSING_AUDIO'
            }), 400
        
        audio_file = request.files['audio']
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            spoken_text = analyzer.transcribe_audio(tmp_path)
            
            return jsonify({
                'success': True,
                'text': spoken_text
            }), 200
        
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'TRANSCRIPTION_FAILED'
        }), 500


@app.route('/api/score', methods=['POST'])
def score_pronunciation():
    """
    텍스트 기반 발음 스코어링 (오디오 없이)
    
    Request:
        - reference_text: 참조 텍스트
        - spoken_text: 사용자가 말한 텍스트
    
    Response:
        - score: 발음 스코어
        - details: 상세 분석 결과
    """
    try:
        data = request.get_json()
        
        if not data or 'reference_text' not in data or 'spoken_text' not in data:
            return jsonify({
                'error': 'reference_text and spoken_text are required',
                'code': 'MISSING_PARAMETERS'
            }), 400
        
        reference_text = data['reference_text']
        spoken_text = data['spoken_text']
        
        result = analyzer.calculate_pronunciation_score(reference_text, spoken_text)
        feedback = analyzer.generate_feedback(result)
        
        return jsonify({
            'success': True,
            'score': result['overall_score'],
            'details': result,
            'feedback': feedback
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'SCORING_FAILED'
        }), 500


@app.route('/api/phonemes', methods=['POST'])
def get_phonemes():
    """
    텍스트의 음소 추출
    
    Request:
        - text: 입력 텍스트
    
    Response:
        - phonemes: 음소 리스트
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'text is required',
                'code': 'MISSING_TEXT'
            }), 400
        
        text = data['text']
        phonemes = analyzer.get_phonemes(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'phonemes': phonemes,
            'phoneme_count': len(phonemes)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'PHONEME_EXTRACTION_FAILED'
        }), 500


@app.route('/api/practice-sentences', methods=['GET'])
def get_practice_sentences():
    """
    연습용 문장 목록 제공
    
    Query Parameters:
        - level: beginner/intermediate/advanced
        - category: daily/business/travel
    """
    level = request.args.get('level', 'beginner')
    category = request.args.get('category', 'daily')
    
    sentences = {
        'beginner': {
            'daily': [
                "Hello, how are you?",
                "Nice to meet you",
                "What's your name?",
                "I am fine, thank you"
            ],
            'business': [
                "Good morning",
                "Thank you for your time",
                "Please send me the file",
                "Let's have a meeting"
            ],
            'travel': [
                "Where is the hotel?",
                "How much is this?",
                "I need help please",
                "Thank you very much"
            ]
        },
        'intermediate': {
            'daily': [
                "What's the weather like today?",
                "I'd like a cup of coffee please",
                "Could you help me with this?",
                "That sounds like a great idea"
            ],
            'business': [
                "Could you send me the report?",
                "Let's schedule a meeting next week",
                "I'll get back to you soon",
                "What's your opinion on this?"
            ],
            'travel': [
                "How do I get to the airport?",
                "I'd like to make a reservation",
                "Is there a pharmacy nearby?",
                "What time does it close?"
            ]
        },
        'advanced': {
            'daily': [
                "I've been thinking about trying that new restaurant",
                "It's been quite challenging to manage everything lately",
                "The presentation went better than I expected",
                "I appreciate your understanding in this matter"
            ],
            'business': [
                "We need to reassess our strategy moving forward",
                "I'd like to discuss the quarterly projections",
                "Could you elaborate on your proposal?",
                "Let's align our objectives for the next quarter"
            ],
            'travel': [
                "I'd like to extend my reservation for two more nights",
                "Could you recommend any local attractions?",
                "Is there a shuttle service to the city center?",
                "What's the best way to get around the city?"
            ]
        }
    }
    
    return jsonify({
        'success': True,
        'level': level,
        'category': category,
        'sentences': sentences.get(level, {}).get(category, [])
    }), 200


# ============================================================================
# 면접 연습 API (Interview Practice API)
# ============================================================================

@app.route('/api/interview/questions', methods=['GET'])
def get_interview_questions():
    """
    면접 질문 목록 조회

    Query Parameters:
        - category: 질문 카테고리 (self-introduction, behavioral, situational, etc.)
        - difficulty: 난이도 (beginner, intermediate, advanced)
        - industry: 산업 (general, tech, business, marketing, sales)
        - limit: 반환할 질문 수 제한 (optional)

    Response:
        - questions: 질문 리스트
        - total: 전체 질문 수
        - filters: 적용된 필터
    """
    try:
        category = request.args.get('category', None)
        difficulty = request.args.get('difficulty', None)
        industry = request.args.get('industry', None)
        limit = request.args.get('limit', None)

        # 질문 로드 (필터 적용)
        questions = load_questions(
            category=category,
            difficulty=difficulty,
            industry=industry
        )

        # 제한 적용
        if limit:
            try:
                limit = int(limit)
                questions = questions[:limit]
            except ValueError:
                pass

        # 민감한 정보 제거 (follow_up_questions 등은 선택적)
        simplified_questions = []
        for q in questions:
            simplified_questions.append({
                'id': q['id'],
                'question': q['question'],
                'question_ko': q['question_ko'],
                'category': q['category'],
                'difficulty': q['difficulty'],
                'industry': q['industry'],
                'ideal_duration': q['ideal_duration'],
                'tips': q.get('tips', [])
            })

        return jsonify({
            'success': True,
            'total': len(simplified_questions),
            'filters': {
                'category': category,
                'difficulty': difficulty,
                'industry': industry
            },
            'questions': simplified_questions
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'QUESTION_LOAD_FAILED'
        }), 500


@app.route('/api/interview/questions/random', methods=['GET'])
def get_random_interview_question():
    """
    랜덤 면접 질문 가져오기

    Query Parameters:
        - count: 질문 개수 (default: 1)
        - category: 질문 카테고리 (optional)
        - difficulty: 난이도 (optional)
        - industry: 산업 (optional)

    Response:
        - questions: 랜덤 질문 리스트
    """
    try:
        count = int(request.args.get('count', 1))
        category = request.args.get('category', None)
        difficulty = request.args.get('difficulty', None)
        industry = request.args.get('industry', None)

        # 최대 10개로 제한
        count = min(count, 10)

        # 모든 질문 로드
        all_questions = load_questions(
            category=category,
            difficulty=difficulty,
            industry=industry
        )

        if not all_questions:
            return jsonify({
                'success': False,
                'error': 'No questions found with the given filters',
                'code': 'NO_QUESTIONS_FOUND'
            }), 404

        # 랜덤 선택
        import random
        selected = random.sample(all_questions, min(count, len(all_questions)))

        return jsonify({
            'success': True,
            'count': len(selected),
            'questions': selected
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'RANDOM_QUESTION_FAILED'
        }), 500


@app.route('/api/interview/analyze', methods=['POST'])
def analyze_interview_answer():
    """
    면접 답변 분석

    Request:
        - audio: 오디오 파일 (multipart/form-data)
        - question_id: 질문 ID (optional, 또는 question_text 사용)
        - question_text: 질문 텍스트 (optional, question_id가 없을 때)

    Response:
        - transcription: 인식된 텍스트
        - scores: 점수 (overall, pronunciation, content, structure, grammar, duration)
        - feedback: AI 피드백
        - improvements: 개선 제안
        - filler_words: 필러 워드 분석
    """
    try:
        # 파라미터 검증
        if 'audio' not in request.files:
            return jsonify({
                'error': 'audio file is required',
                'code': 'MISSING_AUDIO'
            }), 400

        audio_file = request.files['audio']
        question_id = request.form.get('question_id', None)
        question_text = request.form.get('question_text', None)

        # 질문 정보 가져오기
        question = None
        if question_id:
            # ID로 질문 찾기
            all_questions = load_questions()
            question = next((q for q in all_questions if q['id'] == question_id), None)

            if not question:
                return jsonify({
                    'error': f'Question with id {question_id} not found',
                    'code': 'QUESTION_NOT_FOUND'
                }), 404
        elif question_text:
            # 텍스트로 간단한 질문 객체 생성
            question = {
                'id': 'custom',
                'question': question_text,
                'question_ko': question_text,
                'category': 'custom',
                'difficulty': 'intermediate',
                'industry': 'general',
                'keywords': [],
                'ideal_duration': 90,
                'tips': []
            }
        else:
            return jsonify({
                'error': 'Either question_id or question_text is required',
                'code': 'MISSING_QUESTION'
            }), 400

        # 오디오 파일 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_path = tmp_file.name

        try:
            # 면접 답변 분석
            result = interview_analyzer.analyze_interview_answer(
                audio_path=tmp_path,
                question=question
            )

            return jsonify({
                'success': True,
                'data': {
                    'transcription': result['transcription'],
                    'duration': result['duration'],
                    'scores': result['scores'],
                    'feedback': result['feedback'],
                    'improvements': result['improvements'],
                    'filler_words': result['filler_words'],
                    'question': {
                        'id': question['id'],
                        'question': question['question'],
                        'question_ko': question['question_ko']
                    }
                }
            }), 200

        finally:
            # 임시 파일 삭제
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'INTERVIEW_ANALYSIS_FAILED'
        }), 500


@app.route('/api/interview/session/start', methods=['POST'])
def start_interview_session():
    """
    모의 면접 세션 시작

    Request Body (JSON):
        - interview_type: 면접 유형 (예: "behavioral", "technical", "general")
        - num_questions: 질문 개수 (default: 5)
        - category: 질문 카테고리 (optional)
        - difficulty: 난이도 (optional)
        - industry: 산업 (optional)

    Response:
        - session_id: 세션 ID
        - questions: 질문 리스트
        - total_questions: 총 질문 수
        - started_at: 시작 시간
    """
    try:
        data = request.get_json() or {}

        interview_type = data.get('interview_type', 'general')
        num_questions = int(data.get('num_questions', 5))
        category = data.get('category', None)
        difficulty = data.get('difficulty', None)
        industry = data.get('industry', None)

        # 질문 개수 제한 (1-10)
        num_questions = max(1, min(num_questions, 10))

        # 질문 로드
        all_questions = load_questions(
            category=category,
            difficulty=difficulty,
            industry=industry
        )

        if not all_questions:
            return jsonify({
                'success': False,
                'error': 'No questions found with the given filters',
                'code': 'NO_QUESTIONS_FOUND'
            }), 404

        # 랜덤 질문 선택
        import random
        selected_questions = random.sample(
            all_questions,
            min(num_questions, len(all_questions))
        )

        # 세션 생성
        session_id = str(uuid.uuid4())
        session = {
            'session_id': session_id,
            'interview_type': interview_type,
            'questions': selected_questions,
            'total_questions': len(selected_questions),
            'current_question': 0,
            'answers': [],
            'started_at': datetime.now().isoformat(),
            'completed_at': None,
            'filters': {
                'category': category,
                'difficulty': difficulty,
                'industry': industry
            }
        }

        # 세션 저장
        interview_sessions[session_id] = session

        # 응답용 질문 리스트 (민감한 정보 제거)
        question_list = []
        for i, q in enumerate(selected_questions):
            question_list.append({
                'index': i,
                'id': q['id'],
                'question': q['question'],
                'question_ko': q['question_ko'],
                'ideal_duration': q['ideal_duration'],
                'tips': q.get('tips', [])
            })

        return jsonify({
            'success': True,
            'session_id': session_id,
            'questions': question_list,
            'total_questions': len(selected_questions),
            'started_at': session['started_at']
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'SESSION_START_FAILED'
        }), 500


@app.route('/api/interview/session/<session_id>/answer', methods=['POST'])
def submit_interview_answer(session_id):
    """
    면접 세션에 답변 제출

    URL Parameter:
        - session_id: 세션 ID

    Request:
        - audio: 오디오 파일
        - question_index: 질문 인덱스 (0부터 시작)

    Response:
        - answer_index: 답변 인덱스
        - scores: 점수
        - feedback: 피드백
        - next_question: 다음 질문 (있으면)
    """
    try:
        # 세션 확인
        if session_id not in interview_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found',
                'code': 'SESSION_NOT_FOUND'
            }), 404

        session = interview_sessions[session_id]

        # 파라미터 검증
        if 'audio' not in request.files:
            return jsonify({
                'error': 'audio file is required',
                'code': 'MISSING_AUDIO'
            }), 400

        audio_file = request.files['audio']
        question_index = int(request.form.get('question_index', session['current_question']))

        # 질문 인덱스 유효성 검사
        if question_index < 0 or question_index >= len(session['questions']):
            return jsonify({
                'error': 'Invalid question index',
                'code': 'INVALID_QUESTION_INDEX'
            }), 400

        question = session['questions'][question_index]

        # 오디오 파일 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_path = tmp_file.name

        try:
            # 답변 분석
            result = interview_analyzer.analyze_interview_answer(
                audio_path=tmp_path,
                question=question
            )

            # 답변 저장
            answer_record = {
                'question_index': question_index,
                'question_id': question['id'],
                'transcription': result['transcription'],
                'duration': result['duration'],
                'scores': result['scores'],
                'feedback': result['feedback'],
                'improvements': result['improvements'],
                'filler_words': result['filler_words'],
                'answered_at': datetime.now().isoformat()
            }

            session['answers'].append(answer_record)
            session['current_question'] = question_index + 1

            # 다음 질문 정보
            next_question = None
            if session['current_question'] < len(session['questions']):
                next_q = session['questions'][session['current_question']]
                next_question = {
                    'index': session['current_question'],
                    'id': next_q['id'],
                    'question': next_q['question'],
                    'question_ko': next_q['question_ko'],
                    'ideal_duration': next_q['ideal_duration']
                }
            else:
                # 모든 질문 완료
                session['completed_at'] = datetime.now().isoformat()

            return jsonify({
                'success': True,
                'answer_index': len(session['answers']) - 1,
                'scores': result['scores'],
                'feedback': result['feedback'],
                'improvements': result['improvements'],
                'filler_words': result['filler_words'],
                'progress': {
                    'answered': len(session['answers']),
                    'total': session['total_questions'],
                    'percentage': (len(session['answers']) / session['total_questions']) * 100
                },
                'next_question': next_question,
                'completed': session['completed_at'] is not None
            }), 200

        finally:
            # 임시 파일 삭제
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ANSWER_SUBMISSION_FAILED'
        }), 500


@app.route('/api/interview/session/<session_id>/results', methods=['GET'])
def get_interview_session_results(session_id):
    """
    면접 세션 결과 조회

    URL Parameter:
        - session_id: 세션 ID

    Response:
        - session_info: 세션 정보
        - summary: 점수 요약
        - answers: 모든 답변 및 분석 결과
    """
    try:
        # 세션 확인
        if session_id not in interview_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found',
                'code': 'SESSION_NOT_FOUND'
            }), 404

        session = interview_sessions[session_id]

        # 점수 요약 계산
        if session['answers']:
            scores_summary = {
                'overall': 0,
                'pronunciation': 0,
                'content': 0,
                'structure': 0,
                'grammar': 0,
                'duration': 0
            }

            for answer in session['answers']:
                for key in scores_summary:
                    scores_summary[key] += answer['scores'][key]

            # 평균 계산
            num_answers = len(session['answers'])
            for key in scores_summary:
                scores_summary[key] = round(scores_summary[key] / num_answers, 1)

            # 가장 좋은/나쁜 답변
            best_answer = max(session['answers'], key=lambda x: x['scores']['overall'])
            worst_answer = min(session['answers'], key=lambda x: x['scores']['overall'])

            # 필러 워드 통계
            total_filler_count = sum(a['filler_words']['count'] for a in session['answers'])
            avg_filler_density = sum(a['filler_words']['density'] for a in session['answers']) / num_answers
        else:
            scores_summary = None
            best_answer = None
            worst_answer = None
            total_filler_count = 0
            avg_filler_density = 0

        return jsonify({
            'success': True,
            'session_info': {
                'session_id': session['session_id'],
                'interview_type': session['interview_type'],
                'total_questions': session['total_questions'],
                'answered': len(session['answers']),
                'started_at': session['started_at'],
                'completed_at': session['completed_at'],
                'filters': session['filters']
            },
            'summary': {
                'average_scores': scores_summary,
                'best_score': best_answer['scores']['overall'] if best_answer else None,
                'worst_score': worst_answer['scores']['overall'] if worst_answer else None,
                'total_filler_words': total_filler_count,
                'avg_filler_density': round(avg_filler_density, 2) if session['answers'] else 0
            },
            'answers': [{
                'question_index': a['question_index'],
                'question_id': a['question_id'],
                'question': session['questions'][a['question_index']]['question'],
                'transcription': a['transcription'],
                'duration': a['duration'],
                'scores': a['scores'],
                'feedback': a['feedback'],
                'filler_words': a['filler_words']
            } for a in session['answers']]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'RESULTS_RETRIEVAL_FAILED'
        }), 500


@app.route('/api/interview/session/<session_id>', methods=['DELETE'])
def delete_interview_session(session_id):
    """
    면접 세션 삭제

    URL Parameter:
        - session_id: 세션 ID

    Response:
        - success: 삭제 성공 여부
    """
    try:
        if session_id not in interview_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found',
                'code': 'SESSION_NOT_FOUND'
            }), 404

        del interview_sessions[session_id]

        return jsonify({
            'success': True,
            'message': 'Session deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'SESSION_DELETE_FAILED'
        }), 500


# ============================================================================
# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'endpoint not found',
        'code': 'NOT_FOUND'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500


if __name__ == '__main__':
    # 개발 서버 실행
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
