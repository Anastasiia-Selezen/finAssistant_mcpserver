import re
from collections.abc import Iterable

import html2text
import requests
from config import settings
from sec_api import ExtractorApi, MappingApi, QueryApi


class SECClient:
    """
    Minimal helper class that exposes three SEC API interactions:
      • map_ticker_to_cik      — Map a ticker symbol to its CIK identifier.
      • get_latest_10k_filing  — Retrieve metadata for the latest 10-K filing.
      • extract_filing_text    — Extract human-readable text from a filing.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_sections: Iterable[str] | None = None,
    ) -> None:
        self.api_key = api_key or settings.SEC_API_KEY
        if not self.api_key:
            raise OSError("SEC_API_KEY environment variable is required.")

        self.query_api = QueryApi(api_key=self.api_key)
        self.extractor_api = ExtractorApi(api_key=self.api_key)
        self.mapping_api = MappingApi(api_key=self.api_key)
        self.default_sections = tuple(default_sections or ("1", "1A", "7", "7A", "8"))
        self._cik_cache: dict[str, str] = {}

    def map_ticker_to_cik(self, ticker: str) -> str:
        """Return the CIK for the given ticker symbol."""
        normalized = ticker.strip().upper()
        if not normalized:
            raise ValueError("Ticker symbol must be provided.")

        if normalized not in self._cik_cache:
            cik = self._resolve_cik_by_ticker(normalized)
            if not cik:
                raise ValueError(f"Unable to map ticker {ticker!r} to a CIK.")
            self._cik_cache[normalized] = cik

        return self._cik_cache[normalized]

    def _resolve_cik_by_ticker(self, ticker: str) -> str | None:
        """
        Use the Mapping API to resolve `ticker` and return the first CIK found.
        The API can respond with either a dict, a dict containing `data`, or a list.
        """
        try:
            response = self.mapping_api.resolve("ticker", ticker)
        except Exception as exc:  # pragma: no cover - network call failure
            raise RuntimeError(f"Mapping API lookup failed for ticker {ticker!r}") from exc

        entries = []
        if isinstance(response, dict):
            data = response.get("data")
            if isinstance(data, list):
                entries = data
            else:
                entries = [response]
        elif isinstance(response, list):
            entries = response

        for entry in entries:
            cik = entry.get("cik") or entry.get("CIK") or entry.get("cik_str") or entry.get("cikNumber")
            if cik:
                return str(cik).strip()
        return None

    def get_latest_10k_filing(self, cik: str) -> dict | None:
        """Fetch metadata for the most recent 10-K filing associated with `cik`."""
        normalized = cik.strip()
        if not normalized:
            raise ValueError("CIK must be provided.")

        query = {
            "query": {"query_string": {"query": f'cik:{normalized} AND formType:"10-K"'}},
            "from": "0",
            "size": "1",
            "sort": [{"filedAt": {"order": "desc"}}],
        }
        result = self.query_api.get_filings(query)
        filings = result.get("filings", [])
        return filings[0] if filings else None

    def extract_filing_text(
        self,
        filing: dict,
        *,
        sections: Iterable[str] | None = None,
    ) -> str | None:
        """
        Extract plain text for `filing`. If the Extractor API cannot provide the full
        document, the specified `sections` (or default 10-K sections) are concatenated.
        Falls back to downloading `linkToTxt` when available.
        """
        filing_url = filing.get("linkToFilingDetails")
        text: str | None = None

        if filing_url:
            text = self._extract_with_extractor_api(
                filing_url,
                tuple(sections) if sections is not None else self.default_sections,
            )

        if not text and filing.get("linkToTxt"):
            text = self._download_filing_text(filing["linkToTxt"])

        if not text:
            return None

        return self._normalize_text(text)

    def _extract_with_extractor_api(
        self,
        filing_url: str,
        sections: Iterable[str],
    ) -> str | None:
        try:
            text = self.extractor_api.get_section(filing_url, "all", "text")
            if text:
                return text
        except Exception:
            text = None

        collected = []
        for section in sections:
            try:
                section_text = self.extractor_api.get_section(filing_url, section, "text")
            except Exception:
                continue
            if section_text:
                collected.append(f"Item {section}\n{section_text}")

        return "\n\n".join(collected) if collected else None

    @staticmethod
    def _download_filing_text(url: str) -> str | None:
        headers = {
            "User-Agent": "finAssistant/1.0 (contact: support@finassistant)",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov",
        }
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            return None
        return response.text

    @staticmethod
    def _normalize_text(raw_text: str) -> str:
        if "<" in raw_text and ">" in raw_text:
            parser = html2text.HTML2Text()
            parser.ignore_links = False
            parser.ignore_tables = False
            raw_text = parser.handle(raw_text)

        cleaned = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", " ", raw_text)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()
