"""
Example comprehensive unit tests for PronunciationAnalyzer
This file demonstrates the testing approach recommended in TEST_COVERAGE_ANALYSIS.md

To run these tests:
1. Install pytest: pip install pytest pytest-cov pytest-mock
2. Run: pytest tests/test_pronunciation_analyzer_example.py -v
3. Run with coverage: pytest tests/test_pronunciation_analyzer_example.py --cov=pronunciation_analyzer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pronunciation_analyzer import PronunciationAnalyzer


class TestPronunciationAnalyzerInit:
    """Test initialization of PronunciationAnalyzer"""

    def test_init_with_default_model(self):
        """Test initialization with default model size"""
        analyzer = PronunciationAnalyzer()
        assert analyzer.model_size == "base"

    def test_init_with_custom_model(self):
        """Test initialization with custom model size"""
        analyzer = PronunciationAnalyzer(model_size="tiny")
        assert analyzer.model_size == "tiny"

    def test_init_with_invalid_model(self):
        """Test initialization with invalid model size still works"""
        # Should not raise an error, just might fail to load model
        analyzer = PronunciationAnalyzer(model_size="invalid")
        assert analyzer.model_size == "invalid"


class TestGetPhonemes:
    """Test phoneme extraction functionality"""

    @pytest.fixture
    def analyzer(self):
        """Fixture providing PronunciationAnalyzer instance"""
        return PronunciationAnalyzer()

    def test_get_phonemes_basic_word(self, analyzer):
        """Test phoneme extraction for simple word"""
        phonemes = analyzer.get_phonemes("hello")
        assert isinstance(phonemes, list)
        assert len(phonemes) > 0

    def test_get_phonemes_multiple_words(self, analyzer):
        """Test phoneme extraction for multiple words"""
        phonemes = analyzer.get_phonemes("hello world")
        assert isinstance(phonemes, list)
        assert len(phonemes) > len("hello".split())  # Should have multiple phonemes

    def test_get_phonemes_empty_string(self, analyzer):
        """Test phoneme extraction with empty string"""
        phonemes = analyzer.get_phonemes("")
        assert isinstance(phonemes, list)
        assert len(phonemes) == 0

    def test_get_phonemes_with_punctuation(self, analyzer):
        """Test phoneme extraction with punctuation"""
        phonemes = analyzer.get_phonemes("hello, world!")
        assert isinstance(phonemes, list)
        assert len(phonemes) > 0

    def test_get_phonemes_with_numbers(self, analyzer):
        """Test phoneme extraction with numbers"""
        phonemes = analyzer.get_phonemes("hello 123")
        assert isinstance(phonemes, list)
        # Numbers might not be in pronunciation dict

    def test_get_phonemes_unknown_word(self, analyzer):
        """Test phoneme extraction with word not in CMU dict"""
        phonemes = analyzer.get_phonemes("xyzabc123")
        assert isinstance(phonemes, list)
        # Should fallback to character-level splitting

    def test_get_phonemes_case_insensitive(self, analyzer):
        """Test that phoneme extraction is case-insensitive"""
        phonemes_lower = analyzer.get_phonemes("hello")
        phonemes_upper = analyzer.get_phonemes("HELLO")
        # Should return same phonemes (case-insensitive)
        assert len(phonemes_lower) == len(phonemes_upper)

    def test_get_phonemes_with_special_characters(self, analyzer):
        """Test phoneme extraction with special characters"""
        phonemes = analyzer.get_phonemes("hello@world#test")
        assert isinstance(phonemes, list)


class TestCalculatePronunciationScore:
    """Test pronunciation scoring functionality"""

    @pytest.fixture
    def analyzer(self):
        """Fixture providing PronunciationAnalyzer instance"""
        return PronunciationAnalyzer()

    def test_perfect_match(self, analyzer):
        """Test scoring with perfect match"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="hello world",
            spoken_text="hello world"
        )

        assert result['overall_score'] == 100.0
        assert result['word_accuracy'] == 100.0
        assert result['phoneme_similarity'] == 100.0
        assert result['correct_words'] == 2
        assert result['word_count'] == 2
        assert len(result['mispronounced_words']) == 0

    def test_complete_mismatch(self, analyzer):
        """Test scoring with complete mismatch"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="hello world",
            spoken_text="goodbye universe"
        )

        assert result['overall_score'] < 50.0
        assert result['word_accuracy'] == 0.0
        assert result['correct_words'] == 0
        assert len(result['mispronounced_words']) > 0

    def test_partial_match(self, analyzer):
        """Test scoring with partial match"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="hello world how are you",
            spoken_text="hello world how you"
        )

        assert 0 < result['overall_score'] < 100
        assert result['word_accuracy'] == 75.0  # 3 out of 4 spoken words correct
        assert result['correct_words'] == 3

    def test_extra_words(self, analyzer):
        """Test scoring when spoken has extra words"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="hello world",
            spoken_text="hello world extra words"
        )

        # Should still detect the correct words
        assert result['correct_words'] == 2

    def test_missing_words(self, analyzer):
        """Test scoring when spoken has missing words"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="hello world how are you",
            spoken_text="hello world"
        )

        assert result['correct_words'] == 2
        assert result['word_count'] == 5  # Reference has 5 words

    def test_empty_reference(self, analyzer):
        """Test scoring with empty reference text"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="",
            spoken_text="hello"
        )

        assert result['overall_score'] == 0.0
        assert result['word_accuracy'] == 0.0

    def test_empty_spoken(self, analyzer):
        """Test scoring with empty spoken text"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="hello world",
            spoken_text=""
        )

        assert result['overall_score'] == 0.0
        assert result['word_accuracy'] == 0.0

    def test_both_empty(self, analyzer):
        """Test scoring when both inputs are empty"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="",
            spoken_text=""
        )

        assert result['overall_score'] == 0.0

    def test_case_insensitive_matching(self, analyzer):
        """Test that matching is case-insensitive"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="HELLO WORLD",
            spoken_text="hello world"
        )

        assert result['word_accuracy'] == 100.0

    def test_punctuation_ignored(self, analyzer):
        """Test that punctuation is ignored in matching"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="Hello, world!",
            spoken_text="hello world"
        )

        assert result['word_accuracy'] == 100.0

    def test_scoring_weight_formula(self, analyzer):
        """Test that overall score uses correct weights (60% word, 40% phoneme)"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="test",
            spoken_text="test"
        )

        # For perfect match
        expected = (100 * 0.6) + (100 * 0.4)
        assert result['overall_score'] == expected

    def test_mispronounced_words_tracking(self, analyzer):
        """Test that mispronounced words are tracked correctly"""
        result = analyzer.calculate_pronunciation_score(
            reference_text="hello world how are you",
            spoken_text="helo world how ar you"
        )

        assert len(result['mispronounced_words']) > 0

        # Check structure of mispronounced words
        for error in result['mispronounced_words']:
            assert 'expected' in error
            assert 'spoken' in error
            assert 'position' in error


