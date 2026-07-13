import struct
from pathlib import Path

import pytest
from PIL import Image

from ani2xcur.cursor_conversion.native_cursor.models import CursorFrame, CursorImage
from ani2xcur.cursor_conversion.native_cursor.parsers import parse_blob
from ani2xcur.cursor_conversion.native_cursor.process import win2xcur_process, x2wincur_process
from ani2xcur.cursor_conversion.native_cursor.transforms import (
    DEFAULT_XCURSOR_SIZES,
    add_shadow_to_frames,
    normalize_xcursor_sizes,
    scale_frames,
)
from ani2xcur.cursor_conversion.native_cursor.writers import to_ani, to_cur, to_xcursor


MOUSE_POINTER_DIR = Path(__file__).resolve().parent / "Sunaokami-Shiroko-Windows"


def test_parse_cur_preserves_all_sizes_and_hotspots(windows_cursor_dir):
    frames = parse_blob((windows_cursor_dir / "Arrow.cur").read_bytes())

    assert len(frames) == 1
    assert [(image.image.size, image.hotspot, image.nominal) for image in frames[0].images] == [
        ((24, 24), (7, 4), 24),
        ((32, 32), (10, 5), 32),
        ((48, 48), (14, 8), 48),
    ]


def test_parse_ani_preserves_frame_delay_and_multi_size_images(windows_cursor_dir):
    frames = parse_blob((windows_cursor_dir / "Wait.ani").read_bytes())

    assert len(frames) == 23
    assert frames[0].delay == 2 / 60
    assert [image.image.size for image in frames[0].images] == [(32, 32), (48, 48), (64, 64)]


def test_xcursor_writer_round_trips_multisize_cursor():
    frames = [
        CursorFrame(
            images=[
                CursorImage(Image.new("RGBA", (2, 2), (100, 20, 40, 128)), (1, 1), 2),
                CursorImage(Image.new("RGBA", (4, 4), (40, 80, 120, 255)), (2, 2), 4),
            ],
            delay=0.125,
        )
    ]

    parsed = parse_blob(to_xcursor(frames))

    assert len(parsed) == 1
    assert parsed[0].delay == 0.125
    assert [(image.image.size, image.hotspot, image.nominal) for image in parsed[0].images] == [
        ((2, 2), (1, 1), 2),
        ((4, 4), (2, 2), 4),
    ]
    assert parsed[0].images[0].image.getpixel((0, 0)) == (100, 20, 40, 128)


def test_parse_xcursor_selects_complete_32px_animation_when_size_sequences_differ():
    small_red = CursorImage(Image.new("RGBA", (32, 32), (255, 0, 0, 255)), (3, 4), 32)
    small_green = CursorImage(Image.new("RGBA", (32, 32), (0, 255, 0, 255)), (5, 6), 32)
    large_blue = CursorImage(Image.new("RGBA", (128, 128), (0, 0, 255, 255)), (12, 16), 128)
    blob = to_xcursor(
        [
            CursorFrame([small_red, large_blue], delay=0.1),
            CursorFrame([small_green], delay=0.2),
        ]
    )

    frames = parse_blob(blob)

    assert len(frames) == 2
    assert [frame.delay for frame in frames] == [0.1, 0.2]
    assert [[image.nominal for image in frame.images] for frame in frames] == [[32], [32]]
    assert frames[0].images[0].image.getpixel((0, 0)) == (255, 0, 0, 255)
    assert frames[1].images[0].image.getpixel((0, 0)) == (0, 255, 0, 255)


def test_parse_xcursor_preserves_static_images_with_independent_delays():
    small = CursorImage(Image.new("RGBA", (32, 32), (255, 0, 0, 255)), (3, 4), 32)
    large = CursorImage(Image.new("RGBA", (128, 128), (0, 0, 255, 255)), (12, 16), 128)
    blob = to_xcursor(
        [
            CursorFrame([small], delay=0.1),
            CursorFrame([large], delay=0.2),
        ]
    )

    frames = parse_blob(blob)

    assert len(frames) == 1
    assert [image.nominal for image in frames[0].images] == [32, 128]


