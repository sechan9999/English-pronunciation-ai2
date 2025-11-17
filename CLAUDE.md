# CLAUDE.md - AI Assistant Guide

**English Pronunciation AI Analysis System**
*A comprehensive guide for AI assistants working on this codebase*

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Architecture](#codebase-architecture)
3. [Core Components](#core-components)
4. [Development Workflows](#development-workflows)
5. [Coding Conventions](#coding-conventions)
6. [Testing Strategy](#testing-strategy)
7. [Deployment](#deployment)
8. [Common Tasks](#common-tasks)
9. [Important Notes](#important-notes)
10. [Git Workflow](#git-workflow)

---

## 🎯 Project Overview

### Purpose
An AI-powered English pronunciation analysis platform that provides real-time feedback on pronunciation accuracy using:
- **OpenAI Whisper** for Speech-to-Text (STT)
- **Phoneme analysis** using CMU Pronouncing Dictionary
- **Prosody analysis** for speech rhythm, pitch, and energy
- **AI-generated feedback** for personalized improvement suggestions

### Target Users
- English language learners (beginner to advanced)
- Anyone looking to improve English pronunciation
- Educators and language learning platforms

### Key Features
- Real-time microphone recording via web browser
- Audio file upload support (WAV, MP3, M4A)
- Pronunciation accuracy scoring (0-100)
- Word-level and phoneme-level analysis
- Prosody analysis (speaking rate, pitch variation, energy)
- Practice sentence library (daily/business/travel)
- REST API for integration with other applications

---

## 🏗️ Codebase Architecture

### Project Structure

```
English-pronunciation-ai2/
│
├── pronunciation_analyzer.py    # Core analysis engine (business logic)
│   └── PronunciationAnalyzer    # Main class with all analysis methods
│
├── api.py                       # Flask REST API server
│   ├── /health                  # Health check endpoint
│   ├── /api/analyze             # Full pronunciation analysis
│   ├── /api/transcribe          # STT only
│   ├── /api/score               # Text-based scoring
│   ├── /api/phonemes            # Phoneme extraction
│   └── /api/practice-sentences  # Get practice sentences
│
├── app.py                       # Streamlit web application
│   ├── UI components            # User interface
│   ├── Audio recording          # Microphone integration
│   └── Results visualization    # Score display and feedback
│
├── demo.py                      # CLI demo and testing
├── test_api.py                  # API integration tests
│
├── requirements.txt             # Python dependencies
├── packages.txt                 # System packages (FFmpeg)
├── .env.example                 # Environment configuration template
│
└── Documentation/
    ├── README.md                # Main documentation (Korean)
    ├── ARCHITECTURE.md          # System architecture details
    ├── QUICKSTART.md            # Quick start guide
    ├── UPDATE_RECORDING.md      # Microphone recording feature docs
    └── STREAMLIT_DEPLOY.md      # Deployment instructions
```

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│               PRESENTATION LAYER                        │
├──────────────────┬──────────────────┬──────────────────┤
│  Streamlit UI    │  Flask REST API  │  Future: Mobile  │
│  (app.py)        │  (api.py)        │                  │
└──────────────────┴──────────────────┴──────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              BUSINESS LOGIC LAYER                       │
│        PronunciationAnalyzer Class                      │
│        (pronunciation_analyzer.py)                      │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │   STT    │  │ Scoring  │  │ Feedback │            │
│  │ Whisper  │  │  Engine  │  │Generator │            │
│  └──────────┘  └──────────┘  └──────────┘            │
│                                                         │
│  ┌──────────┐  ┌──────────┐                           │
│  │ Phoneme  │  │ Prosody  │                           │
│  │ Analyzer │  │ Analyzer │                           │
│  └──────────┘  └──────────┘                           │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  DATA LAYER                             │
├──────────────┬──────────────┬──────────────────────────┤
│   librosa    │  CMU Dict    │  Whisper Models          │
│   (audio)    │  (phonemes)  │  (ML models)             │
└──────────────┴──────────────┴──────────────────────────┘
```

---

## 🔧 Core Components

### 1. `pronunciation_analyzer.py` - Core Engine

**Class: `PronunciationAnalyzer`**

This is the **heart of the system**. All pronunciation analysis logic lives here.

#### Key Methods:

```python
__init__(model_size="base")
# Initializes Whisper model
# Model sizes: "tiny", "base", "small", "medium", "large"
# Trade-off: larger = more accurate but slower + more memory

transcribe_audio(audio_path: str) -> str
# Converts audio to text using Whisper
# Returns: lowercase transcribed text
# Location: pronunciation_analyzer.py:53

get_phonemes(text: str) -> List[str]
# Converts text to phoneme list using CMU Dictionary
# Returns: list of phonemes (e.g., ["HH", "AH0", "L", "OW1"])
# Location: pronunciation_analyzer.py:72

calculate_pronunciation_score(reference_text: str, spoken_text: str) -> Dict
# Core scoring algorithm
# Returns: {
#   'overall_score': float,        # 0-100 weighted score
#   'word_accuracy': float,        # % of correct words
#   'phoneme_similarity': float,   # % phoneme match
#   'mispronounced_words': list,   # [{expected, spoken, position}]
#   'word_count': int,
#   'correct_words': int
# }
# Location: pronunciation_analyzer.py:98

analyze_prosody(audio_path: str) -> Dict
# Analyzes speech patterns using librosa
# Returns: {
#   'speaking_rate': float,      # syllables per second
#   'pitch_variation': float,    # F0 standard deviation
#   'energy_variation': float    # RMS standard deviation
# }
# Location: pronunciation_analyzer.py:157

generate_feedback(pronunciation_result: Dict, prosody_result: Dict) -> str
# Generates human-friendly feedback in Korean
# Uses score thresholds:
#   90-100: Excellent
#   75-89: Good
#   60-74: Average
#   0-59: Needs improvement
# Location: pronunciation_analyzer.py:209

full_analysis(audio_path: str, reference_text: str) -> Dict
# Complete pipeline: STT → Scoring → Prosody → Feedback
# This is the main entry point for full analysis
# Location: pronunciation_analyzer.py:262
```

#### Scoring Algorithm

```python
# Word Accuracy (60% weight)
word_accuracy = (matching_words / total_words) * 100

# Phoneme Similarity (40% weight)
phoneme_similarity = SequenceMatcher(ref_phonemes, spoken_phonemes).ratio() * 100

# Overall Score
overall_score = (word_accuracy * 0.6) + (phoneme_similarity * 0.4)
```

**Why these weights?**
- Word accuracy (60%): Semantic meaning is more important
- Phoneme similarity (40%): Fine-grained pronunciation details

---

### 2. `api.py` - REST API Server

**Framework:** Flask with CORS enabled

#### Endpoints:

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| GET | `/health` | Health check | None | `{status, service, version}` |
| POST | `/api/analyze` | Full analysis | `audio` (file), `reference_text` (string) | Full analysis result |
| POST | `/api/transcribe` | STT only | `audio` (file) | `{text}` |
| POST | `/api/score` | Text scoring | `{reference_text, spoken_text}` (JSON) | `{score, details, feedback}` |
| POST | `/api/phonemes` | Extract phonemes | `{text}` (JSON) | `{phonemes, phoneme_count}` |
| GET | `/api/practice-sentences` | Get practice sentences | `?level=&category=` | List of sentences |

#### Important Patterns:

**Temporary File Handling:**
```python
# Pattern used throughout api.py
with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
    audio_file.save(tmp_file.name)
    tmp_path = tmp_file.name

try:
    result = analyzer.full_analysis(tmp_path, reference_text)
finally:
    if os.path.exists(tmp_path):
        os.remove(tmp_path)  # Always cleanup!
```

**Global Analyzer Instance:**
```python
# Single instance loaded once at startup (api.py:16)
analyzer = PronunciationAnalyzer(model_size="base")
```
**Why?** Whisper model loading is expensive (~1-3 seconds). Reuse the same instance.

---

### 3. `app.py` - Streamlit Web UI

**Key Features:**
- File upload or microphone recording
- Practice sentence selection
- Real-time analysis with progress indicators
- Visual score display with progress bars
- Session state management for history

#### Session State:

```python
st.session_state.analyzer      # PronunciationAnalyzer instance
st.session_state.history        # List of past analysis results
```

#### Microphone Recording:

Uses `audio-recorder-streamlit` package (app.py:150):
```python
audio_bytes = audio_recorder(
    text="🎙️ 녹음 시작/중지",
    recording_color="#e74c3c",
    neutral_color="#6aa84f",
    icon_name="microphone",
    icon_size="3x",
)
```

**Browser Compatibility:**
- Chrome ✅ (recommended)
- Edge ✅
- Safari ✅ (desktop + iOS)
- Firefox ✅
- Requires HTTPS for microphone access (Streamlit Cloud provides this)

---

### 4. `demo.py` - CLI Demo

**Purpose:** Test the system without audio files using text-based simulation

**Functions:**
- `demo_text_analysis()`: Run test cases (demo.py:16)
- `demo_phoneme_extraction()`: Show phoneme conversion (demo.py:87)
- `demo_interactive_mode()`: Interactive CLI test (demo.py:111)
- `demo_comparison()`: Compare different proficiency levels (demo.py:153)
- `show_api_examples()`: Display API usage examples (demo.py:198)

---

## 🔄 Development Workflows

### Adding a New Feature

1. **Read existing code first**
   - Check if similar functionality exists
   - Understand the current architecture
   - Look for reusable components

2. **Modify the core engine** (`pronunciation_analyzer.py`)
   - Add new methods to `PronunciationAnalyzer` class
   - Follow existing patterns (type hints, docstrings)
   - Return dictionaries for structured data

3. **Expose via API** (`api.py`)
   - Add new endpoint following REST conventions
   - Use `try/except` with proper error codes
   - Clean up temporary files in `finally` block

4. **Update UI** (`app.py`)
   - Add UI controls in sidebar or main area
   - Use `st.session_state` for persistent data
   - Show results with appropriate Streamlit components

5. **Test**
   - Add test case to `test_api.py`
   - Test manually with `demo.py`
   - Verify on Streamlit UI

6. **Document**
   - Update README.md with new feature
   - Add examples to QUICKSTART.md
   - Update ARCHITECTURE.md if architecture changes

### Debugging Common Issues

**Issue: Whisper model not loading**
```python
# Check in pronunciation_analyzer.py:46
if WHISPER_AVAILABLE:
    try:
        self.whisper_model = whisper.load_model(model_size)
```
**Solution:** Use smaller model (`tiny` or `base`) or ensure sufficient RAM

**Issue: Phoneme library not available**
```python
# Fallback in pronunciation_analyzer.py:80
if not PRONOUNCING_AVAILABLE:
    return text.lower().split()  # Simple word split
```
**Solution:** Install `pronouncing` library: `pip install pronouncing`

**Issue: CORS errors in API**
```python
# Check api.py:13
CORS(app)  # Should be enabled
```
**Solution:** Add specific origins if needed: `CORS(app, origins=["http://localhost:3000"])`

---

## 📝 Coding Conventions

### Python Style

**Follow PEP 8** with these project-specific conventions:

1. **Type Hints (Encouraged)**
   ```python
   def get_phonemes(self, text: str) -> List[str]:
       ...
   ```

2. **Docstrings (Required for public methods)**
   ```python
   def calculate_pronunciation_score(
       self,
       reference_text: str,
       spoken_text: str
   ) -> Dict[str, any]:
       """
       발음 정확도 스코어 계산
       Args:
           reference_text: 참조(정답) 텍스트
           spoken_text: 사용자가 말한 텍스트 (STT 결과)
       Returns:
           스코어 정보 딕셔너리
       """
   ```

3. **Korean Comments OK**
   - This project uses Korean comments for Korean-speaking team
   - User-facing messages are in Korean
   - Code/variable names are in English

4. **Error Handling Pattern**
   ```python
   try:
       # Main logic
       result = process_data()
   except SpecificError as e:
       # Handle specific errors
       print(f"Error: {e}")
       return default_value
   finally:
       # Always cleanup (files, resources)
       cleanup()
   ```

5. **Constants and Configuration**
   - Use `.env.example` template for configuration
   - Reference: `.env.example:1-48`
   - Load with environment variables (not implemented yet, TODO)

### File Organization

**Keep related code together:**
- All analysis logic → `pronunciation_analyzer.py`
- All API routes → `api.py`
- All UI code → `app.py`

**Don't mix concerns:**
- ❌ Don't put API logic in `pronunciation_analyzer.py`
- ❌ Don't put UI code in `api.py`
- ✅ Keep business logic separate from presentation

---

## 🧪 Testing Strategy

### Current Testing

**Manual Testing:**
1. `python demo.py` - Text-based tests
2. `python test_api.py` - API integration tests
3. `streamlit run app.py` - UI testing

**API Tests** (`test_api.py`):
- Health check test (test_api.py:10)
- Transcription test (test_api.py:16)
- Scoring test (test_api.py:30)
- Phoneme extraction test (test_api.py:50)
- Practice sentences test (test_api.py:66)

### Testing Best Practices

**Before committing:**
1. Run `python demo.py` to verify core logic
2. Run `python test_api.py` (requires API server running)
3. Test one feature in Streamlit UI
4. Check for Python errors: `python -m py_compile *.py`

**When adding new features:**
1. Add test case to `test_api.py` if API-related
2. Add example to `demo.py` if core logic-related
3. Manually test in Streamlit app

### Future Testing TODO

- [ ] Add pytest unit tests
- [ ] Add test coverage reports (target: 80%+)
- [ ] Add CI/CD pipeline with automated tests
- [ ] Add load testing for API endpoints
- [ ] Add browser compatibility tests for UI

---

## 🚀 Deployment

### Streamlit Cloud Deployment

**Current Deployment:** https://english-pronunciation-ai.streamlit.app

**Deployment Process:**
1. Push to GitHub repository
2. Streamlit Cloud auto-deploys from `main` branch
3. Takes 2-3 minutes to rebuild

**Required Files:**
- `requirements.txt` - Python dependencies
- `packages.txt` - System packages (FFmpeg)
- `.streamlit/config.toml` - Streamlit configuration (if exists)

**Environment:**
- Python 3.10+
- Limited RAM (~1GB free tier)
- Uses Whisper `base` model (good balance)

### API Deployment (Future)

**Options:**
1. **Docker** - See ARCHITECTURE.md:379 for Dockerfile template
2. **AWS/GCP** - Use container services
3. **Heroku** - Simple deployment option

**Considerations:**
- Whisper model size vs. available RAM
- Cold start time (model loading)
- Request timeout limits (Whisper can take 5-10s)

---

## 🛠️ Common Tasks

### Task 1: Change Whisper Model Size

**When:** If deployment runs out of memory or needs faster processing

```python
# In api.py:16 or app.py:21
analyzer = PronunciationAnalyzer(model_size="tiny")  # Fastest, less accurate
analyzer = PronunciationAnalyzer(model_size="base")  # Default, balanced
analyzer = PronunciationAnalyzer(model_size="small") # Slower, more accurate
```

**Model Comparison:**

| Model | Size | Speed | Accuracy | RAM |
|-------|------|-------|----------|-----|
| tiny  | 39MB | Very Fast | Low | ~1GB |
| base  | 74MB | Fast | Medium | ~1GB |
| small | 244MB | Medium | High | ~2GB |
| medium| 769MB | Slow | Very High | ~5GB |

### Task 2: Add New Practice Sentences

**Location:** `api.py:231-292` (practice sentence dictionary)

```python
sentences = {
    'beginner': {
        'daily': [
            "Your new sentence here",  # Add here
            ...
        ],
        'business': [...],
        'travel': [...]
    },
    ...
}
```

Also update `app.py:53-70` for UI dropdowns if needed.

### Task 3: Adjust Scoring Weights

**Location:** `pronunciation_analyzer.py:146`

```python
# Current: 60% word accuracy, 40% phoneme similarity
overall_score = (word_accuracy * 0.6) + (phoneme_similarity * 0.4)

# Example: Emphasize phoneme accuracy more
overall_score = (word_accuracy * 0.5) + (phoneme_similarity * 0.5)
```

**Also update:** `.env.example:23-25` to document the change

### Task 4: Add New API Endpoint

**Pattern:**
```python
@app.route('/api/your-endpoint', methods=['POST'])
def your_function():
    """
    Brief description

    Request: describe input
    Response: describe output
    """
    try:
        # 1. Validate input
        if 'required_field' not in request.json:
            return jsonify({'error': 'missing field', 'code': 'ERROR_CODE'}), 400

        # 2. Process
        result = analyzer.your_method(...)

        # 3. Return success
        return jsonify({'success': True, 'data': result}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'code': 'FAILED'}), 500
```

**Don't forget:**
1. Add error code to documentation
2. Add test to `test_api.py`
3. Update API documentation in README.md

### Task 5: Modify Feedback Messages

**Location:** `pronunciation_analyzer.py:209-260`

```python
def generate_feedback(self, pronunciation_result: Dict, prosody_result: Dict) -> str:
    score = pronunciation_result['overall_score']
    feedback_parts = []

    # Modify thresholds or messages here
    if score >= 90:
        feedback_parts.append("🎉 훌륭합니다! 발음이 매우 정확해요.")
    elif score >= 75:
        feedback_parts.append("👍 좋아요! 발음이 꽤 정확합니다.")
    # ... add more conditions or change messages
```

---

## ⚠️ Important Notes

### Critical Dependencies

1. **FFmpeg** (System Package)
   - Required for: Audio file processing
   - Installation: See `packages.txt` and README.md:87-93
   - Missing FFmpeg = Audio processing fails

2. **OpenAI Whisper**
   - Large download on first run (~74MB for base model)
   - Model cached after first load
   - Requires significant RAM

3. **Pronouncing Library**
   - Uses CMU Pronouncing Dictionary
   - Fallback available if missing (word-level split)
   - Essential for phoneme analysis

### Performance Considerations

**Whisper Transcription:**
- Typical time: 3-10 seconds for 5-second audio
- Blocking operation (user must wait)
- Consider showing progress indicator

**Memory Usage:**
- Base model: ~1GB RAM when loaded
- Keep analyzer as singleton (don't create multiple instances)
- Clean up temporary audio files

**API Request Timeout:**
- Flask default: 30 seconds
- Whisper can exceed this for long audio
- Consider async processing for production

### Security Notes

**Current State:**
- ⚠️ No authentication
- ⚠️ No rate limiting
- ⚠️ CORS fully open (`CORS(app)`)

**Production TODO:**
- Add API key authentication
- Implement rate limiting (see `.env.example:40`)
- Restrict CORS origins
- Validate file types strictly
- Limit audio file size
- Sanitize user inputs

### Known Limitations

1. **Phoneme Dictionary Coverage**
   - CMU dict doesn't have all words
   - Fallback: character-level split (pronunciation_analyzer.py:93)
   - May affect scoring for uncommon words

2. **Prosody Analysis Accuracy**
   - Basic implementation using librosa
   - Not as accurate as specialized tools
   - Good for relative comparison, not absolute measurement

3. **Single Language Support**
   - Only English pronunciation analysis
   - Adding languages requires new phoneme dictionaries

4. **No User Accounts**
   - No progress tracking across sessions
   - History lost on page refresh
   - Future: Add database + authentication

---

## 🔀 Git Workflow

### Branch Strategy

**Main Branch:** `main`
- Production-ready code
- Auto-deploys to Streamlit Cloud
- Protected (should require PR reviews in production)

**Feature Branches:** `claude/claude-md-*` pattern
- Example: `claude/claude-md-mi3ae1m26us748gh-01Bz3Sc5NvYPkMiZMUxnqBak`
- Created for specific tasks/features
- Merged to main after completion

### Commit Message Conventions

**Format:**
```
<emoji> <type>: <subject>

Examples:
🎤 Add real-time microphone recording feature
📚 Update documentation for API endpoints
🐛 Fix phoneme extraction for unknown words
♻️ Refactor scoring algorithm
📝 Add GitHub push instructions
🚀 Add Streamlit Cloud deployment configuration
```

**Common Emojis:**
- 🎤 Audio/recording features
- 📚 Documentation
- 🐛 Bug fixes
- ♻️ Refactoring
- 📝 Documentation/instructions
- 🚀 Deployment
- ✨ New features
- 🔧 Configuration

### Git Commands Reference

**Creating Feature Branch:**
```bash
git checkout -b claude/claude-md-feature-name
```

**Committing Changes:**
```bash
git add .
git status  # Verify changes
git commit -m "🎤 Add your feature description"
```

**Pushing to Remote:**
```bash
# First push (set upstream)
git push -u origin claude/claude-md-feature-name

# Subsequent pushes
git push
```

**Important:** Branch names must start with `claude/` and end with matching session ID for Claude Code integration.

---

## 📚 Additional Resources

### Documentation Files

- **README.md** - User guide, installation, API docs
- **ARCHITECTURE.md** - System architecture, algorithms
- **QUICKSTART.md** - Quick start examples, integration samples
- **UPDATE_RECORDING.md** - Microphone feature documentation
- **STREAMLIT_DEPLOY.md** - Deployment guide
- **PROJECT_SUMMARY.md** - Project summary
- **GIT_SETUP_COMPLETE.md** - Git setup instructions
- **GITHUB_PUSH_INSTRUCTIONS.md** - Push instructions

### External Documentation

- **Whisper:** https://github.com/openai/whisper
- **Pronouncing:** https://pronouncing.readthedocs.io/
- **Librosa:** https://librosa.org/doc/latest/
- **Flask:** https://flask.palletsprojects.com/
- **Streamlit:** https://docs.streamlit.io/
- **audio-recorder-streamlit:** https://github.com/stefanrmmr/streamlit_audio_recorder

### Key Files by Size/Importance

1. **pronunciation_analyzer.py** (10.7 KB) - Core logic ⭐⭐⭐⭐⭐
2. **app.py** (11.2 KB) - Main UI ⭐⭐⭐⭐
3. **api.py** (9.3 KB) - API server ⭐⭐⭐⭐
4. **demo.py** (8.6 KB) - Testing/examples ⭐⭐⭐
5. **test_api.py** (8.0 KB) - API tests ⭐⭐⭐

---

## 🎯 Quick Reference Cheat Sheet

### Running the Application

```bash
# Web UI (recommended for users)
streamlit run app.py

# API Server (for integrations)
python api.py

# CLI Demo (for testing)
python demo.py

# API Tests (server must be running)
python test_api.py
```

### Common Code Locations

| What | Where |
|------|-------|
| Scoring algorithm | `pronunciation_analyzer.py:98-155` |
| Feedback generation | `pronunciation_analyzer.py:209-260` |
| Whisper STT | `pronunciation_analyzer.py:53-70` |
| Phoneme conversion | `pronunciation_analyzer.py:72-96` |
| Prosody analysis | `pronunciation_analyzer.py:157-207` |
| API endpoints | `api.py:19-299` |
| Streamlit UI | `app.py:12-302` |
| Practice sentences | `api.py:231-292` |
| Scoring weights | `pronunciation_analyzer.py:146` |
| Model initialization | `pronunciation_analyzer.py:37-51` |

### Environment Variables (.env.example)

```bash
WHISPER_MODEL_SIZE=base          # Model size
API_PORT=5000                    # API port
MAX_AUDIO_LENGTH=60              # Max audio seconds
WORD_ACCURACY_WEIGHT=0.6         # Scoring weight
PHONEME_SIMILARITY_WEIGHT=0.4    # Scoring weight
```

### Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Out of memory | Use `model_size="tiny"` |
| Slow transcription | Use smaller model or shorter audio |
| CORS errors | Check `CORS(app)` in api.py:13 |
| FFmpeg not found | Install: `sudo apt-get install ffmpeg` |
| Phoneme errors | Install: `pip install pronouncing` |
| Import errors | Run: `pip install -r requirements.txt` |

---

## 📋 Checklist for AI Assistants

When working on this codebase:

**Before Starting:**
- [ ] Read this CLAUDE.md file completely
- [ ] Understand the architecture (3-layer design)
- [ ] Check existing functionality before adding new code
- [ ] Review recent commits for context

**During Development:**
- [ ] Follow the established patterns (error handling, docstrings)
- [ ] Keep business logic in `pronunciation_analyzer.py`
- [ ] Clean up temporary files in `finally` blocks
- [ ] Use type hints for function signatures
- [ ] Add docstrings for public methods

**Before Committing:**
- [ ] Test with `python demo.py`
- [ ] Test with `python test_api.py` (if API changes)
- [ ] Test manually in Streamlit UI (if UI changes)
- [ ] Update relevant documentation files
- [ ] Use descriptive commit message with emoji
- [ ] Verify no hardcoded secrets or credentials

**After Committing:**
- [ ] Push to appropriate branch
- [ ] Verify deployment if pushing to main
- [ ] Update project documentation if architecture changed
- [ ] Notify team of breaking changes

---

## 🤝 Contributing Guidelines for AI Assistants

### Communication Style
- Explain changes clearly
- Provide code examples when suggesting modifications
- Reference line numbers (e.g., `pronunciation_analyzer.py:146`)
- Highlight trade-offs and implications

### Code Quality
- Maintain existing code style
- Don't over-engineer simple solutions
- Prefer readability over cleverness
- Keep functions focused and single-purpose

### Documentation
- Update docs when changing functionality
- Keep CLAUDE.md in sync with codebase
- Add comments for non-obvious logic
- Maintain Korean comments where they exist

### Testing
- Test changes before committing
- Don't break existing functionality
- Add tests for new features
- Verify edge cases

---

**Last Updated:** 2025-11-17
**Version:** 1.0.0
**Maintained by:** AI Assistants working on this project

---

*This guide should be updated whenever significant architectural changes occur or new patterns are established.*
