# 🎯 Interview Skills Module

**영어 면접 스킬 향상 모듈**

---

## 📋 Overview

This module extends the English pronunciation AI system with comprehensive interview practice features.

### ✨ Current Features (Implemented)

✅ **Interview Question Database**
- 25+ curated interview questions
- Multiple categories (behavioral, situational, technical, etc.)
- Industry-specific questions (Tech, Business, Marketing, Sales)
- Difficulty levels (Beginner, Intermediate, Advanced)

✅ **Interview Answer Analyzer**
- Pronunciation analysis (integrated with existing system)
- Content evaluation (keyword matching)
- STAR structure detection
- Basic grammar checking
- Filler word detection
- Duration assessment
- Comprehensive feedback generation
- Improvement suggestions

---

## 📁 File Structure

```
interview/
├── README.md                      # This file
├── interview_questions.json       # Question database (25 questions)
├── interview_analyzer.py          # Core analysis engine
└── (to be added)
    ├── interview_api.py          # API endpoints
    ├── interview_ui.py           # Streamlit UI components
    └── interview_session.py      # Mock interview session manager
```

---

## 🚀 Quick Start

### 1. Test the Interview Analyzer

```python
from interview.interview_analyzer import InterviewAnalyzer, get_random_question

# Initialize analyzer
analyzer = InterviewAnalyzer()

# Get a random question
question = get_random_question(category='behavioral', difficulty='intermediate')
print(f"Question: {question['question']}")

# Analyze an answer (assuming you have an audio file)
result = analyzer.analyze_interview_answer(
    audio_path='answer.wav',
    question=question
)

print(f"Overall Score: {result['scores']['overall']}")
print(f"Feedback: {result['feedback']}")
```

### 2. Load Questions

```python
from interview.interview_analyzer import load_questions

# Load all questions
all_questions = load_questions()

# Filter by category
behavioral_questions = load_questions(category='behavioral')

# Filter by difficulty
intermediate_questions = load_questions(difficulty='intermediate')

# Multiple filters
tech_advanced = load_questions(industry='tech', difficulty='advanced')
```

---

## 📊 Question Database

### Categories

- **self-introduction** - 자기소개
- **behavioral** - 경험 기반 질문
- **situational** - 상황 대처 질문
- **strengths-weaknesses** - 강점/약점
- **career-goals** - 커리어 목표
- **company-role** - 회사/직무 관련
- **technical** - 기술 질문

### Industries

- **general** - 일반
- **tech** - IT/기술
- **business** - 비즈니스
- **marketing** - 마케팅
- **sales** - 영업

### Difficulty Levels

- **beginner** - 초급 (3 questions)
- **intermediate** - 중급 (14 questions)
- **advanced** - 고급 (8 questions)

---

## 🔍 Analysis Components

### 1. Pronunciation Analysis (20%)
- Leverages existing `PronunciationAnalyzer`
- Word accuracy
- Phoneme similarity
- Prosody (speaking rate, pitch, energy)

### 2. Content Evaluation (30%)
- Keyword matching with question keywords
- Answer length assessment
- Relevance scoring

### 3. Structure Analysis (20%)
- STAR method detection
  - **S**ituation - 상황 설명
  - **T**ask - 과제/목표
  - **A**ction - 실제 행동
  - **R**esult - 결과/배운 점
- Structure completeness scoring

### 4. Grammar Check (15%)
- Basic grammar pattern checking
- Capitalization
- Punctuation
- Spacing

### 5. Filler Word Detection
- Detects: "um", "uh", "like", "you know", etc.
- Counts occurrences
- Calculates density (fillers per 100 words)

### 6. Duration Evaluation (15%)
- Compares actual vs. ideal duration
- Allows ±30% tolerance
- Penalizes too short or too long answers

---

## 📈 Scoring System

### Overall Score Calculation

```
Overall Score = (
    Pronunciation × 0.20 +
    Content      × 0.30 +
    Structure    × 0.20 +
    Grammar      × 0.15 +
    Duration     × 0.15
)
```

### Score Ranges

| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | 🎉 Excellent | 훌륭한 답변 |
| 80-89 | 👍 Good | 좋은 답변 |
| 70-79 | 📚 Fair | 괜찮은 답변 |
| 60-69 | 💪 Needs Work | 연습 필요 |
| 0-59 | 📖 Poor | 많은 개선 필요 |

---

## 💡 Example Usage

### Complete Analysis Flow

