# 🧪 Interview API Testing Guide

**Complete walkthrough for testing the Interview API**

---

## 📋 Prerequisites

Before testing, ensure you have:
- ✅ Python 3.10+ installed
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ Flask and related packages working

---

## 🚀 Step-by-Step Testing Guide

### Step 1: Start the API Server

Open a terminal and start the Flask server:

```bash
cd /home/user/English-pronunciation-ai2
python api.py
```

**Expected Output:**
```
Whisper base 모델 로드 완료
 * Serving Flask app 'api'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

**✅ Server is now running at**: `http://localhost:5000`

---

### Step 2: Run the Test Script

Open a **new terminal** (keep the server running) and run:

```bash
cd /home/user/English-pronunciation-ai2
python test_interview_api.py
```

---

## 📊 What You'll See

### Test 0: Health Check ✅

```
======================================================================
Test 0: Health Check
======================================================================

[Response]
Status Code: 200
{
  "service": "pronunciation-analyzer",
  "status": "healthy",
  "version": "1.0.0"
}

✅ API 서버가 정상적으로 실행 중입니다.
```

**What this tests**: Server is running and responding

---

### Test 1: Get Interview Questions ✅

#### Test 1-1: All Questions
```
======================================================================
  Test 1: GET /api/interview/questions
======================================================================

[Test 1-1] 전체 질문 조회

[Response]
Status Code: 200
{
  "filters": {
    "category": null,
    "difficulty": null,
    "industry": null
  },
  "questions": [
    {
      "category": "self-introduction",
      "difficulty": "beginner",
      "id": "q001",
      "ideal_duration": 90,
      "industry": "general",
      "question": "Tell me about yourself",
      "question_ko": "자기소개를 해주세요",
      "tips": [
        "Keep it 1-2 minutes",
        "Focus on relevant experience",
        "End with why you're interested in this role"
      ]
    },
    {
      "category": "behavioral",
      "difficulty": "intermediate",
      "id": "q002",
      "question": "Tell me about a time when you faced a difficult challenge at work",
      ...
    },
    ... (25 total questions)
  ],
  "success": true,
  "total": 25
}
```

#### Test 1-2: Filtered by Category
```
[Test 1-2] Behavioral 카테고리 질문

[Response]
Status Code: 200
{
  "filters": {
    "category": "behavioral",
    "difficulty": null,
    "industry": null
  },
  "questions": [ ... ],
  "success": true,
  "total": 14
}
```

**What this tests**: Question database loading and filtering

---

### Test 2: Random Questions ✅

```
======================================================================
  Test 2: GET /api/interview/questions/random
======================================================================

[Test 2-1] 랜덤 질문 1개

[Response]
Status Code: 200
{
  "count": 1,
  "questions": [
    {
      "category": "behavioral",
      "difficulty": "intermediate",
      "id": "q003",
      "question": "Describe a situation where you had to work with a difficult team member",
      "question_ko": "어려운 팀원과 함께 일해야 했던 상황을 설명해주세요",
      ...
    }
  ],
  "success": true
}
```

**What this tests**: Random question selection

---

### Test 3: Analyze Interview Answer ⚠️

```
======================================================================
  Test 3: POST /api/interview/analyze
======================================================================

⚠️  이 테스트는 실제 오디오 파일이 필요합니다.
테스트 오디오 파일 경로를 입력하거나 Enter를 눌러 건너뛰세요.
Audio file path (or press Enter to skip):
```

**If you have an audio file**, enter the path:
```
Audio file path: /path/to/answer.wav
```

