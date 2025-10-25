# Literature Review Scenario Walkthrough

This walkthrough demonstrates the nudge middleware in action during a realistic academic literature review session.

## Scenario: PhD Student Literature Review

**Researcher**: PhD student in computer science
**Topic**: Explainable AI in healthcare (dissertation background section)
**Goal**: Survey current approaches, identify gaps, prepare for original research
**Time constraint**: Need comprehensive review in 2-3 days

---

## Session Timeline

### [09:00] Session Start - SCOPING STAGE

**Initial Prompt from Researcher**:
> "I need to do a literature review on explainable AI in healthcare for my dissertation. I'm not sure exactly how to scope this yet – it's a huge area."

**Grounding Box Initialized**:
```
┌─ RESEARCH GROUNDING ─────────────────────────────────────┐
│ Question: What is the state of explainable AI in healthcare?
│ Stage: scoping (1/4) — 0 papers, 0 databases
│ Assumptions: none
│ Open Questions:
│   • Which healthcare domains to focus on?
│   • Include research tools or only clinical applications?
│   • How recent? (XAI is rapidly evolving)
│ Next: agent → explore terminology variations by 10am
└───────────────────────────────────────────────────────────┘
```

**Agent Response**:
> "Let's start by understanding the landscape. Before searching, I need to clarify a few things:
>
> 1. **Healthcare scope**: Are you interested in clinical applications (diagnosis, treatment, decision support) or broader (including research lab tools, drug discovery)?
> 2. **XAI definition**: Are you using 'explainable' broadly (interpretability, transparency) or narrowly (post-hoc explanations)?
> 3. **Time frame**: XAI in healthcare really emerged around 2017-2018. Should we focus on recent work (2020+) or comprehensive coverage?"

**Researcher Input**:
> "I'm specifically interested in clinical decision support systems where doctors interact with AI recommendations. Recent work is most relevant – let's say 2020 onwards."

**Turn Receipt**:
```
[09:15] Researcher clarified scope: clinical decision support, 2020+
→ Refined research question
→ Added initial assumptions
→ Resolved 2 open questions
→ Next: Plan first database search
```

**Updated Grounding Box**:
```
┌─ RESEARCH GROUNDING ─────────────────────────────────────┐
Δ Question: What approaches exist for XAI in clinical decision support systems?
Δ Stage: scoping → retrieval (2/4) — 0 papers, 0 databases
Δ Assumptions:
│   • Clinical applications only (excluded research lab tools)
│   • 2020-present (focus on recent approaches)
Δ Open Questions:
│   • Include both diagnosis and treatment recommendations?
Δ Next: agent → search SemanticScholar by 10am
└───────────────────────────────────────────────────────────┘
```

---

### [09:20] First Search - RETRIEVAL STAGE BEGINS

**Search Plan Gate** (agent presents plan):

```
┌─ SEARCH PLAN ────────────────────────────────────────────┐
│ Database: Semantic Scholar                               │
│ Query: "explainable AI clinical decision support"        │
│ Filters:                                                  │
│   • Year: 2020-present                                   │
│   • Fields: Medicine, Computer Science                   │
│   • Minimum citations: none (exploratory)                │
│                                                           │
│ Rationale:                                                │
│ Starting with Semantic Scholar because it has excellent  │
│ interdisciplinary coverage of medicine + CS, good        │
│ metadata quality, and comprehensive citation data.       │
│                                                           │
│ Expected Results: 30-80 papers (mix of methods,          │
│ applications, surveys)                                    │
│                                                           │
│ Cost/Time: 1 API call, ~2 seconds                        │
│                                                           │
│ Alternative: Could start with PubMed for clinical focus, │
│ but would miss CS systems/HCI perspectives.              │
└───────────────────────────────────────────────────────────┘

OPTIONS:
[OK] Proceed with full search
[Short Run] Preview top 10 results first
[Modify] Adjust query/filters
[Cancel] Skip this search
```

**Researcher**: Clicks [OK]

**Search Execution** → **Results: 34 papers found**

**Turn Receipt**:
```
[09:21] Searched SemanticScholar: "explainable AI clinical decision support" (2020+)
→ Found 34 papers (8 surveys, 14 methods, 12 applications)
→ Good coverage of recent work, mix of CS and medical venues
→ Added to grounding: papers found, database searched
→ Next: Search arXiv for very recent preprints
⚠️ Most papers focus on post-hoc explanations – few on intrinsic interpretability
```

