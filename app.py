"""
영어 발음 학습 웹 앱 (Streamlit)
사용자가 녹음하고 즉시 피드백을 받을 수 있습니다
"""

import streamlit as st
import tempfile
import os
import requests
import json
from pronunciation_analyzer import PronunciationAnalyzer
from audio_recorder_streamlit import audio_recorder
from interview.interview_analyzer import InterviewAnalyzer, load_questions_db

# 페이지 설정
st.set_page_config(
    page_title="영어 발음 AI 코치",
    page_icon="🎤",
    layout="wide"
)

# 세션 상태 초기화
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = PronunciationAnalyzer(model_size="base")
if 'history' not in st.session_state:
    st.session_state.history = []

# 면접 관련 세션 상태
if 'interview_analyzer' not in st.session_state:
    st.session_state.interview_analyzer = InterviewAnalyzer(pronunciation_analyzer=st.session_state.analyzer)
if 'interview_questions_db' not in st.session_state:
    st.session_state.interview_questions_db = load_questions_db()
if 'interview_mode' not in st.session_state:
    st.session_state.interview_mode = 'single'  # 'single' or 'mock'
if 'interview_session_active' not in st.session_state:
    st.session_state.interview_session_active = False
if 'interview_questions' not in st.session_state:
    st.session_state.interview_questions = []
if 'interview_current_index' not in st.session_state:
    st.session_state.interview_current_index = 0
if 'interview_results' not in st.session_state:
    st.session_state.interview_results = []
if 'interview_history' not in st.session_state:
    st.session_state.interview_history = []

# 앱 헤더
st.title("🎤 영어 발음 AI 코치")
st.markdown("""
**AI가 당신의 영어 발음을 분석하고 개선 방법을 알려드립니다!**
- ✅ 실시간 발음 정확도 측정
- ✅ 음소 단위 상세 분석
- ✅ 면접 답변 분석 및 피드백
- ✅ 개인 맞춤 피드백
""")

st.divider()

# 탭 생성
tab1, tab2 = st.tabs(["🗣️ 발음 연습 (Pronunciation Practice)", "💼 면접 연습 (Interview Practice)"])

