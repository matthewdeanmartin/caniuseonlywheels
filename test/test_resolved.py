"""Offline regressions for resolved inputs and exact-release wheel checks."""

import sys
from unittest.mock import Mock

from packaging.tags import Tag
import pytest
import requests

from caniuseonlywheels import pypi, resolved
from caniuseonlywheels import __main__ as cli


def release(name, version="1", requirements=None, filenames=None, **info):
    if filenames is None:
        filenames = ["{}-{}-py3-none-any.whl".format(name, version)]
    return {
        "info": dict(name=name, version=version, requires_dist=requirements, **info),
        "urls": [
            {"filename": filename, "yanked": False, "requires_python": None}
            for filename in filenames
        ],
    }


@pytest.fixture
def index(monkeypatch):
    releases = {}
    calls = []

    def get(url, timeout):
        assert timeout == (5, 30)
        calls.append(url)
        name, version = url.rsplit("/", 3)[1:3]
        response = Mock()
        if (name, version) not in releases:
            response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        else:
            response.json.return_value = releases[name, version]
        return response

    monkeypatch.setattr(pypi.requests, "get", get)
    monkeypatch.setattr("packaging.tags.sys_tags", lambda: [Tag("py3", "none", "any")])
    return releases, calls


def lock(tmp_path, text):
    path = tmp_path / "requirements.txt"
    path.write_text(text, encoding="utf-8")
    return resolved.from_requirements([path])


def test_wheeled_parent_does_not_hide_source_only_child(index, tmp_path):
    releases, calls = index
    releases["parent", "1"] = release("parent", requirements=["docopt==0.6.2"])
    releases["docopt", "0.6.2"] = release(
        "docopt", "0.6.2", filenames=["docopt-0.6.2.tar.gz"]
    )
    report = resolved.audit(lock(tmp_path, "parent==1\ndocopt==0.6.2\n"))
    assert report.blockers.keys() == {"docopt==0.6.2"}
    assert not report.unknown
    assert not report.passed
    assert len(calls) == 2  # No substitution override or unversioned metadata lookup.


def test_exact_version_never_uses_other_release_wheels(index):
    releases, calls = index
    releases["foo", "1"] = release("foo", filenames=["foo-1.tar.gz"])
    releases["foo", "2"] = release("foo", "2")
    releases["foo", "1"]["releases"] = {"2": releases["foo", "2"]["urls"]}
    assert not pypi.supports_wheels("foo", "1")
    assert pypi.supports_wheels("foo", "2")
    assert all(url.endswith(("/foo/1/json", "/foo/2/json")) for url in calls)
    with pytest.raises(pypi.MetadataError, match="exact version"):
        pypi.supports_wheels("foo")


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("foo-1-py3-none-any.whl", True),
        ("foo-1-py2.py3-none-any.whl", True),
        ("foo-1-cp310-cp310-win_amd64.whl", False),
        ("foo-1-cp311-cp311-manylinux_2_17_x86_64.whl", False),
    ],
)
def test_tags(index, filename, expected):
    index[0]["foo", "1"] = release("foo", filenames=[filename])
    assert pypi.supports_wheels("foo", "1") is expected


@pytest.mark.parametrize("change", ["yanked", "requires-python"])
def test_unusable_wheels(index, change):
    data = release("foo")
    if change == "yanked":
        data["urls"][0]["yanked"] = True
    else:
        data["urls"][0]["requires_python"] = ">=99"
    index[0]["foo", "1"] = data
    assert not pypi.supports_wheels("foo", "1")


@pytest.mark.parametrize(
    "failure",
    [requests.Timeout("timed out"), requests.HTTPError("503"), ValueError("bad JSON")],
)
def test_transport_failure_is_unknown(monkeypatch, failure):
    monkeypatch.setattr(pypi.requests, "get", Mock(side_effect=failure))
    report = resolved.audit({"foo": resolved.Pin("foo", "1")})
    assert not report.passed
    assert report.unknown.keys() == {"foo==1"}