**Updated Grounding Box**:
```
┌─ RESEARCH GROUNDING ─────────────────────────────────────┐
│ Question: What approaches exist for XAI in clinical decision support systems?
Δ Stage: retrieval (2/4) — 34 papers, 1 database
│ Assumptions:
│   • Clinical applications only
│   • 2020-present
Δ Open Questions:
│   • Include intrinsic interpretability (not just post-hoc)?
│   • Missing very recent work (2024)?
Δ Next: agent → search arXiv for recent preprints by 11am
└───────────────────────────────────────────────────────────┘
```

---

### [09:25] Second Search - arXiv

**Search Plan Gate**:

```
┌─ SEARCH PLAN ────────────────────────────────────────────┐
│ Database: arXiv                                           │
│ Query: "explainable AI clinical" OR "interpretable ML    │
│        medical diagnosis"                                 │
│ Filters:                                                  │
│   • Category: cs.AI, cs.LG, cs.HC                        │
│   • Submitted: 2023-2024 (very recent)                   │
│                                                           │
│ Rationale:                                                │
│ arXiv will catch cutting-edge work not yet in journals.  │
│ Broadening to "interpretable" since initial results      │
│ showed post-hoc bias.                                     │
│                                                           │
│ Expected Results: 15-30 preprints                         │
│                                                           │
│ Cost/Time: 1 API call, ~2 seconds                        │
│                                                           │
│ Alternative: Could wait and only search arXiv if gaps    │
│ found later, but preprints show latest trends.           │
└───────────────────────────────────────────────────────────┘

OPTIONS:
[OK] Proceed    [Short Run] Preview    [Modify] Adjust    [Cancel] Skip
```

**Researcher**: Clicks [Short Run] (wants to preview first)

**Short Run Execution** → **Top 10 results shown**

Sample results preview:
```
1. "SHAP-based Clinical Decision Support..." (2024, cs.AI)
2. "Attention Mechanisms for Interpretable Diagnosis..." (2024, cs.LG)
3. "Physician Trust in AI Explanations..." (2023, cs.HC)
...
```

**Agent Follow-up**:
> "Preview shows good mix: technical methods (SHAP, attention), HCI perspective (physician trust), recent 2023-2024 work. Proceed with full search?"

**Researcher**: "Yes, looks relevant"

**Full Search** → **18 papers found**

**Turn Receipt**:
```
[09:28] Searched arXiv: "explainable|interpretable" + "clinical" (2023-2024)
→ Found 18 preprints (5 cs.AI, 8 cs.LG, 5 cs.HC)
→ Excellent HCI coverage (physician interaction with explanations)
→ Papers: 34 → 52 total
→ Next: Search ACM for HCI perspectives
⚠️ Preprints not peer-reviewed – verify claims if citing
```

---

### [09:35] Third Search - ACM Digital Library

**Search Plan** (abbreviated):
```
Database: ACM Digital Library
Query: "explainable AI healthcare" OR "interpretable medical AI"
Filters: CHI, IUI, CSCW conferences + AI in Medicine journals, 2020+
Rationale: Get HCI/system design perspectives on how clinicians use XAI
Expected: 12-20 papers
```

**Researcher**: [OK]

**Search Execution** → **PROBLEM: Only 3 papers found (unexpectedly low)**

**Search Failure Detection** → **Classified as: DATABASE_COVERAGE_GAP**

**Targeted Help Response**:

```
┌─ SEARCH HELP ────────────────────────────────────────────┐
│ Only 3 papers found in ACM – this seems low given topic. │
│                                                           │
│ Possible reasons:                                         │
│ • ACM has strong CS coverage but weaker medical focus    │
│ • Clinical decision support may be in medical venues     │
│   (not indexed by ACM)                                    │
│ • HCI venues (CHI, IUI) may use different terminology    │
│   (e.g., "AI transparency", "algorithmic explainability")│
│                                                           │
│ READY-TO-CLICK ACTIONS:                                  │
│ → [Try Synonyms] "AI transparency" OR "algorithmic       │
│   explainability" in CHI/IUI venues                      │
│ → [Different Database] Search IEEE for medical           │
│   informatics perspectives                               │
│ → [Broaden Query] Remove "clinical" (just "XAI           │
│   healthcare")                                            │
│ → [Accept Limited] Continue with 3 papers, note ACM gap  │
│                                                           │
│ Recommendation: Try synonyms first (HCI uses different   │
│ terminology), then note coverage limitation.             │
└───────────────────────────────────────────────────────────┘
```

