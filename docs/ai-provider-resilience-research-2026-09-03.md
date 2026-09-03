# focusChrist No-Cost AI Provider Resilience Research

Date: 2026-09-03

Purpose: identify official AI APIs that can reduce latency and quota failures without weakening Church-source verification, using unofficial endpoints, or silently adding cost.

## Decision

Use a purpose-built tandem pipeline for real-time questions:

1. Reviewed local answers first, with no network call.
2. Shared deterministic safety and scope classification.
3. Groq Compound Mini for official-source web research.
4. Cloudflare Workers AI for independent evidence verification.
5. Existing Groq 20B verifier as a one-shot operational fallback.
6. Deterministic source, source-index, substance, and known-false-claim guards before rendering.

Do not race verifiers. Racing doubles consumption and can turn a valid rejection into model shopping. Operational fallback is permitted only for a missing binding, timeout, rate limit, unavailable service, empty output, or malformed output contract.

## Provider comparison

| Candidate | Official API | Free availability | Privacy / production finding | Decision |
|---|---|---|---|---|
| Cloudflare Workers AI | Yes, native Worker binding and REST API | 10,000 neurons/day; 300 text-generation RPM | Cloudflare says customer content is not used for model training or service improvement without explicit consent; the selected Llama 3.3 70B fast model is on the official JSON Mode list | Primary verifier candidate |
| Groq | Yes, OpenAI-compatible API | Compound Mini 70K TPM; GPT-OSS verifier models 8K TPM on Free | Current provider; live 429 reproduced on the verifier | Keep research and one fallback lane |
| Duck.ai | No official developer API located | Free end-user chat | Consumer chat UI is not a production integration contract | Reject unofficial wrappers |
| OpenRouter free models | Yes | 50 requests/day and 20 RPM without purchased credits | OpenRouter says the free-model limits are usually unsuitable for production | Evaluation only |
| NVIDIA Nemotron 3 Super through OpenRouter | Yes, through OpenRouter | The `nvidia/nemotron-3-super-120b-a12b:free` endpoint is currently $0 per token but shares OpenRouter free-model limits | Supports tools and JSON-schema output, but the free endpoint logs content for NVIDIA product improvement and showed only 65.43% three-day availability when checked | Background reviewer/canary evaluation only; never a required live dependency |
| MiniMax M3 through OpenRouter | Yes, through OpenRouter | The `minimax/minimax-m3:free` endpoint is currently $0 per token, but shares OpenRouter's free-model limits | Strong long-context/coding model; free availability can vary, and OpenRouter/provider privacy controls must be configured | Offline/canary evaluation only |
| MiniMax direct API | Yes | No durable free production tier documented; M3 is pay-as-you-go or subscription | Direct production use would violate the current no-cost requirement | Reject for live path |
| DeepSeek direct API | Yes | Token-priced; granted balance is not a permanent free tier | Direct production use would require a funded balance | Reject for live path |
| Kimi direct API | Yes | Requires recharge/paid balance for durable API use | No durable zero-cost production API established | Reject for live path |
| DeepSeek/Kimi on Cloudflare | Yes, Workers AI model catalog | Some older/distilled models may fit the daily neuron allocation; current flagship variants require paid billing and Kimi K2.5 is deprecated | DeepSeek R1 Distill is substantially more neuron-expensive than GPT-OSS 20B for this compact verifier; current Kimi choices do not improve the no-cost production contract | Benchmark offline only |
| Gemini API unpaid tier | Yes | Free tier exists; exact limits vary by model/project | Google may use unpaid prompts and responses to improve products, and human reviewers may process them | Do not use as default without an explicit privacy decision |
| Cerebras | Yes | New-account trial credits expire after 30 days and require a verified payment method | Trial, not durable no-cost capacity | Evaluation only |

## Source record

- Cloudflare pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Cloudflare limits: https://developers.cloudflare.com/workers-ai/platform/limits/
- Cloudflare data usage: https://developers.cloudflare.com/workers-ai/platform/data-usage/
- Cloudflare GPT-OSS 20B: https://developers.cloudflare.com/workers-ai/models/gpt-oss-20b/
- Cloudflare Llama 3.3 70B fast: https://developers.cloudflare.com/workers-ai/models/llama-3.3-70b-instruct-fp8-fast/
- Cloudflare AI binding: https://developers.cloudflare.com/workers-ai/configuration/bindings/
- Cloudflare JSON mode: https://developers.cloudflare.com/workers-ai/features/json-mode/
- Groq rate limits: https://console.groq.com/docs/rate-limits
- Groq supported models: https://console.groq.com/docs/models
- Duck.ai help: https://duckduckgo.com/duckduckgo-help-pages/duckai
- OpenRouter limits: https://openrouter.ai/docs/api_reference/limits
- OpenRouter FAQ: https://openrouter.ai/docs/faq
- OpenRouter MiniMax M3 free endpoint: https://openrouter.ai/minimax/minimax-m3:free
- OpenRouter NVIDIA Nemotron 3 Super free endpoint: https://openrouter.ai/nvidia/nemotron-3-super-120b-a12b:free
- OpenRouter provider privacy controls: https://openrouter.ai/docs/guides/privacy/provider-logging
- MiniMax direct pricing: https://platform.minimax.io/docs/guides/pricing-paygo
- DeepSeek direct pricing: https://api-docs.deepseek.com/quick_start/pricing/
- Kimi direct limits and pricing: https://platform.moonshot.ai/docs/pricing/limits
- Cloudflare Workers AI model pricing and paid-model list: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Gemini API terms: https://ai.google.dev/gemini-api/terms
- Gemini API rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
- Cerebras account and billing: https://inference-docs.cerebras.ai/console/account-billing