def test_x2wincur_process_converts_independent_size_sequences_to_ani(tmp_path):
    input_file = tmp_path / "independent-xcursor"
    small_red = CursorImage(Image.new("RGBA", (32, 32), (255, 0, 0, 255)), (3, 4), 32)
    small_green = CursorImage(Image.new("RGBA", (32, 32), (0, 255, 0, 255)), (5, 6), 32)
    large_blue = CursorImage(Image.new("RGBA", (128, 128), (0, 0, 255, 255)), (12, 16), 128)
    input_file.write_bytes(
        to_xcursor(
            [
                CursorFrame([small_red, large_blue], delay=0.1),
                CursorFrame([small_green], delay=0.2),
            ]
        )
    )

    output_file = x2wincur_process(input_file, tmp_path)
    frames = parse_blob(output_file.read_bytes())

    assert output_file.suffix == ".ani"
    assert len(frames) == 2
    assert [frame.images[0].image.getpixel((0, 0)) for frame in frames] == [
        (255, 0, 0, 255),
        (0, 255, 0, 255),
    ]


def test_windows_writers_round_trip_static_and_animated_cursors():
    frame_a = CursorFrame([CursorImage(Image.new("RGBA", (16, 16), (255, 0, 0, 255)), (3, 4), 16)], delay=0.1)
    frame_b = CursorFrame([CursorImage(Image.new("RGBA", (16, 16), (0, 0, 255, 255)), (5, 6), 16)], delay=0.2)

    parsed_cur = parse_blob(to_cur(frame_a))
    parsed_ani = parse_blob(to_ani([frame_a, frame_b]))

    assert [(image.image.size, image.hotspot) for image in parsed_cur[0].images] == [((16, 16), (3, 4))]
    assert len(parsed_ani) == 2
    assert [frame.delay for frame in parsed_ani] == [0.1, 0.2]
    assert [frame.images[0].hotspot for frame in parsed_ani] == [(3, 4), (5, 6)]


def test_windows_writers_use_png_for_static_and_dib_for_animated_payloads():
    image = Image.new("RGBA", (2, 2), (255, 255, 255, 255))
    image.putpixel((1, 0), (0, 0, 0, 0))
    frame = CursorFrame([CursorImage(image, (1, 1), 2)], delay=0.1)

    cur_blob = to_cur(frame)
    ani_blob = to_ani([frame, frame.clone()])

    cur_payload = _first_cur_payload(cur_blob)
    ani_payload = _first_cur_payload(_first_ani_icon_cur(ani_blob))
    assert cur_payload.startswith(b"\x89PNG\r\n\x1a\n")
    assert _png_ihdr(cur_payload) == (2, 2, 8, 4, 0, 0, 0)
    assert not ani_payload.startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack_from("<IiiHHI", ani_payload, 0) == (40, 2, 4, 1, 32, 0)

    assert _ani_display_rate(ani_blob) == 1
    parsed = parse_blob(cur_blob)
    assert parsed[0].images[0].image.getpixel((1, 0)) == (0, 0, 0, 0)


def test_windows_writers_use_dib_payloads_for_high_resolution_images():
    small = CursorImage(Image.new("RGBA", (32, 32), (255, 0, 0, 255)), (4, 4), 32)
    large = CursorImage(Image.new("RGBA", (128, 128), (0, 0, 255, 255)), (16, 16), 128)

    cur_blob = to_cur(CursorFrame([small, large]))
    payloads = _cur_payloads(cur_blob)

    assert len(payloads) == 1
    assert not payloads[0].startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack_from("<IiiHHI", payloads[0], 0) == (40, 128, 256, 1, 32, 0)


