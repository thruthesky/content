# Content Quality Score System (100-point Rubric)

A self-evaluation rubric the AI **must apply to every generated post before calling `POST /posts`**. Posts scoring below **90** must not be published — the AI revises (up to 2 retries) or abandons the reservation.

The score system is the final quality gate between generation and submission. The `topic_slug` / reservation system in [api-content.md](api-content.md) prevents duplicate topics; this score system prevents **shallow, padded, or low-value posts** from polluting the site even when the topic is unique.

---

## 1. When to apply the score

Apply the rubric at **Step 4.5** of the workflow (just before `POST /posts`):

```
Plan (topic-coverage) → Reserve (topic-reserve) → Generate (research + draft)
                                                        ↓
                                                 Score (self-eval)
                                                        ↓
                                    ┌──────────── pass (≥ 90) ────────────┐
                                    ↓                                      ↓
                                  Submit (POST /posts)             (below 90 → revise up to 2x)
```

- Apply the rubric **once per draft**, recording the subscore for every category.
- Score honestly. Inflating scores to get past the gate defeats the purpose.
- If three drafts (1 original + 2 revisions) all score below 90, **release the reservation** (let it expire) and move to the next topic instead of publishing garbage.

---

## 2. Gating requirements (pass/fail — not scored, but required before scoring)

These must all be **true** before any rubric score is computed. If any item fails, the draft fails outright regardless of the rest of the rubric — do not submit; revise.

| Gate | Requirement | How to check |
|------|-------------|--------------|
| G1 | **Source coverage** | Research step gathered data from **≥ 20 distinct web sources** (different domains), documented in the draft's working notes |
| G2 | **Minimum length** | `content` body ≥ **800 words** (Korean: ≥ 1,500 characters excluding spaces) |
| G3 | **Minimum structure** | ≥ **5 top-level sections** (`<h2>` / `<h3>` or equivalent markdown headings) |
| G4 | **Topic match** | Draft content genuinely addresses the `topic_slug` that was reserved — not a bait-and-switch |
| G5 | **No duplicate content_hash** | `topic-check` confirmed the slug is `available`; the draft is not a trivial rephrase of an existing post |
| G6 | **Language match** | Content is in the site's primary language (Korean for most Korea SNS sub-sites) and is coherent prose, not machine-translated word salad |
| G7 | **HTML valid** | If HTML is used, tags are balanced, no stray `<script>` tags, tables/lists properly closed |

> If any gate fails, stop and fix **that specific problem** before scoring the rubric.

---

## 3. Rubric — 100 points across 6 categories

### 3.1 Originality & Uniqueness — 20 points

Does this post bring something new to the site, or is it a reworded rehash of easily-Googled content?

| Band | Score | Description |
|------|------:|-------------|
| Excellent | 17–20 | Fresh framing, original analysis, or novel combination of sources. Includes angles/takes not easily found in the top 10 Google results for the topic. |
| Good | 13–16 | Solid synthesis of multiple sources. Some original structure or commentary, but no new insight a reader couldn't assemble themselves. |
| Fair | 9–12 | Mostly a reorganization of existing material. Few original sentences. |
| Weak | 0–8 | Closely paraphrases a single source. Reader could find this trivially elsewhere. |

**Red flags (force ≤ 8):**
- Opening paragraph reads like Wikipedia's first sentence
- Content follows the structure of the #1 search result line-by-line
- No original examples, case studies, or commentary

### 3.2 Depth & Substance — 20 points

Does the post go beyond surface-level definitions into useful detail?

| Band | Score | Description |
|------|------:|-------------|
| Excellent | 17–20 | Concrete examples, numbers, comparisons, trade-offs. Reader leaves with actionable understanding. |
| Good | 13–16 | Explains the "why" as well as the "what". Several examples. |
| Fair | 9–12 | Covers the "what" adequately but thin on "why" and "how". |
| Weak | 0–8 | Bullet-point definitions only. Padding phrases ("In today's world…"). |