# =============================================================================
# TAB 1: 발음 연습 (기존 기능)
# =============================================================================
with tab1:
    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 설정 (Settings)")

        # 연습 문장 선택
        practice_mode = st.selectbox(
            "연습 모드 (Practice Mode)",
            ["기본 문장 (Basic Sentence)", "사용자 입력 (Custom Input)", "일상 회화 (Daily Conversation)", "비즈니스 영어 (Business English)"]
        )

        if "사용자 입력" in practice_mode or "Custom Input" in practice_mode:
            custom_text = st.text_area(
                "연습할 문장을 입력하세요 (Enter your practice sentence)",
                placeholder="예: How are you doing today?"
            )
            reference_text = custom_text if custom_text else "Hello world"
        elif "일상 회화" in practice_mode or "Daily Conversation" in practice_mode:
            reference_text = st.selectbox(
                "문장 선택 (Select Sentence)",
                [
                    "How are you doing today?",
                    "Nice to meet you",
                    "What's the weather like?",
                    "I'd like a cup of coffee please"
                ]
            )
        elif "비즈니스 영어" in practice_mode or "Business English" in practice_mode:
            reference_text = st.selectbox(
                "문장 선택 (Select Sentence)",
                [
                    "Let's schedule a meeting",
                    "Could you send me the report?",
                    "I'll get back to you soon",
                    "Thank you for your time"
                ]
            )
        else:
            reference_text = "Hello world, how are you today?"

        st.divider()

        # 분석 옵션
        st.subheader("분석 옵션 (Analysis Options)")
        analyze_prosody = st.checkbox("운율 분석 (Prosody Analysis) - 속도, 억양 (Speed, Intonation)", value=True)
        show_phonemes = st.checkbox("음소 상세 보기 (Show Phoneme Details)", value=False)

        st.divider()

        # 통계
        if st.session_state.history:
            st.subheader("📈 학습 통계 (Learning Statistics)")
            avg_score = sum(h['score'] for h in st.session_state.history) / len(st.session_state.history)
            st.metric("평균 점수 (Average Score)", f"{avg_score:.1f}점")
            st.metric("총 연습 횟수 (Total Sessions)", len(st.session_state.history))

    # 메인 영역
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("🎯 연습할 문장 (Practice Sentence)")
        st.info(reference_text)

        # 발음 팁
        with st.expander("💡 발음 팁 (Pronunciation Tips)"):
            st.markdown("""
            - 천천히, 또박또박 발음하세요 (Speak slowly and clearly)
            - 각 단어의 강세를 신경쓰세요 (Pay attention to word stress)
            - 자연스러운 속도로 말하세요 (Speak at a natural pace)
            - 문장 끝의 억양에 주의하세요 (Watch sentence intonation)
            """)

        st.divider()

        # 오디오 업로드 또는 녹음
        st.subheader("🎙️ 음성 입력 (Audio Input)")

        audio_source = st.radio(
            "입력 방식 (Input Method)",
            ["파일 업로드 (File Upload)", "녹음하기 (Record)"],
            horizontal=True
        )

        audio_file = None

        if "파일 업로드" in audio_source or "File Upload" in audio_source:
            uploaded_file = st.file_uploader(
                "오디오 파일을 업로드하세요 (Upload audio file) - mp3, wav, m4a",
                type=['mp3', 'wav', 'm4a', 'ogg']
            )
            if uploaded_file:
                audio_file = uploaded_file
                st.audio(uploaded_file, format='audio/wav')
        else:
            # 실시간 마이크 녹음
            st.info("🎤 아래 버튼을 눌러 녹음을 시작하세요 (Click button below to start recording)")

            # 첫 사용 안내
            with st.expander("📱 마이크 권한 안내 (Microphone Permission Guide)"):
                st.markdown("""
                **처음 사용하시는 경우 (First time users):**
                1. 녹음 버튼을 누르면 브라우저에서 마이크 권한을 요청합니다 (Browser will request microphone permission)
                2. "허용" 버튼을 클릭해주세요 (Click "Allow")
                3. 마이크 아이콘이 빨간색으로 바뀌면 녹음 시작 (Recording starts when icon turns red)
                4. 문장을 또박또박 읽어주세요 (Read the sentence clearly)
                5. 다시 버튼을 눌러 녹음 종료 (Click again to stop)

                **녹음 팁 (Recording Tips):**
                - 조용한 환경에서 녹음하세요 (Record in quiet environment)
                - 마이크에 너무 가까이 말하지 마세요 (Keep 10-20cm distance from mic)
                - 자연스러운 속도로 말씀해주세요 (Speak at natural pace)
                - 배경 소음이 있으면 정확도가 떨어질 수 있습니다 (Background noise affects accuracy)
                """)

            # 오디오 녹음 컴포넌트
            audio_bytes = audio_recorder(
                text="🎙️ 녹음 시작/중지",
                recording_color="#e74c3c",
                neutral_color="#6aa84f",
                icon_name="microphone",
                icon_size="3x",
            )

            if audio_bytes:
                st.success("✅ 녹음 완료! (Recording Complete!)")
                st.audio(audio_bytes, format='audio/wav')

                # 녹음된 오디오를 임시 파일로 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                    tmp_audio.write(audio_bytes)
                    audio_file = tmp_audio.name

        # 분석 버튼
        analyze_button = st.button(
            "🔍 발음 분석 시작 (Start Analysis)",
            type="primary",
            disabled=(audio_file is None),
            use_container_width=True
        )

    with col2:
        st.header("📊 분석 결과 (Analysis Results)")

        if analyze_button and audio_file:
            with st.spinner("AI가 발음을 분석하고 있습니다... (AI is analyzing your pronunciation...)"):
                # 파일 경로 또는 파일 객체 처리
                if isinstance(audio_file, str):
                    # 녹음된 파일 (이미 경로)
                    tmp_path = audio_file
                    cleanup_needed = False
                else:
                    # 업로드된 파일 (파일 객체)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                        tmp_file.write(audio_file.read())
                        tmp_path = tmp_file.name
                    cleanup_needed = True

                try:
                    # 전체 분석 실행
                    result = st.session_state.analyzer.full_analysis(
                        tmp_path,
                        reference_text
                    )

                    # 결과 표시
                    st.success("분석 완료! (Analysis Complete!)")

                    # 인식된 텍스트
                    st.subheader("🗣️ 인식된 텍스트 (Recognized Text)")
                    st.code(result['spoken_text'], language=None)

                    # 점수 표시
                    st.subheader("🎯 발음 점수 (Pronunciation Score)")
                    score = result['pronunciation']['overall_score']

                    # 게이지 차트 (progress bar)
                    score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                    st.markdown(f"### {score_color} {score}점 (points)")
                    st.progress(score / 100)

                    # 세부 점수
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric(
                            "단어 정확도 (Word Accuracy)",
                            f"{result['pronunciation']['word_accuracy']}%"
                        )
                    with col_b:
                        st.metric(
                            "음소 유사도 (Phoneme Similarity)",
                            f"{result['pronunciation']['phoneme_similarity']}%"
                        )

                    st.divider()

                    # 피드백
                    st.subheader("💬 AI 피드백 (AI Feedback)")
                    st.markdown(result['feedback'])

                    # 틀린 단어 상세
                    if result['pronunciation']['mispronounced_words']:
                        st.divider()
                        st.subheader("❌ 개선이 필요한 부분 (Areas for Improvement)")

                        for error in result['pronunciation']['mispronounced_words']:
                            with st.container():
                                st.markdown(
                                    f"**위치 (Position) {error['position'] + 1}**: "
                                    f"`{error['expected']}` → 당신 (You): `{error['spoken']}`"
                                )

                    # 음소 상세 (옵션)
                    if show_phonemes:
                        st.divider()
                        st.subheader("🔤 음소 분석 (Phoneme Analysis)")
                        ref_phonemes = st.session_state.analyzer.get_phonemes(reference_text)
                        spoken_phonemes = st.session_state.analyzer.get_phonemes(result['spoken_text'])

                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            st.caption("참조 음소 (Reference Phonemes)")
                            st.code(' '.join(ref_phonemes), language=None)
                        with col_p2:
                            st.caption("인식 음소 (Recognized Phonemes)")
                            st.code(' '.join(spoken_phonemes), language=None)

                    # 운율 분석 (옵션)
                    if analyze_prosody and result['prosody'].get('speaking_rate', 0) > 0:
                        st.divider()
                        st.subheader("🎵 운율 분석 (Prosody Analysis)")

                        col_pr1, col_pr2, col_pr3 = st.columns(3)
                        with col_pr1:
                            st.metric("말하기 속도 (Speaking Rate)", f"{result['prosody']['speaking_rate']:.1f}")
                        with col_pr2:
                            st.metric("피치 변화 (Pitch Variation)", f"{result['prosody']['pitch_variation']:.1f}")
                        with col_pr3:
                            st.metric("에너지 변화 (Energy Variation)", f"{result['prosody']['energy_variation']:.4f}")

                    # 히스토리에 추가
                    st.session_state.history.append({
                        'reference': reference_text,
                        'spoken': result['spoken_text'],
                        'score': score
                    })

                except Exception as e:
                    st.error(f"분석 중 오류 발생 (Error during analysis): {e}")
                    st.info("오디오 파일 형식을 확인해주세요 (Please check audio file format). WAV 파일을 권장합니다 (WAV recommended).")

                finally:
                    # 임시 파일 삭제 (업로드된 파일만)
                    if cleanup_needed and os.path.exists(tmp_path):
                        os.remove(tmp_path)

        elif not audio_file:
            st.info("👆 왼쪽에서 음성을 녹음하거나 파일을 업로드하세요 (Record or upload audio on the left)")

    # 푸터
    st.divider()
    st.caption("💡 Powered by OpenAI Whisper, Pronouncing Library & AI Analysis")

    # 학습 히스토리
    if st.session_state.history:
        with st.expander("📚 최근 학습 기록 (Recent Practice History)"):
            for i, record in enumerate(reversed(st.session_state.history[-5:])):
                st.text(f"{len(st.session_state.history) - i}. {record['reference'][:50]}... - 점수 (Score): {record['score']:.1f}점")