def test_windows_ani_writer_keeps_only_largest_high_resolution_frame_image():
    small = CursorImage(Image.new("RGBA", (32, 32), (255, 0, 0, 255)), (4, 4), 32)
    medium = CursorImage(Image.new("RGBA", (96, 96), (0, 255, 0, 255)), (12, 12), 96)
    large = CursorImage(Image.new("RGBA", (256, 256), (0, 0, 255, 255)), (32, 32), 256)

    ani_blob = to_ani([CursorFrame([small, medium, large], delay=0.1)])
    payloads = _cur_payloads(_first_ani_icon_cur(ani_blob))

    assert len(payloads) == 1
    assert not payloads[0].startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack_from("<IiiHHI", payloads[0], 0) == (40, 256, 512, 1, 32, 0)


def test_windows_ani_writer_keeps_single_standard_image_for_normal_frames():
    small = CursorImage(Image.new("RGBA", (24, 24), (255, 0, 0, 255)), (3, 3), 24)
    standard = CursorImage(Image.new("RGBA", (32, 32), (0, 255, 0, 255)), (4, 4), 32)
    large = CursorImage(Image.new("RGBA", (96, 96), (0, 0, 255, 255)), (12, 12), 96)

    ani_blob = to_ani([CursorFrame([small, standard, large], delay=0.1)])
    payloads = _cur_payloads(_first_ani_icon_cur(ani_blob))
    frames = parse_blob(ani_blob)

    assert len(payloads) == 1
    assert not payloads[0].startswith(b"\x89PNG\r\n\x1a\n")
    assert struct.unpack_from("<IiiHHI", payloads[0], 0) == (40, 32, 64, 1, 32, 0)
    assert [(image.image.size, image.hotspot, image.nominal) for image in frames[0].images] == [((32, 32), (4, 4), 32)]


def test_parse_32bit_dib_cur_uses_alpha_channel():
    cur_blob = _make_cur_blob(_make_32bit_dib_payload())

    frames = parse_blob(cur_blob)

    image = frames[0].images[0].image
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (255, 0, 0, 128)
    assert image.getpixel((1, 1)) == (255, 255, 255, 0)


def test_parse_dib_cur_prefers_bitmap_height_when_directory_height_is_wrong():
    cur_blob = _make_cur_blob(_make_32bit_dib_payload_for_size(4, 4), width=2, height=2, hotspot=(3, 3))

    frames = parse_blob(cur_blob)

    image = frames[0].images[0].image
    assert [(cursor.image.size, cursor.hotspot, cursor.nominal) for cursor in frames[0].images] == [((4, 4), (3, 3), 4)]
    assert image.getpixel((3, 3)) == (3, 3, 100, 255)


def test_parse_24bit_dib_cur_uses_and_mask():
    cur_blob = _make_cur_blob(_make_24bit_dib_payload())

    frames = parse_blob(cur_blob)

    image = frames[0].images[0].image
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (255, 0, 0, 255)
    assert image.getpixel((1, 0)) == (0, 255, 0, 0)


def test_parse_8bit_dib_cur_uses_palette_and_mask():
    cur_blob = _make_cur_blob(
        _make_indexed_dib_payload(
            8,
            bottom_indices=[2, 1],
            top_indices=[0, 3],
            palette=[
                (10, 20, 30),
                (40, 50, 60),
                (70, 80, 90),
                (100, 110, 120),
            ],
        )
    )

    frames = parse_blob(cur_blob)

    image = frames[0].images[0].image
    assert image.size == (2, 2)
    assert image.getpixel((0, 0)) == (10, 20, 30, 255)
    assert image.getpixel((1, 0)) == (100, 110, 120, 0)
    assert image.getpixel((0, 1)) == (70, 80, 90, 255)
    assert image.getpixel((1, 1)) == (40, 50, 60, 255)


@pytest.mark.parametrize(
    ("bit_count", "palette"),
    [
        (1, [(0, 0, 0), (255, 255, 255)]),
        (4, [(index, index + 1, index + 2) for index in range(16)]),
    ],
)
def test_parse_bit_packed_indexed_dib_cur_uses_palette(bit_count: int, palette: list[tuple[int, int, int]]):
    cur_blob = _make_cur_blob(
        _make_indexed_dib_payload(
            bit_count,
            bottom_indices=[1, 0],
            top_indices=[0, 1],
            palette=palette,
            colors_used=0,
        )
    )

    frames = parse_blob(cur_blob)

    image = frames[0].images[0].image
    assert image.getpixel((0, 0)) == (*palette[0], 255)
    assert image.getpixel((1, 0)) == (*palette[1], 0)
    assert image.getpixel((0, 1)) == (*palette[1], 255)
    assert image.getpixel((1, 1)) == (*palette[0], 255)


