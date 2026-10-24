/*
 * focuschrist-answer-bank matcher (step 1 preparation build, 2026-10-23).
 *
 * Dependency-free implementation of the bank lane defined in
 * engine-spec.md Revision 2 (sections 1.2-1.6, 2.4, 3, 4), matched
 * against bank-dataset.json (the 168 reviewed records converted from
 * the reviewed markdown bank). Client-side shape: a plain script that
 * attaches `FocusChristAnswerBank` to the global object and also
 * exports through module.exports when present, so the same file runs
 * in the browser and under the Node test harness.
 *
 * Invariants this module enforces, not settings:
 *   - Step S (the site's existing safety evaluation) runs before any
 *     lookup or matching. The evaluator is INJECTED by the caller;
 *     this module contains no safety rules of its own and, with no
 *     evaluator configured, refuses to serve anything.
 *   - A record serves only if review.status is exactly "reviewed"
 *     AND its whole-entry integrity pin verifies at load
 *     (engine-spec 4.2, 2.4). Pin verification failures, unreviewed
 *     records, and records missing fields the spec requires at serve
 *     time are excluded at load and named in the load report.
 *   - Vetoes (profile, domain guard, match_none) are applied before
 *     exact and rule tests at every layer, and are never bypassed.
 *   - Layer 3 direct serves are DISABLED (spec 1.4 gating A3):
 *     LAYER3_DIRECT_SERVES_ENABLED is a hard false in this release.
 *     Layer 3 can only offer suggestions. Sensitive records are never
 *     Layer 3 candidates at all (spec 4.4, invariant S4).
 */
