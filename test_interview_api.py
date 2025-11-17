#!/usr/bin/env python3
"""
면접 API 테스트 스크립트
Interview API Test Script

이 스크립트를 실행하기 전에 API 서버가 실행되고 있어야 합니다:
python api.py

테스트 실행:
python test_interview_api.py
"""

import requests
import json
from pathlib import Path

# API 서버 URL
BASE_URL = 'http://localhost:5000'

def print_separator(title=""):
    """구분선 출력"""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    else:
        print(f"{'='*70}")


def print_response(response, title="Response"):
    """응답 출력"""
    print(f"\n[{title}]")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)


def test_get_questions():
    """테스트 1: 면접 질문 목록 조회"""
    print_separator("Test 1: GET /api/interview/questions")

    # 1-1. 전체 질문 조회
    print("\n[Test 1-1] 전체 질문 조회")
    response = requests.get(f'{BASE_URL}/api/interview/questions')
    print_response(response)

    # 1-2. 카테고리 필터
    print("\n[Test 1-2] Behavioral 카테고리 질문")
    response = requests.get(
        f'{BASE_URL}/api/interview/questions',
        params={'category': 'behavioral'}
    )
    print_response(response)

    # 1-3. 난이도 필터
    print("\n[Test 1-3] Intermediate 난이도 질문")
    response = requests.get(
        f'{BASE_URL}/api/interview/questions',
        params={'difficulty': 'intermediate'}
    )
    print_response(response)

    # 1-4. 산업 필터
    print("\n[Test 1-4] Tech 산업 질문")
    response = requests.get(
        f'{BASE_URL}/api/interview/questions',
        params={'industry': 'tech'}
    )
    print_response(response)

    # 1-5. 복합 필터 + 제한
    print("\n[Test 1-5] Tech + Intermediate, 최대 3개")
    response = requests.get(
        f'{BASE_URL}/api/interview/questions',
        params={
            'industry': 'tech',
            'difficulty': 'intermediate',
            'limit': 3
        }
    )
    print_response(response)


def test_get_random_questions():
    """테스트 2: 랜덤 질문 가져오기"""
    print_separator("Test 2: GET /api/interview/questions/random")

    # 2-1. 랜덤 1개
    print("\n[Test 2-1] 랜덤 질문 1개")
    response = requests.get(f'{BASE_URL}/api/interview/questions/random')
    print_response(response)

    # 2-2. 랜덤 5개
    print("\n[Test 2-2] 랜덤 질문 5개")
    response = requests.get(
        f'{BASE_URL}/api/interview/questions/random',
        params={'count': 5}
    )
    print_response(response)

    # 2-3. 필터 + 랜덤
    print("\n[Test 2-3] Behavioral 카테고리에서 랜덤 3개")
    response = requests.get(
        f'{BASE_URL}/api/interview/questions/random',
        params={
            'count': 3,
            'category': 'behavioral'
        }
    )
    print_response(response)


