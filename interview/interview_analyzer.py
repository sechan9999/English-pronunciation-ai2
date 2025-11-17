"""
면접 답변 분석 모듈
Interview Answer Analysis Module

기능:
- 발음 분석 (기존 PronunciationAnalyzer 활용)
- 답변 내용 평가
- 구조 분석 (STAR method)
- 문법 체크
- 필러 워드 감지
- 시간 관리 평가
"""

import re
import json
from typing import Dict, List, Tuple
from pathlib import Path
import librosa

# 부모 디렉토리의 pronunciation_analyzer import
import sys
sys.path.append(str(Path(__file__).parent.parent))
from pronunciation_analyzer import PronunciationAnalyzer


class InterviewAnalyzer:
    """면접 답변 종합 분석 클래스"""

    # 필러 워드 목록
    FILLER_WORDS = [
        'um', 'uh', 'er', 'ah', 'like', 'you know', 'i mean',
        'actually', 'basically', 'literally', 'sort of', 'kind of'
    ]

    # STAR 메서드 키워드
    STAR_KEYWORDS = {
        'situation': ['situation', 'context', 'background', 'when', 'where'],
        'task': ['task', 'challenge', 'problem', 'goal', 'objective', 'responsibility'],
        'action': ['action', 'did', 'implemented', 'created', 'developed', 'used', 'applied'],
        'result': ['result', 'outcome', 'achieved', 'accomplished', 'improved', 'success', 'learned']
    }

    def __init__(self, pronunciation_analyzer: PronunciationAnalyzer = None):
        """
        초기화
        Args:
            pronunciation_analyzer: 기존 발음 분석기 (없으면 새로 생성)
        """
        self.pronunciation_analyzer = pronunciation_analyzer or PronunciationAnalyzer()

    def analyze_interview_answer(
        self,
        audio_path: str,
        question: Dict,
        reference_answer: str = None
    ) -> Dict:
        """
        면접 답변 종합 분석

        Args:
            audio_path: 오디오 파일 경로
            question: 질문 정보 딕셔너리
            reference_answer: 참조 답변 (선택)

        Returns:
            종합 분석 결과 딕셔너리
        """
        # 1. STT 및 발음 분석
        transcription = self.pronunciation_analyzer.transcribe_audio(audio_path)

        # 2. 발음 점수 (참조 답변이 있으면 사용, 없으면 전사 텍스트 그대로)
        if reference_answer:
            pronunciation_result = self.pronunciation_analyzer.calculate_pronunciation_score(
                reference_answer,
                transcription
            )
        else:
            # 참조 답변이 없을 때는 기본 점수
            pronunciation_result = {
                'overall_score': 85.0,
                'word_accuracy': 85.0,
                'phoneme_similarity': 85.0
            }

        # 3. 운율 분석
        prosody_result = self.pronunciation_analyzer.analyze_prosody(audio_path)

        # 4. 내용 분석
        content_score = self.evaluate_content(transcription, question)

        # 5. 구조 분석 (STAR)
        structure_score = self.analyze_structure(transcription)

        # 6. 문법 분석
        grammar_score = self.check_grammar(transcription)

        # 7. 필러 워드 감지
        filler_analysis = self.detect_fillers(transcription)

        # 8. 시간 분석
        duration = self.get_audio_duration(audio_path)
        duration_score = self.evaluate_duration(duration, question.get('ideal_duration', 90))

        # 9. 종합 점수 계산
        overall_score = self.calculate_overall_interview_score(
            pronunciation_score=pronunciation_result['overall_score'],
            content_score=content_score,
            structure_score=structure_score,
            grammar_score=grammar_score,
            duration_score=duration_score
        )

        # 10. 피드백 생성
        feedback = self.generate_interview_feedback(
            transcription=transcription,
            question=question,
            scores={
                'overall': overall_score,
                'pronunciation': pronunciation_result['overall_score'],
                'content': content_score,
                'structure': structure_score,
                'grammar': grammar_score,
                'duration': duration_score
            },
            filler_analysis=filler_analysis,
            duration=duration
        )

        # 11. 개선 제안
        improvements = self.suggest_improvements(
            transcription=transcription,
            question=question,
            scores={
                'content': content_score,
                'structure': structure_score,
                'grammar': grammar_score,
                'duration': duration_score
            },
            filler_analysis=filler_analysis
        )

        return {
            'transcription': transcription,
            'duration': duration,
            'scores': {
                'overall': overall_score,
                'pronunciation': pronunciation_result['overall_score'],
                'content': content_score,
                'structure': structure_score,
                'grammar': grammar_score,
                'duration': duration_score
            },
            'pronunciation_details': pronunciation_result,
            'prosody': prosody_result,
            'filler_words': filler_analysis,
            'feedback': feedback,
            'improvements': improvements,
            'question': question
        }

    def evaluate_content(self, transcription: str, question: Dict) -> float:
        """
        답변 내용 평가 (키워드 기반)

        Args:
            transcription: 전사된 텍스트
            question: 질문 정보

        Returns:
            내용 점수 (0-100)
        """
        if not transcription:
            return 0.0

        transcription_lower = transcription.lower()
        keywords = question.get('keywords', [])

        if not keywords:
            return 70.0  # 기본 점수

        # 키워드 매칭
        matched_keywords = sum(1 for keyword in keywords if keyword.lower() in transcription_lower)
        keyword_score = (matched_keywords / len(keywords)) * 100

        # 답변 길이 평가 (너무 짧거나 길지 않은지)
        word_count = len(transcription.split())
        if word_count < 20:
            length_score = 50  # 너무 짧음
        elif word_count < 50:
            length_score = 70  # 짧음
        elif word_count < 200:
            length_score = 100  # 적절
        elif word_count < 300:
            length_score = 90  # 약간 김
        else:
            length_score = 70  # 너무 김

        # 종합 점수 (키워드 70%, 길이 30%)
        content_score = (keyword_score * 0.7) + (length_score * 0.3)

        return round(content_score, 1)

    def analyze_structure(self, transcription: str) -> float:
        """
        답변 구조 분석 (STAR 메서드)

        Args:
            transcription: 전사된 텍스트

        Returns:
            구조 점수 (0-100)
        """
        if not transcription:
            return 0.0

        transcription_lower = transcription.lower()

        # STAR 각 요소 감지
        star_detected = {
            'situation': False,
            'task': False,
            'action': False,
            'result': False
        }

        for element, keywords in self.STAR_KEYWORDS.items():
            for keyword in keywords:
                if keyword in transcription_lower:
                    star_detected[element] = True
                    break

        # 감지된 요소 개수
        detected_count = sum(star_detected.values())

        # 점수 계산
        if detected_count == 4:
            return 100.0  # 완벽한 STAR 구조
        elif detected_count == 3:
            return 85.0  # 대부분의 요소 포함
        elif detected_count == 2:
            return 70.0  # 일부 요소 포함
        elif detected_count == 1:
            return 50.0  # 구조가 약함
        else:
            return 30.0  # 구조 없음

    def check_grammar(self, transcription: str) -> float:
        """
        기본적인 문법 체크

        Args:
            transcription: 전사된 텍스트

        Returns:
            문법 점수 (0-100)
        """
        if not transcription:
            return 0.0

        # 기본 점수
        score = 85.0

        # 간단한 문법 패턴 체크
        sentences = re.split(r'[.!?]+', transcription)

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 문장이 소문자로 시작하면 감점
            if sentence and sentence[0].islower():
                score -= 2

            # 이중 공백 감점
            if '  ' in sentence:
                score -= 1

        # 최소 점수는 50
        return max(50.0, round(score, 1))

    def detect_fillers(self, transcription: str) -> Dict:
        """
        필러 워드 감지

        Args:
            transcription: 전사된 텍스트

        Returns:
            필러 워드 분석 결과
        """
        if not transcription:
            return {'count': 0, 'words': {}, 'density': 0.0}

        transcription_lower = transcription.lower()
        word_count = len(transcription.split())

        filler_counts = {}
        total_fillers = 0

        for filler in self.FILLER_WORDS:
            # 단어 경계를 고려한 매칭
            pattern = r'\b' + re.escape(filler) + r'\b'
            matches = re.findall(pattern, transcription_lower)
            count = len(matches)

            if count > 0:
                filler_counts[filler] = count
                total_fillers += count

        # 밀도 계산 (100단어당 필러 워드 수)
        density = (total_fillers / word_count * 100) if word_count > 0 else 0

        return {
            'count': total_fillers,
            'words': filler_counts,
            'density': round(density, 2),
            'word_count': word_count
        }

    def get_audio_duration(self, audio_path: str) -> float:
        """
        오디오 파일 길이 가져오기

        Args:
            audio_path: 오디오 파일 경로

        Returns:
            길이 (초)
        """
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            return round(duration, 1)
        except Exception as e:
            print(f"Duration 계산 실패: {e}")
            return 0.0

    def evaluate_duration(self, actual_duration: float, ideal_duration: float) -> float:
        """
        답변 시간 평가

        Args:
            actual_duration: 실제 답변 시간 (초)
            ideal_duration: 이상적인 답변 시간 (초)

        Returns:
            시간 점수 (0-100)
        """
        if actual_duration == 0:
            return 0.0

        # 허용 범위: 이상 시간의 ±30%
        lower_bound = ideal_duration * 0.7
        upper_bound = ideal_duration * 1.3

        if lower_bound <= actual_duration <= upper_bound:
            return 100.0  # 완벽한 시간
        elif actual_duration < lower_bound:
            # 너무 짧음
            ratio = actual_duration / lower_bound
            return max(50.0, ratio * 100)
        else:
            # 너무 김
            ratio = upper_bound / actual_duration
            return max(50.0, ratio * 100)

    def calculate_overall_interview_score(
        self,
        pronunciation_score: float,
        content_score: float,
        structure_score: float,
        grammar_score: float,
        duration_score: float
    ) -> float:
        """
        면접 답변 종합 점수 계산

        가중치:
        - 발음: 20%
        - 내용: 30%
        - 구조: 20%
        - 문법: 15%
        - 시간: 15%
        """
        overall = (
            pronunciation_score * 0.20 +
            content_score * 0.30 +
            structure_score * 0.20 +
            grammar_score * 0.15 +
            duration_score * 0.15
        )

        return round(overall, 1)

    def generate_interview_feedback(
        self,
        transcription: str,
        question: Dict,
        scores: Dict,
        filler_analysis: Dict,
        duration: float
    ) -> str:
        """
        면접 피드백 생성

        Args:
            transcription: 전사 텍스트
            question: 질문 정보
            scores: 점수들
            filler_analysis: 필러 워드 분석
            duration: 답변 시간

        Returns:
            피드백 텍스트
        """
        feedback_parts = []

        overall_score = scores['overall']

        # 전체 평가
        if overall_score >= 90:
            feedback_parts.append("🎉 훌륭한 답변입니다! 면접관에게 강한 인상을 줄 것입니다.")
        elif overall_score >= 80:
            feedback_parts.append("👍 좋은 답변입니다! 약간의 개선으로 완벽해질 수 있습니다.")
        elif overall_score >= 70:
            feedback_parts.append("📚 괜찮은 답변입니다. 몇 가지 부분을 보완하면 좋겠습니다.")
        elif overall_score >= 60:
            feedback_parts.append("💪 기본은 갖추었지만 더 많은 연습이 필요합니다.")
        else:
            feedback_parts.append("📖 답변을 더 체계적으로 준비해보세요.")

        # 점수 요약
        feedback_parts.append(
            f"\n📊 종합 점수: {overall_score}점"
            f"\n   • 발음: {scores['pronunciation']:.0f}점"
            f"\n   • 내용: {scores['content']:.0f}점"
            f"\n   • 구조: {scores['structure']:.0f}점"
            f"\n   • 문법: {scores['grammar']:.0f}점"
            f"\n   • 시간관리: {scores['duration']:.0f}점"
        )

        # 강점
        strengths = []
        if scores['pronunciation'] >= 85:
            strengths.append("발음이 명확합니다")
        if scores['content'] >= 80:
            strengths.append("내용이 충실합니다")
        if scores['structure'] >= 80:
            strengths.append("답변 구조가 좋습니다")
        if scores['grammar'] >= 85:
            strengths.append("문법이 정확합니다")

        if strengths:
            feedback_parts.append("\n✅ 강점: " + ", ".join(strengths))

        # 개선점
        weaknesses = []
        if scores['pronunciation'] < 70:
            weaknesses.append("발음 연습이 필요합니다")
        if scores['content'] < 70:
            weaknesses.append("내용을 더 구체적으로 설명하세요")
        if scores['structure'] < 70:
            weaknesses.append("STAR 구조로 답변을 정리해보세요")
        if scores['grammar'] < 70:
            weaknesses.append("문법을 다시 확인해보세요")
        if scores['duration'] < 70:
            ideal = question.get('ideal_duration', 90)
            if duration < ideal * 0.7:
                weaknesses.append(f"답변이 너무 짧습니다 (권장: {ideal}초)")
            else:
                weaknesses.append(f"답변이 너무 깁니다 (권장: {ideal}초)")

        if weaknesses:
            feedback_parts.append("\n⚠️ 개선할 점: " + ", ".join(weaknesses))

        # 필러 워드 피드백
        if filler_analysis['count'] > 0:
            feedback_parts.append(
                f"\n🗣️ 필러 워드를 {filler_analysis['count']}회 사용했습니다. "
                f"(밀도: {filler_analysis['density']:.1f}%) 줄이도록 노력하세요."
            )

            # 가장 많이 사용한 필러 워드
            if filler_analysis['words']:
                top_filler = max(filler_analysis['words'].items(), key=lambda x: x[1])
                feedback_parts.append(f"   특히 '{top_filler[0]}'을(를) {top_filler[1]}회 사용했습니다.")

        return '\n'.join(feedback_parts)

    def suggest_improvements(
        self,
        transcription: str,
        question: Dict,
        scores: Dict,
        filler_analysis: Dict
    ) -> List[str]:
        """
        개선 제안 생성

        Returns:
            개선 제안 리스트
        """
        improvements = []

        # 내용 개선
        if scores['content'] < 80:
            improvements.append(
                "💡 질문의 핵심 키워드를 답변에 포함시키세요: " +
                ", ".join(question.get('keywords', [])[:3])
            )

            if len(transcription.split()) < 50:
                improvements.append(
                    "📝 답변을 더 자세하게 설명해보세요. 구체적인 예시를 추가하면 좋습니다."
                )

        # 구조 개선
        if scores['structure'] < 80:
            improvements.append(
                "🏗️ STAR 메서드를 활용하세요:\n"
                "   • Situation (상황): 어떤 상황이었나요?\n"
                "   • Task (과제): 무엇을 해야 했나요?\n"
                "   • Action (행동): 어떻게 했나요?\n"
                "   • Result (결과): 결과는 어땠나요?"
            )

        # 문법 개선
        if scores['grammar'] < 80:
            improvements.append(
                "✍️ 문법을 다시 확인하세요. 문장 구조와 시제에 주의하세요."
            )

        # 필러 워드 개선
        if filler_analysis['count'] > 5:
            improvements.append(
                f"🎯 필러 워드({filler_analysis['count']}회)를 줄이세요:\n"
                "   • 말하기 전에 잠깐 생각하세요\n"
                "   • 천천히 또박또박 말하세요\n"
                "   • 불필요한 추임새를 의식적으로 피하세요"
            )

        # 시간 관리
        if scores['duration'] < 80:
            ideal = question.get('ideal_duration', 90)
            improvements.append(
                f"⏱️ 답변 시간을 {ideal}초 내외로 조절하세요. 연습할 때 타이머를 사용해보세요."
            )

        # 질문별 팁 추가
        if question.get('tips'):
            improvements.append(
                "💡 이 질문에 대한 팁:\n" +
                "\n".join(f"   • {tip}" for tip in question['tips'])
            )

        return improvements


