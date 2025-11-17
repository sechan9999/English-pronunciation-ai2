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
from interview.interview_analyzer import InterviewAnalyzer, load_questions

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
    st.session_state.interview_questions_db = load_questions()
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
tab1, tab2 = st.tabs(["🗣️ 발음 연습", "💼 면접 연습"])

# =============================================================================
# TAB 1: 발음 연습 (기존 기능)
# =============================================================================
with tab1:
    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 설정")

        # 연습 문장 선택
        practice_mode = st.selectbox(
            "연습 모드",
            ["기본 문장", "사용자 입력", "일상 회화", "비즈니스 영어"]
        )

        if practice_mode == "사용자 입력":
            custom_text = st.text_area(
                "연습할 문장을 입력하세요",
                placeholder="예: How are you doing today?"
            )
            reference_text = custom_text if custom_text else "Hello world"
        elif practice_mode == "일상 회화":
            reference_text = st.selectbox(
                "문장 선택",
                [
                    "How are you doing today?",
                    "Nice to meet you",
                    "What's the weather like?",
                    "I'd like a cup of coffee please"
                ]
            )
        elif practice_mode == "비즈니스 영어":
            reference_text = st.selectbox(
                "문장 선택",
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
        st.subheader("분석 옵션")
        analyze_prosody = st.checkbox("운율 분석 (속도, 억양)", value=True)
        show_phonemes = st.checkbox("음소 상세 보기", value=False)

        st.divider()

        # 통계
        if st.session_state.history:
            st.subheader("📈 학습 통계")
            avg_score = sum(h['score'] for h in st.session_state.history) / len(st.session_state.history)
            st.metric("평균 점수", f"{avg_score:.1f}점")
            st.metric("총 연습 횟수", len(st.session_state.history))

    # 메인 영역
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("🎯 연습할 문장")
        st.info(reference_text)

        # 발음 팁
        with st.expander("💡 발음 팁"):
            st.markdown("""
            - 천천히, 또박또박 발음하세요
            - 각 단어의 강세를 신경쓰세요
            - 자연스러운 속도로 말하세요
            - 문장 끝의 억양에 주의하세요
            """)

        st.divider()

        # 오디오 업로드 또는 녹음
        st.subheader("🎙️ 음성 입력")

        audio_source = st.radio(
            "입력 방식",
            ["파일 업로드", "녹음하기"],
            horizontal=True
        )

        audio_file = None

        if audio_source == "파일 업로드":
            uploaded_file = st.file_uploader(
                "오디오 파일을 업로드하세요 (mp3, wav, m4a)",
                type=['mp3', 'wav', 'm4a', 'ogg']
            )
            if uploaded_file:
                audio_file = uploaded_file
                st.audio(uploaded_file, format='audio/wav')
        else:
            # 실시간 마이크 녹음
            st.info("🎤 아래 버튼을 눌러 녹음을 시작하세요")

            # 첫 사용 안내
            with st.expander("📱 마이크 권한 안내"):
                st.markdown("""
                **처음 사용하시는 경우:**
                1. 녹음 버튼을 누르면 브라우저에서 마이크 권한을 요청합니다
                2. "허용" 버튼을 클릭해주세요
                3. 마이크 아이콘이 빨간색으로 바뀌면 녹음 시작
                4. 문장을 또박또박 읽어주세요
                5. 다시 버튼을 눌러 녹음 종료

                **녹음 팁:**
                - 조용한 환경에서 녹음하세요
                - 마이크에 너무 가까이 말하지 마세요 (10-20cm 거리)
                - 자연스러운 속도로 말씀해주세요
                - 배경 소음이 있으면 정확도가 떨어질 수 있습니다
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
                st.success("✅ 녹음 완료!")
                st.audio(audio_bytes, format='audio/wav')

                # 녹음된 오디오를 임시 파일로 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                    tmp_audio.write(audio_bytes)
                    audio_file = tmp_audio.name

        # 분석 버튼
        analyze_button = st.button(
            "🔍 발음 분석 시작",
            type="primary",
            disabled=(audio_file is None),
            use_container_width=True
        )

    with col2:
        st.header("📊 분석 결과")

        if analyze_button and audio_file:
            with st.spinner("AI가 발음을 분석하고 있습니다..."):
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
                    st.success("분석 완료!")

                    # 인식된 텍스트
                    st.subheader("🗣️ 인식된 텍스트")
                    st.code(result['spoken_text'], language=None)

                    # 점수 표시
                    st.subheader("🎯 발음 점수")
                    score = result['pronunciation']['overall_score']

                    # 게이지 차트 (progress bar)
                    score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                    st.markdown(f"### {score_color} {score}점")
                    st.progress(score / 100)

                    # 세부 점수
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric(
                            "단어 정확도",
                            f"{result['pronunciation']['word_accuracy']}%"
                        )
                    with col_b:
                        st.metric(
                            "음소 유사도",
                            f"{result['pronunciation']['phoneme_similarity']}%"
                        )

                    st.divider()

                    # 피드백
                    st.subheader("💬 AI 피드백")
                    st.markdown(result['feedback'])

                    # 틀린 단어 상세
                    if result['pronunciation']['mispronounced_words']:
                        st.divider()
                        st.subheader("❌ 개선이 필요한 부분")

                        for error in result['pronunciation']['mispronounced_words']:
                            with st.container():
                                st.markdown(
                                    f"**위치 {error['position'] + 1}**: "
                                    f"`{error['expected']}` → 당신: `{error['spoken']}`"
                                )

                    # 음소 상세 (옵션)
                    if show_phonemes:
                        st.divider()
                        st.subheader("🔤 음소 분석")
                        ref_phonemes = st.session_state.analyzer.get_phonemes(reference_text)
                        spoken_phonemes = st.session_state.analyzer.get_phonemes(result['spoken_text'])

                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            st.caption("참조 음소")
                            st.code(' '.join(ref_phonemes), language=None)
                        with col_p2:
                            st.caption("인식 음소")
                            st.code(' '.join(spoken_phonemes), language=None)

                    # 운율 분석 (옵션)
                    if analyze_prosody and result['prosody'].get('speaking_rate', 0) > 0:
                        st.divider()
                        st.subheader("🎵 운율 분석")

                        col_pr1, col_pr2, col_pr3 = st.columns(3)
                        with col_pr1:
                            st.metric("말하기 속도", f"{result['prosody']['speaking_rate']:.1f}")
                        with col_pr2:
                            st.metric("피치 변화", f"{result['prosody']['pitch_variation']:.1f}")
                        with col_pr3:
                            st.metric("에너지 변화", f"{result['prosody']['energy_variation']:.4f}")

                    # 히스토리에 추가
                    st.session_state.history.append({
                        'reference': reference_text,
                        'spoken': result['spoken_text'],
                        'score': score
                    })

                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
                    st.info("오디오 파일 형식을 확인해주세요. WAV 파일을 권장합니다.")

                finally:
                    # 임시 파일 삭제 (업로드된 파일만)
                    if cleanup_needed and os.path.exists(tmp_path):
                        os.remove(tmp_path)

        elif not audio_file:
            st.info("👆 왼쪽에서 음성을 녹음하거나 파일을 업로드하세요")

    # 푸터
    st.divider()
    st.caption("💡 Powered by OpenAI Whisper, Pronouncing Library & AI Analysis")

    # 학습 히스토리
    if st.session_state.history:
        with st.expander("📚 최근 학습 기록"):
            for i, record in enumerate(reversed(st.session_state.history[-5:])):
                st.text(f"{len(st.session_state.history) - i}. {record['reference'][:50]}... - 점수: {record['score']:.1f}점")

# =============================================================================
# TAB 2: 면접 연습 (새로운 기능)
# =============================================================================
with tab2:
    # 헬퍼 함수들
    def get_filtered_questions(category=None, difficulty=None, industry=None):
        """필터링된 질문 목록 반환"""
        questions = st.session_state.interview_questions_db['questions']
        filtered = questions

        if category and category != "전체":
            category_map = {
                "자기소개": "self-introduction",
                "행동 질문": "behavioral",
                "상황 질문": "situational",
                "강점/약점": "strengths-weaknesses",
                "경력 목표": "career-goals",
                "회사/직무": "company-role",
                "기술 질문": "technical"
            }
            filtered = [q for q in filtered if q['category'] == category_map.get(category, category)]

        if difficulty and difficulty != "전체":
            difficulty_map = {"초급": "beginner", "중급": "intermediate", "고급": "advanced"}
            filtered = [q for q in filtered if q['difficulty'] == difficulty_map.get(difficulty, difficulty)]

        if industry and industry != "전체":
            industry_map = {"일반": "general", "기술": "tech", "비즈니스": "business", "마케팅": "marketing", "영업": "sales"}
            filtered = [q for q in filtered if q['industry'] == industry_map.get(industry, industry)]

        return filtered

    def reset_interview_session():
        """면접 세션 초기화"""
        st.session_state.interview_session_active = False
        st.session_state.interview_questions = []
        st.session_state.interview_current_index = 0
        st.session_state.interview_results = []

    # 사이드바 - 면접 설정
    with st.sidebar:
        st.header("💼 면접 설정")

        # 연습 모드 선택
        interview_practice_mode = st.radio(
            "연습 모드",
            ["단일 질문 연습", "모의 면접 (3-5문)"],
            key="interview_practice_mode"
        )

        st.divider()

        # 질문 필터
        st.subheader("질문 필터")

        interview_category = st.selectbox(
            "카테고리",
            ["전체", "자기소개", "행동 질문", "상황 질문", "강점/약점", "경력 목표", "회사/직무", "기술 질문"],
            key="interview_category"
        )

        interview_difficulty = st.selectbox(
            "난이도",
            ["전체", "초급", "중급", "고급"],
            key="interview_difficulty"
        )

        interview_industry = st.selectbox(
            "산업",
            ["전체", "일반", "기술", "비즈니스", "마케팅", "영업"],
            key="interview_industry"
        )

        st.divider()

        # 모의 면접 설정
        if interview_practice_mode == "모의 면접 (3-5문)":
            num_questions = st.slider(
                "질문 수",
                min_value=3,
                max_value=5,
                value=3,
                key="num_questions"
            )

        # 통계
        if st.session_state.interview_history:
            st.subheader("📊 면접 통계")
            total_interviews = len(st.session_state.interview_history)
            if total_interviews > 0:
                avg_score = sum(h['overall_score'] for h in st.session_state.interview_history) / total_interviews
                st.metric("평균 점수", f"{avg_score:.1f}점")
                st.metric("총 연습 횟수", total_interviews)

    # 메인 영역
    interview_col1, interview_col2 = st.columns([1, 1])

    with interview_col1:
        st.header("📝 질문 선택 & 녹음")

        # 단일 질문 모드
        if interview_practice_mode == "단일 질문 연습":
            if not st.session_state.interview_session_active:
                # 랜덤 질문 가져오기 버튼
                if st.button("🎲 랜덤 질문 가져오기", type="primary", use_container_width=True):
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
                        st.warning("선택한 필터 조건에 맞는 질문이 없습니다.")

                st.info("👆 버튼을 눌러 질문을 가져오세요")

            else:
                # 현재 질문 표시
                current_question = st.session_state.interview_questions[0]

                st.subheader("🎯 현재 질문")
                st.info(current_question['question'])
                st.caption(f"💬 한국어: {current_question['question_ko']}")

                # 질문 정보
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.caption(f"📁 카테고리: {current_question['category']}")
                with col_info2:
                    st.caption(f"📊 난이도: {current_question['difficulty']}")
                with col_info3:
                    st.caption(f"⏱️ 권장 시간: {current_question['ideal_duration']}초")

                # 팁
                with st.expander("💡 답변 팁"):
                    for tip in current_question.get('tips', []):
                        st.markdown(f"- {tip}")

                st.divider()

        # 모의 면접 모드
        else:
            if not st.session_state.interview_session_active:
                # 모의 면접 시작 버튼
                if st.button("🚀 모의 면접 시작", type="primary", use_container_width=True):
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
                        st.warning(f"선택한 필터 조건에 맞는 질문이 {num_questions}개 이상 필요합니다. (현재: {len(filtered_questions)}개)")

                st.info("👆 버튼을 눌러 모의 면접을 시작하세요")

            else:
                # 진행 상황 표시
                progress = (st.session_state.interview_current_index) / len(st.session_state.interview_questions)
                st.progress(progress)
                st.caption(f"진행 상황: {st.session_state.interview_current_index}/{len(st.session_state.interview_questions)} 질문 완료")

                # 모든 질문 완료 체크
                if st.session_state.interview_current_index >= len(st.session_state.interview_questions):
                    st.success("🎉 모든 질문을 완료했습니다!")
                    st.info("👉 오른쪽에서 최종 결과를 확인하세요")
                else:
                    # 현재 질문 표시
                    current_question = st.session_state.interview_questions[st.session_state.interview_current_index]

                    st.subheader(f"🎯 질문 {st.session_state.interview_current_index + 1}/{len(st.session_state.interview_questions)}")
                    st.info(current_question['question'])
                    st.caption(f"💬 한국어: {current_question['question_ko']}")

                    # 질문 정보
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.caption(f"📁 {current_question['category']}")
                    with col_info2:
                        st.caption(f"📊 {current_question['difficulty']}")
                    with col_info3:
                        st.caption(f"⏱️ {current_question['ideal_duration']}초")

                    # 팁
                    with st.expander("💡 답변 팁"):
                        for tip in current_question.get('tips', []):
                            st.markdown(f"- {tip}")

                    st.divider()

        # 오디오 녹음/업로드 (세션 활성화되고 아직 질문이 남은 경우)
        if st.session_state.interview_session_active and st.session_state.interview_current_index < len(st.session_state.interview_questions):
            st.subheader("🎙️ 답변 녹음")

            interview_audio_source = st.radio(
                "입력 방식",
                ["파일 업로드", "녹음하기"],
                horizontal=True,
                key="interview_audio_source"
            )

            interview_audio_file = None

            if interview_audio_source == "파일 업로드":
                uploaded_interview_file = st.file_uploader(
                    "오디오 파일을 업로드하세요",
                    type=['mp3', 'wav', 'm4a', 'ogg'],
                    key="interview_audio_upload"
                )
                if uploaded_interview_file:
                    interview_audio_file = uploaded_interview_file
                    st.audio(uploaded_interview_file, format='audio/wav')
            else:
                st.info("🎤 아래 버튼을 눌러 녹음을 시작하세요")

                interview_audio_bytes = audio_recorder(
                    text="🎙️ 녹음 시작/중지",
                    recording_color="#e74c3c",
                    neutral_color="#6aa84f",
                    icon_name="microphone",
                    icon_size="3x",
                    key="interview_audio_recorder"
                )

                if interview_audio_bytes:
                    st.success("✅ 녹음 완료!")
                    st.audio(interview_audio_bytes, format='audio/wav')

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                        tmp_audio.write(interview_audio_bytes)
                        interview_audio_file = tmp_audio.name

            # 분석 버튼
            interview_analyze_button = st.button(
                "🔍 답변 분석 시작",
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
            if st.button("🔄 새로운 연습 시작", key="reset_interview"):
                reset_interview_session()
                st.rerun()

    with interview_col2:
        st.header("📊 분석 결과")

        # 분석 실행
        if interview_analyze_button and interview_audio_file:
            with st.spinner("AI가 면접 답변을 분석하고 있습니다..."):
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
                    st.success("✅ 분석 완료!")

                    # 인식된 텍스트
                    st.subheader("🗣️ 답변 내용")
                    st.code(result['transcription'], language=None)

                    # 전체 점수
                    st.subheader("🎯 종합 점수")
                    overall_score = result['overall_score']
                    score_color = "🟢" if overall_score >= 80 else "🟡" if overall_score >= 60 else "🔴"
                    st.markdown(f"### {score_color} {overall_score:.1f}점")
                    st.progress(overall_score / 100)

                    # 세부 점수
                    st.subheader("📊 세부 점수")
                    score_cols = st.columns(5)

                    scores_info = [
                        ("발음", result['scores']['pronunciation'], "🗣️"),
                        ("내용", result['scores']['content'], "📝"),
                        ("구조", result['scores']['structure'], "🏗️"),
                        ("문법", result['scores']['grammar'], "✍️"),
                        ("시간", result['scores']['duration'], "⏱️")
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
                    st.subheader("💬 AI 피드백")
                    st.markdown(result['feedback'])

                    # Filler words
                    if result['filler_words']['count'] > 0:
                        st.divider()
                        st.subheader("🔤 Filler Words 분석")
                        st.caption(f"총 {result['filler_words']['count']}개 발견 (밀도: {result['filler_words']['density']:.1f}%)")

                        filler_words_list = [f"{word}: {count}회" for word, count in result['filler_words']['words'].items()]
                        st.write(", ".join(filler_words_list))

                    # 개선 제안
                    if result['improvements']:
                        st.divider()
                        st.subheader("💡 개선 제안")
                        for improvement in result['improvements']:
                            st.markdown(f"- {improvement}")

                    # 다음 질문으로 이동 (모의 면접 모드)
                    if interview_practice_mode == "모의 면접 (3-5문)":
                        st.divider()
                        st.session_state.interview_current_index += 1

                        if st.session_state.interview_current_index < len(st.session_state.interview_questions):
                            if st.button("➡️ 다음 질문으로", type="primary", use_container_width=True, key="next_question"):
                                st.rerun()
                        else:
                            st.success("🎉 모든 질문을 완료했습니다!")

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
                    st.error(f"분석 중 오류 발생: {e}")
                    st.info("오디오 파일 형식을 확인해주세요.")

                finally:
                    if cleanup_needed and os.path.exists(tmp_path):
                        os.remove(tmp_path)

        # 최종 결과 대시보드 (모의 면접 완료 시)
        elif st.session_state.interview_session_active and interview_practice_mode == "모의 면접 (3-5문)" and st.session_state.interview_current_index >= len(st.session_state.interview_questions):
            st.subheader("📈 최종 결과 대시보드")

            if st.session_state.interview_results:
                # 평균 점수
                all_scores = [r['result']['overall_score'] for r in st.session_state.interview_results]
                avg_score = sum(all_scores) / len(all_scores)

                score_color = "🟢" if avg_score >= 80 else "🟡" if avg_score >= 60 else "🔴"
                st.markdown(f"### {score_color} 평균 점수: {avg_score:.1f}점")
                st.progress(avg_score / 100)

                st.divider()

                # 각 질문별 점수
                st.subheader("📝 질문별 상세 점수")
                for i, item in enumerate(st.session_state.interview_results):
                    with st.expander(f"질문 {i+1}: {item['question']['question'][:50]}..."):
                        result = item['result']

                        st.caption(f"**종합 점수:** {result['overall_score']:.1f}점")

                        score_detail_cols = st.columns(5)
                        scores = [
                            ("발음", result['scores']['pronunciation']),
                            ("내용", result['scores']['content']),
                            ("구조", result['scores']['structure']),
                            ("문법", result['scores']['grammar']),
                            ("시간", result['scores']['duration'])
                        ]

                        for col, (label, score) in zip(score_detail_cols, scores):
                            with col:
                                st.caption(f"{label}: {score:.0f}")

                        st.caption(f"**답변:** {result['transcription'][:100]}...")

                st.divider()

                # 평균 세부 점수
                st.subheader("📊 평균 세부 점수")
                avg_scores_cols = st.columns(5)

                avg_pronunciation = sum(r['result']['scores']['pronunciation'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)
                avg_content = sum(r['result']['scores']['content'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)
                avg_structure = sum(r['result']['scores']['structure'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)
                avg_grammar = sum(r['result']['scores']['grammar'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)
                avg_duration = sum(r['result']['scores']['duration'] for r in st.session_state.interview_results) / len(st.session_state.interview_results)

                avg_scores_data = [
                    ("발음", avg_pronunciation, "🗣️"),
                    ("내용", avg_content, "📝"),
                    ("구조", avg_structure, "🏗️"),
                    ("문법", avg_grammar, "✍️"),
                    ("시간", avg_duration, "⏱️")
                ]

                for col, (label, score, emoji) in zip(avg_scores_cols, avg_scores_data):
                    with col:
                        st.metric(f"{emoji} {label}", f"{score:.1f}")

                # 강점과 약점
                st.divider()
                st.subheader("💪 강점 및 개선 영역")

                scores_dict = {
                    "발음": avg_pronunciation,
                    "내용": avg_content,
                    "구조": avg_structure,
                    "문법": avg_grammar,
                    "시간 관리": avg_duration
                }

                max_score_area = max(scores_dict, key=scores_dict.get)
                min_score_area = min(scores_dict, key=scores_dict.get)

                strength_col, weakness_col = st.columns(2)
                with strength_col:
                    st.success(f"**강점:** {max_score_area} ({scores_dict[max_score_area]:.1f}점)")
                with weakness_col:
                    st.warning(f"**개선 필요:** {min_score_area} ({scores_dict[min_score_area]:.1f}점)")

        elif not st.session_state.interview_session_active:
            st.info("👈 왼쪽에서 질문을 선택하세요")
        elif interview_audio_file is None:
            st.info("🎙️ 왼쪽에서 답변을 녹음하세요")

    # 푸터
    st.divider()
    st.caption("💡 Powered by OpenAI Whisper & AI Interview Analysis")

    # 면접 히스토리
    if st.session_state.interview_history:
        with st.expander("📚 최근 면접 기록"):
            for i, record in enumerate(reversed(st.session_state.interview_history[-5:])):
                mode_text = "모의 면접" if record['mode'] == 'mock' else "단일 질문"
                st.text(f"{len(st.session_state.interview_history) - i}. {mode_text} ({record['num_questions']}문) - 평균: {record['overall_score']:.1f}점")