**Red flags (force ≤ 8):**
- No specific numbers, dates, prices, or measurements
- No comparisons (between options, regions, time periods)
- Filler sentences that say nothing ("This is a very important topic.")

### 3.3 Accuracy & Verifiability — 15 points

Are factual claims correct and traceable to credible sources?

| Band | Score | Description |
|------|------:|-------------|
| Excellent | 13–15 | Every non-obvious claim is grounded in at least one credible source cited in research notes. Numbers are current (within 12 months for volatile data). |
| Good | 9–12 | Most claims supported. Minor outdated references or minor unsourced details. |
| Fair | 5–8 | Some unverifiable claims. Key figures are stale or approximated. |
| Weak | 0–4 | Invented names, wrong dates, hallucinated statistics. |

**Red flags (force 0):**
- Any fabricated URL, person, or citation
- Any currency/price that contradicts the source's publication date
- Any legal/medical/financial claim without a credible source

### 3.4 Structure & Readability — 15 points

Is the post easy to scan and navigate?

| Band | Score | Description |
|------|------:|-------------|
| Excellent | 13–15 | Clear title. 5+ well-labeled sections. Lists, tables, or pull quotes where they aid comprehension. Short paragraphs (≤ 4 sentences). |
| Good | 9–12 | Logical sections. Mostly short paragraphs. One or two walls of text. |
| Fair | 5–8 | Sections exist but headings are vague. Many long paragraphs. |
| Weak | 0–4 | Single wall of text. No headings. No lists. |

**Red flags:**
- A single paragraph > 6 sentences (−2)
- No table or list in a comparison/spec-heavy post (−2)
- Heading text identical to the post title (−1)

### 3.5 Reader Value — 20 points

Will the target audience (Korean expatriates on this sub-site) actually benefit?

| Band | Score | Description |
|------|------:|-------------|
| Excellent | 17–20 | Tailored to Korean expat context (local currency, visa, language, time zone). Includes practical next steps, warnings, cost ranges, or "how to verify this yourself" pointers. |
| Good | 13–16 | Generally useful. Mentions local context but misses one or two opportunities. |
| Fair | 9–12 | Generic global advice. No local specifics. |
| Weak | 0–8 | Off-topic, irrelevant, or so generic it adds no value over a random blog. |

**Red flags (force ≤ 8):**
- All prices in USD with no KRW or local currency equivalent
- References only English-language service names when Korean equivalents exist
- No mention of any Korea- or expat-specific nuance

### 3.6 Polish — 10 points

Final presentation quality.

| Band | Score | Description |
|------|------:|-------------|
| Excellent | 9–10 | Zero typos. Consistent voice. Proper punctuation. Korean spacing/particle use natural. No awkward machine-translation artifacts. |
| Good | 7–8 | 1–2 minor typos or awkward sentences. |
| Fair | 4–6 | Multiple typos. Noticeably stilted. Inconsistent tone. |
| Weak | 0–3 | Broken grammar, garbled sentences, untranslated English fragments inside Korean body. |

**Red flags (force 0):**
- Any `[TODO]`, `[FIXME]`, lorem ipsum, or placeholder text
- Any obvious translation artifact (e.g. "It is a kind of place" for 곳입니다)

---

## 4. Self-evaluation output

The AI must produce a JSON block like this **internally** (not posted publicly) before deciding to submit:

```json
{
  "topic_slug": "ph-cebu-diving",
  "word_count": 1247,
  "section_count": 7,
  "source_count": 23,
  "gates_passed": ["G1","G2","G3","G4","G5","G6","G7"],
  "scores": {
    "originality": 18,
    "depth": 17,
    "accuracy": 14,
    "structure": 13,
    "reader_value": 19,
    "polish": 9
  },
  "total": 90,
  "pass": true,
  "weak_areas": [],
  "revision_round": 0
}
```

**Required fields:**
- All 6 scores must be present (no `null`).
- `total` is the sum of all 6 scores (max 100).
- `pass = total ≥ 90 && all gates passed`.
- `weak_areas`: every category scoring below the "Good" band (`originality < 13`, `depth < 13`, `accuracy < 9`, `structure < 9`, `reader_value < 13`, `polish < 7`).
- `revision_round`: 0 for first draft, 1 for first revision, 2 for second revision.