def test_parse_real_mouse_pointer_8bit_ani_preserves_animation_metadata():
    frames = parse_blob((MOUSE_POINTER_DIR / "pointer.ani").read_bytes())

    assert len(frames) == 16
    assert frames[0].delay == 6 / 60
    assert [(image.image.size, image.hotspot, image.nominal) for image in frames[0].images] == [((32, 32), (1, 1), 32)]


def test_parse_real_mouse_pointer_sample_supports_all_cursor_files():
    cursor_files = sorted(path for path in MOUSE_POINTER_DIR.iterdir() if path.suffix.lower() in {".ani", ".cur"})

    assert len(cursor_files) == 15
    for cursor_file in cursor_files:
        frames = parse_blob(cursor_file.read_bytes())
        assert frames, cursor_file.name


def test_scale_frames_scales_images_and_hotspots():
    frames = [CursorFrame([CursorImage(Image.new("RGBA", (10, 8), (0, 0, 0, 255)), (2, 3), 10)])]

    scale_frames(frames, scale=2)

    assert frames[0].images[0].image.size == (20, 16)
    assert frames[0].images[0].hotspot == (4, 6)


def test_normalize_xcursor_sizes_expands_single_size_cursor():
    frames = [CursorFrame([CursorImage(Image.new("RGBA", (10, 10), (0, 0, 0, 255)), (2, 3), 10)])]

    normalize_xcursor_sizes(frames, [10, 20, 30])

    assert [(image.image.size, image.hotspot, image.nominal) for image in frames[0].images] == [
        ((10, 10), (2, 3), 10),
        ((20, 20), (4, 6), 20),
        ((30, 30), (6, 9), 30),
    ]


def test_normalize_xcursor_sizes_preserves_existing_images():
    small = CursorImage(Image.new("RGBA", (16, 16), (255, 0, 0, 255)), (1, 2), 16)
    large = CursorImage(Image.new("RGBA", (32, 32), (0, 0, 255, 255)), (2, 4), 32)
    frames = [CursorFrame([small, large])]

    normalize_xcursor_sizes(frames, [16, 24, 32])

    assert frames[0].images[0] is small
    assert frames[0].images[2] is large
    assert [(image.image.size, image.hotspot, image.nominal) for image in frames[0].images] == [
        ((16, 16), (1, 2), 16),
        ((24, 24), (2, 3), 24),
        ((32, 32), (2, 4), 32),
    ]


def test_normalize_xcursor_sizes_keeps_animation_delay():
    frames = [
        CursorFrame([CursorImage(Image.new("RGBA", (16, 16), (255, 0, 0, 255)), (3, 4), 16)], delay=0.1),
        CursorFrame([CursorImage(Image.new("RGBA", (16, 16), (0, 0, 255, 255)), (5, 6), 16)], delay=0.2),
    ]

    normalize_xcursor_sizes(frames, [16, 32])

    assert [frame.delay for frame in frames] == [0.1, 0.2]
    assert [[image.nominal for image in frame.images] for frame in frames] == [[16, 32], [16, 32]]


def test_normalize_xcursor_sizes_preserves_source_sizes_outside_target_list():
    frames = [CursorFrame([CursorImage(Image.new("RGBA", (128, 128), (0, 0, 0, 255)), (16, 16), 128)])]

    normalize_xcursor_sizes(frames, [24, 96])

    assert [(image.image.size, image.hotspot, image.nominal) for image in frames[0].images] == [
        ((24, 24), (3, 3), 24),
        ((96, 96), (12, 12), 96),
        ((128, 128), (16, 16), 128),
    ]


