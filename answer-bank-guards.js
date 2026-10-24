/* focusChrist answer bank: production domain guards (step 1 integration).
 *
 * The four guard functions below are the production domain guards copied
 * verbatim from the reviewed registry: reviewed-ask-knowledge.js,
 * DOMAIN_GUARDS (registry lines 1204-1229 at the candidate base head).
 * In the registry a guard returns true to ALLOW its entry to match.
 *
 * The answer bank matcher (answer-bank-matcher.js) uses the opposite
 * convention: its guard table functions receive (normalizedText,
 * tokenSet) and return true to VETO the record. The table exported at
 * the bottom of this file therefore negates each registry guard, so the
 * bank applies exactly the production guard logic with the matcher's
 * boolean sense. Guard parity with the registry is covered by the
 * integration gate tests; no guard logic is added, removed, or altered.
 */
(function (global) {
    'use strict';

    /* Begin verbatim registry logic (allow semantics), from
     * reviewed-ask-knowledge.js DOMAIN_GUARDS. */
    var ALLOW = {
        'physical-sky': function (query) {
            return !/\b(?:song|music|album|book|movie|film|poem|painting|artwork|design)\b/.test(query);
        },
        'joseph-smith': function (query) {
            if (/\b(?:after|before|following|since)\s+(?:the\s+)?(?:death|martyrdom|murder|joseph)\b/.test(query)) return false;
            if (/\bjoseph the prophet\b/.test(query)) return true;
            const explicit = query.match(/\bjoseph smith(?:\s+(\w+))?/);
            if (explicit) {
                if (explicit[1] === 'the') return /\bjoseph smith the prophet\b/.test(query);
                return !explicit[1] || ['jr', 'junior', 'was', 'is', 'did', 'die', 'died', 'death', 'killed', 'martyred', 'martyrdom', 'murdered', 'get', 'got', 'imprisoned', 'held', 'detained', 'at', 'in'].includes(explicit[1]);
            }
            const bare = query.match(/\bjoseph(?:\s+(\w+))?/);
            if (!bare) return false;
            return !bare[1] || ['was', 'is', 'did', 'die', 'died', 'death', 'killed', 'martyred', 'martyrdom', 'murdered', 'get', 'got'].includes(bare[1]);
        },
        'lds-handcart': function (query) {
            if (/\b(?:my|our|she|her|he|his|ancestor|grandmother|grandfather|food|ration|rations|short|shortage|shortages|diet|meal|meals)\b/.test(query)) return false;
            return !/\b(?:amusement park|race|racing|shopping|grocery|patent|video game|game)\b/.test(query);
        },
        'restored-church': function (query) {
            const namedChurch = query.match(/\bchurch of\s+(\w+)/);
            return !namedChurch || ['christ', 'jesus'].includes(namedChurch[1]);
        }
    };
    /* End verbatim registry logic. */

    var VETO = {};
    Object.keys(ALLOW).forEach(function (name) {
        VETO[name] = function (normalizedText) { return !ALLOW[name](normalizedText); };
    });

    global.FocusChristAnswerBankGuards = Object.freeze(VETO);
})(typeof globalThis !== 'undefined' ? globalThis : this);
