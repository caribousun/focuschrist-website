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

    /* Follow-up chips for a served record (spec 3.5; addendum
     * pattern P1, primary plus related): the served record's reviewed
     * `related` targets as canonical questions, in the record's own
     * order, taken only from the matcher's followUpChips() over the
     * pinned loaded bank, so a target the load excluded never
     * appears. A sensitive record's own serve returns its chips
     * like any other serve: spec 4.4's stated interactions are
     * exhaustive and remove no adjunct from the served record
     * itself, and the addendum's sensitive exclusion (2.3 rule 3)
     * is scoped to answer components, barring a sensitive record
     * from another artifact's composition, not from its own P1
     * adjunct. A sensitive record's canonical question may also
     * appear as a chip target in other records' lists (spec 4.4),
     * where a tap is the visitor's deliberate new request through
     * Step S. The list is capped at five, the top of the range
     * spec 3.5 drafts `related` lists in (typically 2 to 5); the
     * shipped bank's longest list is four, so the cap binds
     * nothing today and bounds future data. */
    var FOLLOW_UP_CHIP_LIMIT = 5;
    function followUpChips(recordId) {
        if (typeof recordId !== 'string' || !recordId) return [];
        var record = loaded.bank.byId.get(recordId);
        if (!record) return [];
        return matcher.followUpChips(recordId).slice(0, FOLLOW_UP_CHIP_LIMIT);
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

    /* Display-gate binding for reviewed-bank serves: the gate in
     * site-common.js exempts a marked serve from the scripture check
     * only when this function confirms, against the loaded pin-checked
     * bank, that the claimed record id, whole-entry pin, exact answer
     * text, and sources are a genuine serve of the current bank. A
     * record the load excluded or never carried, a wrong pin, or any
     * edit to the answer or its sources fails the binding. Variant
     * serves (a record's followup block, inside the same pinned whole
     * entry) verify against their variant's answer and sources. */
    function verifyPinnedServe(claim) {
        if (!claim || typeof claim !== 'object') return false;
        if (typeof claim.record_id !== 'string' || !claim.record_id) return false;
        if (typeof claim.pin !== 'string' || !claim.pin) return false;
        if (typeof claim.answer !== 'string') return false;
        var record = loaded.bank.byId.get(claim.record_id);
        if (!record || !record.raw) return false;
        if (claim.pin !== record.raw.integrity) return false;
        var candidates = [{
            answer: record.raw.answer,
            sources: {
                site: Array.isArray(record.raw.sources_site) ? record.raw.sources_site : [],
                church: Array.isArray(record.raw.sources_church) ? record.raw.sources_church : []
            }
        }];
        var block = record.raw.followup;
        if (block && Array.isArray(block.variants)) {
            block.variants.forEach(function (variant) {
                candidates.push({
                    answer: variant.answer,
                    sources: variant.sources || { site: [], church: [] }
                });
            });
        }
        var actual = Array.isArray(claim.sources) ? claim.sources : null;
        if (!actual) return false;
        return candidates.some(function (candidate) {
            if (claim.answer !== candidate.answer) return false;
            var expected = mapSources(candidate.sources);
            if (actual.length !== expected.length) return false;
            for (var i = 0; i < expected.length; i++) {
                if (!actual[i] || actual[i].text !== expected[i].text || actual[i].url !== expected[i].url) return false;
            }
            return true;
        });
    }

    global.FocusChristAnswerBankLane = Object.freeze({
        answer: answer,
        followUpChips: followUpChips,
        serveDisclosure: serveDisclosure,
        verifyPinnedServe: verifyPinnedServe,
        loadReport: global.FocusChristAnswerBankLoadReport
    });
})(typeof globalThis !== 'undefined' ? globalThis : this);
