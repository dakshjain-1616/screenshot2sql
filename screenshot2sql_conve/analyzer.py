"""
Screenshot analyzer: uses a vision LLM via OpenRouter (or mock mode) to extract UI structure.
Default model: google/gemini-2.5-flash-lite — fast, cheap, 1M context, excellent vision.
Override via SCREENSHOT_MODEL env var.
"""

import base64
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .mock_data import MOCK_RESPONSES, KEYWORD_MAPPINGS


ANALYZE_PROMPT = """You are a database architect analyzing a UI screenshot to reverse-engineer its data model.

Examine this screenshot and respond with a JSON object (no markdown, raw JSON only) with this structure:
{
  "is_ui": true/false,
  "ui_type": "Name of the application (e.g. Shopify Admin, Twitter, Notion)",
  "confidence": 0.0-1.0,
  "description": "Brief description of what the UI shows",
  "entities": [
    {
      "name": "table_name",
      "description": "What this table represents",
      "fields": [
        {
          "name": "field_name",
          "type": "SQL_TYPE",
          "constraints": "e.g. PRIMARY KEY, NOT NULL, REFERENCES other(id)"
        }
      ]
    }
  ],
  "sample_queries": [
    {
      "description": "Human-readable query purpose",
      "sql": "SELECT ..."
    }
  ]
}

Rules:
- If the image is NOT a software UI (e.g. nature photo, person, object), set is_ui=false, entities=[], sample_queries=[]
- Include an "error" field with "No UI detected. Please upload a screenshot of a software application." if is_ui=false
- Use SQLite-compatible types: INTEGER, TEXT, VARCHAR(n), DECIMAL(p,s), BOOLEAN, TIMESTAMP
- Every table MUST have an id field as PRIMARY KEY
- Use REFERENCES for foreign keys
- Generate 2-4 tables that cover the main entities visible in the UI
- Generate 2-3 practical SQL queries that a developer would actually use
- Think about what data the UI is displaying and what tables would be needed to power it
"""


class ScreenshotAnalyzer:
    """Analyzes UI screenshots to produce database entity/field definitions."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        mock_mode: Optional[bool] = None,
        max_tokens: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "") or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or os.getenv("SCREENSHOT_MODEL", "google/gemini-2.5-flash-lite")
        self.max_tokens = max_tokens or int(os.getenv("MAX_TOKENS", "4096"))
        self.max_retries = max_retries if max_retries is not None else int(
            os.getenv("MAX_RETRIES", "3")
        )
        self.retry_delay = retry_delay if retry_delay is not None else float(
            os.getenv("RETRY_DELAY", "2.0")
        )

        # Auto-detect mock mode: use real API only if key is present
        if mock_mode is not None:
            self.mock_mode = mock_mode
        else:
            self.mock_mode = not bool(self.api_key)

        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                )
            except ImportError:
                raise RuntimeError(
                    "openai package required. Run: pip install openai"
                )
        return self._client

    def _image_to_base64(self, image_path: str) -> tuple[str, str]:
        """Convert image file to base64 string and detect media type."""
        path = Path(image_path)
        suffix = path.suffix.lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        media_type = media_type_map.get(suffix, "image/png")
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        return data, media_type

    def _mock_analyze(self, image_path: str, hint: Optional[str] = None) -> dict:
        """Return a mock analysis result based on filename or hint keywords."""
        search_text = ""
        if hint:
            search_text = hint.lower()
        if image_path:
            search_text += " " + Path(image_path).stem.lower()

        matched_key = "default"
        for keyword, response_key in KEYWORD_MAPPINGS.items():
            if keyword in search_text:
                matched_key = response_key
                break

        result = dict(MOCK_RESPONSES.get(matched_key, MOCK_RESPONSES["default"]))
        result["_mock"] = True
        result["_analyzed_at"] = datetime.now(timezone.utc).isoformat()
        return result

    def _call_api(self, image_data: str, media_type: str) -> str:
        """Call vision LLM via OpenRouter with retry/backoff. Returns raw text."""
        client = self._get_client()
        last_exc = None

        for attempt in range(self.max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{media_type};base64,{image_data}"
                                    },
                                },
                                {"type": "text", "text": ANALYZE_PROMPT},
                            ],
                        }
                    ],
                )
                return response.choices[0].message.content or ""
            except Exception as exc:
                last_exc = exc
                error_str = str(exc).lower()
                if any(
                    kw in error_str
                    for kw in ("rate_limit", "overloaded", "timeout", "503", "529")
                ):
                    if attempt < self.max_retries - 1:
                        wait = self.retry_delay * (2 ** attempt)
                        time.sleep(wait)
                    continue
                raise

        raise RuntimeError(
            f"API call failed after {self.max_retries} attempts. Last error: {last_exc}"
        ) from last_exc

    def analyze(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        image_media_type: str = "image/png",
        hint: Optional[str] = None,
    ) -> dict:
        """
        Analyze a UI screenshot.

        Args:
            image_path: Path to image file on disk.
            image_bytes: Raw image bytes (alternative to image_path).
            image_media_type: MIME type when using image_bytes.
            hint: Optional text hint (filename, description) for mock mode routing.

        Returns:
            dict with keys: is_ui, ui_type, confidence, description,
            entities, sample_queries, _analyzed_at.
            Plus optional 'error' if no UI detected.
        """
        if self.mock_mode:
            return self._mock_analyze(image_path or "", hint=hint)

        # Real API call
        if image_path:
            image_data, media_type = self._image_to_base64(image_path)
        elif image_bytes:
            image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
            media_type = image_media_type
        else:
            raise ValueError("Provide image_path or image_bytes")

        analyzed_at = datetime.now(timezone.utc).isoformat()
        raw = self._call_api(image_data, media_type).strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Model returned invalid JSON: {exc}\nRaw response (first 500 chars): {raw[:500]}"
            )

        result["_analyzed_at"] = analyzed_at
        result["_model"] = self.model
        return result
