import hashlib
import re
from dataclasses import dataclass


class PolicyViolation(RuntimeError):
    pass


@dataclass(frozen=True)
class SanitizedPayload:
    text: str
    sha256: str
    data_class: str


class OutboundPolicy:
    _secret_patterns = (
        re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
        re.compile(r"(?i)(api[_-]?key|token|password)\s*[:=]\s*\S+"),
    )

    def sanitize(
        self,
        text: str,
        *,
        data_class: str,
        exact_address: str | None,
        latitude: float | None,
        longitude: float | None,
    ) -> SanitizedPayload:
        forbidden: list[str] = []
        if exact_address and exact_address.strip() and exact_address in text:
            forbidden.append("exact_address")

        coordinate_tokens: list[str] = []
        if latitude is not None:
            coordinate_tokens.extend((str(latitude), f"{latitude:.6f}"))
        if longitude is not None:
            coordinate_tokens.extend((str(longitude), f"{longitude:.6f}"))
        if any(token and token in text for token in coordinate_tokens):
            forbidden.append("exact_home_coordinates")

        if any(pattern.search(text) for pattern in self._secret_patterns):
            forbidden.append("secret_like_value")

        if forbidden:
            raise PolicyViolation(
                "Outbound payload blocked by policy: "
                + ", ".join(sorted(set(forbidden)))
            )

        compact = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if len(compact) > 40_000:
            compact = compact[:40_000]
        return SanitizedPayload(
            text=compact,
            sha256=hashlib.sha256(compact.encode("utf-8")).hexdigest(),
            data_class=data_class,
        )