def test_missing_release_is_unknown(index):
    report = resolved.audit({"missing": resolved.Pin("missing", "1")})
    assert report.unknown
    assert not report.passed


@pytest.mark.parametrize(
    "text",
    [
        "foo>=1",
        "foo",
        "foo==1.*",
        "foo @ https://example.com/foo.whl",
        "-r other.txt",
        "--index-url https://example.com",
        "foo==1 --hash=sha256:abc",
        "foo==1\nfoo==2",
        'foo==1\nbar==1; extra == "optional"',
        'foo==1\nbar==1; "optional" == extra',
        'foo==1\nbar==1; extra >= "optional"',
    ],
)
def test_unsupported_or_unresolved_lock_fails(tmp_path, text):
    with pytest.raises(resolved.InputError):
        lock(tmp_path, text)


def test_pin_markers_select_running_target(tmp_path):
    pins = lock(
        tmp_path,
        '# exported lock\nfoo==1; python_version >= "3"\nfoo==2; python_version < "3"\n',
    )
    assert list(pins) == ["foo"]
    assert pins["foo"].version == "1"


def test_marker_literal_extra_is_not_a_variable(tmp_path):
    pins = lock(tmp_path, 'foo==1; os_name != "extra"')
    assert list(pins) == ["foo"]


@pytest.mark.parametrize(
    "dependency,pins",
    [
        ("child>=2", "child==1"),
        ("child", ""),
        ("child @ https://example.com/c.whl", "child==1"),
    ],
)
def test_incomplete_inconsistent_or_direct_dependency_is_unknown(
    index, tmp_path, dependency, pins
):
    index[0]["parent", "1"] = release("parent", requirements=[dependency])
    index[0]["child", "1"] = release("child")
    report = resolved.audit(lock(tmp_path, "parent==1\n" + pins))
    assert report.unknown
    assert not report.passed


def test_extras_propagate_through_existing_pins_and_cycles(index, tmp_path):
    index[0]["parent", "1"] = release(
        "parent", requirements=['child[feature]; extra == "test"']
    )
    index[0]["child", "1"] = release(
        "child",
        requirements=[
            "parent[test]",
            'source; extra == "feature"',
            'absent; python_version < "3"',
        ],
    )
    index[0]["source", "1"] = release("source", filenames=["source-1.tar.gz"])
    report = resolved.audit(lock(tmp_path, "parent[test]==1\nchild==1\nsource==1\n"))
    assert report.blockers.keys() == {"source==1"}
    assert not report.unknown
    report = resolved.audit(lock(tmp_path, "parent[test]==1\nchild==1\n"))
    assert any("missing source" in reason for reason in report.unknown.values())


def test_inactive_extra_does_not_add_dependency(index, tmp_path):
    index[0]["parent", "1"] = release(
        "parent", requirements=['absent; extra == "optional"']
    )
    assert resolved.audit(lock(tmp_path, "parent==1")).passed


@pytest.mark.parametrize(
    "data",
    [
        None,
        {},
        {"info": {}},
        release("different"),
        {"info": {"name": "foo", "version": "1"}, "urls": []},
    ],
)
def test_malformed_release_is_unknown(index, data):
    index[0]["foo", "1"] = data
    assert resolved.audit({"foo": resolved.Pin("foo", "1")}).unknown


@pytest.mark.parametrize("change", ["filename", "yanked", "version", "requirements"])
def test_malformed_wheel_or_dependencies_is_unknown(index, change):
    data = release("foo")
    if change == "filename":
        data["urls"][0]["filename"] = "not-a-wheel.whl"
    elif change == "yanked":
        del data["urls"][0]["yanked"]
    elif change == "version":
        data["urls"][0]["filename"] = "foo-2-py3-none-any.whl"
    else:
        data["info"]["requires_dist"] = "child"
    index[0]["foo", "1"] = data
    assert resolved.audit({"foo": resolved.Pin("foo", "1")}).unknown


