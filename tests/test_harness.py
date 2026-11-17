"""The harness command the Build Specification shows (python -m evaluation.harness --input ... --output ...) runs the
same unattended run as src.run_evaluation (17 Nov 2026)."""
import src.run_evaluation as R
from evaluation import harness


def test_output_can_be_a_folder_or_a_file():
    assert str(harness.output_file("data/validation_tickets.json", "evaluation/results/")).replace("\\", "/") == \
        "evaluation/results/validation_tickets_results.json"
    assert str(harness.output_file("x/hidden.json", "out/run.json")).replace("\\", "/") == "out/run.json"


def test_it_calls_the_real_run(monkeypatch):
    seen = {}
    monkeypatch.setattr(R, "run_evaluation", lambda i, o, p=None: seen.update(i=i, o=o, p=p) or {"ok": True})
    assert harness.main(["--input", "data/hidden.json", "--output", "results"]) == {"ok": True}
    assert seen["i"] == "data/hidden.json" and seen["o"].replace("\\", "/") == "results/hidden_results.json"