---

## 5. Revision loop (when `pass = false`)

```
if total < 90 and revision_round < 2:
    # Focus only on the weak_areas; do not rewrite the whole post from scratch.
    rewrite_weak_areas(weak_areas)
    revision_round += 1
    re-score
else:
    # 3 attempts exhausted — release the reservation.
    abandon_topic()       # do NOT call POST /posts
    # The reservation will auto-expire after TTL; no explicit release endpoint is needed.
    pick_next_topic()
```

### How to revise per category

| Weak area | Targeted fix |
|-----------|-------------|
| Originality low | Add analysis, a contrarian angle, or a personal/case example. Remove paragraphs that mirror the #1 Google result. |
| Depth low | Insert specific numbers, comparisons, and trade-offs. Remove filler sentences. |
| Accuracy low | Cross-check every claim against ≥ 2 sources. Remove unsupported assertions. Refresh stale figures. |
| Structure low | Split long paragraphs. Add sub-headings. Add a comparison table or bullet list where appropriate. |
| Reader value low | Add a "Korean expat perspective" subsection. Convert prices to KRW. Add practical next-steps. |
| Polish low | Re-read aloud. Fix typos, awkward particles, inconsistent honorific levels. Remove any English fragments. |

**Rules for revisions:**
1. Never restart from scratch on round 1 — targeted edits only.
2. Round 2 may do a larger rewrite but must preserve the reserved `topic_slug` (the reservation is for that specific slug).
3. Do not re-use any sentence that the previous round flagged as filler or inaccurate.

---

## 6. Worked example

**Topic reserved:** `ph-cebu-diving`
**Draft 1 scores:**
```json
{
  "originality": 11, "depth": 10, "accuracy": 12,
  "structure": 13, "reader_value": 12, "polish": 8,
  "total": 66, "pass": false,
  "weak_areas": ["originality","depth","reader_value"],
  "revision_round": 0
}
```

**Round 1 targeted edits:**
- Originality: Rewrote intro, added a comparison between Moalboal and Malapascua that no top-10 article had
- Depth: Added diving season table (visibility by month), price ranges in PHP and KRW
- Reader value: Added "한국인 다이버가 놓치기 쉬운 포인트" subsection

**Draft 2 scores:**
```json
{
  "originality": 17, "depth": 18, "accuracy": 14,
  "structure": 14, "reader_value": 19, "polish": 9,
  "total": 91, "pass": true
}
```
→ Submit.

---

## 7. Interaction with topic reservation

- The rubric runs **after** a successful `POST /topics/reserve`. The reservation holds the slug for the TTL (default 30 minutes). Use this window for drafting, scoring, and up to 2 revisions.
- If scoring exhausts the TTL (rare for normal drafts), the reservation expires naturally; the next `topic-reserve` call for the same slug will succeed again (expired rows are lazy-cleaned).
- **Do not** call `POST /posts` with `reservation_id` until the rubric passes. Submitting a low-quality post consumes the reservation and permanently locks the slug against re-publishing for this user — wasting a reservation on junk is worse than abandoning it.

---

## 8. Quick checklist (copy this into your drafting workspace)

```
Gates:
  [ ] G1  ≥ 20 distinct sources consulted
  [ ] G2  ≥ 800 words (or ≥ 1500 Korean chars)
  [ ] G3  ≥ 5 top-level sections
  [ ] G4  Content matches reserved topic_slug
  [ ] G5  topic-check returned "available"
  [ ] G6  Language coherent and target-language
  [ ] G7  HTML/Markdown is valid

Scores (must sum ≥ 90):
  Originality   /20 _____
  Depth         /20 _____
  Accuracy      /15 _____
  Structure     /15 _____
  Reader Value  /20 _____
  Polish        /10 _____
  Total         /100 _____

If < 90 → revise weak areas (max 2 revisions) or abandon reservation.
```