**Researcher**: Clicks [Try Synonyms]

**Refined Search**: "AI transparency healthcare" OR "algorithmic explainability clinical"

**Results**: **11 more papers found** (14 total from ACM)

**Turn Receipt**:
```
[09:40] Searched ACM: refined with "transparency|explainability" terminology
→ Found 11 additional papers (14 total from ACM)
→ Terminology matters! HCI community uses different terms
→ Papers: 52 → 63 total
→ Added assumption: "Terminology variation across disciplines"
→ Next: Search PubMed for clinical/medical perspectives
⚠️ Note: ACM still light on medical venues – need clinical database
```

**Updated Grounding Box**:
```
┌─ RESEARCH GROUNDING ─────────────────────────────────────┐
│ Question: What approaches exist for XAI in clinical decision support systems?
│ Stage: retrieval (2/4) — 63 papers, 3 databases
Δ Assumptions:
│   • Clinical applications only
│   • 2020-present
│   • "Explainable" includes transparency/interpretability/algorithmic explanations
│ Open Questions:
│   • Missing clinical/medical venue perspectives?
Δ Next: agent → search PubMed by 12pm
└───────────────────────────────────────────────────────────┘
```

---

### [10:00] Fourth Search - PubMed (Medical Perspective)

**Search Plan**:
```
Database: PubMed (medical literature)
Query: "explainable artificial intelligence" AND "clinical decision support"
Filters: 2020+, Review OR Clinical Trial OR Journal Article
Rationale: Get clinical/medical perspectives, physician viewpoints, real-world deployments
Expected: 10-25 papers (more conservative medical publication)
```

**Researcher**: [OK]

**Search Execution** → **16 papers found**

**Turn Receipt**:
```
[10:02] Searched PubMed: medical literature on XAI in clinical settings
→ Found 16 papers (4 systematic reviews, 7 clinical trials, 5 perspectives)
→ Excellent clinical viewpoint coverage
→ Papers: 63 → 79 total
→ Many focus on regulatory/ethical aspects (not just technical)
→ Next: Validate coverage and synthesize themes
⚠️ Some overlap with SemanticScholar (same papers, different indexing)
```

---

### [10:15] Coverage Validation Check

**Agent Proactive Suggestion**:
> "We've searched 4 major databases (SemanticScholar, arXiv, ACM, PubMed) and found 79 papers. Before moving to synthesis, let's check coverage:
>
> **Potential gaps**:
> - Geographic: Mostly US/Western papers (missing Asian/European research?)
> - Language: English only
> - Venue types: Strong on conferences/journals, light on workshops/grey literature
> - Citation bias: Many highly-cited papers, but missing recent (<10 citations) emerging work
>
> **Questions for you**:
> 1. Should we search for non-English sources (esp. European medical journals)?
> 2. Include grey literature (hospital reports, white papers)?
> 3. Acceptable to focus on highly-established work, or include very recent low-citation papers?
>
> This will affect comprehensiveness of your review."

**Researcher Response**:
> "English-only is fine for my dissertation. I don't think I need grey literature, but I am worried about missing recent work. Can we make sure we're not just getting the 'classics'?"

**Turn Receipt**:
```
[10:20] Coverage validation discussion with researcher
→ Confirmed scope: English-only, no grey literature
→ Concern raised: citation bias toward highly-cited papers
→ Decision: Add low-citation filter to capture emerging work
→ Next: Supplemental search for recent low-citation papers
```

**Updated Grounding Box**:
```
┌─ RESEARCH GROUNDING ─────────────────────────────────────┐
│ Question: What approaches exist for XAI in clinical decision support systems?
Δ Stage: retrieval → validation (4/4) — 79 papers, 4 databases
Δ Assumptions:
│   • Clinical applications only
│   • 2020-present
│   • English language
│   • Peer-reviewed (no grey literature)
Δ Open Questions:
│   • Citation bias toward highly-cited papers?
Δ Next: agent → search for recent low-citation papers by 11am
└───────────────────────────────────────────────────────────┘
```

