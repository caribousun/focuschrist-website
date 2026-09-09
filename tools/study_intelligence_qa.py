from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
GROUNDED = ROOT / "study-intelligence-v3.js"
COMMON = ROOT / "site-common.js"


def read_required(path: Path, errors: list[str]) -> str:
    if not path.exists() or path.stat().st_size == 0:
        errors.append(f"{path.name} missing or empty")
        return ""
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    grounded = read_required(GROUNDED, errors)
    common = read_required(COMMON, errors)

    required_grounded_markers = (
        "focusChrist Study Intelligence v3",
        "VERIFIED CORE RESTORATION FACTS:",
        "John the Baptist conferred the Aaronic Priesthood",
        "Peter, James, and John later conferred the Melchizedek Priesthood",
        "Do not use Markdown tables",
        "normal spaces and ordinary hyphens",
        "normalizeDisplayText",
        "convertMarkdownTables",
        "focusChristStudyAskV3",
        "temperature: 0.25",
        "requestWithRetry(messages, profile)",
        "CLIENT_FIRST_ATTEMPT_MS = 12000",
        "CLIENT_RETRY_DELAY_MS = 400",
        "data-focuschrist-study-intelligence-version', '3'",
    )
    for marker in required_grounded_markers:
        if marker not in grounded:
            errors.append(f"study-intelligence-v3.js missing grounded-policy marker: {marker}")

    forbidden_policy_markers = (
        "Every response must end by connecting to Jesus Christ",
        "ALWAYS tie appropriate answers back to Jesus Christ",
        "May the love of Jesus Christ bring you peace and clarity",
        "That's a great question!",
        "temperature: 0.7",
        "max_tokens: 800",
        "innerHTML = text",
        "innerHTML=text",
        "[25000, 18000]",
    )
    for marker in forbidden_policy_markers:
        if marker in grounded:
            errors.append(f"Study Intelligence contains legacy/unsafe marker: {marker}")

    required_common_markers = (
        "loadStudyIntelligence",
        "study-intelligence-v3.js?v=20260909-20",
        "data-focuschrist-study-intelligence-v3",
        "path.endsWith('/ask.html')",
        "path.endsWith('/pioneers.html')",
        "window.focusChristSourceIntegrity",
        "unreviewed-source-dependent-generation",
    )
    for marker in required_common_markers:
        if marker not in common:
            errors.append(f"site-common.js missing Study Intelligence loader marker: {marker}")

    # Provider and model selection belong exclusively to the server. The existing
    # workers.dev service hostname is a compatibility address, not a provider API.
    active_files = ("ask.html", "pioneers.html", "pioneer-experience.js", "study-intelligence-v3.js")
    for name in active_files:
        source = read_required(ROOT / name, errors)
        if re.search(r"\bmodel\s*:|\bconst\s+MODEL\s*=|api\.groq\.com|groq/compound|openai/gpt-oss", source):
            errors.append(f"{name} contains a client-owned model or retired provider dependency")
    for name in ("study-intelligence.js", "study-intelligence-v2.js"):
        if (ROOT / name).exists():
            errors.append(f"Retired Study Intelligence layer remains: {name}")

    if errors:
        print("focusChrist STUDY INTELLIGENCE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist STUDY INTELLIGENCE QA PASSED")
    print(
        "Verified active v3 grounding, display normalization, bounded browser retry, "
        "cache-versioned Ask/Pioneer loading, server-owned model selection, and retirement of unused v1/v2 layers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