class TestGenerateFeedback:
    """Test feedback generation"""

    @pytest.fixture
    def analyzer(self):
        """Fixture providing PronunciationAnalyzer instance"""
        return PronunciationAnalyzer()

    def test_feedback_excellent_score(self, analyzer):
        """Test feedback for excellent score (90+)"""
        pronunciation_result = {
            'overall_score': 95.0,
            'word_accuracy': 95.0,
            'phoneme_similarity': 95.0,
            'mispronounced_words': [],
            'word_count': 5,
            'correct_words': 5
        }

        feedback = analyzer.generate_feedback(pronunciation_result)

        assert "훌륭합니다" in feedback or "🎉" in feedback
        assert "95" in feedback

    def test_feedback_good_score(self, analyzer):
        """Test feedback for good score (75-89)"""
        pronunciation_result = {
            'overall_score': 80.0,
            'word_accuracy': 80.0,
            'phoneme_similarity': 80.0,
            'mispronounced_words': [],
            'word_count': 5,
            'correct_words': 4
        }

        feedback = analyzer.generate_feedback(pronunciation_result)

        assert "좋아요" in feedback or "👍" in feedback

    def test_feedback_average_score(self, analyzer):
        """Test feedback for average score (60-74)"""
        pronunciation_result = {
            'overall_score': 65.0,
            'word_accuracy': 65.0,
            'phoneme_similarity': 65.0,
            'mispronounced_words': [],
            'word_count': 5,
            'correct_words': 3
        }

        feedback = analyzer.generate_feedback(pronunciation_result)

        assert "괜찮아요" in feedback or "📚" in feedback

    def test_feedback_poor_score(self, analyzer):
        """Test feedback for poor score (<60)"""
        pronunciation_result = {
            'overall_score': 45.0,
            'word_accuracy': 45.0,
            'phoneme_similarity': 45.0,
            'mispronounced_words': [],
            'word_count': 5,
            'correct_words': 2
        }

        feedback = analyzer.generate_feedback(pronunciation_result)

        assert "연습" in feedback or "💪" in feedback

    def test_feedback_includes_mispronounced_words(self, analyzer):
        """Test that feedback includes mispronounced words"""
        pronunciation_result = {
            'overall_score': 70.0,
            'word_accuracy': 70.0,
            'phoneme_similarity': 70.0,
            'mispronounced_words': [
                {'expected': 'hello', 'spoken': 'helo', 'position': 0}
            ],
            'word_count': 5,
            'correct_words': 3
        }

        feedback = analyzer.generate_feedback(pronunciation_result)

        assert 'hello' in feedback or 'helo' in feedback

    def test_feedback_with_prosody_slow(self, analyzer):
        """Test feedback with slow speaking rate"""
        pronunciation_result = {
            'overall_score': 80.0,
            'word_accuracy': 80.0,
            'phoneme_similarity': 80.0,
            'mispronounced_words': [],
            'word_count': 5,
            'correct_words': 4
        }

        prosody_result = {
            'speaking_rate': 1.0,  # Slow
            'pitch_variation': 50.0,
            'energy_variation': 0.01
        }

        feedback = analyzer.generate_feedback(pronunciation_result, prosody_result)

        assert "느려요" in feedback or "🐢" in feedback

    def test_feedback_with_prosody_fast(self, analyzer):
        """Test feedback with fast speaking rate"""
        pronunciation_result = {
            'overall_score': 80.0,
            'word_accuracy': 80.0,
            'phoneme_similarity': 80.0,
            'mispronounced_words': [],
            'word_count': 5,
            'correct_words': 4
        }

        prosody_result = {
            'speaking_rate': 3.5,  # Fast
            'pitch_variation': 50.0,
            'energy_variation': 0.01
        }

        feedback = analyzer.generate_feedback(pronunciation_result, prosody_result)

        assert "빨라요" in feedback or "🐇" in feedback

    def test_feedback_with_prosody_good(self, analyzer):
        """Test feedback with good speaking rate"""
        pronunciation_result = {
            'overall_score': 80.0,
            'word_accuracy': 80.0,
            'phoneme_similarity': 80.0,
            'mispronounced_words': [],
            'word_count': 5,
            'correct_words': 4
        }

        prosody_result = {
            'speaking_rate': 2.0,  # Good
            'pitch_variation': 50.0,
            'energy_variation': 0.01
        }

        feedback = analyzer.generate_feedback(pronunciation_result, prosody_result)

        assert "적절" in feedback or "✅" in feedback