def test_scale_then_normalize_preserves_scaled_visual_size():
    frames = [CursorFrame([CursorImage(Image.new("RGBA", (10, 10), (0, 0, 0, 255)), (2, 3), 10)])]

    scale_frames(frames, scale=2)
    normalize_xcursor_sizes(frames, [10, 20])

    assert [(image.image.size, image.hotspot, image.nominal) for image in frames[0].images] == [
        ((20, 20), (4, 6), 10),
        ((40, 40), (8, 12), 20),
    ]


def test_win2xcur_process_synthesizes_default_sizes_from_single_size_cur(tmp_path):
    input_file = tmp_path / "single.cur"
    input_file.write_bytes(to_cur(CursorFrame([CursorImage(Image.new("RGBA", (16, 16), (0, 0, 0, 255)), (4, 5), 16)])))

    output_file = win2xcur_process(input_file, tmp_path)

    frames = parse_blob(output_file.read_bytes())
    assert [image.nominal for image in frames[0].images] == [16, *DEFAULT_XCURSOR_SIZES]


def test_shadow_uses_requested_opacity():
    frames = [CursorFrame([CursorImage(Image.new("RGBA", (4, 4), (255, 255, 255, 255)), (1, 1), 4)])]

    add_shadow_to_frames(
        frames,
        color="#000000",
        opacity=64,
        radius=0,
        sigma=0,
        xoffset=1,
        yoffset=0,
    )

    alpha_histogram = frames[0].images[0].image.convert("RGBA").getchannel("A").histogram()
    assert alpha_histogram[64] > 0


def _make_cur_blob(payload: bytes, *, width: int = 2, height: int = 2, hotspot: tuple[int, int] = (1, 1)) -> bytes:
    header = struct.pack("<HHH", 0, 2, 1)
    entry = struct.pack("<BBBBHHII", width, height, 0, 0, hotspot[0], hotspot[1], len(payload), len(header) + 16)
    return header + entry + payload


def _first_cur_payload(cur_blob: bytes) -> bytes:
    _, cursor_type, image_count = struct.unpack_from("<HHH", cur_blob, 0)
    assert cursor_type == 2
    assert image_count > 0
    _, _, _, _, _, _, image_size, image_offset = struct.unpack_from("<BBBBHHII", cur_blob, 6)
    return cur_blob[image_offset : image_offset + image_size]


def _cur_payloads(cur_blob: bytes) -> list[bytes]:
    _, cursor_type, image_count = struct.unpack_from("<HHH", cur_blob, 0)
    assert cursor_type == 2
    payloads: list[bytes] = []
    offset = 6
    for _ in range(image_count):
        _, _, _, _, _, _, image_size, image_offset = struct.unpack_from("<BBBBHHII", cur_blob, offset)
        payloads.append(cur_blob[image_offset : image_offset + image_size])
        offset += 16
    return payloads


def _first_ani_icon_cur(ani_blob: bytes) -> bytes:
    signature, riff_size, subtype = struct.unpack_from("<4sI4s", ani_blob, 0)
    assert signature == b"RIFF"
    assert subtype == b"ACON"
    offset = 12
    end = min(len(ani_blob), 8 + riff_size)
    while offset + 8 <= end:
        name, size = struct.unpack_from("<4sI", ani_blob, offset)
        payload_start = offset + 8
        payload_end = payload_start + size
        if name == b"LIST" and ani_blob[payload_start : payload_start + 4] == b"fram":
            child_offset = payload_start + 4
            while child_offset + 8 <= payload_end:
                child_name, child_size = struct.unpack_from("<4sI", ani_blob, child_offset)
                child_start = child_offset + 8
                child_end = child_start + child_size
                if child_name == b"icon":
                    return ani_blob[child_start:child_end]
                child_offset = child_end + (child_end & 1)
        offset = payload_end + (payload_end & 1)
    raise AssertionError("ANI file does not contain icon frames")


