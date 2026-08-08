from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any


class FasterWhisperSpeechToText:
    """Local speech-to-text provider backed by faster-whisper."""

    def __init__(
        self,
        model_name: str = "small",
        *,
        device: str = "cpu",
        compute_type: str = "int8",
        language: str | None = "vi",
        beam_size: int = 5,
    ) -> None:
        self._model_name = model_name
        self._device = device
        self._compute_type = compute_type
        self._language = language or None
        self._beam_size = beam_size
        self._model: Any | None = None

    async def transcribe(self, wav_bytes: bytes) -> str:
        if not wav_bytes:
            raise ValueError("wav_bytes cannot be empty")
        return await asyncio.to_thread(self._transcribe_blocking, wav_bytes)

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "Local STT requires faster-whisper. Install it with: "
                'pip install -e ".[local-stt]"'
            ) from exc

        print(
            "Loading local speech model "
            f"'{self._model_name}' ({self._device}/{self._compute_type})..."
        )
        self._model = WhisperModel(
            self._model_name,
            device=self._device,
            compute_type=self._compute_type,
        )
        return self._model

    def _transcribe_blocking(self, wav_bytes: bytes) -> str:
        model = self._load_model()

        path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
                audio_file.write(wav_bytes)
                path = Path(audio_file.name)

            segments, _ = model.transcribe(
                str(path),
                language=self._language,
                beam_size=self._beam_size,
            )
            return " ".join(
                segment.text.strip()
                for segment in segments
                if segment.text and segment.text.strip()
            ).strip()
        finally:
            if path is not None:
                path.unlink(missing_ok=True)