(function (global) {
    'use strict';

    /* ---------------- constants (spec Appendix B) ---------------- */

    var MODE = 'focuschrist-answer-bank';
    var PROVENANCE = 'reviewed-bank';
    var LAYER3_SUGGESTION_FLOOR = 0.55;   // [PROPOSAL, spec 1.4]
    var LAYER3_SERVE_BAR = 0.80;          // [PROPOSAL] inert: see below
    var LAYER3_DIRECT_SERVES_ENABLED = false; // A3 gate: hard off
    var COVERAGE_DEMOTION_THRESHOLD = 0.50;   // [PROPOSAL, spec 1.4]

    /* ------------- normalization (registry verbatim, spec 1.4) ------------- */

    function normalize(value) {
        return String(value || '')
            .toLowerCase()
            .replace(/[^a-z0-9\s'-]/g, ' ')
            .replace(/[-']/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }

    /* ---------------- sha256 (FIPS 180-4, no dependencies) ---------------- */

    function utf8Bytes(str) {
        var bytes = [];
        for (var i = 0; i < str.length; i++) {
            var code = str.charCodeAt(i);
            if (code < 0x80) {
                bytes.push(code);
            } else if (code < 0x800) {
                bytes.push(0xc0 | (code >> 6), 0x80 | (code & 0x3f));
            } else if (code >= 0xd800 && code <= 0xdbff && i + 1 < str.length) {
                var next = str.charCodeAt(i + 1);
                if (next >= 0xdc00 && next <= 0xdfff) {
                    var cp = 0x10000 + ((code - 0xd800) * 0x400) + (next - 0xdc00);
                    bytes.push(0xf0 | (cp >> 18), 0x80 | ((cp >> 12) & 0x3f),
                        0x80 | ((cp >> 6) & 0x3f), 0x80 | (cp & 0x3f));
                    i++;
                } else {
                    bytes.push(0xef, 0xbf, 0xbd); // replacement char, as encoders do
                }
            } else {
                bytes.push(0xe0 | (code >> 12), 0x80 | ((code >> 6) & 0x3f),
                    0x80 | (code & 0x3f));
            }
        }
        return bytes;
    }

    var SHA256_K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
        0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
        0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
        0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
        0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ];

    function sha256Hex(message) {
        var bytes = utf8Bytes(String(message));
        var bitLen = bytes.length * 8;
        bytes.push(0x80);
        while (bytes.length % 64 !== 56) bytes.push(0);
        var hi = Math.floor(bitLen / 0x100000000);
        var lo = bitLen >>> 0;
        bytes.push((hi >>> 24) & 0xff, (hi >>> 16) & 0xff, (hi >>> 8) & 0xff, hi & 0xff);
        bytes.push((lo >>> 24) & 0xff, (lo >>> 16) & 0xff, (lo >>> 8) & 0xff, lo & 0xff);

        var h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a;
        var h4 = 0x510e527f, h5 = 0x9b05688c, h6 = 0x1f83d9ab, h7 = 0x5be0cd19;
        var w = new Array(64);
        function rotr(x, n) { return (x >>> n) | (x << (32 - n)); }

        for (var block = 0; block < bytes.length; block += 64) {
            var t, i;
            for (t = 0; t < 16; t++) {
                var o = block + t * 4;
                w[t] = ((bytes[o] << 24) | (bytes[o + 1] << 16) |
                    (bytes[o + 2] << 8) | bytes[o + 3]) | 0;
            }
            for (t = 16; t < 64; t++) {
                var s0 = (rotr(w[t - 15], 7) ^ rotr(w[t - 15], 18) ^ (w[t - 15] >>> 3)) | 0;
                var s1 = (rotr(w[t - 2], 17) ^ rotr(w[t - 2], 19) ^ (w[t - 2] >>> 10)) | 0;
                w[t] = (w[t - 16] + s0 + w[t - 7] + s1) | 0;
            }
            var a = h0, b = h1, c = h2, d = h3, e = h4, f = h5, g = h6, h = h7;
            for (i = 0; i < 64; i++) {
                var S1 = (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) | 0;
                var ch = ((e & f) ^ (~e & g)) | 0;
                var temp1 = (h + S1 + ch + SHA256_K[i] + w[i]) | 0;
                var S0 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) | 0;
                var maj = ((a & b) ^ (a & c) ^ (b & c)) | 0;
                var temp2 = (S0 + maj) | 0;
                h = g; g = f; f = e; e = (d + temp1) | 0;
                d = c; c = b; b = a; a = (temp1 + temp2) | 0;
            }
            h0 = (h0 + a) | 0; h1 = (h1 + b) | 0; h2 = (h2 + c) | 0; h3 = (h3 + d) | 0;
            h4 = (h4 + e) | 0; h5 = (h5 + f) | 0; h6 = (h6 + g) | 0; h7 = (h7 + h) | 0;
        }
        function hex(x) { return ('00000000' + (x >>> 0).toString(16)).slice(-8); }
        return hex(h0) + hex(h1) + hex(h2) + hex(h3) + hex(h4) + hex(h5) + hex(h6) + hex(h7);
    }

    /* ------- stable stringify + whole-entry pin (spec 2.4, builder def) -------
     * The dataset builder computed each record's `integrity` as
     * "sha256:" + sha256 hex of the stable stringification of the entire
     * record EXCLUDING the integrity field itself, where stable
     * stringification is Python json.dumps(sort_keys=True,
     * separators=(",", ":"), ensure_ascii=False) encoded as UTF-8.
     * This function reproduces that definition: object keys sorted
     * recursively, arrays in order, compact separators, JSON string
     * escaping. (The current dataset is pure ASCII with no numeric
     * field values, so the Python and JS renderings coincide exactly;
     * see MODULE-REPORT.md.) */

    function stableStringify(value) {
        if (value === null || value === undefined) return 'null';
        if (Array.isArray(value)) {
            return '[' + value.map(stableStringify).join(',') + ']';
        }
        if (typeof value === 'object') {
            var keys = Object.keys(value).sort();
            var parts = [];
            for (var i = 0; i < keys.length; i++) {
                parts.push(JSON.stringify(keys[i]) + ':' + stableStringify(value[keys[i]]));
            }
            return '{' + parts.join(',') + '}';
        }
        return JSON.stringify(value);
    }

    function computePin(record) {
        var copy = {};
        var keys = Object.keys(record);
        for (var i = 0; i < keys.length; i++) {
            if (keys[i] !== 'integrity') copy[keys[i]] = record[keys[i]];
        }
        return 'sha256:' + sha256Hex(stableStringify(copy));
    }

    /* ---------------- domain guards (spec 1.4, 4.9) ----------------
     * Guards are reviewed CODE, never data. The four production guards
     * (physical-sky, joseph-smith, lds-handcart, restored-church) live
     * in the site's reviewed-ask-knowledge.js and are registered here
     * at integration from that code. This preparation module ships the
     * table empty: no bank record in the current dataset names a
     * guard, and a record naming an unregistered guard fails closed
     * at load with reason "unknown-guard". A guard function receives
     * (normalizedText, tokenSet) and returns true to VETO the record. */

    var DOMAIN_GUARDS = {};

    /* ---------------- term matching (registry hasTerm semantics) ---------------- */

    function hasTerm(normalizedText, tokenSet, normalizedTerm) {
        if (!normalizedTerm) return false;
        if (normalizedTerm.indexOf(' ') !== -1) {
            return (' ' + normalizedText + ' ').indexOf(' ' + normalizedTerm + ' ') !== -1;
        }
        return tokenSet.has(normalizedTerm);
    }

    function tokenSetOf(normalizedText) {
        if (!normalizedText) return new Set();
        return new Set(normalizedText.split(' '));
    }

    /* ---------------- bank load (fail closed, named report) ---------------- */

    var REASON = {
        MALFORMED: 'malformed-record',
        DUPLICATE_ID: 'duplicate-id',
        NOT_REVIEWED: 'not-reviewed',
        MISSING_INTEGRITY: 'missing-integrity',
        PIN_MISMATCH: 'pin-mismatch',
        MISSING_SOURCES: 'missing-sources',
        UNKNOWN_KIND: 'unknown-kind',
        MISSING_MATCH_ALL: 'missing-match_all',
        MATCH_ALL_EMPTY: 'match_all-empty',
        EMPTY_MATCH_GROUP: 'empty-match-group',
        EXACT_ONLY_ENCODING: 'exact_only-encoding',
        UNKNOWN_GUARD: 'unknown-guard',
        MISSING_PRIORITY: 'missing-priority',
        MISSING_PROFILES: 'missing-profiles',
        MISSING_ITEM_KEY: 'missing-item-key',
        MISSING_PAGE: 'missing-page',
        DUPLICATE_ITEM_KEY: 'duplicate-item-key'
    };

    function prepareRecord(raw, priority, profiles) {
        var rec = {
            id: raw.id,
            kind: raw.kind,
            raw: raw,
            priority: priority,
            profiles: profiles.slice(),
            sensitive: raw.sensitive === true,
            exactOnly: raw.exact_only === true,
            guard: (typeof raw.guard === 'string' && raw.guard) ? raw.guard : null,
            exactSet: new Set(),
            groups: [],
            noneTerms: [],
            topics: Array.isArray(raw.topics) ? raw.topics.slice() : [],
            contentWords: new Set()
        };
        if (raw.kind === 'question') {
            var exactStrings = [];
            if (typeof raw.question === 'string') exactStrings.push(raw.question);
            if (Array.isArray(raw.phrasings)) {
                for (var i = 0; i < raw.phrasings.length; i++) exactStrings.push(raw.phrasings[i]);
            }
            exactStrings.forEach(function (s) {
                var n = normalize(s);
                if (n) rec.exactSet.add(n);
            });
            rec.groups = (raw.match_all || []).map(function (group) {
                return group.map(function (term) { return normalize(term); })
                    .filter(function (t) { return t; });
            });
            rec.noneTerms = (Array.isArray(raw.match_none) ? raw.match_none : [])
                .map(function (t) { return normalize(t); })
                .filter(function (t) { return t; });
            // Layer 3 content words: tokens of question + phrasings,
            // minus a small stopword set (spec 1.4 weighted overlap).
            var stop = STOPWORDS;
            exactStrings.forEach(function (s) {
                normalize(s).split(' ').forEach(function (tok) {
                    if (tok && !stop.has(tok)) rec.contentWords.add(tok);
                });
            });
        }
        return rec;
    }

    var STOPWORDS = new Set(('a an the is are was were do does did what who whom ' +
        'why how when where which can could would should i you he she it we they ' +
        'me him her us them my your his its our their of in on at to for with ' +
        'about and or but if then than so as by from').split(' '));

    /*
     * loadBank(records, options)
     *   options.assignments: { [recordId]: { priority, profiles } } —
     *     values integration/review assigns to fields the record does
     *     not itself carry (the current dataset carries neither
     *     priority nor profiles on any record). Never defaults: a
     *     record with no value from either source is excluded with a
     *     named reason.
     *   options.guards: extra guard functions merged over DOMAIN_GUARDS.
     * Returns { bank, report } where report names every exclusion:
     * { total, loadedIds, excluded: [{id, reasons}], countsByReason }.
     */
    function loadBank(records, options) {
        options = options || {};
        var assignments = options.assignments || {};
        var guards = {};
        Object.keys(DOMAIN_GUARDS).forEach(function (k) { guards[k] = DOMAIN_GUARDS[k]; });
        if (options.guards) {
            Object.keys(options.guards).forEach(function (k) { guards[k] = options.guards[k]; });
        }
        var report = { total: 0, loadedIds: [], excluded: [], countsByReason: {} };
        function noteExclusion(id, reasons) {
            report.excluded.push({ id: id, reasons: reasons.slice() });
            reasons.forEach(function (r) {
                report.countsByReason[r] = (report.countsByReason[r] || 0) + 1;
            });
        }
        var seenIds = new Set();
        var prepared = [];
        var list = Array.isArray(records) ? records : [];
        list.forEach(function (raw) {
            report.total++;
            if (!raw || typeof raw !== 'object' || typeof raw.id !== 'string' || !raw.id) {
                noteExclusion('(no id)', [REASON.MALFORMED]);
                return;
            }
            var id = raw.id;
            if (seenIds.has(id)) { noteExclusion(id, [REASON.DUPLICATE_ID]); return; }
            seenIds.add(id);
            var reasons = [];
            if (!raw.review || raw.review.status !== 'reviewed') reasons.push(REASON.NOT_REVIEWED);
            if (typeof raw.integrity !== 'string' || !raw.integrity) reasons.push(REASON.MISSING_INTEGRITY);
            else if (computePin(raw) !== raw.integrity) reasons.push(REASON.PIN_MISMATCH);
            var sourceCount =
                (Array.isArray(raw.sources_site) ? raw.sources_site.length : 0) +
                (Array.isArray(raw.sources_church) ? raw.sources_church.length : 0);
            if (sourceCount === 0) reasons.push(REASON.MISSING_SOURCES);
            var assign = assignments[id] || {};
            var profiles = Array.isArray(raw.profiles) ? raw.profiles
                : (Array.isArray(assign.profiles) ? assign.profiles : null);
            if (!profiles) reasons.push(REASON.MISSING_PROFILES);
            var priority = null;
            if (raw.kind === 'question') {
                if (!Array.isArray(raw.match_all)) {
                    reasons.push(REASON.MISSING_MATCH_ALL);
                } else {
                    if (raw.match_all.length === 0) reasons.push(REASON.MATCH_ALL_EMPTY);
                    var sanctionedExactOnly = raw.exact_only === true &&
                        raw.match_all.length === 1 && Array.isArray(raw.match_all[0]) &&
                        raw.match_all[0].length === 0;
                    var hasEmptyGroup = raw.match_all.some(function (g) {
                        return !Array.isArray(g) || g.length === 0;
                    });
                    if (hasEmptyGroup && !sanctionedExactOnly) reasons.push(REASON.EMPTY_MATCH_GROUP);
                    if (raw.exact_only === true && !sanctionedExactOnly) reasons.push(REASON.EXACT_ONLY_ENCODING);
                }
                if (typeof raw.guard === 'string' && raw.guard && !(raw.guard in guards)) {
                    reasons.push(REASON.UNKNOWN_GUARD);
                }
                priority = (typeof raw.priority === 'number') ? raw.priority
                    : (typeof assign.priority === 'number' ? assign.priority : null);
                if (priority === null) reasons.push(REASON.MISSING_PRIORITY);
            } else if (raw.kind === 'item') {
                if (typeof raw.item_key !== 'string' || !raw.item_key) reasons.push(REASON.MISSING_ITEM_KEY);
                if (typeof raw.page !== 'string' || !raw.page) reasons.push(REASON.MISSING_PAGE);
            } else {
                reasons.push(REASON.UNKNOWN_KIND);
            }
            if (reasons.length) { noteExclusion(id, reasons); return; }
            prepared.push(prepareRecord(raw, priority, profiles));
        });
        // Item (page, item_key) uniqueness: a duplicate pair fails closed.
        var byId = new Map();
        var items = new Map();
        var itemOwner = new Map();
        prepared.forEach(function (rec) {
            if (rec.kind === 'item') {
                var key = rec.raw.page + '\u0000' + rec.raw.item_key;
                if (itemOwner.has(key)) {
                    var prev = itemOwner.get(key);
                    byId.delete(prev.id);
                    items.delete(key);
                    itemOwner.delete(key);
                    noteExclusion(prev.id, [REASON.DUPLICATE_ITEM_KEY]);
                    report.loadedIds = report.loadedIds.filter(function (x) { return x !== prev.id; });
                    noteExclusion(rec.id, [REASON.DUPLICATE_ITEM_KEY]);
                    return;
                }
                itemOwner.set(key, rec);
                items.set(key, rec);
            }
            byId.set(rec.id, rec);
            report.loadedIds.push(rec.id);
        });
        var bank = { byId: byId, items: items, guards: guards, size: byId.size };
        return { bank: bank, report: report };
    }

    /* ---------------- candidacy and vetoes (spec 1.4) ---------------- */

    function vetoReason(rec, text, tokenSet, profile, guards) {
        if (rec.profiles.indexOf(profile) === -1) return 'profile';
        if (rec.guard) {
            var g = guards[rec.guard];
            if (g && g(text, tokenSet)) return 'guard';
        }
        for (var i = 0; i < rec.noneTerms.length; i++) {
            if (hasTerm(text, tokenSet, rec.noneTerms[i])) return 'none';
        }
        return null;
    }

    function exactHit(rec, text) { return rec.exactSet.has(text); }

    function ruleHit(rec, text, tokenSet) {
        if (rec.exactOnly) return false; // the [[]] group can never be satisfied
        return rec.groups.every(function (group) {
            return group.some(function (term) { return hasTerm(text, tokenSet, term); });
        });
    }

    function coverageOf(rec, text, tokenSet) {
        if (tokenSet.size === 0) return 0;
        var consumed = new Set();
        rec.groups.forEach(function (group) {
            group.forEach(function (term) {
                if (hasTerm(text, tokenSet, term)) {
                    term.split(' ').forEach(function (tok) { consumed.add(tok); });
                }
            });
        });
        var n = 0;
        consumed.forEach(function (tok) { if (tokenSet.has(tok)) n++; });
        return n / tokenSet.size;
    }

    function topPriority(records) {
        var best = null;
        records.forEach(function (r) { if (best === null || r.priority > best) best = r.priority; });
        return records.filter(function (r) { return r.priority === best; });
    }

    /* ---------------- serve / suggestion results ---------------- */

    function serveResult(rec, layer, extra) {
        var result = {
            status: 'serve',
            mode: MODE,
            provenance: PROVENANCE,
            layer: layer,
            record_id: rec.id,
            pin: rec.raw.integrity,
            answer: rec.raw.answer,
            sources: {
                site: Array.isArray(rec.raw.sources_site) ? rec.raw.sources_site : [],
                church: Array.isArray(rec.raw.sources_church) ? rec.raw.sources_church : []
            }
        };
        if (extra) Object.keys(extra).forEach(function (k) { result[k] = extra[k]; });
        return result;
    }

    function suggestionResult(reason, entries) {
        return {
            status: 'suggestion',
            mode: MODE,
            reason: reason,
            suggestions: entries.map(function (e) {
                var s = { record_id: e.rec.id, question: e.rec.raw.question };
                if (typeof e.score === 'number') s.score = e.score;
                return s;
            })
        };
    }

    /* ---------------- Layer 3 (gated, suggestion-only) ---------------- */

    function layer3Candidates(bank, text, tokenSet, profile, excludeIds) {
        var scored = [];
        bank.byId.forEach(function (rec) {
            if (rec.kind !== 'question') return;
            if (rec.sensitive) return;      // invariant S4: never a candidate
            if (rec.exactOnly) return;      // never a scored candidate (spec 1.4)
            if (excludeIds && excludeIds.has(rec.id)) return;
            if (vetoReason(rec, text, tokenSet, profile, bank.guards)) return;
            if (ruleHit(rec, text, tokenSet)) return; // Layer 3 is for rule failures
            var sharedTopics = 0;
            rec.topics.forEach(function (tag) {
                var words = String(tag).split('-');
                var all = words.every(function (w) { return tokenSet.has(w); });
                if (all && words.length) sharedTopics++;
            });
            var sharedWords = 0;
            rec.contentWords.forEach(function (w) { if (tokenSet.has(w)) sharedWords++; });
            var possible = 3 * rec.topics.length + rec.contentWords.size;
            if (possible === 0) return;
            var score = (3 * sharedTopics + sharedWords) / possible;
            if (score >= LAYER3_SUGGESTION_FLOOR) scored.push({ rec: rec, score: score });
        });
        scored.sort(function (a, b) {
            if (b.score !== a.score) return b.score - a.score;
            return b.rec.priority - a.rec.priority;
        });
        return scored.slice(0, 3);
    }

    /* ---------------- text matching: Layers 1 and 2 ---------------- */

    function matchQuestion(bank, questionText, profile) {
        var text = normalize(questionText);
        var tokenSet = tokenSetOf(text);
        var exactCands = [];
        var ruleCands = [];
        bank.byId.forEach(function (rec) {
            if (rec.kind !== 'question') return;
            if (vetoReason(rec, text, tokenSet, profile, bank.guards)) return;
            if (exactHit(rec, text)) exactCands.push(rec);
            else if (ruleHit(rec, text, tokenSet)) ruleCands.push(rec);
        });
        if (exactCands.length) {
            var top = topPriority(exactCands);
            if (top.length === 1) return serveResult(top[0], 'exact');
            return suggestionResult('exact-tie', top.map(function (r) { return { rec: r }; }));
        }
        if (ruleCands.length) {
            var winners = topPriority(ruleCands);
            if (winners.length > 1) {
                return suggestionResult('priority-tie', winners.map(function (r) { return { rec: r }; }));
            }
            var winner = winners[0];
            var cov = coverageOf(winner, text, tokenSet);
            if (cov < COVERAGE_DEMOTION_THRESHOLD) {
                var entries = [{ rec: winner }];
                layer3Candidates(bank, text, tokenSet, profile, new Set([winner.id]))
                    .forEach(function (e) { entries.push(e); });
                return suggestionResult('coverage-demotion', entries.slice(0, 3));
            }
            return serveResult(winner, 'rule', { coverage: cov });
        }
        var l3 = layer3Candidates(bank, text, tokenSet, profile, null);
        if (l3.length) return suggestionResult('layer3', l3);
        return { status: 'no-match', mode: MODE };
    }

    /* ---------------- Step 0: item lookup (spec 1.3) ---------------- */

    function lookupItem(bank, page, itemKey, profile) {
        var rec = bank.items.get(page + '\u0000' + itemKey);
        if (!rec) return { status: 'no-match', mode: MODE, miss_kind: 'item-uncovered' };
        if (rec.profiles.indexOf(profile) === -1) {
            return { status: 'no-match', mode: MODE, miss_kind: 'item-uncovered' };
        }
        // Serve the pinned whole entry: the full record travels with
        // the result so the page renders exactly the reviewed entry.
        return serveResult(rec, 'item', { entry: rec.raw });
    }

    /* ---------------- follow-ups (spec 3, as far as the data supports) ---------------- */

    var GENERIC_ELLIPSIS = new Set([
        'what time', 'and what time', 'when exactly', 'what date',
        'what year', 'where exactly', 'why exactly', 'how exactly', 'who exactly'
    ]);
    var REFERENTIAL = new Set(('it its that this they them he she him her his hers ' +
        'their those these').split(' '));
    var ELLIPSIS_STARTERS = new Set(['and', 'what', 'when', 'where', 'how', 'do', 'did', 'was', 'is', 'about']);

    function isScriptureSupport(text, tokenSet) {
        if (!(tokenSet.has('scripture') || tokenSet.has('verse') || tokenSet.has('verses'))) return false;
        var cues = ['cite', 'show', 'give', 'quote', 'support', 'supporting', 'please', 'can'];
        return cues.some(function (c) { return tokenSet.has(c); });
    }

    function isFollowUpShaped(text, tokenSet) {
        var tokens = text ? text.split(' ') : [];
        var referential = tokens.some(function (t) { return REFERENTIAL.has(t); });
        var elliptical = tokens.length > 0 && tokens.length <= 8 && ELLIPSIS_STARTERS.has(tokens[0]);
        return referential || elliptical || isScriptureSupport(text, tokenSet);
    }

    function antecedentOf(bank, contextRecordId, history) {
        if (contextRecordId && bank.byId.has(contextRecordId)) return bank.byId.get(contextRecordId);
        if (Array.isArray(history)) {
            for (var i = history.length - 1; i >= 0; i--) {
                var turn = history[i];
                if (turn && turn.contextEntryId && bank.byId.has(turn.contextEntryId)) {
                    return bank.byId.get(turn.contextEntryId);
                }
            }
        }
        return null;
    }

    function variantMatches(variant, text, tokenSet) {
        var intent = variant.intent || {};
        var none = Array.isArray(intent.none) ? intent.none : [];
        for (var i = 0; i < none.length; i++) {
            if (hasTerm(text, tokenSet, normalize(none[i]))) return false;
        }
        var all = Array.isArray(intent.all) ? intent.all : [];
        return all.every(function (group) {
            return (Array.isArray(group) ? group : [group]).some(function (term) {
                return hasTerm(text, tokenSet, normalize(term));
            });
        });
    }

    /*
     * resolveFollowUp(questionText, { profile, contextRecordId, history })
     * Spec 3.1 order: a direct serve always stands on its own; then a
     * context record carrying a registry-shaped followup block may
     * claim the follow-up (cues / block / ellipsis / anchor re-test /
     * variants, with the data-driven part of the competing-subject
     * veto); a remaining follow-up-shaped question resolves
     * generically to the live path and is never a bank serve.
     * No record in the current dataset carries a followup block, so
     * in practice this resolves direct serves and generic fallbacks;
     * the block path is implemented and fixture-tested for the
     * records that will carry one.
     */
    function resolveFollowUp(bank, questionText, options) {
        options = options || {};
        var profile = options.profile;
        var direct = matchQuestion(bank, questionText, profile);
        if (direct.status === 'serve') {
            return { recordId: direct.record_id, resolved: false, via: 'direct', result: direct };
        }
        var text = normalize(questionText);
        var tokenSet = tokenSetOf(text);
        var prior = antecedentOf(bank, options.contextRecordId, options.history);
        if (prior && prior.raw.followup && typeof prior.raw.followup === 'object') {
            var block = prior.raw.followup;
            var antecedentText = '';
            if (Array.isArray(options.history)) {
                for (var i = options.history.length - 1; i >= 0; i--) {
                    if (options.history[i] && options.history[i].question) {
                        antecedentText = normalize(options.history[i].question);
                        break;
                    }
                }
            }
            var anteTokens = tokenSetOf(antecedentText);
            var cancelled = false;
            // Competing-subject veto, data-driven part: a term from the
            // prior record's block list or match_none list that appears
            // in the follow-up but was not part of the antecedent.
            var vetoTerms = (Array.isArray(block.block) ? block.block : []).concat(prior.noneTerms);
            for (var v = 0; v < vetoTerms.length; v++) {
                var vt = normalize(vetoTerms[v]);
                if (vt && hasTerm(text, tokenSet, vt) && !hasTerm(antecedentText, anteTokens, vt)) {
                    cancelled = true;
                    break;
                }
            }
            if (!cancelled) {
                var blockHit = (Array.isArray(block.block) ? block.block : []).some(function (t) {
                    return hasTerm(text, tokenSet, normalize(t));
                });
                var cueHit = (Array.isArray(block.cues) ? block.cues : []).some(function (t) {
                    return hasTerm(text, tokenSet, normalize(t));
                });
                var subjectless = !Array.from(tokenSet).some(function (t) {
                    return !ELLIPSIS_STARTERS.has(t) && !REFERENTIAL.has(t);
                });
                var ellipsisOk = false;
                if (subjectless) {
                    var declared = (Array.isArray(block.ellipsis) ? block.ellipsis : [])
                        .map(function (s) { return normalize(s); });
                    ellipsisOk = declared.indexOf(text) !== -1 || GENERIC_ELLIPSIS.has(text);
                }
                if (!blockHit && (cueHit || ellipsisOk)) {
                    var appended = normalize(questionText + ' ' + (block.anchor || ''));
                    var aTokens = tokenSetOf(appended);
                    var passes = !vetoReason(prior, appended, aTokens, profile, bank.guards) &&
                        (exactHit(prior, appended) || ruleHit(prior, appended, aTokens));
                    if (passes) {
                        var variants = Array.isArray(block.variants) ? block.variants : [];
                        for (var j = 0; j < variants.length; j++) {
                            if (variantMatches(variants[j], text, tokenSet)) {
                                return {
                                    recordId: prior.id,
                                    variantId: variants[j].id || null,
                                    resolved: true,
                                    via: 'followup-variant',
                                    result: {
                                        status: 'serve',
                                        mode: MODE,
                                        provenance: PROVENANCE,
                                        layer: 'followup-variant',
                                        record_id: prior.id,
                                        variant_id: variants[j].id || null,
                                        pin: prior.raw.integrity,
                                        answer: variants[j].answer,
                                        sources: variants[j].sources || { site: [], church: [] }
                                    }
                                };
                            }
                        }
                        return { recordId: prior.id, resolved: true, via: 'followup-context', result: serveResult(prior, 'followup') };
                    }
                }
            }
        }
        // Generic resolution needs a conversation to resolve against:
        // a prior bank record, or at least a preceding user turn. A
        // follow-up-shaped FIRST question has no antecedent and is
        // simply a miss (it falls through like any other no-match).
        var hasConversation = !!prior ||
            (Array.isArray(options.history) && options.history.length > 0);
        if (hasConversation && isFollowUpShaped(text, tokenSet)) {
            return {
                recordId: null,
                resolved: false,
                genericContext: true,
                contextRecordId: prior ? prior.id : null
            };
        }
        return { recordId: null, resolved: false, genericContext: false };
    }

    /* Chips: a served record's reviewed `related` links (spec 3.5).
     * Targets that are not loaded (retired, excluded, dangling)
     * degrade silently here; a tap on a rendered chip submits the
     * canonical question as a new request through Step S and the
     * vetoed exact path, exactly like typed text. */
    function followUpChips(bank, recordId) {
        var rec = bank.byId.get(recordId);
        if (!rec || !Array.isArray(rec.raw.related)) return [];
        var chips = [];
        rec.raw.related.forEach(function (targetId) {
            var target = bank.byId.get(targetId);
            if (target && target.kind === 'question') {
                chips.push({ record_id: target.id, question: target.raw.question });
            }
        });
        return chips;
    }

    /* ---------------- the orchestrated answer flow ----------------
     * Step S -> Step 0 item lookup -> Layers 1/2 -> Layer 3
     * suggestions -> follow-up generic resolution -> no-match.
     * evaluateSafety is the site's own evaluator, injected:
     *   options.evaluateSafety(request) -> { kind, profile? }
     * with kind one of "allowed", "urgent-safety", "respect-boundary",
     * "non-explicit-support", "brief-sensitive-topic". Any kind other
     * than "allowed" ends bank processing for the request (spec 1.2:
     * support requests bypass bank matching entirely; the rest are
     * the evaluator's own responses). With no evaluator configured
     * the matcher serves nothing: Step S is not this module's to
     * invent, and its absence is a configuration error, not a pass. */

    function createMatcher(bank, options) {
        options = options || {};
        var evaluateSafety = (typeof options.evaluateSafety === 'function')
            ? options.evaluateSafety
            : function () { return { kind: 'unavailable' }; };

        function answer(request) {
            request = request || {};
            var safety = evaluateSafety(request);
            if (!safety || safety.kind !== 'allowed') {
                return { status: 'safety', mode: MODE, kind: safety ? safety.kind : 'unavailable' };
            }
            var profile = safety.profile || request.profile;
            if (request.item_key) {
                return lookupItem(bank, request.page, request.item_key, profile);
            }
            var direct = matchQuestion(bank, request.question_text || '', profile);
            if (direct.status !== 'no-match') return direct;
            var fu = resolveFollowUp(bank, request.question_text || '', {
                profile: profile,
                contextRecordId: request.context_record_id || null,
                history: request.history || []
            });
            if (fu.genericContext) {
                return {
                    status: 'generic-context',
                    mode: MODE,
                    contextRecordId: fu.contextRecordId
                };
            }
            return direct;
        }

        return {
            answer: answer,
            matchQuestion: function (q, profile) { return matchQuestion(bank, q, profile); },
            lookupItem: function (page, itemKey, profile) { return lookupItem(bank, page, itemKey, profile); },
            resolveFollowUp: function (q, opts) { return resolveFollowUp(bank, q, opts || {}); },
            followUpChips: function (recordId) { return followUpChips(bank, recordId); },
            layer3Candidates: function (q, profile) {
                var text = normalize(q);
                return layer3Candidates(bank, text, tokenSetOf(text), profile, null);
            },
            bank: bank
        };
    }

    var api = {
        MODE: MODE,
        PROVENANCE: PROVENANCE,
        LAYER3_SUGGESTION_FLOOR: LAYER3_SUGGESTION_FLOOR,
        LAYER3_SERVE_BAR: LAYER3_SERVE_BAR,
        LAYER3_DIRECT_SERVES_ENABLED: LAYER3_DIRECT_SERVES_ENABLED,
        COVERAGE_DEMOTION_THRESHOLD: COVERAGE_DEMOTION_THRESHOLD,
        GENERIC_ELLIPSIS: GENERIC_ELLIPSIS,
        REASON: REASON,
        DOMAIN_GUARDS: DOMAIN_GUARDS,
        normalize: normalize,
        sha256Hex: sha256Hex,
        stableStringify: stableStringify,
        computePin: computePin,
        loadBank: loadBank,
        createMatcher: createMatcher
    };

    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    global.FocusChristAnswerBank = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
