"""Tests for text utilities."""

from lime_survey_analyzer.viz.utils.text import clean_html_tags, wrap_text_labels, clean_filename


def test_clean_html_tags():
    """Test HTML tag removal."""
    assert clean_html_tags("<p>Hello world</p>") == "Hello world"
    assert clean_html_tags("<p dir='ltr'>Test</p>") == "Test"
    assert clean_html_tags("No tags here") == "No tags here"
    assert clean_html_tags("") == ""
    assert clean_html_tags("<b>Bold</b> and <i>italic</i>") == "Bold and italic"


def test_clean_html_tags_non_string():
    """Test HTML tag removal with non-string input."""
    assert clean_html_tags(123) == "123"
    assert clean_html_tags(None) == "None"


def test_wrap_text_labels_short():
    """Test text wrapping with short labels."""
    labels = ["Short", "Also short"]
    result = wrap_text_labels(labels, max_length=20)
    assert result == ["Short", "Also short"]


def test_wrap_text_labels_long():
    """Test text wrapping with long labels."""
    labels = ["This is a very long label that should be wrapped"]
    result = wrap_text_labels(labels, max_length=20)
    assert "<br>" in result[0]
    assert len(result) == 1


def test_wrap_text_labels_with_html():
    """Test text wrapping removes HTML tags first."""
    labels = ["<p>This is a very long label with HTML tags</p>"]
    result = wrap_text_labels(labels, max_length=20)
    assert "<p>" not in result[0]
    assert "</p>" not in result[0]
    assert "<br>" in result[0]


def test_clean_filename():
    """Test filename cleaning."""
    assert clean_filename("Simple filename") == "Simple_filename"
    assert clean_filename("<p>HTML filename</p>") == "HTML_filename"
    assert clean_filename("File with special chars!@#") == "File_with_special_chars"
    assert clean_filename("Português ção") == "Português_ção"


def test_clean_filename_max_length():
    """Test filename length limiting."""
    long_name = "A" * 200
    result = clean_filename(long_name, max_length=50)
    assert len(result) == 50 