**Expected Response:**
```
[Test 3-1] 질문 ID로 분석

질문: Tell me about a time when you faced a difficult challenge at work

[Response]
Status Code: 200
{
  "data": {
    "duration": 118.5,
    "feedback": "👍 좋은 답변입니다! 약간의 개선으로 완벽해질 수 있습니다.\n\n📊 종합 점수: 78.5점\n   • 발음: 85점\n   • 내용: 75점\n   • 구조: 70점\n   • 문법: 90점\n   • 시간관리: 98점\n\n✅ 강점: 발음이 명확합니다, 문법이 정확합니다\n⚠️ 개선할 점: STAR 구조로 답변을 정리해보세요\n\n🗣️ 필러 워드를 5회 사용했습니다. (밀도: 2.8%) 줄이도록 노력하세요.\n   특히 'well'을(를) 2회 사용했습니다.",
    "filler_words": {
      "count": 5,
      "density": 2.8,
      "word_count": 178,
      "words": {
        "like": 1,
        "um": 2,
        "well": 2
      }
    },
    "improvements": [
      "💡 질문의 핵심 키워드를 답변에 포함시키세요: challenge, problem-solving, overcome",
      "🏗️ STAR 메서드를 활용하세요:\n   • Situation (상황): 어떤 상황이었나요?\n   • Task (과제): 무엇을 해야 했나요?\n   • Action (행동): 어떻게 했나요?\n   • Result (결과): 결과는 어땠나요?",
      "🎯 필러 워드(5회)를 줄이세요:\n   • 말하기 전에 잠깐 생각하세요\n   • 천천히 또박또박 말하세요\n   • 불필요한 추임새를 의식적으로 피하세요"
    ],
    "question": {
      "id": "q002",
      "question": "Tell me about a time when you faced a difficult challenge at work",
      "question_ko": "업무에서 어려운 도전에 직면했을 때에 대해 말해주세요"
    },
    "scores": {
      "content": 75.0,
      "duration": 98.0,
      "grammar": 90.0,
      "overall": 78.5,
      "pronunciation": 85.0,
      "structure": 70.0
    },
    "transcription": "well in my previous role as a software engineer i faced a challenging situation when our main database server crashed during peak hours um we had thousands of users affected and i had to act quickly i coordinated with the team like we implemented a backup solution and communicated with stakeholders the result was we restored service within two hours and implemented better monitoring to prevent future issues"
  },
  "success": true
}
```

**What this tests**: Complete interview answer analysis including:
- Whisper STT transcription
- Pronunciation scoring
- Content evaluation
- STAR structure detection
- Grammar checking
- Filler word detection
- Duration assessment
- Feedback generation

---

### Test 4: Interview Session Management ✅

#### Test 4-1: Start Session
```
======================================================================
  Test 4: Interview Session Management
======================================================================

[Test 4-1] POST /api/interview/session/start

[Response]
Status Code: 201
{
  "questions": [
    {
      "id": "q002",
      "ideal_duration": 120,
      "index": 0,
      "question": "Tell me about a time when you faced a difficult challenge at work",
      "question_ko": "업무에서 어려운 도전에 직면했을 때에 대해 말해주세요",
      "tips": [
        "Use STAR method (Situation, Task, Action, Result)",
        "Be specific about your role",
        "Highlight the positive outcome"
      ]
    },
    {
      "id": "q003",
      "index": 1,
      ...
    },
    {
      "id": "q020",
      "index": 2,
      ...
    }
  ],
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "started_at": "2025-11-17T10:30:00.123456",
  "success": true,
  "total_questions": 3
}

✅ 세션 ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
질문 수: 3
```

#### Test 4-2: Submit Answer (if audio available)
```
[Test 4-2] POST /api/interview/session/{session_id}/answer

⚠️  이 테스트는 실제 오디오 파일이 필요합니다.
Audio file path: /path/to/answer.wav

첫 번째 질문에 답변 제출:
질문: Tell me about a time when you faced a difficult challenge at work

[Response]
Status Code: 200
{
  "answer_index": 0,
  "completed": false,
  "feedback": "👍 좋은 답변입니다!...",
  "filler_words": {
    "count": 5,
    "density": 2.8,
    ...
  },
  "improvements": [...],
  "next_question": {
    "id": "q003",
    "ideal_duration": 120,
    "index": 1,
    "question": "Describe a situation where you had to work with a difficult team member",
    "question_ko": "어려운 팀원과 함께 일해야 했던 상황을 설명해주세요"
  },
  "progress": {
    "answered": 1,
    "percentage": 33.33,
    "total": 3
  },
  "scores": {
    "content": 75.0,
    "duration": 98.0,
    "grammar": 90.0,
    "overall": 78.5,
    "pronunciation": 85.0,
    "structure": 70.0
  },
  "success": true
}
```

