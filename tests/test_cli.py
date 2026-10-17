from keel.cli import main
from keel.llm import OfflineLLM


def test_cli_full_flow(tmp_path):
    inputs = iter(["Avi"] + [""] * 11 + ["I need to ask for a raise", "/commit list three tasks", "/profile", "/quit"])
    out = []
    rc = main(["--offline", "--profile", str(tmp_path / "p.json")], ask=lambda q: next(inputs), say=out.append, llm=OfflineLLM())
    text = "\n".join(map(str, out))
    assert rc == 0 and "unofficial" in text and "[offline:ROLEPLAY]" in text and "Recorded" in text
    assert (tmp_path / "life_plan.md").exists()


def test_cli_safety_shows_resources(tmp_path):
    inputs = iter(["x"] + [""] * 11 + ["I want to end my life", "/quit"])
    out = []
    main(["--offline", "--profile", str(tmp_path / "p.json")], ask=lambda q: next(inputs), say=out.append, llm=OfflineLLM())
    assert any("988" in str(o) for o in out)


def test_cli_tts_flag(tmp_path):
    inputs = iter(["x"] + [""] * 11 + ["hello", "/quit"])
    out = []
    main(["--offline", "--tts", "--profile", str(tmp_path / "p.json")], ask=lambda q: next(inputs), say=out.append, llm=OfflineLLM())
    assert any(str(o).startswith("<speak>") for o in out)