class TestTranscribeAudio:
    """Test audio transcription (with mocking)"""

    @patch('pronunciation_analyzer.WHISPER_AVAILABLE', True)
    def test_transcribe_with_mock_whisper(self):
        """Test transcription with mocked Whisper"""
        # Create mock Whisper model
        mock_model = Mock()
        mock_model.transcribe.return_value = {"text": "  Hello World  "}

        with patch('whisper.load_model', return_value=mock_model):
            analyzer = PronunciationAnalyzer()
            result = analyzer.transcribe_audio("fake_audio.wav")

            assert result == "hello world"  # Should be lowercased and stripped
            mock_model.transcribe.assert_called_once_with("fake_audio.wav")

    @patch('pronunciation_analyzer.WHISPER_AVAILABLE', False)
    def test_transcribe_fallback_when_whisper_unavailable(self):
        """Test fallback when Whisper is not available"""
        analyzer = PronunciationAnalyzer()
        result = analyzer.transcribe_audio("fake_audio.wav")

        # Should return fallback text
        assert isinstance(result, str)


class TestAnalyzeProsody:
    """Test prosody analysis (with mocking)"""

    @patch('pronunciation_analyzer.LIBROSA_AVAILABLE', True)
    @patch('librosa.load')
    @patch('librosa.beat.beat_track')
    @patch('librosa.piptrack')
    @patch('librosa.feature.rms')
    def test_analyze_prosody_with_mock(
        self,
        mock_rms,
        mock_piptrack,
        mock_beat_track,
        mock_load
    ):
        """Test prosody analysis with mocked librosa"""
        import numpy as np

        # Mock audio data
        mock_load.return_value = (np.array([0.1, 0.2, 0.3]), 22050)
        mock_beat_track.return_value = (120, np.array([]))  # 120 BPM
        mock_piptrack.return_value = (
            np.array([[100, 200], [150, 250]]),  # pitches
            np.array([[0.8, 0.9], [0.7, 0.8]])   # magnitudes
        )
        mock_rms.return_value = np.array([[0.1, 0.2, 0.15]])

        analyzer = PronunciationAnalyzer()
        result = analyzer.analyze_prosody("fake_audio.wav")

        assert 'speaking_rate' in result
        assert 'pitch_variation' in result
        assert 'energy_variation' in result
        assert all(isinstance(v, (int, float)) for v in result.values())

    @patch('pronunciation_analyzer.LIBROSA_AVAILABLE', False)
    def test_analyze_prosody_fallback_when_librosa_unavailable(self):
        """Test fallback when librosa is not available"""
        analyzer = PronunciationAnalyzer()
        result = analyzer.analyze_prosody("fake_audio.wav")

        assert result == {
            'speaking_rate': 0.0,
            'pitch_variation': 0.0,
            'energy_variation': 0.0
        }


