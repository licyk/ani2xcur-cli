# Pillow Cursor Converter Refactor

## Goal
- Rewrite the cursor conversion core inside `ani2xcur` with Pillow.
- Preserve both conversion directions: Windows `.cur/.ani` to Linux Xcursor, and Linux Xcursor to Windows `.cur/.ani`.
- Remove the third-party `win2xcur` conversion dependency from runtime code and packaging metadata.
- Keep Linux output as a standard Xcursor theme that works for X11 and Wayland/XWayland loaders.
- Keep conversion self-contained around Pillow without external image-processing tools.

## Done
- Created `dev` branch for the refactor.
- Chose the scope: dual-direction rewrite, Xcursor theme compatibility, no Hyprcursor output.
- Decided that `todo.md` is tracked and the external reference `win2xcur/` directory is ignored.
- Added the first native Pillow converter package with shared models, CUR/ANI/Xcursor parsers, Xcursor/CUR/ANI writers, scale, shadow, and public conversion entry points.
- Switched conversion imports to the native converter, removed the old external converter wrapper, and removed the package dependency on `win2xcur`.
- Added unit coverage for CUR PNG/DIB parsing, ANI parsing, Xcursor roundtrip, Windows writer roundtrip, scale, and shadow opacity.
- Updated real-sample conversion tests to use the native parser when reading back generated cursor files.
- Updated README and update/system options so conversion is described as Pillow-based and no longer source-updates `win2xcur`.
- Ran full validation: pytest, ruff, and ty all pass.
- Added a libwayland-cursor verifier tool under `tests/tools/` and a headless Weston integration test for generated Xcursor themes.
- Found that generated themes inherited themselves (`Inherits=<theme>`), which can make `wl_cursor_theme_load()` hang; switched generated fallback inheritance to a non-recursive theme.
- Added a dedicated GitHub Actions Wayland loader job that installs Weston/libwayland and runs the `wayland` marker tests.
- Added file-level Xcursor size normalization so Windows -> Linux conversion writes standard nominal sizes by default and desktop environments can expose cursor size choices.

## Todo
- Parser:
  - Done.
- Writer:
  - Done.
- Image operations:
  - Done.
- Integration:
  - Done.
- Tests:
  - Done.
- Docs:
  - Done.

## Refactor Notes
- CUR parsing must not rely on Pillow's default CUR loader alone because it only exposes one image size. The converter will read the CUR directory itself and decode each image payload individually.
- Xcursor output follows the X.Org binary format: image chunks carry nominal size, actual size, hotspot, frame delay, and packed ARGB pixels.
- Wayland compatibility is handled through standard Xcursor theme structure and cursor names, including existing aliases and `wayland-cursor` completion.
- The existing CLI command names can stay as user-facing names, but code imports should no longer depend on the external `win2xcur` package.
- Xcursor size switching is handled inside each real cursor file, not through `index.theme` or `cursor.theme`; generated themes default to `24, 28, 32, 40, 48, 56, 64, 72, 80`, and `--xcursor-size` can override that list.
- Missing Xcursor sizes are synthesized from the nearest available nominal size with Pillow Lanczos resizing, while hotspots are scaled with the same ratio.

## Risks / Follow-ups
- DIB/BMP cursor variants in the wild can be more varied than the current test fixtures. Initial support covers common uncompressed 24-bit and 32-bit variants.
- Real KDE/Wayland cursor crashes still need separate investigation after conversion output is stable.
- Wayland loader CI coverage depends on system packages: `weston`, `pkg-config`, `cc`, and `libwayland-dev`. The test skips when those are unavailable.
- The dedicated CI job sets `ANI2XCUR_REQUIRE_WAYLAND_TEST=1`, so missing Wayland test dependencies fail there instead of skipping.
- Real desktop size menus should still be checked manually across KDE/GNOME/XFCE/LXQt because each shell may cache cursor themes differently.

## References
- Xcursor manual: https://www.x.org/archive/X11R7.5/doc/man/man3/Xcursor.3.html
- xcursorgen manual: https://www.x.org/releases/X11R6.8.1/doc/xcursorgen.1.html
- Freedesktop Icon Theme Specification: https://specifications.freedesktop.org/icon-theme/latest/
- wayland-cursor CursorTheme docs: https://docs.rs/wayland-cursor/latest/wayland_cursor/struct.CursorTheme.html
- Pillow image format docs: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

## Validation Log
- `/root/micromamba/envs/py311/bin/python -m pytest tests/test_native_cursor_converter.py tests/test_cursor_conversion_samples.py tests/test_cli_convert_samples.py` -> 15 passed.
- `/root/micromamba/envs/py311/bin/python -m ruff check .` -> passed.
- `/root/micromamba/envs/py311/bin/python -m ty check . --python /root/micromamba/envs/py311/bin/python` -> passed.
- `/root/micromamba/envs/py311/bin/python -m pytest` -> 67 passed.
- `/root/micromamba/envs/py311/bin/python -m pytest tests/test_wayland_cursor_loader.py -q` -> 1 passed; headless Weston + libwayland-cursor loaded generated `DMZ-White`.
- `/root/micromamba/envs/py311/bin/python -m pytest tests/test_cursor_conversion_samples.py tests/test_native_cursor_converter.py -q` -> 12 passed.
- `/root/micromamba/envs/py311/bin/python -m ruff check .` -> passed.
- `/root/micromamba/envs/py311/bin/python -m ty check . --python /root/micromamba/envs/py311/bin/python` -> passed.
- `/root/micromamba/envs/py311/bin/python -m pytest` -> 68 passed.
- `/root/micromamba/envs/py311/bin/python -m pytest tests/test_native_cursor_converter.py tests/test_cursor_conversion_samples.py tests/test_cli_convert_samples.py -q` -> 21 passed.
- `/root/micromamba/envs/py311/bin/python -m ruff check .` -> passed.
- `/root/micromamba/envs/py311/bin/python -m ty check . --python /root/micromamba/envs/py311/bin/python` -> passed.
- `/root/micromamba/envs/py311/bin/python -m python_docstring_checker ani2xcur` -> passed.
- `/root/micromamba/envs/py311/bin/python -m pytest` -> 79 passed.
- `ANI2XCUR_REQUIRE_WAYLAND_TEST=1 /root/micromamba/envs/py311/bin/python -m pytest -m wayland -q` -> 1 passed, 67 deselected.
- `/root/micromamba/envs/py311/bin/python -m ruff check .` -> passed.
- `/root/micromamba/envs/py311/bin/python -m ty check . --python /root/micromamba/envs/py311/bin/python` -> passed.
- `/root/micromamba/envs/py311/bin/python -m pytest` -> 68 passed.
