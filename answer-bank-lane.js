/* focusChrist reviewed answer bank lane (step 1 integration candidate).
 *
 * Wires the concurred answer bank into the Ask and Pioneer surfaces:
 *
 * - The bank is loaded once, at script load, through the matcher's
 *   fail-closed loadBank(): every record's whole-entry integrity pin is
 *   verified and any record that fails verification, review status, or
 *   data checks is excluded. The load report is published as
 *   window.FocusChristAnswerBankLoadReport for QA inspection.
 * - Step S: the matcher never evaluates a request without the site's
 *   production safety evaluator. createMatcher receives an adapter that
 *   calls window.focusChristQuestionSafety.evaluate (site-common.js),
 *   the same evaluator the current Ask and Pioneer flows use. If that
 *   evaluator is unavailable the adapter reports kind 'unavailable'
 *   and the matcher serves nothing. No allow-all double exists here.
 * - Production domain guards from reviewed-ask-knowledge.js are
 *   registered through answer-bank-guards.js (veto convention).
 * - Ask surface: answer() returns a serve, a suggestion set, or null.
 *   Null means fall through to the existing lanes unchanged. Serves
 *   carry mode 'focuschrist-answer-bank' and provenance 'reviewed-bank'
 *   exactly as the matcher builds them; this lane never sets
 *   focuschrist_source_integrity_verified.
 * - Pioneer surface: serveDisclosure() answers a timeline card
 *   expansion from the bank by stable item id (Step 0 item lookup)
 *   and renders the pinned whole entry through the card's existing
 *   disclosure container. It returns false when the bank has no item
 *   for the card, leaving the existing research path untouched.
 */