#### Test 4-3: Get Session Results
```
[Test 4-3] GET /api/interview/session/{session_id}/results

[Response]
Status Code: 200
{
  "answers": [
    {
      "duration": 118.5,
      "feedback": "...",
      "filler_words": {...},
      "question": "Tell me about a time when you faced a difficult challenge at work",
      "question_id": "q002",
      "question_index": 0,
      "scores": {
        "content": 75.0,
        "duration": 98.0,
        "grammar": 90.0,
        "overall": 78.5,
        "pronunciation": 85.0,
        "structure": 70.0
      },
      "transcription": "well in my previous role..."
    }
  ],
  "session_info": {
    "answered": 1,
    "completed_at": null,
    "filters": {
      "category": "behavioral",
      "difficulty": "intermediate",
      "industry": null
    },
    "interview_type": "behavioral",
    "session_id": "a1b2c3d4-...",
    "started_at": "2025-11-17T10:30:00.123456",
    "total_questions": 3
  },
  "success": true,
  "summary": {
    "average_scores": {
      "content": 75.0,
      "duration": 98.0,
      "grammar": 90.0,
      "overall": 78.5,
      "pronunciation": 85.0,
      "structure": 70.0
    },
    "avg_filler_density": 2.8,
    "best_score": 78.5,
    "total_filler_words": 5,
    "worst_score": 78.5
  }
}
```

#### Test 4-4: Delete Session
```
[Test 4-4] DELETE /api/interview/session/{session_id}

[Response]
Status Code: 200
{
  "message": "Session deleted successfully",
  "success": true
}
```

#### Test 4-5: Verify Deletion
```
[Test 4-5] 삭제된 세션 조회 (404 예상)

[Response]
Status Code: 404
{
  "code": "SESSION_NOT_FOUND",
  "error": "Session not found",
  "success": false
}
```

**What this tests**: Complete session workflow

---

### Test 5: Error Cases ✅

```
======================================================================
  Test 5: Error Cases
======================================================================

[Test 5-1] 존재하지 않는 질문 ID

[Response]
Status Code: 404
{
  "code": "QUESTION_NOT_FOUND",
  "error": "Question with id q999 not found",
  "success": false
}

[Test 5-2] 오디오 파일 없이 분석 요청 (400 예상)

[Response]
Status Code: 400
{
  "code": "MISSING_AUDIO",
  "error": "audio file is required"
}

[Test 5-3] 존재하지 않는 세션 조회 (404 예상)

[Response]
Status Code: 404
{
  "code": "SESSION_NOT_FOUND",
  "error": "Session not found",
  "success": false
}
```

**What this tests**: Error handling and validation

---

### Test Completion

```
======================================================================
테스트 완료!
======================================================================

✅ 모든 테스트가 완료되었습니다.

📝 참고:
  - 오디오 파일이 있는 테스트는 건너뛸 수 있습니다.
  - 실제 오디오 파일로 테스트하려면 WAV 파일을 준비하세요.
  - 전체 API 문서는 interview/API_DOCUMENTATION.md를 참조하세요.
```

---

## 🎯 Manual Testing with cURL

If you prefer testing endpoints individually:

### 1. Health Check
```bash
curl http://localhost:5000/health
```

### 2. Get All Questions
```bash
curl "http://localhost:5000/api/interview/questions"
```

### 3. Get Behavioral Questions Only
```bash
curl "http://localhost:5000/api/interview/questions?category=behavioral"
```

### 4. Get Random Question
```bash
curl "http://localhost:5000/api/interview/questions/random"
```

### 5. Get 5 Random Questions
```bash
curl "http://localhost:5000/api/interview/questions/random?count=5"
```

### 6. Analyze Interview Answer
```bash
curl -X POST http://localhost:5000/api/interview/analyze \
  -F "audio=@answer.wav" \
  -F "question_id=q002"
```

### 7. Start Interview Session
```bash
curl -X POST http://localhost:5000/api/interview/session/start \
  -H "Content-Type: application/json" \
  -d '{
    "interview_type": "behavioral",
    "num_questions": 3,
    "category": "behavioral"
  }'
```

### 8. Submit Answer to Session
```bash
# Replace SESSION_ID with actual session ID from step 7
curl -X POST "http://localhost:5000/api/interview/session/SESSION_ID/answer" \
  -F "audio=@answer.wav" \
  -F "question_index=0"
```

### 9. Get Session Results
```bash
curl "http://localhost:5000/api/interview/session/SESSION_ID/results"
```

### 10. Delete Session
```bash
curl -X DELETE "http://localhost:5000/api/interview/session/SESSION_ID"
```

---

## 🧪 Testing with Python

### Quick Test Script

