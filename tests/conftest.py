"""
Pytest configuration and shared fixtures
This file is automatically loaded by pytest and provides reusable test fixtures
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import numpy as np


# ============================================================================
# Analyzer Fixtures
# ============================================================================

@pytest.fixture
def pronunciation_analyzer():
    """
    Fixture providing a PronunciationAnalyzer instance
    Uses 'tiny' model for faster testing
    """
    from pronunciation_analyzer import PronunciationAnalyzer
    return PronunciationAnalyzer(model_size="tiny")


@pytest.fixture
def interview_analyzer():
    """
    Fixture providing an InterviewAnalyzer instance
    """
    from interview.interview_analyzer import InterviewAnalyzer
    return InterviewAnalyzer()


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_whisper_model():
    """
    Mock Whisper model for fast testing without actual model loading
    Returns a mock that can be configured in tests
    """
    mock_model = Mock()
    mock_model.transcribe.return_value = {"text": "hello world"}
    return mock_model


@pytest.fixture
def mock_whisper(monkeypatch, mock_whisper_model):
    """
    Patches Whisper to use mock model
    Use this fixture to avoid loading actual Whisper models in tests
    """
    monkeypatch.setattr(
        'whisper.load_model',
        lambda model_size: mock_whisper_model
    )
    monkeypatch.setattr('pronunciation_analyzer.WHISPER_AVAILABLE', True)
    return mock_whisper_model


@pytest.fixture
def mock_librosa(monkeypatch):
    """
    Patches librosa functions for prosody analysis testing
    """
    # Mock audio loading
    def mock_load(path, sr=None):
        return (np.random.rand(22050), 22050)  # 1 second of random audio

    # Mock beat tracking
    def mock_beat_track(y=None, sr=None):
        return (120.0, np.array([]))  # 120 BPM

    # Mock pitch tracking
    def mock_piptrack(y=None, sr=None):
        pitches = np.random.rand(1025, 100) * 200
        magnitudes = np.random.rand(1025, 100)
        return (pitches, magnitudes)

    # Mock RMS energy
    def mock_rms(y=None):
        return np.random.rand(1, 100)

    # Mock duration
    def mock_get_duration(y=None, sr=None):
        return 5.0  # 5 seconds

    # Apply patches
    import librosa
    monkeypatch.setattr('librosa.load', mock_load)
    monkeypatch.setattr('librosa.beat.beat_track', mock_beat_track)
    monkeypatch.setattr('librosa.piptrack', mock_piptrack)
    monkeypatch.setattr('librosa.feature.rms', mock_rms)
    monkeypatch.setattr('librosa.get_duration', mock_get_duration)
    monkeypatch.setattr('pronunciation_analyzer.LIBROSA_AVAILABLE', True)


# ============================================================================
# File Fixtures
# ============================================================================

@pytest.fixture
def temp_audio_file():
    """
    Creates a temporary audio file for testing
    Automatically cleaned up after test
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        tmp_path = tmp.name

    yield tmp_path

    # Cleanup
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


@pytest.fixture
def temp_directory():
    """
    Creates a temporary directory for testing
    Automatically cleaned up after test
    """
    import shutil

    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_audio_files(temp_directory):
    """
    Creates multiple sample audio files for testing
    Returns dictionary of file paths
    """
    files = {}

    # Create various test files
    for duration in [1, 5, 10]:
        file_path = os.path.join(temp_directory, f"sample_{duration}s.wav")
        # Create empty file (in real tests, would generate actual audio)
        with open(file_path, 'wb') as f:
            f.write(b'RIFF' + b'\x00' * 100)  # Minimal WAV header
        files[f'{duration}s'] = file_path

    return files


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def sample_pronunciation_result():
    """
    Sample pronunciation analysis result
    Useful for testing feedback and reporting functions
    """
    return {
        'overall_score': 85.0,
        'word_accuracy': 90.0,
        'phoneme_similarity': 80.0,
        'mispronounced_words': [
            {'expected': 'world', 'spoken': 'worl', 'position': 1}
        ],
        'word_count': 5,
        'correct_words': 4
    }