def test_analyze_interview_answer():
    """테스트 3: 면접 답변 분석"""
    print_separator("Test 3: POST /api/interview/analyze")

    print("\n⚠️  이 테스트는 실제 오디오 파일이 필요합니다.")
    print("테스트 오디오 파일 경로를 입력하거나 Enter를 눌러 건너뛰세요.")

    audio_path = input("Audio file path (or press Enter to skip): ").strip()

    if audio_path and Path(audio_path).exists():
        print("\n[Test 3-1] 질문 ID로 분석")

        # 먼저 랜덤 질문 하나 가져오기
        response = requests.get(f'{BASE_URL}/api/interview/questions/random')
        if response.status_code == 200:
            question = response.json()['questions'][0]
            question_id = question['id']

            print(f"질문: {question['question']}")

            with open(audio_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {'question_id': question_id}

                response = requests.post(
                    f'{BASE_URL}/api/interview/analyze',
                    files=files,
                    data=data
                )
                print_response(response)
    else:
        print("⏭️  오디오 파일이 없어 테스트를 건너뜁니다.")

    # 3-2. 커스텀 질문 텍스트로 분석 (오디오 있을 때만)
    if audio_path and Path(audio_path).exists():
        print("\n[Test 3-2] 커스텀 질문 텍스트로 분석")

        with open(audio_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {'question_text': 'Tell me about yourself'}

            response = requests.post(
                f'{BASE_URL}/api/interview/analyze',
                files=files,
                data=data
            )
            print_response(response)


def test_interview_session():
    """테스트 4: 면접 세션 관리"""
    print_separator("Test 4: Interview Session Management")

    # 4-1. 세션 시작
    print("\n[Test 4-1] POST /api/interview/session/start")
    response = requests.post(
        f'{BASE_URL}/api/interview/session/start',
        json={
            'interview_type': 'behavioral',
            'num_questions': 3,
            'category': 'behavioral',
            'difficulty': 'intermediate'
        }
    )
    print_response(response)

    if response.status_code != 201:
        print("❌ 세션 시작 실패, 나머지 테스트 건너뜀")
        return

    session_data = response.json()
    session_id = session_data['session_id']
    questions = session_data['questions']

    print(f"\n✅ 세션 ID: {session_id}")
    print(f"질문 수: {len(questions)}")

    # 4-2. 답변 제출 (오디오 파일 있을 때만)
    print("\n[Test 4-2] POST /api/interview/session/{session_id}/answer")
    print("⚠️  이 테스트는 실제 오디오 파일이 필요합니다.")

    audio_path = input("Audio file path (or press Enter to skip): ").strip()

    if audio_path and Path(audio_path).exists():
        print(f"\n첫 번째 질문에 답변 제출:")
        print(f"질문: {questions[0]['question']}")

        with open(audio_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {'question_index': 0}

            response = requests.post(
                f'{BASE_URL}/api/interview/session/{session_id}/answer',
                files=files,
                data=data
            )
            print_response(response)
    else:
        print("⏭️  오디오 파일이 없어 답변 제출 테스트를 건너뜁니다.")

    # 4-3. 세션 결과 조회
    print("\n[Test 4-3] GET /api/interview/session/{session_id}/results")
    response = requests.get(
        f'{BASE_URL}/api/interview/session/{session_id}/results'
    )
    print_response(response)

    # 4-4. 세션 삭제
    print("\n[Test 4-4] DELETE /api/interview/session/{session_id}")
    response = requests.delete(
        f'{BASE_URL}/api/interview/session/{session_id}'
    )
    print_response(response)

    # 4-5. 삭제된 세션 조회 (404 예상)
    print("\n[Test 4-5] 삭제된 세션 조회 (404 예상)")
    response = requests.get(
        f'{BASE_URL}/api/interview/session/{session_id}/results'
    )
    print_response(response)


def test_error_cases():
    """테스트 5: 에러 케이스"""
    print_separator("Test 5: Error Cases")

    # 5-1. 존재하지 않는 질문 ID
    print("\n[Test 5-1] 존재하지 않는 질문 ID")
    response = requests.get(
        f'{BASE_URL}/api/interview/questions',
        params={'limit': 1}
    )
    if response.status_code == 200:
        # 더미 오디오 데이터로 테스트 (실패 예상)
        files = {'audio': ('test.wav', b'dummy data', 'audio/wav')}
        data = {'question_id': 'q999'}

        response = requests.post(
            f'{BASE_URL}/api/interview/analyze',
            files=files,
            data=data
        )
        print_response(response)

    # 5-2. 오디오 파일 없이 분석 요청
    print("\n[Test 5-2] 오디오 파일 없이 분석 요청 (400 예상)")
    response = requests.post(
        f'{BASE_URL}/api/interview/analyze',
        data={'question_id': 'q001'}
    )
    print_response(response)

    # 5-3. 존재하지 않는 세션 조회
    print("\n[Test 5-3] 존재하지 않는 세션 조회 (404 예상)")
    response = requests.get(
        f'{BASE_URL}/api/interview/session/invalid-session-id/results'
    )
    print_response(response)


def test_health_check():
    """테스트 0: 서버 상태 확인"""
    print_separator("Test 0: Health Check")

    try:
        response = requests.get(f'{BASE_URL}/health', timeout=2)
        print_response(response)

        if response.status_code == 200:
            print("\n✅ API 서버가 정상적으로 실행 중입니다.")
            return True
        else:
            print("\n⚠️  API 서버 응답이 비정상입니다.")
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ API 서버에 연결할 수 없습니다.")
        print("다음 명령으로 API 서버를 먼저 실행하세요:")
        print("  python api.py")
        return False
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        return False


def main():
    """메인 함수"""
    print("=" * 70)
    print("  면접 API 테스트 스크립트")
    print("  Interview API Test Script")
    print("=" * 70)

    # 서버 상태 확인
    if not test_health_check():
        return

    print("\n테스트를 시작합니다...\n")

    try:
        # 테스트 실행
        test_get_questions()
        test_get_random_questions()
        test_analyze_interview_answer()
        test_interview_session()
        test_error_cases()

        # 완료
        print_separator("테스트 완료!")
        print("\n✅ 모든 테스트가 완료되었습니다.")
        print("\n📝 참고:")
        print("  - 오디오 파일이 있는 테스트는 건너뛸 수 있습니다.")
        print("  - 실제 오디오 파일로 테스트하려면 WAV 파일을 준비하세요.")
        print("  - 전체 API 문서는 interview/API_DOCUMENTATION.md를 참조하세요.")

    except KeyboardInterrupt:
        print("\n\n⚠️  테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
