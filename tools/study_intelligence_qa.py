from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "study-intelligence.js"
COMMON = ROOT / "site-common.js"


def main() -> int:
    errors = []

    if not SCRIPT.exists() or SCRIPT.stat().st_size == 0:
        errors.append("study-intelligence.js missing or empty")
        script = ""
    else:
        script = SCRIPT.read_text(encoding="utf-8")

    if not COMMON.exists() or COMMON.stat().st_size == 0:
        errors.append("site-common.js missing or empty")
        common = ""
    else:
        common = COMMON.read_text(encoding="utf-8")

    required_script_markers = (
        "focusChrist shared Study Intelligence layer",
        "openai/gpt-oss-20b",
        "ANSWER QUALITY:",
        "SOURCE AND DOCTRINE DISCIPLINE:",
        "PASTORAL AND SAFETY DISCIPLINE:",
        "enhancedLocalMatch",
        "buildMessages",
        "requestOnce",
        "rememberExchange",
        "installSafeMessageRenderer",
        "installAskConversation",
        "installPioneerIntelligence",
        "Studying the question and available sources",
        "Study sources",
    )
    for marker in required_script_markers:
        if marker not in script:
            errors.append(f"study-intelligence.js missing marker: {marker}")

    forbidden_script_markers = (
        "innerHTML = text",
        "innerHTML=text",
        "temperature: 0.7",
        "max_tokens: 800",
        "Every response must end by connecting to Jesus Christ",
        "That's a great question!",
    )
    for marker in forbidden_script_markers:
        if marker in script:
            errors.append(f"study-intelligence.js contains legacy/unsafe marker: {marker}")

    required_common_markers = (
        "loadStudyIntelligence",
        "study-intelligence.js",
        "data-focuschrist-study-intelligence",
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
    print("Verified shared AI prompt discipline, semantic local matching, retry/timeouts, visible Ask continuity, safe rendering, and Ask/Pioneer loader integration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
