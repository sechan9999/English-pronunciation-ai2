# 🎯 Interview API Documentation

**면접 연습 API 완전 가이드**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Endpoints](#endpoints)
   - [Get Questions](#1-get-interview-questions)
   - [Get Random Questions](#2-get-random-questions)
   - [Analyze Answer](#3-analyze-interview-answer)
   - [Start Session](#4-start-interview-session)
   - [Submit Answer](#5-submit-answer-to-session)
   - [Get Results](#6-get-session-results)
   - [Delete Session](#7-delete-session)
5. [Error Codes](#error-codes)
6. [Examples](#examples)

---

## Overview

The Interview API provides endpoints for:
- Browsing and filtering interview questions
- Analyzing interview answers (pronunciation + content + structure)
- Managing mock interview sessions
- Tracking progress and getting detailed feedback

---

## Base URL

```
http://localhost:5000
```

For production, replace with your deployed API URL.

---

## Authentication

**Current Status**: No authentication required (development mode)

**Production**: Will require API key authentication
```
Header: Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Get Interview Questions

Get a list of interview questions with optional filtering.

**Endpoint**: `GET /api/interview/questions`

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | No | Question category (self-introduction, behavioral, situational, etc.) |
| difficulty | string | No | Difficulty level (beginner, intermediate, advanced) |
| industry | string | No | Industry (general, tech, business, marketing, sales) |
| limit | integer | No | Maximum number of questions to return |

**Response**: `200 OK`

```json
{
  "success": true,
  "total": 10,
  "filters": {
    "category": "behavioral",
    "difficulty": "intermediate",
    "industry": null
  },
  "questions": [
    {
      "id": "q002",
      "question": "Tell me about a time when you faced a difficult challenge at work",
      "question_ko": "업무에서 어려운 도전에 직면했을 때에 대해 말해주세요",
      "category": "behavioral",
      "difficulty": "intermediate",
      "industry": "general",
      "ideal_duration": 120,
      "tips": [
        "Use STAR method (Situation, Task, Action, Result)",
        "Be specific about your role",
        "Highlight the positive outcome"
      ]
    },
    ...
  ]
}
```

**Example**:

```bash
# Get all behavioral questions
curl "http://localhost:5000/api/interview/questions?category=behavioral"

# Get tech questions for intermediate level
curl "http://localhost:5000/api/interview/questions?industry=tech&difficulty=intermediate"

# Get maximum 5 questions
curl "http://localhost:5000/api/interview/questions?limit=5"
```

---

### 2. Get Random Questions

Get random interview questions.

**Endpoint**: `GET /api/interview/questions/random`

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| count | integer | No | Number of random questions (default: 1, max: 10) |
| category | string | No | Filter by category |
| difficulty | string | No | Filter by difficulty |
| industry | string | No | Filter by industry |

**Response**: `200 OK`

```json
{
  "success": true,
  "count": 3,
  "questions": [
    {
      "id": "q015",
      "question": "How would you handle a situation where a project is behind schedule?",
      ...
    },
    ...
  ]
}
```

**Example**:

```bash
# Get 1 random question
curl "http://localhost:5000/api/interview/questions/random"

# Get 5 random behavioral questions
curl "http://localhost:5000/api/interview/questions/random?count=5&category=behavioral"
```

---

### 3. Analyze Interview Answer

Analyze an interview answer (audio + question).

**Endpoint**: `POST /api/interview/analyze`

**Content-Type**: `multipart/form-data`

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| audio | file | Yes | Audio file (WAV, MP3, M4A) |
| question_id | string | No* | Question ID from database |
| question_text | string | No* | Custom question text |

*Either `question_id` or `question_text` is required

**Response**: `200 OK`

```json
{
  "success": true,
  "data": {
    "transcription": "well in my previous role i faced a challenging situation when...",
    "duration": 118.5,
    "scores": {
      "overall": 78.5,
      "pronunciation": 85.0,
      "content": 75.0,
      "structure": 70.0,
      "grammar": 90.0,
      "duration": 98.0
    },
    "feedback": "👍 좋은 답변입니다! 약간의 개선으로 완벽해질 수 있습니다...",
    "improvements": [
      "💡 질문의 핵심 키워드를 답변에 포함시키세요...",
      "🏗️ STAR 메서드를 활용하세요..."
    ],
    "filler_words": {
      "count": 5,
      "words": {"well": 2, "um": 2, "like": 1},
      "density": 2.8,
      "word_count": 178
    },
    "question": {
      "id": "q002",
      "question": "Tell me about a time when you faced a difficult challenge at work",
      "question_ko": "업무에서 어려운 도전에 직면했을 때에 대해 말해주세요"
    }
  }
}
```

**Example**:

```bash
# With question ID
curl -X POST http://localhost:5000/api/interview/analyze \
  -F "audio=@answer.wav" \
  -F "question_id=q002"

# With custom question
curl -X POST http://localhost:5000/api/interview/analyze \
  -F "audio=@answer.wav" \
  -F "question_text=Tell me about yourself"
```

**Python Example**:

```python
import requests

with open('answer.wav', 'rb') as audio_file:
    files = {'audio': audio_file}
    data = {'question_id': 'q002'}

    response = requests.post(
        'http://localhost:5000/api/interview/analyze',
        files=files,
        data=data
    )

result = response.json()
print(f"Overall Score: {result['data']['scores']['overall']}")
print(f"Feedback: {result['data']['feedback']}")
```

---

### 4. Start Interview Session

Start a mock interview session with multiple questions.

**Endpoint**: `POST /api/interview/session/start`

**Content-Type**: `application/json`

**Request Body**:

```json
{
  "interview_type": "behavioral",
  "num_questions": 5,
  "category": "behavioral",
  "difficulty": "intermediate",
  "industry": "general"
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| interview_type | string | No | Type of interview (default: "general") |
| num_questions | integer | No | Number of questions (default: 5, range: 1-10) |
| category | string | No | Filter by category |
| difficulty | string | No | Filter by difficulty |
| industry | string | No | Filter by industry |

**Response**: `201 Created`

```json
{
  "success": true,
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "questions": [
    {
      "index": 0,
      "id": "q002",
      "question": "Tell me about a time when you faced a difficult challenge at work",
      "question_ko": "업무에서 어려운 도전에 직면했을 때에 대해 말해주세요",
      "ideal_duration": 120,
      "tips": ["Use STAR method...", ...]
    },
    {
      "index": 1,
      "id": "q003",
      ...
    },
    ...
  ],
  "total_questions": 5,
  "started_at": "2025-11-17T10:30:00"
}
```

**Example**:

```bash
curl -X POST http://localhost:5000/api/interview/session/start \
  -H "Content-Type: application/json" \
  -d '{
    "interview_type": "technical",
    "num_questions": 5,
    "category": "technical",
    "difficulty": "advanced",
    "industry": "tech"
  }'
```

**Python Example**:

```python
import requests

response = requests.post(
    'http://localhost:5000/api/interview/session/start',
    json={
        'interview_type': 'behavioral',
        'num_questions': 5,
        'category': 'behavioral'
    }
)

session = response.json()
session_id = session['session_id']
questions = session['questions']

print(f"Session ID: {session_id}")
print(f"Total Questions: {len(questions)}")
```

---

### 5. Submit Answer to Session

Submit an answer to a question in an active session.

**Endpoint**: `POST /api/interview/session/{session_id}/answer`

**Content-Type**: `multipart/form-data`

**URL Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | string | Yes | Session ID from start session |

**Form Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| audio | file | Yes | Audio file with answer |
| question_index | integer | No | Question index (default: current question) |

**Response**: `200 OK`

```json
{
  "success": true,
  "answer_index": 0,
  "scores": {
    "overall": 78.5,
    "pronunciation": 85.0,
    "content": 75.0,
    "structure": 70.0,
    "grammar": 90.0,
    "duration": 98.0
  },
  "feedback": "👍 좋은 답변입니다!...",
  "improvements": [...],
  "filler_words": {
    "count": 5,
    "words": {"well": 2, "um": 2, "like": 1},
    "density": 2.8
  },
  "progress": {
    "answered": 1,
    "total": 5,
    "percentage": 20.0
  },
  "next_question": {
    "index": 1,
    "id": "q003",
    "question": "Describe a situation where you had to work with a difficult team member",
    "question_ko": "어려운 팀원과 함께 일해야 했던 상황을 설명해주세요",
    "ideal_duration": 120
  },
  "completed": false
}
```

**When session is completed** (last question):

```json
{
  ...
  "next_question": null,
  "completed": true
}
```

**Example**:

```bash
curl -X POST "http://localhost:5000/api/interview/session/SESSION_ID/answer" \
  -F "audio=@answer1.wav" \
  -F "question_index=0"
```

**Python Example**:

```python
import requests

session_id = "a1b2c3d4-..."

with open('answer1.wav', 'rb') as audio:
    files = {'audio': audio}
    data = {'question_index': 0}

    response = requests.post(
        f'http://localhost:5000/api/interview/session/{session_id}/answer',
        files=files,
        data=data
    )

result = response.json()
print(f"Score: {result['scores']['overall']}")
print(f"Progress: {result['progress']['percentage']}%")

if result['next_question']:
    print(f"Next: {result['next_question']['question']}")
else:
    print("Interview completed!")
```

---

### 6. Get Session Results

Get complete results for an interview session.

**Endpoint**: `GET /api/interview/session/{session_id}/results`

**URL Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | string | Yes | Session ID |

**Response**: `200 OK`

```json
{
  "success": true,
  "session_info": {
    "session_id": "a1b2c3d4-...",
    "interview_type": "behavioral",
    "total_questions": 5,
    "answered": 5,
    "started_at": "2025-11-17T10:30:00",
    "completed_at": "2025-11-17T10:45:00",
    "filters": {
      "category": "behavioral",
      "difficulty": "intermediate",
      "industry": "general"
    }
  },
  "summary": {
    "average_scores": {
      "overall": 78.5,
      "pronunciation": 85.0,
      "content": 75.0,
      "structure": 70.0,
      "grammar": 90.0,
      "duration": 80.0
    },
    "best_score": 92.0,
    "worst_score": 65.0,
    "total_filler_words": 25,
    "avg_filler_density": 2.5
  },
  "answers": [
    {
      "question_index": 0,
      "question_id": "q002",
      "question": "Tell me about a time when you faced a difficult challenge at work",
      "transcription": "well in my previous role...",
      "duration": 118.5,
      "scores": {...},
      "feedback": "...",
      "filler_words": {...}
    },
    ...
  ]
}
```

**Example**:

```bash
curl "http://localhost:5000/api/interview/session/SESSION_ID/results"
```

**Python Example**:

```python
import requests

session_id = "a1b2c3d4-..."

response = requests.get(
    f'http://localhost:5000/api/interview/session/{session_id}/results'
)

results = response.json()

# Print summary
summary = results['summary']
print(f"Average Score: {summary['average_scores']['overall']}")
print(f"Best Score: {summary['best_score']}")
print(f"Worst Score: {summary['worst_score']}")
print(f"Total Filler Words: {summary['total_filler_words']}")

# Print all answers
for answer in results['answers']:
    print(f"\nQ{answer['question_index'] + 1}: {answer['question']}")
    print(f"Score: {answer['scores']['overall']}")
    print(f"Feedback: {answer['feedback']}")
```

---

### 7. Delete Session

Delete an interview session (cleanup).

**Endpoint**: `DELETE /api/interview/session/{session_id}`

**URL Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | string | Yes | Session ID to delete |

**Response**: `200 OK`

```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

**Example**:

```bash
curl -X DELETE "http://localhost:5000/api/interview/session/SESSION_ID"
```

**Python Example**:

```python
import requests

session_id = "a1b2c3d4-..."

response = requests.delete(
    f'http://localhost:5000/api/interview/session/{session_id}'
)

print(response.json()['message'])
```

---

## Error Codes

### Common Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| MISSING_AUDIO | 400 | Audio file not provided |
| MISSING_QUESTION | 400 | Neither question_id nor question_text provided |
| MISSING_PARAMETERS | 400 | Required parameters missing |
| QUESTION_NOT_FOUND | 404 | Question ID not found in database |
| NO_QUESTIONS_FOUND | 404 | No questions match the filters |
| SESSION_NOT_FOUND | 404 | Session ID not found |
| INVALID_QUESTION_INDEX | 400 | Question index out of range |
| QUESTION_LOAD_FAILED | 500 | Failed to load questions from database |
| INTERVIEW_ANALYSIS_FAILED | 500 | Failed to analyze interview answer |
| SESSION_START_FAILED | 500 | Failed to start interview session |
| ANSWER_SUBMISSION_FAILED | 500 | Failed to submit answer |
| RESULTS_RETRIEVAL_FAILED | 500 | Failed to retrieve results |
| SESSION_DELETE_FAILED | 500 | Failed to delete session |

### Error Response Format

```json
{
  "success": false,
  "error": "Error message description",
  "code": "ERROR_CODE"
}
```

---

## Examples

### Complete Interview Session Flow

```python
import requests

BASE_URL = 'http://localhost:5000'

# 1. Start session
response = requests.post(
    f'{BASE_URL}/api/interview/session/start',
    json={'num_questions': 3, 'category': 'behavioral'}
)
session = response.json()
session_id = session['session_id']
questions = session['questions']

print(f"Session started: {session_id}")
print(f"Total questions: {len(questions)}")

# 2. Answer each question
for i, question in enumerate(questions):
    print(f"\nQuestion {i+1}: {question['question']}")

    # Record answer (assuming you have audio files)
    audio_file = f'answer_{i+1}.wav'

    with open(audio_file, 'rb') as audio:
        response = requests.post(
            f'{BASE_URL}/api/interview/session/{session_id}/answer',
            files={'audio': audio},
            data={'question_index': i}
        )

    result = response.json()
    print(f"Score: {result['scores']['overall']}")
    print(f"Progress: {result['progress']['percentage']}%")

# 3. Get final results
response = requests.get(
    f'{BASE_URL}/api/interview/session/{session_id}/results'
)
results = response.json()

print("\n" + "="*50)
print("FINAL RESULTS")
print("="*50)
print(f"Average Score: {results['summary']['average_scores']['overall']}")
print(f"Best Score: {results['summary']['best_score']}")
print(f"Total Filler Words: {results['summary']['total_filler_words']}")

# 4. Clean up
requests.delete(f'{BASE_URL}/api/interview/session/{session_id}')
print("\nSession deleted")
```

### Quick Single Question Analysis

```python
import requests

BASE_URL = 'http://localhost:5000'

# Get a random question
response = requests.get(f'{BASE_URL}/api/interview/questions/random')
question = response.json()['questions'][0]

print(f"Question: {question['question']}")

# Analyze answer
with open('my_answer.wav', 'rb') as audio:
    response = requests.post(
        f'{BASE_URL}/api/interview/analyze',
        files={'audio': audio},
        data={'question_id': question['id']}
    )

result = response.json()['data']

print(f"\nTranscription: {result['transcription']}")
print(f"Overall Score: {result['scores']['overall']}")
print(f"\nFeedback:")
print(result['feedback'])
print(f"\nImprovements:")
for improvement in result['improvements']:
    print(f"  - {improvement}")
```

---

## Rate Limits

**Current**: No rate limiting (development)

**Production**: TBD
- Recommended: 100 requests/hour per IP
- Interview analysis: 10 requests/hour per IP (more expensive operation)

---

## Changelog

### Version 1.0.0 (2025-11-17)
- Initial release
- 7 endpoints
- Full interview session support
- Comprehensive analysis (pronunciation + content + structure + grammar + fillers)

---

## Support

For issues or questions:
- Check the main README: `/README.md`
- Check interview module docs: `/interview/README.md`
- Review implementation plan: `/INTERVIEW_FEATURES_PLAN.md`

---

**Last Updated**: 2025-11-17
**API Version**: 1.0.0