(function (global) {
    'use strict';

    var api = global.FocusChristAnswerBank;
    var data = global.FocusChristAnswerBankData;
    if (!api || !data || !Array.isArray(data.records)) {
        global.FocusChristAnswerBankLane = null;
        return;
    }

    var loaded = api.loadBank(data.records, {
        assignments: data.assignments || {},
        guards: global.FocusChristAnswerBankGuards || {}
    });

    global.FocusChristAnswerBankLoadReport = Object.freeze({
        header: data.header || null,
        loaded: loaded.report.loadedIds.length,
        excluded: loaded.report.excluded.length,
        excluded_detail: loaded.report.excluded,
        counts_by_reason: loaded.report.countsByReason
    });

    /* Step S adapter: the production evaluator, injected into the
     * matcher. The matcher treats any kind other than 'allowed' as a
     * stop, so brief-sensitive-topic, non-explicit-support,
     * respect-boundary, and urgent-safety outcomes never reach bank
     * matching, exactly as the spec requires. */
    function evaluateSafetyAdapter(request) {
        var evaluator = global.focusChristQuestionSafety;
        if (!evaluator || typeof evaluator.evaluate !== 'function') {
            return { kind: 'unavailable' };
        }
        var text = request && typeof request.question_text === 'string' ? request.question_text : '';
        var outcome = evaluator.evaluate(text);
        if (!outcome || typeof outcome.kind !== 'string') return { kind: 'unavailable' };
        return { kind: outcome.kind, profile: request ? request.profile : undefined };
    }

    var matcher = api.createMatcher(loaded.bank, { evaluateSafety: evaluateSafetyAdapter });

    function mapSources(sources) {
        var out = [];
        ['site', 'church'].forEach(function (group) {
            var list = sources && Array.isArray(sources[group]) ? sources[group] : [];
            list.forEach(function (source) {
                if (source && source.url) out.push({ text: source.label || 'Source', url: source.url });
            });
        });
        return out;
    }

    /* The pages keep history as { role, content, contextEntryId? }
     * turns; the matcher's follow-up resolution reads user turns as
     * { question, contextEntryId }. Only user turns are antecedents. */
    function toMatcherHistory(history) {
        if (!Array.isArray(history)) return [];
        return history.filter(function (turn) { return turn && turn.role === 'user'; })
            .map(function (turn) {
                return {
                    question: String(turn.content || ''),
                    contextEntryId: turn.contextEntryId || null
                };
            });
    }

    /* The single entry point for free-form questions. Every serve goes
     * through matcher.answer(), which runs Step S first (Jeff
     * J-2026-10-23-041 nit n4); the sub-APIs are never called directly
     * for a serve. Returns null on safety, no-match, and
     * generic-context outcomes so callers fall through unchanged. */
    function answer(request) {
        request = request || {};
        var result = matcher.answer({
            question_text: request.question_text || '',
            profile: request.profile || 'ask',
            page: request.page,
            item_key: request.item_key,
            context_record_id: request.context_record_id || null,
            history: toMatcherHistory(request.history)
        });
        if (result.status === 'serve') {
            var record = loaded.bank.byId.get(result.record_id);
            return {
                served: true,
                status: 'serve',
                mode: result.mode,
                provenance: result.provenance,
                layer: result.layer,
                record_id: result.record_id,
                pin: result.pin,
                canonicalQuestion: record ? record.raw.question : null,
                answer: result.answer,
                sources: mapSources(result.sources),
                entry: result.entry || null
            };
        }
        if (result.status === 'suggestion') {
            return {
                served: false,
                status: 'suggestion',
                mode: result.mode,
                reason: result.reason,
                suggestions: result.suggestions
            };
        }
        return null;
    }

    /* Pioneer timeline card disclosure: Step 0 item lookup by the
     * card's stable data-topic key, rendered into the card's existing
     * .ai-response container with the same paragraph, source-link, and
     * Collapse presentation the verified-research path uses. Church
     * source links follow the existing disclosure rule (official
     * Church hosts only). Returns true only when the bank served. */
    function serveDisclosure(control, container) {
        if (!control || !container) return false;
        var key = control.getAttribute('data-topic');
        if (!key) return false;
        var result = matcher.answer({
            page: 'pioneers',
            item_key: key,
            profile: 'pioneers',
            question_text: ''
        });
        if (!result || result.status !== 'serve' || !result.entry) return false;
        var entry = result.entry;
        container.innerHTML = '';
        String(entry.answer || '').split('\n')
            .map(function (part) { return part.trim(); })
            .filter(Boolean)
            .forEach(function (part) {
                var p = document.createElement('p');
                p.textContent = part;
                container.appendChild(p);
            });
        mapSources(result.sources).forEach(function (source) {
            var url;
            try { url = new URL(source.url); } catch (_error) { return; }
            if (url.protocol !== 'https:' || !(url.hostname === 'churchofjesuschrist.org' || url.hostname.endsWith('.churchofjesuschrist.org'))) return;
            var paragraph = document.createElement('p');
            var link = document.createElement('a');
            link.href = url.href;
            link.textContent = 'Read the source: ' + String(source.text || 'Official Church history');
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            paragraph.appendChild(link);
            container.appendChild(paragraph);
        });
        var collapse = document.createElement('button');
        collapse.type = 'button';
        collapse.className = 'pioneer-collapse-action';
        collapse.textContent = 'Collapse';
        collapse.addEventListener('click', function (event) {
            event.stopPropagation();
            container.style.display = 'none';
            var owner = container.closest('[data-focus-expand]');
            if (owner) {
                owner.classList.remove('expanded');
                owner.setAttribute('aria-expanded', 'false');
            }
        });
        container.appendChild(collapse);
        container.dataset.focuschristResearchState = 'complete';
        container.dataset.focuschristLoaded = 'reviewed-bank';
        control.setAttribute('data-focuschrist-disclosure-mode', 'reviewed-bank');
        return true;
    }

    global.FocusChristAnswerBankLane = Object.freeze({
        answer: answer,
        serveDisclosure: serveDisclosure,
        loadReport: global.FocusChristAnswerBankLoadReport
    });
})(typeof globalThis !== 'undefined' ? globalThis : this);
