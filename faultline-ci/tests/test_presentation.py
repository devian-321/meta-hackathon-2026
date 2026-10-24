from faultline_ci.presentation import render_html


def test_html_escapes_untrusted_report_text() -> None:
    result = render_html({"source": "gitlab_api"}, '<script>alert("bad")</script>')
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
    assert "Duo provenance and human approval need separate review" in result


def test_missing_checks_do_not_display_pass() -> None:
    result = render_html({}, "No observations")
    assert "FAIL / INCOMPLETE" in result
    assert "FAILED / NOT CHECKED" in result
