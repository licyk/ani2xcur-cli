from pathlib import Path

import pytest
from PIL import Image

from ani2xcur.config_parse.win import parse_inf_file_content
from ani2xcur.cursor_conversion import convert as cursor_convert
from ani2xcur.cursor_conversion.native_cursor.parsers import parse_blob
from ani2xcur.cursor_conversion.native_cursor.transforms import DEFAULT_XCURSOR_SIZES
from ani2xcur.manager.base import CURSOR_KEYS
from ani2xcur.manager.win_cur_manager import extract_scheme_info_from_inf


MOUSE_POINTER_INF_FILE = Path(__file__).resolve().parent / "Sunaokami-Shiroko-Windows" / "Right-click to install.inf"
HIIRO_INF_FILE = Path(__file__).resolve().parent / "Hiiro-Windows" / "AutoSetup.inf"


def test_win_cursor_to_x11_uses_real_windows_sample(monkeypatch, windows_inf_file: Path, tmp_path: Path):
    calls = []

    def fake_win2xcur_process(input_file: Path, output_path: Path, save_name: str | None = None, **kwargs):
        calls.append((input_file, output_path, save_name, kwargs))
        output_file = output_path / (save_name or input_file.stem)
        output_file.write_bytes(f"x11:{input_file.name}".encode())
        return output_file

    monkeypatch.setattr(cursor_convert, "win2xcur_process", fake_win2xcur_process)

    save_dir = cursor_convert.win_cursor_to_x11(windows_inf_file, tmp_path, {})

    assert save_dir == tmp_path / "DMZ-White"
    assert len(calls) == len(CURSOR_KEYS["win"])
    assert (save_dir / "cursor.theme").read_text(encoding="utf-8") == "[Icon Theme]\nName=DMZ-White\nInherits=default"
    assert "Inherits=DMZ-White" not in (save_dir / "index.theme").read_text(encoding="utf-8")
    assert (save_dir / "index.theme").is_file()
    assert (save_dir / "install_cursor.sh").is_file()

    cursors_dir = save_dir / "cursors"
    for linux_cursor in CURSOR_KEYS["linux"]:
        assert (cursors_dir / linux_cursor).exists()

    for completed_cursor in ["vertical-text", "wayland-cursor", "zoom-out", "zoom-in"]:
        assert (cursors_dir / completed_cursor).exists()

    assert (cursors_dir / "context-menu").exists()
    assert (cursors_dir / "default").exists()


def test_x11_cursor_to_win_uses_real_linux_sample(monkeypatch, linux_theme_file: Path, tmp_path: Path):
    calls: dict[str, Path] = {}

    def fake_x2wincur_process(input_file: Path, output_path: Path, save_name: str | None = None, **kwargs):
        assert save_name is not None
        calls[save_name] = input_file
        output_file = output_path / f"{save_name}.cur"
        output_file.write_bytes(f"win:{input_file.name}".encode())
        return output_file

    monkeypatch.setattr(cursor_convert, "x2wincur_process", fake_x2wincur_process)

    save_dir = cursor_convert.x11_cursor_to_win(linux_theme_file, tmp_path, {})

    assert save_dir == tmp_path / "DMZ-White"
    assert len(calls) == len(CURSOR_KEYS["win"])
    assert calls["Arrow"].name == "left_ptr"
    assert calls["Wait"].name == "wait"
    assert calls["Pin"].name == "center_ptr"

    inf_file = save_dir / "AutoSetup.inf"
    parsed = parse_inf_file_content(inf_file)
    scheme_info = extract_scheme_info_from_inf(inf_file)

    assert parsed["Strings"]["SCHEME_NAME"] == "DMZ-White"
    assert len(parsed["CursorFiles"]) == len(CURSOR_KEYS["win"])
    assert scheme_info["scheme_name"] == "DMZ-White"

    for key in CURSOR_KEYS["win"]:
        assert (save_dir / f"{key}.cur").is_file()
        assert scheme_info["cursor_map"][key]["src_path"] is not None


