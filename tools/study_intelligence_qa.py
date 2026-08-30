from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = ROOT / "study-intelligence.js"
POLICY = ROOT / "study-intelligence-v2.js"
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
        "do not manufacture a spiritual analogy",
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
        if marker in policy:
            errors.append(f"study-intelligence-v2.js contains legacy/unsafe marker: {marker}")

    required_common_markers = (
        "loadStudyIntelligence",
        "study-intelligence.js?v=20260830-2",
        "study-intelligence-v2.js?v=20260830-2",
        "data-focuschrist-study-intelligence",
        "data-focuschrist-study-intelligence-v2",
        "path.endsWith('/ask.html')",
        "path.endsWith('/pioneers.html')",
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
        "Verified foundation + adaptive policy, broad general-question handling, optional specific faith bridges, "
        "no forced devotional closings, semantic local matching, retry/timeouts, safe rendering, cache-versioned loading, "
        "and Ask/Pioneer integration."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