# =============================================================================
# TAB 2: 면접 연습 (새로운 기능)
# =============================================================================
with tab2:
    # 헬퍼 함수들
    def get_filtered_questions(category=None, difficulty=None, industry=None):
        """필터링된 질문 목록 반환"""
        # 안전하게 questions 가져오기
        if not st.session_state.interview_questions_db:
            st.error("⚠️ 질문 데이터베이스를 로드할 수 없습니다.")
            return []

        questions = st.session_state.interview_questions_db.get('questions', [])
        if not questions:
            st.error("⚠️ 질문 데이터가 비어있습니다.")
            return []

        # 카테고리 매핑 (한글 → 영문)
        category_map = {
            "전체": None,
            "자기소개": "self-introduction",
            "행동 질문": "behavioral",
            "상황 질문": "situational",
            "강점/약점": "strengths-weaknesses",
            "경력 목표": "career-goals",
            "회사/직무": "company-role",
            "기술 질문": "technical"
        }

        difficulty_map = {
            "전체": None,
            "초급": "beginner",
            "중급": "intermediate",
            "고급": "advanced"
        }

        industry_map = {
            "전체": None,
            "일반": "general",
            "기술": "tech",
            "비즈니스": "business",
            "마케팅": "marketing",
            "영업": "sales"
        }

        # 괄호 앞의 한국어만 추출하는 헬퍼
        def extract_korean(text):
            if not text:
                return ""
            # "전체 (All)" → "전체"
            return text.split('(')[0].strip()

        # 필터 값 추출
        cat_korean = extract_korean(category) if category else None
        diff_korean = extract_korean(difficulty) if difficulty else None
        ind_korean = extract_korean(industry) if industry else None

        # 영문 값으로 변환
        cat_english = category_map.get(cat_korean, None)
        diff_english = difficulty_map.get(diff_korean, None)
        ind_english = industry_map.get(ind_korean, None)

        # 필터링 시작
        filtered = questions[:]  # 복사본 생성

        # 카테고리 필터
        if cat_english is not None:
            filtered = [q for q in filtered if q.get('category') == cat_english]

        # 난이도 필터
        if diff_english is not None:
            filtered = [q for q in filtered if q.get('difficulty') == diff_english]

        # 산업 필터
        if ind_english is not None:
            filtered = [q for q in filtered if q.get('industry') == ind_english]

        return filtered

    def reset_interview_session():
        """면접 세션 초기화"""
        st.session_state.interview_session_active = False
        st.session_state.interview_questions = []
        st.session_state.interview_current_index = 0
        st.session_state.interview_results = []

    # 사이드바 - 면접 설정
    with st.sidebar:
        st.header("💼 면접 설정 (Interview Settings)")

        # 연습 모드 선택
        interview_practice_mode = st.radio(
            "연습 모드 (Practice Mode)",
            ["단일 질문 연습 (Single Question)", "모의 면접 (Mock Interview) - 3-5문"],
            key="interview_practice_mode"
        )

        st.divider()

        # 질문 필터
        st.subheader("질문 필터 (Question Filters)")

        interview_category = st.selectbox(
            "카테고리 (Category)",
            ["전체 (All)", "자기소개 (Self-Intro)", "행동 질문 (Behavioral)", "상황 질문 (Situational)",
             "강점/약점 (Strengths/Weaknesses)", "경력 목표 (Career Goals)", "회사/직무 (Company/Role)", "기술 질문 (Technical)"],
            key="interview_category"
        )

        interview_difficulty = st.selectbox(
            "난이도 (Difficulty)",
            ["전체 (All)", "초급 (Beginner)", "중급 (Intermediate)", "고급 (Advanced)"],
            key="interview_difficulty"
        )

        interview_industry = st.selectbox(
            "산업 (Industry)",
            ["전체 (All)", "일반 (General)", "기술 (Tech)", "비즈니스 (Business)", "마케팅 (Marketing)", "영업 (Sales)"],
            key="interview_industry"
        )

        st.divider()

        # 모의 면접 설정
        if "모의 면접" in interview_practice_mode or "Mock Interview" in interview_practice_mode:
            num_questions = st.slider(
                "질문 수 (Number of Questions)",
                min_value=3,
                max_value=5,
                value=3,
                key="num_questions"
            )

        # 데이터베이스 상태 표시
        st.divider()
        if st.session_state.interview_questions_db:
            total_q = st.session_state.interview_questions_db.get('metadata', {}).get('total_questions', 0)
            st.caption(f"📚 전체 질문 수: {total_q}개")

            # 현재 필터로 몇 개 매칭되는지 표시
            current_filtered = get_filtered_questions(
                interview_category,
                interview_difficulty,
                interview_industry
            )
            st.caption(f"🔍 현재 필터 결과: {len(current_filtered)}개")

        # 통계
        if st.session_state.interview_history:
            st.divider()
            st.subheader("📊 면접 통계 (Interview Statistics)")
            total_interviews = len(st.session_state.interview_history)
            if total_interviews > 0:
                avg_score = sum(h['overall_score'] for h in st.session_state.interview_history) / total_interviews
                st.metric("평균 점수 (Average Score)", f"{avg_score:.1f}점")
                st.metric("총 연습 횟수 (Total Sessions)", total_interviews)

    # 메인 영역
    interview_col1, interview_col2 = st.columns([1, 1])

    with interview_col1:
        st.header("📝 질문 선택 & 녹음 (Question Selection & Recording)")

        # 단일 질문 모드
        if "단일 질문" in interview_practice_mode or "Single Question" in interview_practice_mode:
            if not st.session_state.interview_session_active:
                # 랜덤 질문 가져오기 버튼
                if st.button("🎲 랜덤 질문 가져오기 (Get Random Question)", type="primary", use_container_width=True):
                    try:
                        filtered_questions = get_filtered_questions(
                            interview_category,
                            interview_difficulty,
                            interview_industry
                        )

                        if filtered_questions:
                            import random
                            selected_question = random.choice(filtered_questions)
                            st.session_state.interview_questions = [selected_question]
                            st.session_state.interview_session_active = True
                            st.session_state.interview_current_index = 0
                            st.session_state.interview_results = []
                            st.rerun()
                        else:
                            st.warning("선택한 필터 조건에 맞는 질문이 없습니다 (No questions match selected filters).")
                            st.info("💡 '전체' 카테고리로 시도하거나 필터를 조정해보세요 (Try 'All' category or adjust filters).")
                    except Exception as e:
                        st.error(f"질문을 가져오는 중 오류가 발생했습니다 (Error loading question): {str(e)}")
                        st.info("면접 질문 데이터베이스를 확인하세요 (Please check interview questions database).")

                st.info("👆 버튼을 눌러 질문을 가져오세요 (Click button above to get a question)")

            else:
                # 현재 질문 표시
                current_question = st.session_state.interview_questions[0]

                st.subheader("🎯 현재 질문 (Current Question)")
                st.info(current_question['question'])
                st.caption(f"💬 한국어 (Korean): {current_question['question_ko']}")

                # 질문 정보
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.caption(f"📁 카테고리 (Category): {current_question['category']}")
                with col_info2:
                    st.caption(f"📊 난이도 (Difficulty): {current_question['difficulty']}")
                with col_info3:
                    st.caption(f"⏱️ 권장 시간 (Recommended Time): {current_question['ideal_duration']}초 (sec)")

                # 팁
                with st.expander("💡 답변 팁 (Answer Tips)"):
                    for tip in current_question.get('tips', []):
                        st.markdown(f"- {tip}")

                st.divider()

        # 모의 면접 모드
        else:
            if not st.session_state.interview_session_active:
                # 모의 면접 시작 버튼
                if st.button("🚀 모의 면접 시작 (Start Mock Interview)", type="primary", use_container_width=True):
                    try:
                        filtered_questions = get_filtered_questions(
                            interview_category,
                            interview_difficulty,
                            interview_industry
                        )

                        if len(filtered_questions) >= num_questions:
                            import random
                            selected_questions = random.sample(filtered_questions, num_questions)
                            st.session_state.interview_questions = selected_questions
                            st.session_state.interview_session_active = True
                            st.session_state.interview_current_index = 0
                            st.session_state.interview_results = []
                            st.rerun()
                        else:
                            st.warning(f"선택한 필터 조건에 맞는 질문이 {num_questions}개 이상 필요합니다 (Need at least {num_questions} questions). (현재 (Current): {len(filtered_questions)}개)")
                            st.info("💡 '전체' 카테고리로 시도하거나 필터를 조정해보세요 (Try 'All' category or adjust filters).")
                    except Exception as e:
                        st.error(f"모의 면접을 시작하는 중 오류가 발생했습니다 (Error starting mock interview): {str(e)}")
                        st.info("면접 질문 데이터베이스를 확인하세요 (Please check interview questions database).")

                st.info("👆 버튼을 눌러 모의 면접을 시작하세요 (Click the button above to start mock interview)")

            else:
                # 진행 상황 표시
                progress = (st.session_state.interview_current_index) / len(st.session_state.interview_questions)
                st.progress(progress)
                st.caption(f"진행 상황 (Progress): {st.session_state.interview_current_index}/{len(st.session_state.interview_questions)} 질문 완료 (questions completed)")

                # 모든 질문 완료 체크
                if st.session_state.interview_current_index >= len(st.session_state.interview_questions):
                    st.success("🎉 모든 질문을 완료했습니다! (All questions completed!)")
                    st.info("👉 오른쪽에서 최종 결과를 확인하세요 (Check final results on the right)")
                else:
                    # 현재 질문 표시
                    current_question = st.session_state.interview_questions[st.session_state.interview_current_index]

                    st.subheader(f"🎯 질문 (Question) {st.session_state.interview_current_index + 1}/{len(st.session_state.interview_questions)}")
                    st.info(current_question['question'])
                    st.caption(f"💬 한국어 (Korean): {current_question['question_ko']}")

                    # 질문 정보
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.caption(f"📁 {current_question['category']}")
                    with col_info2:
                        st.caption(f"📊 {current_question['difficulty']}")
                    with col_info3:
                        st.caption(f"⏱️ {current_question['ideal_duration']}초 (sec)")

                    # 팁
                    with st.expander("💡 답변 팁 (Answer Tips)"):
                        for tip in current_question.get('tips', []):
                            st.markdown(f"- {tip}")

                    st.divider()

        # 오디오 녹음/업로드 (세션 활성화되고 아직 질문이 남은 경우)
        if st.session_state.interview_session_active and st.session_state.interview_current_index < len(st.session_state.interview_questions):
            st.subheader("🎙️ 답변 녹음 (Record Answer)")

            interview_audio_source = st.radio(
                "입력 방식 (Input Method)",
                ["파일 업로드 (File Upload)", "녹음하기 (Record)"],
                horizontal=True,
                key="interview_audio_source"
            )

            interview_audio_file = None

            if "파일 업로드" in interview_audio_source or "File Upload" in interview_audio_source:
                uploaded_interview_file = st.file_uploader(
                    "오디오 파일을 업로드하세요 (Upload audio file)",
                    type=['mp3', 'wav', 'm4a', 'ogg'],
                    key="interview_audio_upload"
                )
                if uploaded_interview_file:
                    interview_audio_file = uploaded_interview_file
                    st.audio(uploaded_interview_file, format='audio/wav')
            else:
                st.info("🎤 아래 버튼을 눌러 녹음을 시작하세요 (Click the button below to start recording)")

                interview_audio_bytes = audio_recorder(
                    text="🎙️ 녹음 시작/중지",
                    recording_color="#e74c3c",
                    neutral_color="#6aa84f",
                    icon_name="microphone",
                    icon_size="3x",
                    key="interview_audio_recorder"
                )

                if interview_audio_bytes:
                    st.success("✅ 녹음 완료! (Recording Complete!)")
                    st.audio(interview_audio_bytes, format='audio/wav')

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                        tmp_audio.write(interview_audio_bytes)
                        interview_audio_file = tmp_audio.name

            # 분석 버튼
            interview_analyze_button = st.button(
                "🔍 답변 분석 시작 (Start Answer Analysis)",
                type="primary",
                disabled=(interview_audio_file is None),
                use_container_width=True,
                key="interview_analyze_button"
            )
        else:
            interview_analyze_button = False
            interview_audio_file = None

        # 새로운 연습 시작 버튼 (세션 활성화된 경우)
        if st.session_state.interview_session_active:
            st.divider()
            if st.button("🔄 새로운 연습 시작 (Start New Practice)", key="reset_interview"):
                reset_interview_session()
                st.rerun()

    with interview_col2:
        st.header("📊 분석 결과 (Analysis Results)")

        # 분석 실행
        if interview_analyze_button and interview_audio_file:
            with st.spinner("AI가 면접 답변을 분석하고 있습니다 (AI is analyzing your interview answer)..."):
                current_question = st.session_state.interview_questions[st.session_state.interview_current_index]

                # 파일 경로 처리
                if isinstance(interview_audio_file, str):
                    tmp_path = interview_audio_file
                    cleanup_needed = False
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                        tmp_file.write(interview_audio_file.read())
                        tmp_path = tmp_file.name
                    cleanup_needed = True

                try:
                    # 면접 답변 분석
                    result = st.session_state.interview_analyzer.analyze_interview_answer(
                        tmp_path,
                        current_question
                    )

                    # 결과 저장
                    st.session_state.interview_results.append({
                        'question': current_question,
                        'result': result
                    })

                    # 결과 표시
                    st.success("✅ 분석 완료! (Analysis Complete!)")

                    # 인식된 텍스트
                    st.subheader("🗣️ 답변 내용 (Answer Transcription)")
                    st.code(result['transcription'], language=None)

                    # 전체 점수
                    st.subheader("🎯 종합 점수 (Overall Score)")
                    overall_score = result['overall_score']
                    score_color = "🟢" if overall_score >= 80 else "🟡" if overall_score >= 60 else "🔴"
                    st.markdown(f"### {score_color} {overall_score:.1f}점")
                    st.progress(overall_score / 100)

                    # 세부 점수
                    st.subheader("📊 세부 점수 (Detailed Scores)")
                    score_cols = st.columns(5)

                    scores_info = [
                        ("발음 (Pronunciation)", result['scores']['pronunciation'], "🗣️"),
                        ("내용 (Content)", result['scores']['content'], "📝"),
                        ("구조 (Structure)", result['scores']['structure'], "🏗️"),
                        ("문법 (Grammar)", result['scores']['grammar'], "✍️"),
                        ("시간 (Duration)", result['scores']['duration'], "⏱️")
                    ]

                    for col, (label, score, emoji) in zip(score_cols, scores_info):
                        with col:
                            st.metric(
                                f"{emoji} {label}",
                                f"{score:.0f}",
                                delta=None
                            )

                    st.divider()

                    # 피드백
                    st.subheader("💬 AI 피드백 (AI Feedback)")
                    st.markdown(result['feedback'])

                    # Filler words
                    if result['filler_words']['count'] > 0:
                        st.divider()
                        st.subheader("🔤 Filler Words 분석 (Filler Words Analysis)")
                        st.caption(f"총 (Total) {result['filler_words']['count']}개 발견 (found) (밀도 (Density): {result['filler_words']['density']:.1f}%)")

                        filler_words_list = [f"{word}: {count}회" for word, count in result['filler_words']['words'].items()]
                        st.write(", ".join(filler_words_list))

                    # 개선 제안
                    if result['improvements']:
                        st.divider()
                        st.subheader("💡 개선 제안 (Improvement Suggestions)")
                        for improvement in result['improvements']:
                            st.markdown(f"- {improvement}")

                    # 다음 질문으로 이동 (모의 면접 모드)
                    if "모의 면접" in interview_practice_mode or "Mock Interview" in interview_practice_mode:
                        st.divider()
                        st.session_state.interview_current_index += 1

                        if st.session_state.interview_current_index < len(st.session_state.interview_questions):
                            if st.button("➡️ 다음 질문으로 (Next Question)", type="primary", use_container_width=True, key="next_question"):
                                st.rerun()
                        else:
                            st.success("🎉 모든 질문을 완료했습니다! (All questions completed!)")

                            # 히스토리에 추가
                            st.session_state.interview_history.append({
                                'mode': 'mock',
                                'num_questions': len(st.session_state.interview_questions),
                                'overall_score': sum(r['result']['overall_score'] for r in st.session_state.interview_results) / len(st.session_state.interview_results),
                                'results': st.session_state.interview_results
                            })
                    else:
                        # 단일 질문 모드 - 히스토리에 추가
                        st.session_state.interview_history.append({
                            'mode': 'single',
                            'num_questions': 1,
                            'overall_score': result['overall_score'],
                            'results': [{'question': current_question, 'result': result}]
                        })

                except Exception as e:
                    st.error(f"분석 중 오류 발생 (Error during analysis): {e}")
                    st.info("오디오 파일 형식을 확인해주세요 (Please check audio file format).")

                finally:
                    if cleanup_needed and os.path.exists(tmp_path):
                        os.remove(tmp_path)

        # 최종 결과 대시보드 (모의 면접 완료 시)
        elif st.session_state.interview_session_active and ("모의 면접" in interview_practice_mode or "Mock Interview" in interview_practice_mode) and st.session_state.interview_current_index >= len(st.session_state.interview_questions):
            st.subheader("📈 최종 결과 대시보드 (Final Results Dashboard)")

            if st.session_state.interview_results:
                # 평균 점수
                all_scores = [r['result']['overall_score'] for r in st.session_state.interview_results]
                avg_score = sum(all_scores) / len(all_scores)

                score_color = "🟢" if avg_score >= 80 else "🟡" if avg_score >= 60 else "🔴"
                st.markdown(f"### {score_color} 평균 점수 (Average Score): {avg_score:.1f}점")
                st.progress(avg_score / 100)

                st.divider()

                # 각 질문별 점수
                st.subheader("📝 질문별 상세 점수 (Detailed Scores by Question)")
                for i, item in enumerate(st.session_state.interview_results):
                    with st.expander(f"질문 (Question) {i+1}: {item['question']['question'][:50]}..."):
                        result = item['result']

                        st.caption(f"**종합 점수 (Overall Score):** {result['overall_score']:.1f}점")

                        score_detail_cols = st.columns(5)
                        scores = [
                            ("발음 (Pronunciation)", result['scores']['pronunciation']),
                            ("내용 (Content)", result['scores']['content']),
                            ("구조 (Structure)", result['scores']['structure']),
                            ("문법 (Grammar)", result['scores']['grammar']),
                            ("시간 (Duration)", result['scores']['duration'])
                        ]

                        for col, (label, score) in zip(score_detail_cols, scores):
                            with col:
                                st.caption(f"{label}: {score:.0f}")

                        st.caption(f"**답변 (Answer):** {result['transcription'][:100]}...")

                st.divider()

                # 평균 세부 점수
                st.subheader("📊 평균 세부 점수 (Average Detailed Scores)")
                avg_scores_cols = st.columns(5)

                avg_pronunciation = sum(r['result']['scores']['pronunciation'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)
                avg_content = sum(r['result']['scores']['content'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)
                avg_structure = sum(r['result']['scores']['structure'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)
                avg_grammar = sum(r['result']['scores']['grammar'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)
                avg_duration = sum(r['result']['scores']['duration'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)

                avg_scores_data = [
                    ("발음 (Pronunciation)", avg_pronunciation, "🗣️"),
                    ("내용 (Content)", avg_content, "📝"),
                    ("구조 (Structure)", avg_structure, "🏗️"),
                    ("문법 (Grammar)", avg_grammar, "✍️"),
                    ("시간 (Duration)", avg_duration, "⏱️")
                ]

                for col, (label, score, emoji) in zip(avg_scores_cols, avg_scores_data):
                    with col:
                        st.metric(f"{emoji} {label}", f"{score:.1f}")

                # 강점과 약점
                st.divider()
                st.subheader("💪 강점 및 개선 영역 (Strengths & Areas for Improvement)")

                scores_dict = {
                    "발음 (Pronunciation)": avg_pronunciation,
                    "내용 (Content)": avg_content,
                    "구조 (Structure)": avg_structure,
                    "문법 (Grammar)": avg_grammar,
                    "시간 관리 (Time Management)": avg_duration
                }

                max_score_area = max(scores_dict, key=scores_dict.get)
                min_score_area = min(scores_dict, key=scores_dict.get)

                strength_col, weakness_col = st.columns(2)
                with strength_col:
                    st.success(f"**강점 (Strength):** {max_score_area} ({scores_dict[max_score_area]:.1f}점)")
                with weakness_col:
                    st.warning(f"**개선 필요 (Needs Improvement):** {min_score_area} ({scores_dict[min_score_area]:.1f}점)")

        elif not st.session_state.interview_session_active:
            st.info("👈 왼쪽에서 질문을 선택하세요 (Select a question on the left)")
        elif interview_audio_file is None:
            st.info("🎙️ 왼쪽에서 답변을 녹음하세요 (Record your answer on the left)")

    # 푸터
    st.divider()
    st.caption("💡 Powered by OpenAI Whisper & AI Interview Analysis")

    # 면접 히스토리
    if st.session_state.interview_history:
        with st.expander("📚 최근 면접 기록 (Recent Interview History)"):
            for i, record in enumerate(reversed(st.session_state.interview_history[-5:])):
                mode_text = "모의 면접 (Mock Interview)" if record['mode'] == 'mock' else "단일 질문 (Single Question)"
                st.text(f"{len(st.session_state.interview_history) - i}. {mode_text} ({record['num_questions']}문) - 평균 (Avg): {record['overall_score']:.1f}점")