## Multi-agent framework placement

CrewAI, AutoGen, and MetaGPT can organize specialized roles, but they do not supply free model inference. focusChrist already uses the valuable real-time pattern—specialized safety, research, verification, and deterministic guard roles—without framework overhead. Consider a framework only for asynchronous work such as source-index maintenance, reviewed-answer proposals, nightly regression analysis, artwork/content workflows, and Shorts production. Do not place open-ended agent conversations in the visitor's latency path.

| Framework / agent | License / cost finding | Fit for focusChrist | Decision |
|---|---|---|---|
| Microsoft Agent Framework | MIT open source; inference, hosting, and third-party tools remain separate costs | Durable workflows, checkpointing, concurrent/sequential orchestration, provider flexibility, human review, and OpenTelemetry | Best production-oriented background-framework candidate if the current purpose-built jobs outgrow simple scripts |
| CrewAI | MIT open source; requires a model provider and any search/tool credentials | Fast Python workflow prototyping with roles, flows, state, structured output, and human review | Good bounded background-work prototype candidate |
| AutoGen | MIT code, but Microsoft now states it is in maintenance mode and directs new users to Microsoft Agent Framework | No reason to begin a new long-lived system on the predecessor | Do not adopt for new focusChrist work |
| MetaGPT | MIT open source; model/API use remains separate | Optimized around software-company/product-development roles rather than Church-source editorial governance | Do not adopt as the core brain framework |
| Hermes Agent | MIT open source; still requires model and hosting capacity | General persistent personal agent with broad tools and self-authored skills | Do not place inside the site or give autonomous production access; evaluate only in an isolated sandbox if a later workflow requires it |

Nemotron 3 Super is a model rather than an agent framework. Its tool support, structured output, long context, and agent-oriented training make it a useful candidate model underneath one of those background roles. Its free OpenRouter endpoint is not acceptable as the only visitor-facing provider because free capacity can be throttled or unavailable and the endpoint's stated data-use policy permits logging for NVIDIA product improvement.

Framework sources:

- Microsoft Agent Framework: https://github.com/microsoft/agent-framework
- AutoGen maintenance notice: https://github.com/microsoft/autogen
- CrewAI: https://github.com/crewAIInc/crewAI
- MetaGPT: https://github.com/FoundationAgents/MetaGPT
- Hermes Agent: https://github.com/NousResearch/hermes-agent

Production status remains `VERIFIED FAIL` until repository CI, Worker deployment, exact policy `.26`, the 15-core and three-request burst live matrix, capacity and latency gates, and rendered visitor-path checks all pass.

Policy `.19` proved that GPT-OSS 20B could satisfy the contract on three of five live specimens, but it is not on Cloudflare's documented JSON Mode supported-model list and returned unusable output on the other two. Candidate `.20` uses Cloudflare Llama 3.3 70B fast for the primary verifier and retains Groq 20B only as the one-shot operational fallback. Acceptance requires the exact `.20` policy and at least four of five Cloudflare-primary routes.

## Policy .22 result and .23 verifier selection

Policy `.22` removed Groq research from all index-covered Church questions, but its exact 15-core production matrix passed only nine specimens. The Cloudflare Llama 3.3 70B primary intermittently crossed its bounded time window or rejected usable evidence, and the depleted Groq fallback could not recover. The index architecture is retained; the verifier is the remaining bottleneck.

Candidate `.23` uses `@cf/meta/llama-3.2-11b-vision-instruct` as the primary verifier. Cloudflare lists this exact active model ID in its JSON Mode support page and its pricing table, with 4,410 input and 61,493 output neurons per million tokens. This makes both structured-output capability and capacity receipts auditable without assuming undocumented aliases. The candidate must still pass the unchanged 15-core, three-burst, safety, source, latency, and capacity gates before promotion.

Policy `.23` failed because the 11B endpoint returned Cloudflare `service_unavailable` on the deployed indexed requests and pushed verification to Groq fallback. The run also revealed that the indexed lane mislabeled a task instruction as `DRAFT`, which could prompt a strict verifier to reject it. Candidate `.24` corrects that gateway semantics defect, restores the proven 70B JSON-mode primary with a bounded 12-second window, and reduces normal output to 500 tokens. No retrieval or integrity gate is removed.

Policy `.20` proved the Llama verifier can return strong source-indexed answers, but its 6.5-second ceiling was too tight for all complex prompts. Candidate `.21` allows 9 seconds while reserving 5 seconds for one Groq fallback. Because Groq's strict provider-side JSON enforcement itself returned `json_validate_failed`, the fallback now relies on the existing plain-JSON prompt plus the Worker's strict parser and context-aware verdict validator. Malformed fallback output still fails closed.

Policy `.24` proved the restored 70B primary could answer all 15 core requests without provider failure, while 13 passed the complete answer contract. Two approved answers were rejected by the unchanged source-overlap guard. Candidate `.25` adds a single Cloudflare-only paraphrase/depth repair under the same deadline and caps its normal output at 400 tokens. This uses the already selected no-cost verifier instead of adding a new provider, and the unchanged capacity gate must include both calls when a repair occurs.

Policy `.25` kept the provider path stable but showed that counting every ordered two-word match across a long response can falsely classify common doctrinal phrasing as source reconstruction. Candidate `.26` retains the absolute consecutive-copy limit and adds a 40 percent density requirement only to the cumulative fragmented-copy rule. This is a deterministic guard correction, not a provider change or a weaker evidence requirement.