---

### [10:25] Supplemental Search - Recent Emerging Work

**Search Plan**:
```
Database: Semantic Scholar (best citation metadata)
Query: Same topics as before
Filters:
  • Year: 2023-2024 only (very recent)
  • Citations: 1-20 (emerging work, not yet highly cited)
  • Exclude: Papers already in collection
Rationale: Catch recent innovative approaches not yet widely cited
Expected: 10-15 papers
```

**Search Execution** → **12 new papers found**

**Turn Receipt**:
```
[10:27] Searched SemanticScholar: recent low-citation work (2023-2024, 1-20 cites)
→ Found 12 new papers (emerging approaches)
→ Includes novel explanation modalities (visual, counterfactual, contrastive)
→ Papers: 79 → 91 total
→ Resolved citation bias concern
→ Next: Begin synthesis stage
```

**Final Grounding Box** (Retrieval Complete):
```
┌─ RESEARCH GROUNDING ─────────────────────────────────────┐
│ Question: What approaches exist for XAI in clinical decision support systems?
Δ Stage: validation (4/4) — 91 papers, 4 databases
│ Assumptions:
│   • Clinical applications only
│   • 2020-present
│   • English language
│   • Peer-reviewed sources
│   • Mix of established (high-citation) and emerging (low-citation) work
Δ Open Questions: none (coverage validated)
Δ Next: researcher → begin synthesis (group by approach/method)
└───────────────────────────────────────────────────────────┘
```

---

## Session Summary

### Research Efficiency Metrics

**Time to 91 papers**: ~1.5 hours (vs. days of manual searching)

**Databases covered**: 4 (SemanticScholar, arXiv, ACM, PubMed)

**Query refinements**: 2 (terminology adjustment, citation bias correction)

**Coverage validated**: Yes (geographic/language/venue/citation dimensions checked)

### Cognitive Science Benefits Demonstrated

**Situation Awareness** (Endsley 1995):
- Researcher always knew: papers found, databases searched, gaps remaining
- Level 3 projection: "Next action" kept researcher oriented

**Mixed-Initiative Control** (Allen et al. 2001):
- Agent proposed searches, researcher approved/modified
- Short Run option de-risked uncertain queries
- Researcher maintained control while benefiting from agent expertise

**Error Recovery** (Norman 1983):
- ACM coverage gap caught immediately
- Targeted help with specific remedies (terminology synonyms)
- Quick recovery without starting over

**Transparency**:
- Every search logged with query, filters, rationale
- Assumptions made explicit throughout
- Provenance trail available for methods section

### Reproducible Search Strategy

Complete audit log enables methods section documentation:

```
SEARCH STRATEGY

Databases:
- Semantic Scholar (interdisciplinary coverage)
- arXiv (recent preprints, cs.AI/cs.LG/cs.HC)
- ACM Digital Library (HCI perspectives)
- PubMed (clinical/medical literature)

Search Terms:
- Core: "explainable AI", "interpretable AI/ML"
- Domain: "clinical decision support", "healthcare", "medical diagnosis"
- Variants: "transparency", "algorithmic explainability" (HCI terminology)

Inclusion Criteria:
- Publication date: 2020-present
- Language: English
- Publication type: Peer-reviewed (conferences, journals)
- Scope: Clinical applications only

Coverage: 91 papers across 4 databases (searched 2024-10-25)

Note: Intentionally balanced highly-cited (>20 cites) and emerging (<20 cites, 2023-2024) work to avoid citation bias.
```

---

## Key Takeaways

1. **Grounding Box maintained shared understanding** between researcher and agent
2. **Search Plan Gates prevented wasted effort** on wrong queries
3. **Targeted Help recovered quickly** from coverage gap
4. **Turn Receipts provided audit trail** for reproducibility
5. **Coverage Validation caught bias** toward highly-cited papers
6. **Mixed-initiative approach balanced** automation with researcher control

**Total time**: 1.5 hours for comprehensive, reproducible, validated search across 4 databases.

**Without middleware**: Likely 2-3 days of manual searching with unclear coverage and lost context.
