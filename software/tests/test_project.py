import sys; sys.path.insert(0, 'C:/Users/my/Desktop/daviciresolve/software')
import tempfile, os, json
from core.project import Project, GradeParams, get_recent_files, add_recent_file, RECENT_FILE


def test_grade_params_defaults():
    gp = GradeParams()
    assert gp.lift == [0.0, 0.0, 0.0]
    assert gp.gamma == [1.0, 1.0, 1.0]
    assert gp.gain == [1.0, 1.0, 1.0]
    assert gp.offset == [0.0, 0.0, 0.0]
    assert gp.contrast == 0.0
    assert gp.saturation == 0.0
    assert gp.exposure == 0.0
    assert gp.temp == 0.0
    assert gp.tint == 0.0
    assert gp.lut_path is None


def test_grade_params_custom():
    gp = GradeParams(lift=[0.1, 0.2, 0.3], gamma=[0.9, 1.0, 1.1],
                     gain=[1.1, 1.2, 1.3], saturation=0.5, lut_path="/tmp/cube.cube")
    assert gp.lift == [0.1, 0.2, 0.3]
    assert gp.saturation == 0.5
    assert gp.lut_path == "/tmp/cube.cube"


def test_project_defaults():
    p = Project()
    assert p.version == "1.0"
    assert p.media_path is None
    assert isinstance(p.grade, GradeParams)
    assert p.node_graph is None
    assert p.panel_layout == {}


def test_project_save_load(tmp_path):
    path = str(tmp_path / "test.daviciproj")
    p = Project(media_path="/media/clip.mov", grade=GradeParams(saturation=0.75, exposure=0.5))
    p.save(path)
    assert os.path.exists(path)
    loaded = Project.load(path)
    assert loaded.media_path == "/media/clip.mov"
    assert loaded.grade.saturation == 0.75
    assert loaded.grade.exposure == 0.5
    assert loaded.version == "1.0"


def test_project_save_load_with_node_graph(tmp_path):
    path = str(tmp_path / "test_nodes.daviciproj")
    p = Project(media_path="/media/clip.mov",
                grade=GradeParams(saturation=0.5),
                node_graph={"nodes": [], "edges": []})
    p.save(path)
    loaded = Project.load(path)
    assert loaded.node_graph == {"nodes": [], "edges": []}


def test_project_to_dict_from_dict():
    p = Project(media_path="/media/clip.mov", grade=GradeParams(contrast=0.3, temp=-5.0))
    data = p.to_dict()
    assert data["media_path"] == "/media/clip.mov"
    assert data["grade"]["contrast"] == 0.3
    assert data["grade"]["temp"] == -5.0
    restored = Project.from_dict(data)
    assert restored.media_path == p.media_path
    assert restored.grade.contrast == p.grade.contrast
    assert restored.grade.temp == p.grade.temp


def test_project_from_dict_empty():
    restored = Project.from_dict({})
    assert restored.media_path is None
    assert restored.grade.saturation == 0.0
    assert restored.node_graph is None


def test_recent_files_add_get(monkeypatch, tmp_path):
    fake_recent = str(tmp_path / "recent.json")
    monkeypatch.setattr("core.project.RECENT_FILE", fake_recent)
    add_recent_file(r"C:\videos\a.mp4")
    add_recent_file(r"C:\videos\b.mp4")
    recent = get_recent_files()
    assert recent == [r"C:\videos\b.mp4", r"C:\videos\a.mp4"]


def test_recent_files_dedup(monkeypatch, tmp_path):
    fake_recent = str(tmp_path / "recent.json")
    monkeypatch.setattr("core.project.RECENT_FILE", fake_recent)
    add_recent_file(r"C:\videos\a.mp4")
    add_recent_file(r"C:\videos\a.mp4")
    recent = get_recent_files()
    assert recent == [r"C:\videos\a.mp4"]


def test_recent_files_max_items(monkeypatch, tmp_path):
    fake_recent = str(tmp_path / "recent.json")
    monkeypatch.setattr("core.project.RECENT_FILE", fake_recent)
    for i in range(25):
        add_recent_file(rf"C:\videos\{i}.mp4")
    recent = get_recent_files(max_items=10)
    assert len(recent) == 10
    assert recent[0] == r"C:\videos\24.mp4"


def test_recent_files_empty(monkeypatch, tmp_path):
    fake_recent = str(tmp_path / "nonexistent_recent.json")
    monkeypatch.setattr("core.project.RECENT_FILE", fake_recent)
    assert get_recent_files() == []


def test_recent_files_corrupt(monkeypatch, tmp_path):
    fake_recent = str(tmp_path / "recent.json")
    monkeypatch.setattr("core.project.RECENT_FILE", fake_recent)
    with open(fake_recent, "w") as f:
        f.write("not json")
    assert get_recent_files() == []


def test_save_creates_directory(tmp_path):
    nested = str(tmp_path / "sub" / "deep" / "test.daviciproj")
    p = Project(media_path="/m.clip")
    p.save(nested)
    assert os.path.exists(nested)
    loaded = Project.load(nested)
    assert loaded.media_path == "/m.clip"
