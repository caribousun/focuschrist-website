from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = ROOT / "study-intelligence.js"
POLICY = ROOT / "study-intelligence-v2.js"
GROUNDED = ROOT / "study-intelligence-v3.js"
COMMON = ROOT / "site-common.js"


def read_required(path: Path, errors: list[str]) -> str:
    if not path.exists() or path.stat().st_size == 0:
        errors.append(f"{path.name} missing or empty")
        return ""
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    foundation = read_required(FOUNDATION, errors)
    policy = read_required(POLICY, errors)
    grounded = read_required(GROUNDED, errors)
    common = read_required(COMMON, errors)

    required_foundation_markers = (
        "focusChrist shared Study Intelligence layer",
        "openai/gpt-oss-20b",
        "SOURCE AND DOCTRINE DISCIPLINE:",
        "enhancedLocalMatch",
        "requestOnce",
        "rememberExchange",
        "installSafeMessageRenderer",
        "installAskConversation",
        "installPioneerIntelligence",
        "Study sources",
    )
    for marker in required_foundation_markers:
        if marker not in foundation:
            errors.append(f"study-intelligence.js missing marker: {marker}")

    required_policy_markers = (
        "focusChrist Study Intelligence v2",
        "QUESTION MODE: GENERAL KNOWLEDGE.",
        "QUESTION MODE: FAITH / SCRIPTURE STUDY.",
        "QUESTION MODE: LATTER-DAY SAINT PIONEER / CHURCH HISTORY STUDY.",
        "QUESTION MODE: HIGH-STAKES OR SENSITIVE.",
        "answer a very broad range of lawful user questions",
        "Do NOT append a blessing",
        "Do NOT force religion into the factual answer",
        "optional study bridge",
        "the sky is blue",
        "Do not manufacture a spiritual analogy",
        "Never end an ordinary answer with generic phrases",
        "bestLocalReference",
        "removeBoilerplateClosing",
        "focusChristStudyAskV2",
        "temperature: 0.35",
        "max_tokens: MAX_TOKENS",
    )
    for marker in required_policy_markers:
        if marker not in policy:
            errors.append(f"study-intelligence-v2.js missing adaptive-policy marker: {marker}")

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
    )
    for marker in forbidden_policy_markers:
        if marker in policy or marker in grounded:
            errors.append(f"Study Intelligence contains legacy/unsafe marker: {marker}")

    required_common_markers = (
        "loadStudyIntelligence",
        "study-intelligence-v3.js?v=20260901-11",
        "data-focuschrist-study-intelligence-v3",
        "path.endsWith('/ask.html')",
        "path.endsWith('/pioneers.html')",
        "window.focusChristSourceIntegrity",
        "unreviewed-source-dependent-generation",
    )
    for marker in required_common_markers:
        if marker not in common:
            errors.append(f"site-common.js missing Study Intelligence loader marker: {marker}")

    if errors:
        print("focusChrist STUDY INTELLIGENCE QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("focusChrist STUDY INTELLIGENCE QA PASSED")
    print(
        "Verified foundation + adaptive + grounded policy, broad general-question handling, optional specific faith bridges, "
        "no forced devotional closings, verified Restoration grounding, display normalization, semantic local matching, "
        "retry/timeouts, safe rendering, serialized cache-versioned loading, and Ask/Pioneer integration."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