```python
import requests

BASE_URL = 'http://localhost:5000'

# 1. Check health
response = requests.get(f'{BASE_URL}/health')
print(f"Health: {response.json()}")

# 2. Get random question
response = requests.get(f'{BASE_URL}/api/interview/questions/random')
question = response.json()['questions'][0]
print(f"\nQuestion: {question['question']}")

# 3. Start session
response = requests.post(
    f'{BASE_URL}/api/interview/session/start',
    json={'num_questions': 3, 'category': 'behavioral'}
)
session = response.json()
session_id = session['session_id']
print(f"\nSession ID: {session_id}")
print(f"Questions: {len(session['questions'])}")

# 4. (Optional) Submit answer if you have audio file
# with open('answer.wav', 'rb') as audio:
#     response = requests.post(
#         f'{BASE_URL}/api/interview/session/{session_id}/answer',
#         files={'audio': audio},
#         data={'question_index': 0}
#     )
#     print(f"\nScore: {response.json()['scores']['overall']}")

# 5. Get results
response = requests.get(
    f'{BASE_URL}/api/interview/session/{session_id}/results'
)
results = response.json()
print(f"\nSession Info: {results['session_info']}")

# 6. Cleanup
requests.delete(f'{BASE_URL}/api/interview/session/{session_id}')
print("\nSession deleted")
```

---

## 📊 Expected Test Results Summary

| Test | Endpoint | Expected Status | Expected Result |
|------|----------|-----------------|-----------------|
| Health Check | GET /health | 200 | Service info |
| Get Questions | GET /api/interview/questions | 200 | 25 questions |
| Filter Questions | GET /api/interview/questions?category=behavioral | 200 | 14 questions |
| Random Questions | GET /api/interview/questions/random | 200 | 1 question |
| Analyze Answer | POST /api/interview/analyze | 200 | Analysis result |
| Start Session | POST /api/interview/session/start | 201 | Session ID + questions |
| Submit Answer | POST /api/interview/session/{id}/answer | 200 | Scores + feedback |
| Get Results | GET /api/interview/session/{id}/results | 200 | Summary + answers |
| Delete Session | DELETE /api/interview/session/{id} | 200 | Success message |
| Error Cases | Various | 400/404 | Error messages |

---

## 🎯 What to Look For

### ✅ Success Indicators
- Status code 200/201 for successful requests
- `"success": true` in response
- Complete data structures in responses
- Proper error handling (400/404/500)
- Session state maintained correctly
- Scores in 0-100 range
- Feedback messages in Korean
- Filler word detection working

### ⚠️ Potential Issues
- Server not starting (check Flask installation)
- Audio file format errors (use WAV files)
- Session not found (check session_id)
- Timeout on long audio files (normal for Whisper)

---

## 📝 Notes

### Audio File Requirements
- **Format**: WAV, MP3, or M4A
- **Duration**: Recommended 30-120 seconds
- **Quality**: Clear speech, minimal background noise
- **Sample Rate**: Any (will be processed by Whisper)

### Performance
- **STT Processing**: 3-10 seconds per 5 seconds of audio
- **Content Analysis**: < 0.1 seconds
- **Total Analysis**: Dominated by Whisper STT time

### Session Management
- **Storage**: In-memory (lost on server restart)
- **Limit**: No hard limit (memory-dependent)
- **Cleanup**: Manual (use DELETE endpoint)

---

## 🔍 Debugging Tips

### If server won't start:
```bash
# Check dependencies
pip install flask flask-cors

# Check port availability
lsof -i :5000

# Try different port
python api.py  # edit to use port 5001
```

### If tests fail:
```bash
# Verify server is running
curl http://localhost:5000/health

# Check error messages
# They will indicate the specific issue
```

### If audio analysis fails:
- Verify audio file exists and is readable
- Check file format (WAV recommended)
- Ensure file is not corrupted
- Try with a shorter audio file first

---

## 🎊 Next Steps After Testing

Once testing is complete:

1. **✅ API is working** - Ready to use!
2. **Build Streamlit UI** - Create interview practice interface
3. **Deploy to production** - Add database + authentication
4. **Monitor usage** - Add logging and analytics

---

**Testing Guide Complete!**

For more information:
- **API Documentation**: `interview/API_DOCUMENTATION.md`
- **Implementation Summary**: `API_IMPLEMENTATION_SUMMARY.md`
- **Module README**: `interview/README.md`