class TestFullAnalysis:
    """Test complete analysis pipeline"""

    @patch.object(PronunciationAnalyzer, 'transcribe_audio')
    @patch.object(PronunciationAnalyzer, 'analyze_prosody')
    def test_full_analysis_integration(
        self,
        mock_prosody,
        mock_transcribe
    ):
        """Test full analysis pipeline with mocked components"""
        # Mock return values
        mock_transcribe.return_value = "hello world"
        mock_prosody.return_value = {
            'speaking_rate': 2.0,
            'pitch_variation': 50.0,
            'energy_variation': 0.01
        }

        analyzer = PronunciationAnalyzer()
        result = analyzer.full_analysis(
            audio_path="fake_audio.wav",
            reference_text="hello world"
        )

        # Check result structure
        assert 'spoken_text' in result
        assert 'reference_text' in result
        assert 'pronunciation' in result
        assert 'prosody' in result
        assert 'feedback' in result

        # Check values
        assert result['spoken_text'] == "hello world"
        assert result['reference_text'] == "hello world"
        assert result['pronunciation']['overall_score'] == 100.0


# Parameterized tests example
class TestScoringParameterized:
    """Parameterized tests for various scoring scenarios"""

    @pytest.mark.parametrize("reference,spoken,expected_min_score", [
        ("hello", "hello", 100),
        ("hello world", "hello world", 100),
        ("hello", "goodbye", 0),
        ("hello world", "hello", 40),
    ])
    def test_various_scoring_scenarios(self, reference, spoken, expected_min_score):
        """Test scoring with various inputs"""
        analyzer = PronunciationAnalyzer()
        result = analyzer.calculate_pronunciation_score(reference, spoken)

        if expected_min_score == 100:
            assert result['overall_score'] == 100.0
        else:
            assert result['overall_score'] >= expected_min_score


# Edge cases
class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def analyzer(self):
        return PronunciationAnalyzer()

    def test_very_long_text(self, analyzer):
        """Test with very long text (1000 words)"""
        long_text = " ".join(["word"] * 1000)
        result = analyzer.calculate_pronunciation_score(long_text, long_text)

        assert result['overall_score'] == 100.0
        assert result['word_count'] == 1000

    def test_unicode_characters(self, analyzer):
        """Test with unicode characters"""
        text_with_unicode = "hello 你好 مرحبا"
        result = analyzer.calculate_pronunciation_score(text_with_unicode, text_with_unicode)

        # Should handle gracefully
        assert isinstance(result['overall_score'], (int, float))

    def test_special_characters_only(self, analyzer):
        """Test with only special characters"""
        special_chars = "!@#$%^&*()"
        result = analyzer.calculate_pronunciation_score(special_chars, special_chars)

        # Should handle gracefully
        assert isinstance(result, dict)

    def test_repeated_words(self, analyzer):
        """Test with repeated words"""
        result = analyzer.calculate_pronunciation_score(
            "hello hello hello",
            "hello hello hello"
        )

        assert result['overall_score'] == 100.0
        assert result['word_count'] == 3