@pytest.mark.integration
def test_real_win_cursor_to_x11_conversion_smoke(windows_inf_file: Path, tmp_path: Path):
    save_dir = cursor_convert.win_cursor_to_x11(windows_inf_file, tmp_path, {})
    left_ptr = save_dir / "cursors" / "left_ptr"
    cursors_dir = save_dir / "cursors"

    assert left_ptr.is_file()
    assert (cursors_dir / "default").exists()
    assert (cursors_dir / "wayland-cursor").is_file()
    thumbnail = cursors_dir / "thumbnail.png"
    assert thumbnail.is_file()
    assert (save_dir / "cursor.theme").is_file()
    assert parse_blob(left_ptr.read_bytes())[0].images[0].hotspot == (7, 4)

    with Image.open(thumbnail) as preview:
        assert preview.format == "PNG"
        assert preview.mode == "RGBA"
        assert preview.size == (32, 32)

    for cursor_file in cursors_dir.iterdir():
        if cursor_file.name == "thumbnail.png" or cursor_file.is_symlink() or not cursor_file.is_file():
            continue
        frames = parse_blob(cursor_file.read_bytes())
        assert set(DEFAULT_XCURSOR_SIZES).issubset({image.nominal for frame in frames for image in frame.images})


def test_generate_cinnamon_thumbnail_uses_nearest_left_ptr_size(linux_cursor_dir: Path, tmp_path: Path):
    cursors_dir = tmp_path / "cursors"
    cursors_dir.mkdir()
    left_ptr = cursors_dir / "left_ptr"
    left_ptr.write_bytes((linux_cursor_dir / "cursors" / "left_ptr").read_bytes())

    thumbnail = cursor_convert._generate_cinnamon_cursor_thumbnail(cursors_dir, target_size=30)

    assert thumbnail == cursors_dir / "thumbnail.png"
    source_image = min(
        parse_blob(left_ptr.read_bytes())[0].images,
        key=lambda image: (abs(image.nominal - 30), image.nominal),
    ).image.convert("RGBA")
    with Image.open(thumbnail) as preview:
        assert preview.format == "PNG"
        assert preview.mode == "RGBA"
        assert preview.size == source_image.size
        assert preview.tobytes() == source_image.tobytes()


@pytest.mark.integration
def test_real_mouse_pointer_win_cursor_to_x11_conversion_smoke(tmp_path: Path):
    save_dir = cursor_convert.win_cursor_to_x11(MOUSE_POINTER_INF_FILE, tmp_path, {})
    left_ptr = save_dir / "cursors" / "left_ptr"

    assert save_dir == tmp_path / "Sunaōkami Shiroko"
    assert left_ptr.is_file()
    frames = parse_blob(left_ptr.read_bytes())
    assert len(frames) == 16
    assert frames[0].images[0].hotspot == (1, 1)
    assert sorted({image.nominal for frame in frames for image in frame.images}) == list(DEFAULT_XCURSOR_SIZES)


@pytest.mark.integration
def test_real_hiiro_windows_round_trip_preserves_large_cursor_sizes(tmp_path: Path):
    linux_dir = cursor_convert.win_cursor_to_x11(HIIRO_INF_FILE, tmp_path / "linux", {})
    linux_left_ptr = parse_blob((linux_dir / "cursors" / "left_ptr").read_bytes())

    assert (256, 256) in {image.image.size for frame in linux_left_ptr for image in frame.images}

    win_dir = cursor_convert.x11_cursor_to_win(linux_dir / "cursor.theme", tmp_path / "win", {})
    arrow_frames = parse_blob((win_dir / "Arrow.ani").read_bytes())
    crosshair_frames = parse_blob((win_dir / "Crosshair.cur").read_bytes())

    assert sorted({image.image.size for frame in arrow_frames for image in frame.images}) == [(256, 256)]
    assert sorted({image.image.size for frame in crosshair_frames for image in frame.images}) == [(96, 96), (128, 128)]


@pytest.mark.integration
def test_real_x11_cursor_to_win_conversion_smoke(linux_theme_file: Path, tmp_path: Path):
    save_dir = cursor_convert.x11_cursor_to_win(linux_theme_file, tmp_path, {})
    arrow_file = save_dir / "Arrow.cur"

    assert (save_dir / "AutoSetup.inf").is_file()
    assert arrow_file.is_file()
    assert parse_blob(arrow_file.read_bytes())[0].images[0].hotspot == (7, 4)
