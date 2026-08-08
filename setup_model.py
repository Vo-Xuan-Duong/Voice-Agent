from __future__ import annotations

import shutil
import tarfile
import urllib.request
from pathlib import Path

MODEL_NAME = "sherpa-onnx-zipformer-vi-int8-2025-04-20"
MODEL_URL = (
    "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/"
    f"{MODEL_NAME}.tar.bz2"
)

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
MODEL_DIR = MODELS_DIR / MODEL_NAME
ARCHIVE_PATH = MODELS_DIR / f"{MODEL_NAME}.tar.bz2"

EXPECTED_FILES = (
    "encoder-epoch-12-avg-8.int8.onnx",
    "decoder-epoch-12-avg-8.onnx",
    "joiner-epoch-12-avg-8.int8.onnx",
    "tokens.txt",
)


def model_is_ready() -> bool:
    return all((MODEL_DIR / name).is_file() for name in EXPECTED_FILES)


def show_progress(block_count: int, block_size: int, total_size: int) -> None:
    if total_size <= 0:
        return
    downloaded = min(block_count * block_size, total_size)
    percent = downloaded * 100 / total_size
    print(
        f"\rDownloading model: {percent:5.1f}% "
        f"({downloaded / 1024 / 1024:.1f}/{total_size / 1024 / 1024:.1f} MB)",
        end="",
        flush=True,
    )


def safe_extract(archive_path: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()

    with tarfile.open(archive_path, mode="r:bz2") as archive:
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            if target != destination_resolved and destination_resolved not in target.parents:
                raise RuntimeError(f"Unsafe path in model archive: {member.name}")

        archive.extractall(destination)


def main() -> None:
    if model_is_ready():
        print(f"Model is already ready: {MODEL_DIR}")
        return

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading the official Vietnamese Sherpa-ONNX model...")
    print(MODEL_URL)

    try:
        urllib.request.urlretrieve(MODEL_URL, ARCHIVE_PATH, reporthook=show_progress)
        print("\nExtracting model...")
        safe_extract(ARCHIVE_PATH, MODELS_DIR)
    except Exception:
        ARCHIVE_PATH.unlink(missing_ok=True)
        if MODEL_DIR.exists() and not model_is_ready():
            shutil.rmtree(MODEL_DIR, ignore_errors=True)
        raise
    finally:
        ARCHIVE_PATH.unlink(missing_ok=True)

    if not model_is_ready():
        raise RuntimeError(
            "Model download completed, but required model files were not found."
        )

    print(f"Model ready: {MODEL_DIR}")
    print("Now run: python main.py")


if __name__ == "__main__":
    main()