# 유틸리티 함수
def load_questions_db() -> Dict:
    """
    전체 질문 데이터베이스 로드 (메타데이터 포함)

    Returns:
        전체 질문 데이터베이스 딕셔너리
    """
    questions_file = Path(__file__).parent / 'interview_questions.json'

    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        # 파일이 없을 경우 빈 데이터베이스 반환
        return {
            'questions': [],
            'metadata': {
                'version': '1.0',
                'total_questions': 0
            }
        }
    except Exception as e:
        print(f"Error loading questions: {e}")
        return {
            'questions': [],
            'metadata': {
                'version': '1.0',
                'total_questions': 0
            }
        }


def load_questions(category: str = None, difficulty: str = None, industry: str = None) -> List[Dict]:
    """
    질문 데이터베이스에서 질문 로드

    Args:
        category: 질문 카테고리 필터
        difficulty: 난이도 필터
        industry: 산업 필터

    Returns:
        필터링된 질문 리스트
    """
    data = load_questions_db()
    questions = data.get('questions', [])

    # 필터링
    if category:
        questions = [q for q in questions if q.get('category') == category]
    if difficulty:
        questions = [q for q in questions if q.get('difficulty') == difficulty]
    if industry:
        questions = [q for q in questions if q.get('industry') == industry]

    return questions


def get_random_question(category: str = None, difficulty: str = None, industry: str = None) -> Dict:
    """랜덤 질문 가져오기"""
    import random
    questions = load_questions(category, difficulty, industry)
    return random.choice(questions) if questions else None


# 테스트/데모용
if __name__ == "__main__":
    print("=" * 70)
    print("면접 분석 시스템 데모")
    print("=" * 70)

    # 질문 로드 테스트
    questions = load_questions(category='behavioral', difficulty='intermediate')
    print(f"\n로드된 질문 수: {len(questions)}")

    if questions:
        sample_question = questions[0]
        print(f"\n샘플 질문:")
        print(f"  ID: {sample_question['id']}")
        print(f"  질문: {sample_question['question']}")
        print(f"  한글: {sample_question['question_ko']}")
        print(f"  카테고리: {sample_question['category']}")
        print(f"  난이도: {sample_question['difficulty']}")
        print(f"  권장 시간: {sample_question['ideal_duration']}초")

    print("\n" + "=" * 70)
    print("테스트 완료!")