def _ani_display_rate(ani_blob: bytes) -> int:
    signature, riff_size, subtype = struct.unpack_from("<4sI4s", ani_blob, 0)
    assert signature == b"RIFF"
    assert subtype == b"ACON"
    offset = 12
    end = min(len(ani_blob), 8 + riff_size)
    while offset + 8 <= end:
        name, size = struct.unpack_from("<4sI", ani_blob, offset)
        payload_start = offset + 8
        payload_end = payload_start + size
        if name == b"anih":
            return struct.unpack_from("<IIIIIIIII", ani_blob, payload_start)[7]
        offset = payload_end + (payload_end & 1)
    raise AssertionError("ANI file does not contain anih chunk")


def _png_ihdr(png_blob: bytes) -> tuple[int, int, int, int, int, int, int]:
    assert png_blob.startswith(b"\x89PNG\r\n\x1a\n")
    length, chunk_type = struct.unpack_from(">I4s", png_blob, 8)
    assert length == 13
    assert chunk_type == b"IHDR"
    return struct.unpack_from(">IIBBBBB", png_blob, 16)


def _make_32bit_dib_payload() -> bytes:
    width = 2
    height = 2
    row_stride = width * 4
    mask_stride = 4
    pixels_bottom_up = bytes(
        [
            255,
            0,
            0,
            255,
            255,
            255,
            255,
            0,
            0,
            0,
            255,
            128,
            0,
            255,
            0,
            255,
        ]
    )
    mask = b"\x00" * (mask_stride * height)
    header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, 32, 0, row_stride * height + len(mask), 0, 0, 0, 0)
    return header + pixels_bottom_up + mask


def _make_32bit_dib_payload_for_size(width: int, height: int) -> bytes:
    row_stride = width * 4
    mask_stride = ((width + 31) // 32) * 4
    pixels_bottom_up = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            pixels_bottom_up.extend((100, y, x, 255))
    mask = b"\x00" * (mask_stride * height)
    header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, 32, 0, row_stride * height + len(mask), 0, 0, 0, 0)
    return header + bytes(pixels_bottom_up) + mask


def _make_24bit_dib_payload() -> bytes:
    width = 2
    height = 2
    row_stride = 8
    mask_stride = 4
    bottom_row = bytes([255, 0, 0, 255, 255, 255, 0, 0])
    top_row = bytes([0, 0, 255, 0, 255, 0, 0, 0])
    bottom_mask = b"\x00\x00\x00\x00"
    top_mask = b"\x40\x00\x00\x00"
    header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, 24, 0, row_stride * height + mask_stride * height, 0, 0, 0, 0)
    return header + bottom_row + top_row + bottom_mask + top_mask


def _make_indexed_dib_payload(
    bit_count: int,
    *,
    bottom_indices: list[int],
    top_indices: list[int],
    palette: list[tuple[int, int, int]],
    colors_used: int | None = None,
) -> bytes:
    width = 2
    height = 2
    row_stride = ((width * bit_count + 31) // 32) * 4
    mask_stride = 4
    bottom_row = _pack_indexed_dib_row(bottom_indices, bit_count).ljust(row_stride, b"\x00")
    top_row = _pack_indexed_dib_row(top_indices, bit_count).ljust(row_stride, b"\x00")
    bottom_mask = b"\x00\x00\x00\x00"
    top_mask = b"\x40\x00\x00\x00"
    palette_blob = b"".join(struct.pack("<BBBB", blue, green, red, 0) for red, green, blue in palette)
    image_size = row_stride * height + mask_stride * height
    header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, bit_count, 0, image_size, 0, 0, len(palette) if colors_used is None else colors_used, 0)
    return header + palette_blob + bottom_row + top_row + bottom_mask + top_mask


def _pack_indexed_dib_row(indices: list[int], bit_count: int) -> bytes:
    if bit_count == 8:
        return bytes(indices)
    if bit_count == 4:
        return bytes([(indices[0] << 4) | indices[1]])
    if bit_count == 1:
        value = 0
        for index, palette_index in enumerate(indices):
            if palette_index:
                value |= 0x80 >> index
        return bytes([value])
    raise ValueError(f"Unsupported indexed test bit depth {bit_count}")