```python
from interview.interview_analyzer import InterviewAnalyzer, load_questions

# 1. Initialize
analyzer = InterviewAnalyzer()

# 2. Load questions
questions = load_questions(category='behavioral', difficulty='intermediate')
question = questions[0]

# 3. Analyze answer
result = analyzer.analyze_interview_answer(
    audio_path='my_answer.wav',
    question=question
)

# 4. Display results
print(f"Transcription: {result['transcription']}")
print(f"\nScores:")
for key, value in result['scores'].items():
    print(f"  {key}: {value}")

print(f"\nFeedback:")
print(result['feedback'])

print(f"\nImprovements:")
for improvement in result['improvements']:
    print(f"  - {improvement}")

print(f"\nFiller Words: {result['filler_words']['count']}")
if result['filler_words']['words']:
    print(f"  Most used: {list(result['filler_words']['words'].items())}")
```

### Expected Output

```
Transcription: well in my previous role i faced a challenging situation...

Scores:
  overall: 78.5
  pronunciation: 85.0
  content: 75.0
  structure: 70.0
  grammar: 90.0
  duration: 80.0

Feedback:
👍 좋은 답변입니다! 약간의 개선으로 완벽해질 수 있습니다.

📊 종합 점수: 78.5점
   • 발음: 85점
   • 내용: 75점
   • 구조: 70점
   • 문법: 90점
   • 시간관리: 80점

✅ 강점: 발음이 명확합니다, 문법이 정확합니다
⚠️ 개선할 점: STAR 구조로 답변을 정리해보세요

🗣️ 필러 워드를 3회 사용했습니다. (밀도: 2.5%) 줄이도록 노력하세요.
   특히 'well'을(를) 2회 사용했습니다.

Improvements:
  - 💡 질문의 핵심 키워드를 답변에 포함시키세요: challenge, problem-solving, overcome
  - 🏗️ STAR 메서드를 활용하세요:
      • Situation (상황): 어떤 상황이었나요?
      • Task (과제): 무엇을 해야 했나요?
      • Action (행동): 어떻게 했나요?
      • Result (결과): 결과는 어땠나요?

Filler Words: 3
  Most used: [('well', 2), ('um', 1)]
```

---

## 🎯 Next Steps (To Be Implemented)

### Phase 1: API Integration ⏳
- [ ] Create `/api/interview/*` endpoints
- [ ] Integrate with existing Flask API
- [ ] Add session management

### Phase 2: UI Implementation ⏳
- [ ] Add "면접 연습" tab to Streamlit app
- [ ] Mock interview mode with multiple questions
- [ ] Progress tracking dashboard
- [ ] History viewer

### Phase 3: Advanced Features 🔮
- [ ] GPT integration for follow-up questions
- [ ] Sample answer generation
- [ ] Video recording support
- [ ] AI interviewer with voice (TTS)

---

## 🧪 Testing

### Run the demo

```bash
cd interview
python interview_analyzer.py
```

### Test with real audio

```python
# Create a test script
from interview.interview_analyzer import InterviewAnalyzer, get_random_question

analyzer = InterviewAnalyzer()
question = get_random_question()

result = analyzer.analyze_interview_answer(
    audio_path='path/to/your/answer.wav',
    question=question
)

print(result['feedback'])
```

---

## 📚 Documentation

- **Implementation Plan**: `/INTERVIEW_FEATURES_PLAN.md` - Complete roadmap
- **API Documentation**: (To be added)
- **User Guide**: (To be added)

---

## 🔧 Configuration

### Scoring Weights

Edit in `interview_analyzer.py`:

```python
def calculate_overall_interview_score(...):
    overall = (
        pronunciation_score * 0.20 +  # Adjust weights here
        content_score * 0.30 +
        structure_score * 0.20 +
        grammar_score * 0.15 +
        duration_score * 0.15
    )
```

### Filler Words

Add/remove filler words in `interview_analyzer.py`:

```python
FILLER_WORDS = [
    'um', 'uh', 'er', 'ah', 'like',
    'you know', 'i mean', ...
]
```

### STAR Keywords

Customize STAR detection keywords:

```python
STAR_KEYWORDS = {
    'situation': ['situation', 'context', ...],
    'task': ['task', 'challenge', ...],
    ...
}
```

---

## 🤝 Contributing

To add new questions:

1. Edit `interview_questions.json`
2. Follow the existing format
3. Include all required fields
4. Update metadata counts

---

## 📞 Support

For questions or issues, refer to:
- Main README: `/README.md`
- Implementation plan: `/INTERVIEW_FEATURES_PLAN.md`
- CLAUDE.md for AI assistants: `/CLAUDE.md`

---

**Version:** 1.0 (Alpha)
**Last Updated:** 2025-11-17
**Status:** Core features implemented, API and UI pending