@pytest.fixture
def venv(tmp_path, monkeypatch):
    root = tmp_path / "venv"
    site = root / "site-packages"
    site.mkdir(parents=True)
    (root / "pyvenv.cfg").write_text(
        "include-system-site-packages = false\n", encoding="utf-8"
    )
    monkeypatch.setattr(sys, "prefix", str(root))
    monkeypatch.setattr(resolved.sysconfig, "get_path", lambda key: str(site))

    def distribution(name, requires=()):
        directory = site / (name + "-1.dist-info")
        directory.mkdir()
        text = "Metadata-Version: 2.1\nName: {}\nVersion: 1\n".format(name)
        text += "".join("Requires-Dist: {}\n".format(req) for req in requires)
        (directory / "METADATA").write_text(text, encoding="utf-8")
        return directory

    return root, distribution


def test_venv_checks_transitive_installed_metadata_without_importing(index, venv):
    root, distribution = venv
    distribution("parent", ["source==1"])
    distribution("source")
    # Index dependency metadata differs: use the actual installed metadata.
    index[0]["parent", "1"] = release("parent")
    index[0]["source", "1"] = release("source", filenames=["source-1.tar.gz"])
    report = resolved.audit(resolved.from_venv(root))
    assert report.blockers.keys() == {"source==1"}
    assert not report.unknown


def test_venv_missing_required_distribution_is_unknown(index, venv):
    root, distribution = venv
    distribution("parent", ["source"])
    index[0]["parent", "1"] = release("parent")
    assert resolved.audit(resolved.from_venv(root)).unknown


def test_venv_cannot_silently_use_other_interpreter(tmp_path):
    with pytest.raises(resolved.InputError, match="running interpreter"):
        resolved.from_venv(tmp_path)


def test_venv_rejects_direct_url_install(venv):
    root, distribution = venv
    path = distribution("local")
    (path / "direct_url.json").write_text("{}", encoding="utf-8")
    with pytest.raises(resolved.InputError, match="direct-URL"):
        resolved.from_venv(root)


def test_venv_rejects_shared_site_packages(venv):
    root, _ = venv
    (root / "pyvenv.cfg").write_text(
        "include-system-site-packages = true\n", encoding="utf-8"
    )
    with pytest.raises(resolved.InputError, match="system site-packages"):
        resolved.from_venv(root)


@pytest.mark.parametrize(
    "args", [[], ["--projects", "foo"], ["--metadata", "METADATA"]]
)
def test_cli_rejects_unresolved_input(args):
    with pytest.raises(SystemExit) as exc:
        cli.main(args)
    assert exc.value.code == 2


@pytest.mark.parametrize(
    "kind,exit_code", [("wheel", 0), ("sdist", 3), ("missing", 2), ("incomplete", 2)]
)
def test_cli_exit_codes_and_no_false_success(index, tmp_path, capsys, kind, exit_code):
    path = tmp_path / "lock.txt"
    path.write_text("foo==1", encoding="utf-8")
    if kind != "missing":
        index[0]["foo", "1"] = release(
            "foo",
            requirements=["child"] if kind == "incomplete" else None,
            filenames=["foo-1.tar.gz"] if kind == "sdist" else None,
        )
    if exit_code:
        with pytest.raises(SystemExit) as exc:
            cli.main(["-r", str(path)])
        assert exc.value.code == exit_code
        assert "All recorded distributions" not in capsys.readouterr().out
    else:
        cli.main(["-r", str(path)])
        assert "All recorded distributions" in capsys.readouterr().out


def test_cli_invalid_lock_is_unknown(tmp_path, capsys):
    path = tmp_path / "lock.txt"
    path.write_text("foo", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        cli.main(["-r", str(path)])
    assert exc.value.code == 2
    assert "UNKNOWN" in capsys.readouterr().err
