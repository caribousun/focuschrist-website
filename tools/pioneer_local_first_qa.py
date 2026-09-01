from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = "2026-09-01.11"
CACHE = "20260901-11"


def block(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start)) if begin >= 0 else -1
    return text[begin:finish] if begin >= 0 and finish >= 0 else ""


def main() -> int:
    errors: list[str] = []
    page = (ROOT / "pioneers.html").read_text(encoding="utf-8")
    experience = (ROOT / "pioneer-experience.js").read_text(encoding="utf-8")
    book = (ROOT / "tell-my-story-too.txt").read_text(encoding="utf-8")
    common = (ROOT / "site-common.js").read_text(encoding="utf-8")
    worker = (ROOT / "groq-proxy/src/index.js").read_text(encoding="utf-8")

    selected = block(experience, "async function answerSelectedPioneer", "function renderPioneerChoices")
    if not selected:
        errors.append("selected-person flow is missing")
    else:
        if selected.find("showLocalPioneerStory") > selected.find("requestPioneerAI"):
            errors.append("selected-person flow calls AI before rendering the local biography")
        if "if (localAnswer) return" not in selected:
            errors.append("selected-person flow does not stop after a local biography is rendered")

    disclosure = block(experience, "async function runDisclosure", "function disclosureTopic")
    if not disclosure:
        errors.append("Journey/Trail disclosure flow is missing")
    else:
        if disclosure.find("renderDisclosureAnswer(aiResponse, localAnswer)") > disclosure.find("requestPioneerAI"):
            errors.append("card disclosure calls AI before rendering reviewed local content")
        if "showLoading(" in disclosure:
            errors.append("card disclosure still contains a provider-dependent spinner")
        if "result.sourceIntegrityPassed" not in disclosure:
            errors.append("card disclosure can replace local content without verification")
        if "renderDisclosureAnswer(aiResponse, 'I could not" in disclosure:
            errors.append("card disclosure still installs a refusal after AI failure")

    send_flow = block(experience, "window.sendMessage = async function", "window.askTellMyStory")
    contextual_request = "requestPioneerAI(contextResolution.query || question, pageReference)"
    if send_flow.find("searchTellMyStory(question)") > send_flow.find(contextual_request):
        errors.append("free-form questions call AI before checking the local book")
    if "const contextResolution = resolvePioneerContext(question)" not in send_flow:
        errors.append("free-form Pioneer questions do not resolve immediate conversation context")
    if "const response = await " + contextual_request not in send_flow:
        errors.append("true local no-matches no longer reach the AI queue")

    required_markers = (
        "reviewed-local-book-entry",
        "local-reviewed-card",
        "requestIdleCallback",
        "Tell My Story, Too — ",
        "const nextStory = storyPosition >= 0 ? storyStarts[storyPosition + 1] : null",
    )
    combined = experience + "\n" + page
    for marker in required_markers:
        if marker not in combined:
            errors.append(f"missing local-first marker: {marker}")

    if "(Elizabeth Smith - Page 2)" not in book or "(Elizabeth Smith - Page 3)" not in book:
        errors.append("Elizabeth Smith continuation pages are missing from the local book")

    controls = re.findall(r'<div class="(?:timeline-item|map-point)"\s+data-focus-expand="[^"]+"[\s\S]*?<div class="ai-response"', page)
    total_controls = len(re.findall(r'data-focus-expand="(?:timeline|trail)"', page))
    if total_controls < 25:
        errors.append(f"unexpectedly low Pioneer expandable-card count: {total_controls}")
    if len(controls) != total_controls:
        errors.append(f"{total_controls - len(controls)} expandable Pioneer cards lack a response container")

    descriptions = len(re.findall(r'class="(?:timeline-desc|map-content)"', page))
    if descriptions < total_controls:
        errors.append("one or more expandable Pioneer cards lack reviewed local descriptive content")

    if f"PIONEER_POLICY_VERSION = '{POLICY}'" not in experience:
        errors.append("Pioneer browser policy is not current")
    if f"SOURCE_POLICY_VERSION = '{POLICY}'" not in worker:
        errors.append("Worker source policy is not current")
    if f"policyVersion: '{POLICY}'" not in common:
        errors.append("shared source-integrity policy is not current")
    if f"pioneer-experience.js?v={CACHE}" not in page:
        errors.append("Pioneer page cache marker is not current")
    if "known-false-source-claim" not in common or "reviewedColorPayload" not in worker:
        errors.append("known-false scripture regression protection is missing")
    if "general-ai-consensus" not in worker or "requiresExternalGeneralResearch" not in worker:
        errors.append("site-wide stable general-question fallback is missing")
    if "GENERAL_ANSWER_FALLBACK" not in worker or "general ? GENERAL_ANSWER_FALLBACK : SOURCE_INTEGRITY_FALLBACK" not in worker:
        errors.append("general failures can still be mislabeled as Gospel Library failures")

    if errors:
        print("PIONEER LOCAL-FIRST QA FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("PIONEER LOCAL-FIRST QA PASS")
    print(f"Verified policy {POLICY}, {total_controls} reviewed expandable cards, local biography precedence, multi-page continuity, verified-only AI enhancement, and true no-match AI routing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
