from textwrap import dedent
from string import Template

class General_mood_extractor:
    def __init__(self, note_id, Date, PASTE_THE_RAW_NOTE_TEXT_HERE):
        # store inputs
        self.note_id = note_id
        self.Date = Date
        self.PASTE_THE_RAW_NOTE_TEXT_HERE = PASTE_THE_RAW_NOTE_TEXT_HERE

        # ----- shared system prompt (no braces to escape) -----
        self.prompt = dedent("""\
        You are an information extraction engine.

        TASK
        Given ONE raw note (plain text), extract a neutral, fact-first, style-free JSON object
        that matches the provided schema for the selected mood. Do not write prose. Output JSON ONLY.

        HARD RULES
        - Ground everything in the NOTE_TEXT; DO NOT INVENT names, dates, metrics, links, or outcomes.
        - Provide short verbatim quotes with 0-based character offsets in NOTE_TEXT.
        - Use "" for missing values. Keep unknown scalars null.
        - Clamp ranges: valence ∈ [-1,1]; arousal ∈ [0,1]; any *_0_1 ∈ [0,1].
        - Quotes: ≤ 6 items, each ≤ 140 chars. Spans: include the exact substring and unique span_id (e.g., "s1").
        - ISO dates when explicit; otherwise use "~".
        - Keep arrays tight: ≤ 12 typical items per list unless specified otherwise.
        - Language: 2-letter code if obvious, else "en".

        OUTPUT
        Return a single JSON object in the exact shape given in the User message. No commentary.
        """)

        # helper to fill templates safely (in case NOTE_TEXT has $)
        def _fill(tmpl: str) -> str:
            return Template(dedent(tmpl)).safe_substitute(
                NOTE_ID=self.note_id,
                NOTE_DATE=self.Date,
                NOTE_TEXT=self.PASTE_THE_RAW_NOTE_TEXT_HERE
            )

        # ---------------- General ----------------
        self.General_instruction = _fill("""\
        # INPUT CONTEXT
        MOOD: General
        NOTE_ID: ${NOTE_ID}
        NOTE_DATE: ${NOTE_DATE}
        LANGUAGE_HINT: "en"   # use to fill 'language' field; if "~", infer or default "en"
        NOTE_TEXT:

        ${NOTE_TEXT}

        # REQUIRED OUTPUT SHAPE (GeneralSignalPack JSON)
        {
          "version": 1,
          "extraction_timestamp": "<auto or ~>",
          "language": "<'en' or detected ISO 639-1 code>",
          "source_length_chars": <int>,

          "valence": <float -1..1>,
          "arousal": <float 0..1>,
          "confidence": <float 0..1>,
          "certainty_0_1": <float 0..1>,
          "importance_0_1": <float 0..1>,

          "embedding": null,

          "quotes": [
            { "text":"...", "start":<int>, "end":<int>, "purpose":"fact|decision|task|reference" }
          ],
          "spans": [
            { "span_id":"s1", "start":<int>, "end":<int>, "text":"<exact substring>" }
          ],

          "abstract": "<80-120 word neutral summary>",

          "key_facts": [
            { "fact":"...", "evidence_ref":"s1", "certainty_0_1":<float>, "timestamp":"YYYY-MM-DD|~" }
          ],

          "entities": {
            "people":[ {"name":"...", "role":"...", "span_ref":"s2"} ],
            "orgs":[ {"name":"...", "span_ref":"s3"} ],
            "places":[ {"name":"...", "span_ref":"s4"} ],
            "objects":[ {"name":"...", "span_ref":"s5"} ]
          },

          "timeline": [
            { "when":"YYYY-MM-DD|~", "event":"...", "detail":"...", "span_ref":"s6" }
          ],

          "topics": [
            { "topic":"...", "score_0_1":<float> }
          ],

          "open_questions": [
            { "question":"...", "info_needed":"...", "owner":"self|other|unknown", "span_ref":"s7" }
          ],

          "decisions": [
            { "status":"made|pending", "decision":"...", "by":"self|team|manager", "rationale":"...", "date":"YYYY-MM-DD|~", "span_ref":"s8" }
          ],

          "actions": [
            { "task":"...", "owner":"self|other", "status":"todo|doing|done", "due":"YYYY-MM-DD|time|~", "effort_min":<int or null>, "span_ref":"s9" }
          ],

          "risks": [
            { "risk":"...", "severity_0_1":<float>, "likelihood_0_1":<float>, "mitigation":"...", "span_ref":"s10" }
          ],

          "metrics": [
            { "name":"...", "value":"...", "unit":"...", "timeframe":"...", "span_ref":"s11" }
          ],

          "references": [
            { "kind":"link|doc|image|email", "title":"...", "url_or_id":"...", "span_ref":"s12" }
          ],

          "constraints": [
            { "type":"time|budget|policy|tech", "detail":"...", "span_ref":"s13" }
          ],
          "assumptions": [
            { "assumption":"...", "support":"...", "risk_if_wrong":"...", "span_ref":"s14" }
          ],

          "comparisons": [
            { "axis":"before_after|expected_actual|self_other", "before":"...", "after":"...", "span_ref":"s15" }
          ],

          "mood_hints": {
            "happy": { "candidate_events": [0,1] },
            "hopeful": { "candidate_goals": [] }
          },

          "tag_keywords": ["...", "..."],
          "entity_map": { "people":[], "orgs":[], "places":[], "objects":[] },

          "dominant_items": {
            "top_fact_idx": null,
            "top_task_idx": null,
            "top_decision_idx": null
          }
        }

        # EXTRACTION GUIDELINES
        (1) ABSTRACT
    - 80–120 words, purely neutral, no adjectives about mood, no second-guessing.
    - Answer “what happened / what exists / what’s planned” succinctly.

    2) QUOTES & SPANS
    - Choose ≤ 6 short support quotes (≤ 140 chars), add {"start","end"} offsets.
    - For any field with “*_ref” or “span_ref”, point to an ID in "spans".
    - Every evidence_ref/span_ref must correspond to an existing spans[i].span_id.

    3) KEY FACTS
    - Split into atomic statements (“X met Y”; “deadline is 2025-09-30”).
    - Give a certainty_0_1 score reflecting how explicit the note is.
    - If a date is implied, set timestamp; else "~".

    4) ENTITIES
    - People: names or roles. Add role if explicitly stated.
    - Orgs, places, objects: include if directly mentioned.
    - Each entity should point to a span_ref where it appears.

    5) TIMELINE
    - Extract ordered events the note mentions (up to 10).
    - Prefer specific “when”; else "~". Keep “detail” short.

    6) TOPICS
    - 3–8 neutral tags (e.g., “testing”, “release”, “health”).
    - score_0_1 reflects topical salience in the note.

    7) DECISIONS / ACTIONS
    - Decisions: status (made|pending), decision text, by, rationale, date.
    - Actions: task, owner, status, due, optional effort_min.
    - Only include if explicitly present or strongly implied.

    8) RISKS / METRICS / REFERENCES
    - Risks: concrete, with severity & likelihood.
    - Metrics: name/value/unit/timeframe; don’t normalize numbers you can’t support.
    - References: links/docs/images/emails only if present in the note.

    9) CONSTRAINTS / ASSUMPTIONS / COMPARISONS
    - Constraints are limits (time/budget/policy/tech).
    - Assumptions: what the note presumes; add risk_if_wrong.
    - Comparisons: before_after, expected_actual, self_other.

    10) SCORING
    - valence ∈ [-1,1] (overall pleasantness); arousal ∈ [0,1] (intensity).
    - certainty_0_1: factual clarity of the note; importance_0_1: overall significance.
    - confidence: your extraction confidence (0..1).

    11) DOMINANT ITEMS
    - If any: indices into key_facts/actions/decisions for quick access; else null.

    QUALITY CHECKS (MANDATORY)
    - JSON must parse.
    - All refs (evidence_ref, span_ref) must match an existing spans[*].span_id.
    - Abstract word count within 80–120.
    - All scores clamped to their ranges.
    - No hallucinated links, people, or dates.
)
        """)

        # ---------------- Happy ----------------
        # Fixed: "graditude" -> "gratitude", "risks_or_concers" -> "risks_or_concerns",
        # and "state_metrics": {} instead of a dangling comma.
        self.Happy_instruction = _fill("""\
        # INPUT CONTEXT
        MOOD: Happy
        NOTE_ID: ${NOTE_ID}
        NOTE_DATE: ${NOTE_DATE}
        LANGUAGE_HINT: "en"
        NOTE_TEXT:

        ${NOTE_TEXT}

        # REQUIRED OUTPUT SHAPE (HappySignalPack JSON)
        {
          "version": 1,
          "extraction_timestamp": "<auto or ~>",
          "language": "<'en' or detected ISO 639-1 code>",
          "source_length_chars": <int>,

          "valence": <float -1..1>,
          "arousal": <float 0..1>,
          "confidence": <float 0..1>,

          "embedding": null,

          "quotes": [
            { "text":"...", "start":<int>, "end":<int>, "purpose":"fact|emotion|event" }
          ],
          "spans": [
            { "span_id":"s1","start":<int>,"end":<int>,"text":"<exact substring>" }
          ],

          "positive_events": [
            { "type":"achievement|social|relief|discovery|gift|gratitude|other",
              "what_happened":"...", "who_involved":["..."], "where":"...", "when":"YYYY-MM-DD|~",
              "evidence_ref":"s1", "personal_importance_0_1":0.0, "novelty_0_1":0.0 }
          ],

          "outcomes": [
            { "result":"...", "evidence_quote":"...", "magnitude_0_1":0.0 }
          ],

          "gratitude": [
            { "target":"person|thing|circumstance","reason":"...","quote":"~|...","warmth_0_1":0.0 }
          ],

          "pleasant_emotions": [
            { "label":"joy|pride|serenity|affection|amusement","intensity_0_1":0.0,"trigger_ref":"s2" }
          ],

          "strengths": [
            { "strength":"perseverance|creativity|kindness|leadership|curiosity","situation_ref":"s3" }
          ],

          "social_ties": [
            { "relationship":"friend|mentor|family|team","interaction":"support|celebration|help","warmth_0_1":0.0,"span_ref":"s4" }
          ],

          "growth": [
            { "skill_or_value":"...", "proof_quote":"..." }
          ],

          "future_positives": [
            { "opportunity":"...", "likelihood_0_1":0.0 }
          ],

          "activities": [
            { "category":"hobby|exercise|music|food|nature|other","description":"...","enjoyment_0_1":0.0 }
          ],

          "sensory": [
            { "modality":"sight|sound|smell|touch|taste","detail":"...","valence_0_1":0.0,"span_ref":"s5" }
          ],

          "humor": [
            { "line":"...", "safe":true }
          ],

          "comparatives": [
            { "axis":"before_after|expected_actual|self_other","before":"...","after":"...","span_ref":"s6" }
          ],

          "obstacles_overcome": [
            { "obstacle":"...", "how_overcome":"...", "impact_0_1":0.0, "span_ref":"s7" }
          ],

          "values_alignment": [
            { "value":"family|health|growth|service|creativity|autonomy|community","alignment_0_1":0.0,"span_ref":"s8" }
          ],

          "artifacts": [
            { "kind":"photo|ticket|gift|message","desc":"...", "span_ref":"s9" }
          ],

          "state_metrics": {},

          "risks_or_concerns": [
            { "risk_or_concern":"...", "severity_0_1":0.0, "likelihood_0_1":0.0, "span_ref":"s10" }
          ],

          "boundaries_to_respect": ["no personal identifiers", "avoid sensitive topics"],

          "tag_keywords": ["...", "..."],
          "entity_map": { "people":[], "orgs":[], "places":[], "objects":[] },

          "dominant_items": {
            "top_event_idx": null,
            "top_outcome_idx": null,
            "top_emotion_idx": null
          }
        }

        # EXTRACTION GUIDELINES
        (1) POSITIVE EVENTS
        - Extract clear moments of achievement, social joy, relief, discoveries, gifts, or gratitude.
        - Always include evidence_ref from spans.

        2) OUTCOMES
        - State concrete results or wins, with supporting quotes.

        3) GRATITUDE
        - Capture sources of appreciation (people, things, circumstances).
        - Provide warmth_0_1 to reflect emotional intensity.

        4) PLEASANT EMOTIONS
        - Identify explicit emotions like joy, pride, serenity, affection, amusement.
        - Link to trigger_ref.

        5) STRENGTHS & GROWTH
        - Extract demonstrated personal strengths and evidence of growth.

        6) SOCIAL TIES
        - Capture relationships and interactions that reinforced happiness.

        7) FUTURE POSITIVES
        - Highlight opportunities or anticipated good outcomes.

        8) ACTIVITIES & SENSORY
        - Identify enjoyable hobbies/rituals and sensory details (sights, sounds, smells, etc.).

        9) HUMOR
        - Include safe humorous lines or playful moments.

        10) OBSTACLES OVERCOME
        - If challenges were overcome, describe how and impact.

        11) VALUES ALIGNMENT & ARTIFACTS
        - Capture how events connected to user values and any concrete artifacts.

        12) SCORING
        - valence ∈ [-1,1]; arousal ∈ [0,1]; confidence ∈ [0,1].
        - All 0..1 scores must be clamped.

        # QUALITY CHECKS
        - JSON must parse.
        - All evidence_ref/span_ref must point to valid spans.
        - All floats must be within valid ranges.
        - No fabricated names, artifacts, or events.)
        """)

        # ---------------- Reflective ----------------
        self.Reflective_instruction = _fill("""\
        # INPUT CONTEXT
        MOOD: Reflective
        NOTE_ID: ${NOTE_ID}
        NOTE_DATE: ${NOTE_DATE}
        LANGUAGE_HINT: "en"
        NOTE_TEXT:

        ${NOTE_TEXT}

        # REQUIRED OUTPUT SHAPE (ReflectiveSignalPack JSON)
        {
          "version": 1,
          "extraction_timestamp": "<auto or ~>",
          "language": "<'en' or inferred>",
          "source_length_chars": <int>,

          "valence": <float -1..1>,
          "arousal": <float 0..1>,
          "confidence": <float 0.0..1.0>,
          "depth_0_1": <float 0..1>,
          "clarity_0_1": <float 0..1>,

          "embedding": null,

          "quotes": [
            { "text":"...", "start":<int>, "end":<int>, "purpose":"lesson|reframe|event" }
          ],
          "spans": [
            { "span_id":"s1","start":<int>,"end":<int>,"text":"<exact substring>" }
          ],

          "events_recalled": [
            { "event":"...", "timeframe":"...", "impact":"...", "valence":"positive|negative|mixed", "evidence_ref":"s2" }
          ],
          "lessons": [
            { "lesson":"...", "domain":"work|relationships|self|health|learning|other", "generalizable":true, "evidence_quote":"..." }
          ],
          "mistakes": [
            { "mistake":"...", "realization":"...", "severity_0_1":0.0, "repair_action":"...", "evidence_ref":"s3" }
          ],
          "reframes": [
            { "from":"...", "to":"...", "trigger":"...", "value_strengthened":"...", "evidence_ref":"s4" }
          ],
          "patterns": [
            { "theme":"...", "frequency":"...", "trigger":"...", "span_refs":["s5","s6"] }
          ],
          "values_alignment": [
            { "value":"...", "alignment":"aligned|conflicted", "evidence_quote":"..." }
          ],
          "growth_edges": [
            { "strength":"...", "example":"...", "improvement_needed":"...", "evidence_ref":"s7" }
          ],
          "open_questions": [
            { "question":"...", "category":"purpose|decision|relationship|identity|career|other", "unresolved":true }
          ],
          "turning_points": [
            { "trigger":"...", "realization":"...", "impact":"short_term|long_term", "evidence_ref":"s8" }
          ],
          "comparisons": [
            { "axis":"past_vs_present|self_vs_others|expectation_vs_reality", "before":"...", "after":"...", "insight":"...", "evidence_ref":"s9" }
          ],
          "gratitude": [
            { "target":"person|event|circumstance", "reason":"...", "quote":"..." }
          ],
          "regrets": [
            { "regret":"...", "acceptance_level_0_1":0.0, "next_step":"..." }
          ],
          "future_adjustments": [
            { "change":"...", "why":"...", "confidence_0_1":0.0, "evidence_ref":"s10" }
          ],

          "tag_keywords": ["..."],
          "entity_map": { "people":[], "orgs":[], "places":[], "objects":[] },
          "dominant_items": { "top_lesson_idx":null, "top_reframe_idx":null, "top_growth_edge_idx":null }
        }

        # EXTRACTION GUIDELINES
        (1) EVENTS_RECALLED
  - Capture past experiences or situations mentioned, with timeframe and impact.
  - Mark overall valence (positive/negative/mixed).

  2) LESSONS
  - Extract insights or principles learned.
  - Mark domain (work, relationships, self, etc.) and whether it generalizes.

  3) MISTAKES
  - Identify explicit or implicit mistakes acknowledged.
  - Add realization, severity, and any proposed repair actions.

  4) REFRAMES
  - Capture perspective shifts (from → to).
  - Note value strengthened or clarified.

  5) PATTERNS
  - Repeated themes across events.
  - Link to multiple span_refs if applicable.

  6) VALUES ALIGNMENT
  - Capture if reflections align or conflict with personal values.

  7) GROWTH EDGES
  - Highlight strengths shown and areas for improvement.

  8) OPEN QUESTIONS
  - Self-inquiries or unresolved questions raised by the note.

  9) TURNING POINTS
  - Extract triggers and realizations that led to noticeable change.

  10) COMPARISONS
  - Contrast past vs present, self vs others, or expectation vs reality.

  11) GRATITUDE / REGRETS / FUTURE ADJUSTMENTS
  - Include explicit appreciation, regrets with acceptance levels, and future plans.

  12) SCORING
  - valence ∈ [-1,1]; arousal ∈ [0,1]; depth & clarity ∈ [0,1].
  - All floats must be clamped within range.

  # QUALITY CHECKS
  - JSON must parse.
  - All refs (evidence_ref, span_ref) must exist in spans.
  - No hallucinated entities or events.
  - Keep extraction factual, grounded in the note.)
        """)

        # ---------------- Motivation ----------------
        self.Motivation_instruction = _fill("""\
        # INPUT CONTEXT
        MOOD: Motivation
        NOTE_ID: ${NOTE_ID}
        NOTE_DATE: ${NOTE_DATE}
        LANGUAGE_HINT: "en"
        NOTE_TEXT:

        ${NOTE_TEXT}

        # REQUIRED OUTPUT SHAPE (MotivationSignalPack JSON)
        {
          "version": 1,
          "extraction_timestamp": "<auto or ~>",
          "language": "<'en' or inferred>",
          "source_length_chars": <int>,

          "valence": <float -1..1>,
          "arousal": <float 0..1>,
          "confidence": <float 0..1>,
          "drive_strength_0_1": <float 0..1>,
          "clarity_0_1": <float 0..1>,
          "feasibility_0_1": <float 0..1>,
          "commitment_0_1": <float 0..1>,

          "embedding": null,

          "quotes": [
            { "text":"...", "start":<int>, "end":<int>, "purpose":"goal|driver|action" }
          ],
          "spans": [
            { "span_id":"s1","start":<int>,"end":<int>,"text":"<exact substring>" }
          ],

          "goals": [
            { "type":"outcome|performance|learning|habit", "description":"...", "why_it_matters":"...", "metric":"...", "target_value":"...", "deadline":"YYYY-MM-DD|~", "priority_0_1":0.0, "evidence_ref":"s1" }
          ],
          "anti_goals": [
            { "description":"...", "reason":"...", "evidence_ref":"s2" }
          ],
          "drivers": [
            { "kind":"intrinsic|extrinsic", "label":"mastery|autonomy|purpose|recognition|reward|fear_of_loss|deadline", "evidence_quote":"...", "strength_0_1":0.0 }
          ],
          "identity_claims": [
            { "claim":"...", "proof_quote":"...", "salience_0_1":0.0 }
          ],
          "implementation_intentions": [
            { "if":"...", "then":"...", "context":"where/when", "evidence_ref":"s3" }
          ],
          "next_actions": [
            { "action":"...", "context":"...", "size":"micro|small|normal", "owner":"self|other", "effort_0_1":0.0, "duration_min":0, "due":"YYYY-MM-DD|time|~", "blockers_ref":["s4"], "evidence_ref":"s5" }
          ],
          "time_blocks": [
            { "label":"...", "start":"YYYY-MM-DDTHH:MM", "end":"YYYY-MM-DDTHH:MM", "location":"...", "pomodoro":"25|50|null" }
          ],
          "habits": [
            { "habit":"...", "cue":"time|location|preceding_action", "frequency":"daily|weekly|custom", "streak_days":0, "confidence_0_1":0.0, "evidence_ref":"s6" }
          ],
          "cues_triggers": [
            { "type":"time|location|tool|social|emotion|calendar|notification", "detail":"...", "strength_0_1":0.0, "span_ref":"s7" }
          ],
          "rewards": [
            { "type":"intrinsic|extrinsic", "reward":"...", "timing":"immediate|end_of_block|end_of_day", "safety_checked":true }
          ],
          "accountability": [
            { "kind":"person|team|public_commit|bot|streak_counter", "who_or_what":"...", "cadence":"daily|weekly|adhoc", "contact":"email|dm|in_person|null", "evidence_ref":"s8" }
          ],
          "obstacles": [
            { "obstacle":"...", "type":"skill_gap|unclear_spec|distraction|tooling|fear|logistics", "severity_0_1":0.0, "likelihood_0_1":0.0, "evidence_ref":"s9" }
          ],
          "environment_design": [
            { "change":"...", "effect":"...", "setup_time_min":0 }
          ],
          "leverage_points": [
            { "action":"...", "why_high_impact":"...", "evidence_ref":"s10" }
          ],
          "progress_markers": [
            { "marker":"...", "metric":"...", "baseline":"...", "target":"...", "due":"YYYY-MM-DD|~" }
          ],
          "streaks": [
            { "label":"...", "current":0, "best":0, "last_date":"YYYY-MM-DD|~" }
          ],
          "fallback_plans": [
            { "trigger":"...", "fallback":"...", "cost_0_1":0.0 }
          ],
          "pep_talk_lines": [
            { "line":"...", "evidence_quote":"..." }
          ],
          "readiness_state": {
            "sleep_ok": null,
            "fuel_ok": null,
            "mood": null,
            "time_of_day": null
          },

          "tag_keywords": ["..."],
          "entity_map": { "people":[], "orgs":[], "places":[], "objects":[] },
          "dominant_items": { "top_goal_idx":null, "top_action_idx":null, "top_driver_idx":null }
        }

        # EXTRACTION GUIDELINES
        (1) GOALS
- Extract user’s explicit or implied objectives.
- Include type, description, metric, target, and deadline if available.

2) ANTI-GOALS
- Capture what user wants to avoid (fears, undesired states).

3) DRIVERS
- Identify intrinsic/extrinsic motivators (purpose, mastery, recognition, deadlines).
- Add strength_0_1.

4) IDENTITY CLAIMS
- Pull statements of self-identity or capability.

5) IMPLEMENTATION INTENTIONS
- Capture if-then planning statements.

6) NEXT ACTIONS
- Extract concrete, executable steps with owner, due, and effort.

7) TIME BLOCKS & HABITS
- Include scheduling info and recurring routines.

8) CUES / REWARDS / ACCOUNTABILITY
- Note motivational triggers, reward systems, and accountability mechanisms.

9) OBSTACLES & ENVIRONMENT DESIGN
- Extract blockers and design choices to reduce friction.

10) LEVERAGE POINTS
- Highlight highest impact actions.

11) PROGRESS MARKERS & STREAKS
- Extract explicit milestones or history of progress.

12) FALLBACK PLANS & PEP-TALK LINES
- Capture resilience strategies and energizing affirmations.

13) READINESS STATE
- Extract indicators of energy, wellbeing, or conditions that affect motivation.

14) SCORING
- valence ∈ [-1,1]; arousal ∈ [0,1]; all other 0..1 fields must be clamped.
- Confidence reflects extraction certainty.

# QUALITY CHECKS
- JSON must parse.
- All refs must point to valid spans.
- No hallucinated tasks, deadlines, or people.
- Keep content factual, grounded in the note.)
        """)

        # ---------------- Calm ----------------
        self.Calm_instruction = _fill("""\
        # INPUT CONTEXT
        MOOD: Calm
        NOTE_ID: ${NOTE_ID}
        NOTE_DATE: ${NOTE_DATE}
        LANGUAGE_HINT: "en"
        NOTE_TEXT:

        ${NOTE_TEXT}

        # REQUIRED OUTPUT SHAPE (CalmSignalPack JSON)
        {
          "version": 1,
          "extraction_timestamp": "<auto or ~>",
          "language": "<'en' or inferred>",
          "source_length_chars": <int>,

          "valence": <float -1..1>,
          "arousal": <float 0..1>,
          "confidence": <float 0..1>,
          "serenity_0_1": <float 0..1>,
          "safety_0_1": <float 0..1>,
          "balance_0_1": <float 0..1>,
          "clarity_0_1": <float 0..1>,

          "embedding": null,

          "quotes": [
            { "text":"...", "start":<int>, "end":<int>, "purpose":"soothing|anchor|routine" }
          ],
          "spans": [
            { "span_id":"s1","start":<int>,"end":<int>,"text":"<exact substring>" }
          ],

          "tranquil_moments": [
            { "moment":"...", "when":"...", "where":"...", "with":"...", "evidence_ref":"s1" }
          ],
          "soothing_activities": [
            { "activity":"...", "duration_min":0, "frequency":"daily|weekly|adhoc", "enjoyment_0_1":0.0, "span_ref":"s2" }
          ],
          "calming_environments": [
            { "place":"...", "qualities":["quiet"], "sensory_details":["..."], "span_ref":"s3" }
          ],
          "sensory_anchors": [
            { "modality":"sound|sight|smell|touch|taste", "detail":"...", "valence_0_1":0.0, "span_ref":"s4" }
          ],
          "stressors_reduced": [
            { "stressor":"...", "how_reduced":"...", "relief_0_1":0.0, "evidence_ref":"s5" }
          ],
          "coping_strategies": [
            { "strategy":"...", "effectiveness_0_1":0.0, "span_ref":"s6" }
          ],
          "grounding_practices": [
            { "practice":"...", "frequency":"...", "stability_0_1":0.0, "evidence_ref":"s7" }
          ],
          "routines": [
            { "routine":"...", "time":"..:..", "frequency":"...", "comfort_0_1":0.0, "span_ref":"s8" }
          ],
          "safe_people": [
            { "person":"...", "relationship":"friend|partner|family|mentor", "warmth_0_1":0.0, "quote":"..." }
          ],
          "affirmations": [
            { "line":"...", "tone":"gentle|accepting|spiritual", "evidence_ref":"s9" }
          ],
          "values_alignment": [
            { "value":"...", "alignment_0_1":0.0, "evidence_quote":"..." }
          ],
          "releases": [
            { "released":"anger|resentment|worry", "how":"...", "relief_0_1":0.0 }
          ],
          "recovery_signals": [
            { "signal":"...", "intensity_0_1":0.0, "span_ref":"s10" }
          ],
          "calm_disturbances": [
            { "disturbance":"...", "severity_0_1":0.0, "likelihood_0_1":0.0 }
          ],
          "future_practices": [
            { "practice":"...", "commitment":"daily|weekly|adhoc", "confidence_0_1":0.0 }
          ],

          "tag_keywords": ["..."],
          "entity_map": { "people":[], "orgs":[], "places":[], "objects":[] },
          "dominant_items": { "top_activity_idx":null, "top_anchor_idx":null, "top_routine_idx":null }
        }

        # EXTRACTION GUIDELINES
        (1) TRANQUIL MOMENTS
- Capture moments of peace, relaxation, or safety with time, place, and companions.

2) SOOTHING ACTIVITIES
- Extract hobbies, rituals, or habits that restore calm.
- Include enjoyment_0_1 score.

3) CALMING ENVIRONMENTS
- Describe locations with quiet or restorative qualities.
- Add sensory details where available.

4) SENSORY ANCHORS
- Extract grounding sensory inputs (sights, sounds, smells, touch, taste).

5) STRESSORS REDUCED
- Note what stressors were eased and how.

6) COPING STRATEGIES & GROUNDING PRACTICES
- Pull explicit or implied strategies for self-soothing or grounding.

7) ROUTINES
- Identify structured routines that reinforce stability and comfort.

8) SAFE PEOPLE
- Capture individuals who provide safety or emotional security.

9) AFFIRMATIONS
- Extract gentle, accepting, or spiritual affirmations.

10) VALUES ALIGNMENT & RELEASES
- Indicate where values were upheld and what emotional burdens were let go.

11) RECOVERY SIGNALS
- Track signs of recovery, stability, or regained balance.

12) CALM DISTURBANCES & FUTURE PRACTICES
- Capture threats to calm and proactive plans for maintaining serenity.

13) SCORING
- valence ∈ [-1,1]; arousal, serenity, safety, balance, clarity ∈ [0,1].
- Confidence must reflect extraction reliability.

# QUALITY CHECKS
- JSON must parse.
- All evidence_ref/span_ref must be valid.
- No hallucinated people, places, or practices.
- Output must remain factual and grounded in NOTE_TEXT.)
        """)

        # ---------------- Dramatic ----------------
        self.Dramatic_instruction = _fill("""\
        # INPUT CONTEXT
        MOOD: Dramatic
        NOTE_ID: ${NOTE_ID}
        NOTE_DATE: ${NOTE_DATE}
        LANGUAGE_HINT: "en"
        NOTE_TEXT:

        ${NOTE_TEXT}

        # REQUIRED OUTPUT SHAPE (DramaticSignalPack JSON)
        {
          "version": 1,
          "extraction_timestamp": "<auto or ~>",
          "language": "<'en' or inferred>",
          "source_length_chars": <int>,

          "valence": <float -1..1>,
          "arousal": <float 0..1>,
          "confidence": <float 0..1>,
          "intensity_0_1": <float 0..1>,
          "tension_0_1": <float 0..1>,
          "stakes_0_1": <float 0..1>,
          "pace_0_1": <float 0..1>,
          "contrast_0_1": <float 0..1>,

          "embedding": null,

          "quotes": [
            { "text":"...", "start":<int>, "end":<int>, "purpose":"stake|conflict|turn" }
          ],
          "spans": [
            { "span_id":"s1","start":<int>,"end":<int>,"text":"<exact substring>" }
          ],

          "settings": [
            { "place":"...", "time":"...", "atmosphere":"tense|somber|electric|hopeful", "span_ref":"s1" }
          ],
          "characters": [
            { "name_or_role":"self|ally|antagonist|mentor|teammate|manager", "traits":["..."], "motivation":"...", "span_ref":"s2" }
          ],
          "stakes": [
            { "type":"reputation|relationship|deadline|health|opportunity|money", "description":"...", "severity_0_1":0.0, "urgency_0_1":0.0, "evidence_ref":"s3" }
          ],
          "conflicts": [
            { "kind":"internal|interpersonal|systemic|logistical", "issue":"...", "opposing_forces":["..."], "evidence_ref":"s4" }
          ],
          "inciting_incident": { "what_happened":"...", "why_it_matters":"...", "span_ref":"s5" },
          "escalations": [
            { "complication":"...", "effect":"raises stakes|narrows options|adds time pressure", "span_ref":"s6" }
          ],
          "reversals": [
            { "type":"reversal|revelation|red_herring", "what_changed":"...", "impact_0_1":0.0, "span_ref":"s7" }
          ],
          "turning_points": [
            { "decision":"...", "reason":"...", "cost":"...", "span_ref":"s8" }
          ],
          "climax": { "moment":"...", "action":"...", "result":"...", "span_ref":"s9" },
          "resolution": { "status":"win|loss|mixed|open", "after_effects":"...", "lesson_hint":"...", "span_ref":"s10" },
          "catharsis": { "feeling":"relief|pride|grief|awe|bittersweet", "intensity_0_1":0.0, "quote":"..." },
          "themes": [
            { "theme":"resilience|trust|ambition|belonging|integrity|fate_vs_choice", "evidence_ref":"s11" }
          ],
          "motifs": [
            { "motif":"...", "meaning":"...", "span_ref":"s12" }
          ],
          "symbols": [
            { "symbol":"...", "represents":"...", "span_ref":"s13" }
          ],
          "imagery": [
            { "modality":"sight|sound|smell|touch|taste", "detail":"...", "valence_0_1":0.0, "span_ref":"s14" }
          ],
          "beat_sheet": [
            { "beat":"setup|inciting|rising|reversal|dark_night|climax|resolution", "span_ref":"s15" }
          ],
          "three_act_map": { "act1":"...", "act2":"...", "act3":"..." },
          "heros_journey": { "call_to_adventure":"...", "tests_allies_enemies":"...", "ordeal":"...", "return":"..." },
          "setup_payoff_links": [
            { "setup_span":"sA", "payoff_span":"sB", "note":"..." }
          ],
          "suspense_devices": [
            { "device":"ticking_clock|dramatic_irony|cliffhanger|misdirection", "where":"...", "strength_0_1":0.0 }
          ],
          "open_questions": [
            { "question":"...", "importance_0_1":0.0, "span_ref":"s16" }
          ],
          "risks_or_concerns": [
            { "topic":"self-harm|violence|abuse|phobia", "severity_0_1":0.0, "span_ref":"s17" }
          ],
          "boundaries_to_respect": ["avoid graphic detail","keep names private","gentle around grief"],

          "tag_keywords": ["..."],
          "entity_map": { "people":[], "orgs":[], "places":[], "objects":[] },
          "dominant_items": { "top_stake_idx":null, "top_conflict_idx":null, "top_reversal_idx":null }
        }

        # EXTRACTION GUIDELINES
        (1) SETTINGS
- Capture the environment, atmosphere, and time context with dramatic framing.

2) CHARACTERS
- Identify roles and motivations (self, allies, antagonists, mentors, etc.).

3) STAKES
- Extract risks and what is at stake (reputation, health, relationships, money, etc.).

4) CONFLICTS
- Internal, interpersonal, or systemic issues should be clearly identified.

5) INCITING INCIDENT
- Highlight the triggering event that sets the drama in motion.

6) ESCALATIONS / REVERSALS / TURNING POINTS
- Capture moments that increase stakes, flip situations, or force decisions.

7) CLIMAX & RESOLUTION
- Extract the pivotal climax and outcome resolution, including after-effects.

8) CATHARSIS
- Capture the emotional release (relief, grief, awe, pride, bittersweet).

9) THEMES, MOTIFS, SYMBOLS, IMAGERY
- Identify deeper narrative patterns, symbolic items, and sensory imagery.

10) STRUCTURE
- Provide beat sheet, three-act map, and Hero’s Journey elements if identifiable.

11) SUSPENSE DEVICES
- Capture storytelling devices like ticking clocks, cliffhangers, dramatic irony.

12) RISKS OR CONCERNS
- Carefully flag any sensitive content (self-harm, violence, abuse).
- Apply boundaries to keep safe and respectful.

13) SCORING
- valence ∈ [-1,1]; arousal, intensity, tension, stakes, pace, contrast ∈ [0,1].
- Confidence reflects extraction reliability.

# QUALITY CHECKS
- JSON must parse.
- All evidence_ref/span_ref must exist in spans.
- Do not exaggerate or fabricate conflicts or stakes.
- Ensure dramatic elements are grounded in NOTE_TEXT.)
        """)

        # ---------------- Funny ----------------
        self.Funny_instruction = _fill("""\
        # INPUT CONTEXT
        MOOD: Funny
        NOTE_ID: ${NOTE_ID}
        NOTE_DATE: ${NOTE_DATE}
        LANGUAGE_HINT: "en"
        NOTE_TEXT:

        ${NOTE_TEXT}

        # REQUIRED OUTPUT SHAPE (FunnySignalPack JSON)
        {
          "version": 1,
          "extraction_timestamp": "<auto or ~>",
          "language": "<'en' or inferred>",
          "source_length_chars": <int>,

          "valence": <float -1..1>,
          "arousal": <float 0..1>,
          "confidence": <float 0..1>,
          "surprise_0_1": <float 0..1>,
          "warmth_0_1": <float 0..1>,

          "embedding": null,

          "quotes": [
            { "text":"...", "start":<int>, "end":<int>, "purpose":"setup|observation|callback" }
          ],
          "spans": [
            { "span_id":"s1","start":<int>,"end":<int>,"text":"<exact substring>" }
          ],

          "persona": {
            "speaker":"self|narrator",
            "traits":["dry|playful|wry"],
            "self_deprecating_ok":true
          },
          "audience": {
            "familiar_with":["..."],
            "taboos":["..."],
            "friendliness_0_1":0.0
          },

          "setups": [
            { "premise":"...", "context":"work|home|travel|tech|social", "tension_seed":"...", "evidence_ref":"s1" }
          ],
          "benign_violations": [
            { "violation":"...", "benign_reason":"...", "sensitivity_risk_0_1":0.0, "evidence_ref":"s2" }
          ],
          "wordplay": [
            { "hook":"...", "type":"pun|double_entendre|malapropism|portmanteau", "span_ref":"s3" }
          ],
          "amplifiers": [
            { "type":"hyperbole|understatement|analogy", "line":"...", "span_ref":"s4" }
          ],
          "callbacks": [
            { "reference":"...", "span_ref":"s5" }
          ],
          "observations": [
            { "topic":"...", "line":"...", "relatability_0_1":0.0, "evidence_ref":"s6" }
          ],
          "situational": [
            { "scene":"...", "prop":"...", "awkwardness_0_1":0.0, "span_ref":"s7" }
          ],
          "punchlines": [
            { "line":"...", "built_from":["setup:0|wordplay:0"], "spice":"dry|silly|deadpan|witty", "safety_checked":true }
          ],
          "delivery": {
            "style":"deadpan|playful|wry|animated",
            "beats":["pause_before_punch"],
            "max_line_len":140
          },

          "sensitivity_flags": [
            { "topic":"body|religion|politics|trauma|identity|health", "risk_0_1":0.0 }
          ],
          "boundaries_to_respect": ["no insults","avoid identifiers","no dark humor"],
          "redlines": ["self-harm","violence","minors","protected classes","medical advice"],

          "references": [
            { "kind":"pop|tech|work|internet", "item":"...", "recency":"old|current", "span_ref":"s8" }
          ],

          "tag_keywords": ["..."],
          "entity_map": { "people":[], "orgs":[], "places":[], "objects":[] },
          "dominant_items": { "top_setup_idx":null, "top_punch_idx":null, "top_wordplay_idx":null }
        }

        # EXTRACTION GUIDELINES
        (1) PERSONA
- Capture speaker’s comedic style: dry, playful, wry, or self-deprecating.

2) AUDIENCE
- Extract what audience is familiar with and taboos to avoid.
- Add friendliness_0_1 to reflect rapport.

3) SETUPS
- Identify premises and context where tension or humor seed is introduced.

4) BENIGN VIOLATIONS
- Capture small breaches of expectation that remain safe or playful.

5) WORDPLAY & AMPLIFIERS
- Extract puns, exaggerations, analogies, understatements, etc.

6) CALLBACKS & OBSERVATIONS
- Note recurring references or everyday relatable commentary.

7) SITUATIONAL & PUNCHLINES
- Capture funny scenes, props, and final punchlines.
- Each punchline must reference a setup or wordplay.

8) DELIVERY
- Extract comedic delivery style, beats, and pacing.

9) SENSITIVITY & SAFETY
- Flag risky humor topics.
- Respect boundaries: no insults, dark humor, or sensitive violations.
- Follow redlines strictly (no self-harm, violence, minors, etc.).

10) REFERENCES
- Capture pop culture, tech, internet, or work references.

11) SCORING
- valence ∈ [-1,1]; arousal, surprise, warmth ∈ [0,1].
- Confidence reflects extraction reliability.

# QUALITY CHECKS
- JSON must parse.
- All refs must be valid spans.
- Punchlines must build from setups/wordplay.
- No offensive or unsafe humor.
- Ensure humor extraction is factual and grounded in NOTE_TEXT.
)
        """)

        # ---------------- Hopeful ----------------
        self.Hopeful_instruction = _fill("""\
        # INPUT CONTEXT
        MOOD: Hopeful
        NOTE_ID: ${NOTE_ID}
        NOTE_DATE: ${NOTE_DATE}
        LANGUAGE_HINT: "en"
        NOTE_TEXT:

        ${NOTE_TEXT}

        # REQUIRED OUTPUT SHAPE (HopefulSignalPack JSON)
        {
          "version": 1,
          "extraction_timestamp": "<auto or ~>",
          "language": "<'en' or inferred>",
          "source_length_chars": <int>,

          "valence": <float -1..1>,
          "arousal": <float 0..1>,
          "confidence": <float 0..1>,
          "agency_0_1": 0.0,
          "clarity_0_1": 0.0,
          "feasibility_0_1": 0.0,
          "optimism_0_1": 0.0,

          "embedding": null,

          "quotes": [
            { "text":"...", "start":<int>, "end":<int>, "purpose":"goal|path|support" }
          ],
          "spans": [
            { "span_id":"s1", "start":<int>, "end":<int>, "text":"<exact substring>" }
          ],

          "goals": [
            { "type":"short_term|long_term|vision", "description":"...", "why_it_matters":"...",
              "time_horizon":"today|this_week|this_month|quarter|year|later",
              "priority_0_1":0.0, "evidence_ref":"s1" }
          ],
          "pathways": [
            { "step":"...", "rationale":"...", "resources_needed":["..."], "effort_0_1":0.0,
              "dependency":"...", "evidence_ref":"s2" }
          ],
          "supports": [
            { "kind":"person|team|mentor|tool|environment|habit", "name_or_desc":"...",
              "strength_0_1":0.0, "availability":"now|soon|uncertain", "evidence_ref":"s3" }
          ],
          "blockers": [
            { "obstacle":"...", "severity_0_1":0.0, "likelihood_0_1":0.0, "mitigation":"...",
              "owner":"self|other|unknown", "evidence_ref":"s4" }
          ],
          "milestones": [
            { "marker":"...", "metric":"...", "target_date":"YYYY-MM-DD|~", "confidence_0_1":0.0, "evidence_ref":"s5" }
          ],
          "commitments": [
            { "action":"...", "deadline":"YYYY-MM-DD|~", "effort_0_1":0.0, "risk_if_skipped":"...", "evidence_ref":"s6" }
          ],
          "small_wins": [
            { "win":"...", "evidence_quote":"...", "impact_0_1":0.0 }
          ],
          "reframes": [
            { "from":"...", "to":"...", "proof_quote":"...", "strengthened_value":"..." }
          ],
          "values_alignment": [
            { "value":"...", "alignment_0_1":0.0, "span_ref":"s7" }
          ],
          "contingencies": [
            { "trigger":"...", "alternative_path":"...", "cost_0_1":0.0, "evidence_ref":"s8" }
          ],
          "uncertainties": [
            { "question":"...", "information_needed":"...", "owner":"self|other|unknown" }
          ],
          "hopeful_emotions": [
            { "label":"hope|anticipation|confidence|curiosity", "intensity_0_1":0.0, "trigger_ref":"s9" }
          ],
          "visualizations": [
            { "image":"...", "span_ref":"s10" }
          ],
          "invitations": [
            { "kind":"invite|offer|referral|warm_intro|acceptance", "details":"...", "likelihood_0_1":0.0, "span_ref":"s11" }
          ],

          "tag_keywords": ["..."],
          "entity_map": { "people":[], "orgs":[], "places":[], "objects":[] },
          "dominant_items": { "top_goal_idx":null, "top_pathway_idx":null, "top_support_idx":null }
        }

        # EXTRACTION GUIDELINES
        (1) GOALS
- Extract all user aspirations: short-term, long-term, or vision-level.
- Include why it matters and the expected time horizon.

2) PATHWAYS
- Identify concrete steps or strategies; include rationale and resources.

3) SUPPORTS
- Capture people, tools, habits, or environments that can help.
- Note strength and availability.

4) BLOCKERS
- Extract obstacles and possible mitigations; specify owner (self/other).

5) MILESTONES & COMMITMENTS
- Identify explicit targets, markers of progress, and user commitments.

6) SMALL WINS
- Note past successes, even minor ones, to seed hope.

7) REFRAMES
- Capture shifts in perspective that renew motivation or possibility.

8) VALUES ALIGNMENT
- Link hopes to deeper personal values.

9) CONTINGENCIES
- If Plan A fails, capture Plan B/C alternatives.

10) UNCERTAINTIES
- Extract open questions or unclear areas the user is reflecting on.

11) EMOTIONS & VISUALIZATIONS
- Capture feelings of hope, anticipation, confidence, curiosity.
- Extract future imagery if vivid scenes are described.

12) INVITATIONS
- Note external opportunities, offers, or referrals that reinforce hope.

13) SCORING
- valence ∈ [-1,1]; arousal ∈ [0,1].
- agency, clarity, feasibility, optimism ∈ [0,1].
- confidence reflects extraction reliability.

# QUALITY CHECKS
- JSON must parse.
- All evidence_ref/span_ref must match spans[*].span_id.
- No hallucinated goals, steps, or opportunities.
- Ensure structure reflects NOTE_TEXT faithfully.)
        """)
