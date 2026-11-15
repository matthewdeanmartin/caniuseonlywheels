import pytest

import caniuseonlywheels as ciu
from caniuseonlywheels import resolved


def test_unresolved_public_api_cannot_pass():
    for args in ({}, {"projects": ["pyftpdlib"]}, {"metadata": ["Name: parent"]}):
        with pytest.raises(resolved.InputError):
            ciu.check(**args)


def test_public_api_passes_resolved_input(tmp_path, monkeypatch):
    path = tmp_path / "lock.txt"
    path.write_text("foo==1\n", encoding="utf-8")
    monkeypatch.setattr(
        resolved, "audit", lambda pins, index: resolved.Report(checked=1)
    )
    assert ciu.check(requirements_paths=[path])
    monkeypatch.setattr(
        resolved,
        "audit",
        lambda pins, index: resolved.Report(checked=1, unknown={"foo": "404"}),
    )
    assert not ciu.check(requirements_paths=[path])
