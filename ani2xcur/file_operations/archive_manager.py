import io
import zipfile
import tarfile
import lzma
from pathlib import Path
import rarfile

import zstandard as zstd
import py7zr
import lzo


SUPPORTED_ARCHIVE_FORMAT = [
    ".zip",
    ".7z",
    ".rar",
    ".tar",
    ".tar.Z",
    ".tar.lz",
    ".tar.lzma",
    ".tar.lzo",
    ".tar.bz2",
    ".tar.7z",
    ".tar.gz",
    ".tar.xz",
    ".tar.zst",
]


def extract_archive(archive_path: Path, extract_to: Path) -> None:
    """解压支持的压缩包

    Args:
        archive_path (Path): 压缩包路径
        extract_to (Path): 解压到的路径
    """
    name = archive_path.name.lower()
    extract_to.mkdir(parents=True, exist_ok=True)

    if name.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

    elif name.endswith(".tar"):
        with tarfile.open(archive_path, "r") as tar_ref:
            tar_ref.extractall(extract_to)

    elif name.endswith(".tar.gz"):
        with tarfile.open(archive_path, "r:gz") as tar_ref:
            tar_ref.extractall(extract_to)

    elif name.endswith(".tar.bz2"):
        with tarfile.open(archive_path, "r:bz2") as tar_ref:
            tar_ref.extractall(extract_to)

    elif name.endswith(".tar.xz"):
        with tarfile.open(archive_path, "r:xz") as tar_ref:
            tar_ref.extractall(extract_to)

    elif name.endswith(".tar.lzma") or name.endswith(".tlz"):
        with lzma.open(archive_path, "rb") as f:
            with tarfile.open(fileobj=f) as tar_ref:
                tar_ref.extractall(extract_to)

    elif name.endswith(".tar.zst") or name.endswith(".tar..zst"):
        with open(archive_path, "rb") as fh:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(fh) as reader:
                with tarfile.open(fileobj=reader) as tar_ref:
                    tar_ref.extractall(extract_to)

    elif name.endswith(".tar.lzo"):
        with open(archive_path, "rb") as fh:
            decompressed = lzo.decompress(fh.read())
            bio = io.BytesIO(decompressed)
            with tarfile.open(fileobj=bio) as tar_ref:
                tar_ref.extractall(extract_to)

    elif name.endswith(".7z"):
        with py7zr.SevenZipFile(archive_path, mode="r") as archive:
            archive.extractall(path=extract_to)

    elif name.endswith(".rar"):
        with rarfile.RarFile(archive_path, mode="r") as archive:
            archive.extractall(path=extract_to)

    else:
        raise ValueError(f"不支持的压缩格式: {archive_path}")