@pytest.fixture
def sample_prosody_result():
    """
    Sample prosody analysis result
    """
    return {
        'speaking_rate': 2.0,
        'pitch_variation': 45.5,
        'energy_variation': 0.012
    }


@pytest.fixture
def sample_interview_question():
    """
    Sample interview question for testing
    """
    return {
        'id': 'test-q001',
        'question': 'Tell me about a time when you faced a challenge at work.',
        'question_ko': '직장에서 어려움을 겪었던 경험에 대해 말씀해주세요.',
        'category': 'behavioral',
        'difficulty': 'intermediate',
        'industry': 'general',
        'keywords': ['challenge', 'problem', 'solution', 'result'],
        'ideal_duration': 90,
        'tips': [
            'Use the STAR method',
            'Be specific about your role',
            'Explain the outcome'
        ]
    }


# ============================================================================
# API Testing Fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """
    Flask test client for API testing
    """
    from api import app

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def api_headers():
    """
    Common headers for API requests
    """
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


# ============================================================================
# Database/Session Fixtures (for future use)
# ============================================================================

@pytest.fixture
def mock_interview_session():
    """
    Mock interview session data
    """
    return {
        'session_id': 'test-session-123',
        'interview_type': 'behavioral',
        'questions': [],
        'total_questions': 3,
        'current_question': 0,
        'answers': [],
        'started_at': '2025-11-17T10:00:00',
        'completed_at': None,
        'filters': {
            'category': 'behavioral',
            'difficulty': 'intermediate',
            'industry': 'general'
        }
    }


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """
    Pytest configuration hook
    Add custom markers here
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "requires_audio: marks tests that require real audio files"
    )


# ============================================================================
# Parametrization Helpers
# ============================================================================

# Common test data for parameterized tests
SCORE_RANGES = [
    (95, "excellent"),
    (85, "good"),
    (70, "average"),
    (55, "poor"),
]

TEXT_PAIRS_PERFECT = [
    ("hello", "hello"),
    ("hello world", "hello world"),
    ("how are you", "how are you"),
]

TEXT_PAIRS_PARTIAL = [
    ("hello world", "hello", 50),
    ("hello world how", "hello world", 66),
    ("a b c d e", "a b c", 60),
]

TEXT_PAIRS_MISMATCH = [
    ("hello", "goodbye"),
    ("yes", "no"),
    ("cat", "dog"),
]


# ============================================================================
# Utility Functions for Tests
# ============================================================================

def assert_valid_score(score, min_score=0, max_score=100):
    """
    Helper to assert score is within valid range
    """
    assert isinstance(score, (int, float))
    assert min_score <= score <= max_score


def assert_valid_pronunciation_result(result):
    """
    Helper to assert pronunciation result has correct structure
    """
    required_keys = [
        'overall_score',
        'word_accuracy',
        'phoneme_similarity',
        'mispronounced_words',
        'word_count',
        'correct_words'
    ]

    for key in required_keys:
        assert key in result, f"Missing key: {key}"

    assert_valid_score(result['overall_score'])
    assert_valid_score(result['word_accuracy'])
    assert_valid_score(result['phoneme_similarity'])
    assert isinstance(result['mispronounced_words'], list)
    assert isinstance(result['word_count'], int)
    assert isinstance(result['correct_words'], int)


def assert_valid_interview_result(result):
    """
    Helper to assert interview analysis result has correct structure
    """
    required_keys = [
        'transcription',
        'duration',
        'scores',
        'filler_words',
        'feedback',
        'improvements'
    ]

    for key in required_keys:
        assert key in result, f"Missing key: {key}"

    # Check scores structure
    required_score_keys = [
        'overall',
        'pronunciation',
        'content',
        'structure',
        'grammar',
        'duration'
    ]

    for key in required_score_keys:
        assert key in result['scores'], f"Missing score key: {key}"
        assert_valid_score(result['scores'][key])
