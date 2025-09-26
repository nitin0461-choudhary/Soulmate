from django.db import models
from authentication.models import Login_model
from django.utils import timezone


class new_notes(models.Model):
    user_notes = models.ForeignKey(Login_model, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    note_title = models.CharField(max_length=255)
    note_description = models.CharField(max_length=400)

    def __str__(self):
        return f"{self.note_title}"


class general_agent(models.Model):
    """
    One per (note). Neutral, context-preserving extraction for the 'General' mood.
    """
    note = models.ForeignKey(
        "new_notes",
        on_delete=models.CASCADE,
        related_name="general_signal_pack",
        db_column="general_notes_id",
    )

    # --- Core metadata ---
    version = models.IntegerField(default=1)
    extraction_timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=10, default="en")
    source_length_chars = models.IntegerField(default=0)

    # Scalar signals
    valence = models.FloatField(default=0.0)
    arousal = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)
    certainty_0_1 = models.FloatField(default=0.0)
    importance_0_1 = models.FloatField(default=0.0)

    # Embedding
    embedding = models.JSONField(null=True, blank=True)

    # Evidence
    quotes = models.JSONField(default=list)
    spans = models.JSONField(default=list)

    # Canonical content
    abstract = models.TextField(blank=True, default="")
    key_facts = models.JSONField(default=list)
    entities = models.JSONField(default=dict)
    timeline = models.JSONField(default=list)
    topics = models.JSONField(default=list)
    open_questions = models.JSONField(default=list)
    decisions = models.JSONField(default=list)
    actions = models.JSONField(default=list)
    risks = models.JSONField(default=list)
    metrics = models.JSONField(default=list)
    references = models.JSONField(default=list)
    constraints = models.JSONField(default=list)
    assumptions = models.JSONField(default=list)
    comparisons = models.JSONField(default=list)
    mood_hints = models.JSONField(default=dict)

    # Index helpers
    tag_keywords = models.JSONField(default=list)
    entity_map = models.JSONField(default=dict)
    dominant_items = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("note",),)
        indexes = [
            models.Index(name="general_tags_idx", fields=["tag_keywords"]),
        ]

    # Validators
    def clean(self):
        def clamp(v, lo, hi):
            try:
                v = float(v)
            except Exception:
                return lo
            return max(lo, min(hi, v))

        self.valence = clamp(self.valence, -1.0, 1.0)
        self.arousal = clamp(self.arousal, 0.0, 1.0)
        self.confidence = clamp(self.confidence, 0.0, 1.0)
        self.certainty_0_1 = clamp(self.certainty_0_1, 0.0, 1.0)
        self.importance_0_1 = clamp(self.importance_0_1, 0.0, 1.0)
        if not isinstance(self.entity_map, dict):
            self.entity_map = {}
        if not isinstance(self.dominant_items, dict):
            self.dominant_items = {}

    # Helpers
    @property
    def top_fact(self):
        idx = (self.dominant_items or {}).get("top_fact_idx")
        items = self.key_facts or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_task(self):
        idx = (self.dominant_items or {}).get("top_task_idx")
        items = self.actions or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_decision(self):
        idx = (self.dominant_items or {}).get("top_decision_idx")
        items = self.decisions or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    def brief_context(self, include_quote=True):
        parts = []
        if self.abstract:
            parts.append(f"Abstract: {self.abstract}")
        if self.top_fact:
            parts.append(f"Key fact: {self.top_fact.get('fact','')}")
        if self.top_decision:
            parts.append(
                f"Decision: {self.top_decision.get('decision','')} ({self.top_decision.get('status','')})"
            )
        if self.top_task:
            parts.append(
                f"Next task: {self.top_task.get('task','')} due {self.top_task.get('due','~')}"
            )
        if include_quote and self.quotes:
            parts.append(f'Quote: "{self.quotes[0].get("text","")}"')
        return "\n".join(parts)

    def __str__(self):
        return f"{self.note.note_title}"


class Happy_agent(models.Model):
    note = models.ForeignKey(
        "new_notes",
        on_delete=models.CASCADE,
        related_name="happy_signal_pack",
        db_column="general_notes_id",
    )

    # Core metadata
    version = models.IntegerField(default=1)
    extraction_timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=10, default="en")
    source_length_chars = models.IntegerField(default=0)

    # Scalars
    valence = models.FloatField(default=0.0)
    arousal = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)

    # Data
    embedding = models.JSONField(null=True, blank=True)
    quotes = models.JSONField(default=list)
    spans = models.JSONField(default=list)
    positive_events = models.JSONField(default=list)
    outcomes = models.JSONField(default=list)

    # Correct spelling at the model level, but keep old DB column names for compatibility
    gratitude = models.JSONField(default=list, db_column="graditude")
    pleasant_emotions = models.JSONField(default=list)
    strengths = models.JSONField(default=list)
    social_ties = models.JSONField(default=list)
    growth = models.JSONField(default=list)
    future_positives = models.JSONField(default=list)
    activities = models.JSONField(default=list)
    sensory = models.JSONField(default=list)
    humor = models.JSONField(default=list)
    comparatives = models.JSONField(default=list)
    obstacles_overcome = models.JSONField(default=list)
    values_alignment = models.JSONField(default=list)
    artifacts = models.JSONField(default=list)
    state_metrics = models.JSONField(default=dict)

    risks_or_concerns = models.JSONField(default=list, db_column="risks_or_concers")
    boundaries_to_respect = models.JSONField(default=list)

    # Index helpers
    tag_keywords = models.JSONField(default=list)
    entity_map = models.JSONField(default=dict)
    dominant_items = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("note",),)
        indexes = [
            models.Index(name="happy_tags_idx", fields=["tag_keywords"]),
        ]

    def clean(self):
        self.valence = max(-1.0, min(1.0, float(self.valence)))
        self.arousal = max(0.0, min(1.0, float(self.arousal)))
        self.confidence = max(0.0, min(1.0, float(self.confidence)))
        if not isinstance(self.state_metrics, dict):
            self.state_metrics = {}

    @property
    def top_event(self):
        idx = (self.dominant_items or {}).get("top_event_idx")
        pe = self.positive_events or []
        return pe[idx] if isinstance(idx, int) and 0 <= idx < len(pe) else None

    @property
    def top_outcome(self):
        idx = (self.dominant_items or {}).get("top_outcome_idx")
        oc = self.outcomes or []
        return oc[idx] if isinstance(idx, int) and 0 <= idx < len(oc) else None

    @property
    def top_emotion(self):
        idx = (self.dominant_items or {}).get("top_emotion_idx")
        em = self.pleasant_emotions or []
        return em[idx] if isinstance(idx, int) and 0 <= idx < len(em) else None

    def brief_context(self, bullets=2, include_quote=True):
        parts = []
        if self.top_event:
            parts.append(f"Top event: {self.top_event.get('what_happened','')}")
        if self.top_outcome:
            parts.append(f"Outcome: {self.top_outcome.get('result','')}")
        if self.top_emotion:
            parts.append(
                f"Emotion: {self.top_emotion.get('label','')} ({self.top_emotion.get('intensity_0_1',0)})"
            )
        if include_quote and self.quotes:
            parts.append(f'Quote: "{self.quotes[0].get("text","")}"')
        for g in (self.gratitude or [])[:bullets]:
            parts.append(f"Gratitude -> {g.get('target','')}: {g.get('reason','')}")
        for act in (self.activities or [])[:1]:
            parts.append(f"Activity -> {act.get('category','')}: {act.get('description','')}")
        return "\n".join(parts)

    def __str__(self):
        return f"{self.note.note_title}"


class Hopeful_agent(models.Model):
    note = models.ForeignKey(
        "new_notes",
        on_delete=models.CASCADE,
        related_name="hopeful_signal_pack",
        db_column="general_notes_id",
    )

    # Core metadata
    version = models.IntegerField(default=1)
    extraction_timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=10, default="en")
    source_length_chars = models.IntegerField(default=0)

    # Scalars
    valence = models.FloatField(default=0.0)
    arousal = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)
    agency_0_1 = models.FloatField(default=0.0)
    clarity_0_1 = models.FloatField(default=0.0)
    feasibility_0_1 = models.FloatField(default=0.0)
    optimism_0_1 = models.FloatField(default=0.0)

    embedding = models.JSONField(null=True, blank=True)
    quotes = models.JSONField(default=list)
    spans = models.JSONField(default=list)

    goals = models.JSONField(default=list)
    pathways = models.JSONField(default=list)
    supports = models.JSONField(default=list)
    blockers = models.JSONField(default=list)
    milestones = models.JSONField(default=list)
    commitments = models.JSONField(default=list)
    small_wins = models.JSONField(default=list)
    reframes = models.JSONField(default=list)
    values_alignment = models.JSONField(default=list)
    contingencies = models.JSONField(default=list)
    uncertainties = models.JSONField(default=list)
    hopeful_emotions = models.JSONField(default=list)
    visualizations = models.JSONField(default=list)
    invitations = models.JSONField(default=list)

    tag_keywords = models.JSONField(default=list)
    entity_map = models.JSONField(default=dict)
    dominant_items = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("note",),)
        indexes = [
            models.Index(name="hopeful_tags_idx", fields=["tag_keywords"]),
        ]

    def clean(self):
        def clamp(v, lo, hi):
            try:
                v = float(v)
            except Exception:
                return lo
            return max(lo, min(hi, v))

        self.valence = clamp(self.valence, -1.0, 1.0)
        self.arousal = clamp(self.arousal, 0.0, 1.0)
        self.confidence = clamp(self.confidence, 0.0, 1.0)
        self.agency_0_1 = clamp(self.agency_0_1, 0.0, 1.0)
        self.clarity_0_1 = clamp(self.clarity_0_1, 0.0, 1.0)
        self.feasibility_0_1 = clamp(self.feasibility_0_1, 0.0, 1.0)
        self.optimism_0_1 = clamp(self.optimism_0_1, 0.0, 1.0)
        if not isinstance(self.entity_map, dict):
            self.entity_map = {}
        if not isinstance(self.dominant_items, dict):
            self.dominant_items = {}

    @property
    def top_goal(self):
        idx = (self.dominant_items or {}).get("top_goal_idx")
        items = self.goals or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_pathway(self):
        idx = (self.dominant_items or {}).get("top_pathway_idx")
        items = self.pathways or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_support(self):
        idx = (self.dominant_items or {}).get("top_support_idx")
        items = self.supports or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    def brief_context(self, bullets=2, include_quote=True):
        parts = []
        if self.top_goal:
            parts.append(f"Top goal: {self.top_goal.get('description','')}")
        if self.top_pathway:
            parts.append(f"Key pathway: {self.top_pathway.get('step','')}")
        if self.top_support:
            parts.append(
                f"Support: {self.top_support.get('name_or_desc','')} (strength {self.top_support.get('strength_0_1',0)})"
            )
        for w in (self.small_wins or [])[:1]:
            parts.append(f"Small win: {w.get('win','')}")
        for m in (self.milestones or [])[:1]:
            parts.append(f"Milestone: {m.get('marker','')} → {m.get('target_date','')}")
        for c in (self.commitments or [])[:1]:
            parts.append(f"Next action: {c.get('action','')} by {c.get('deadline','')}")
        if include_quote and self.quotes:
            parts.append(f'Quote: "{self.quotes[0].get("text","")}"')
        return "\n".join(parts)

    def __str__(self):
        return f"{self.note.note_title}"


class Reflective_agent(models.Model):
    note = models.ForeignKey(
        "new_notes",
        on_delete=models.CASCADE,
        related_name="reflective_signal_pack",
        db_column="general_notes_id",
    )

    # Core metadata
    version = models.IntegerField(default=1)
    extraction_timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=10, default="en")
    source_length_chars = models.IntegerField(default=0)

    # Scalars
    valence = models.FloatField(default=0.0)
    arousal = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)
    depth_0_1 = models.FloatField(default=0.0)
    clarity_0_1 = models.FloatField(default=0.0)

    embedding = models.JSONField(null=True, blank=True)
    quotes = models.JSONField(default=list)
    spans = models.JSONField(default=list)

    events_recalled = models.JSONField(default=list)
    lessons = models.JSONField(default=list)
    mistakes = models.JSONField(default=list)
    reframes = models.JSONField(default=list)
    patterns = models.JSONField(default=list)
    values_alignment = models.JSONField(default=list)
    growth_edges = models.JSONField(default=list)
    open_questions = models.JSONField(default=list)
    turning_points = models.JSONField(default=list)
    comparisons = models.JSONField(default=list)
    gratitude = models.JSONField(default=list)
    regrets = models.JSONField(default=list)
    future_adjustments = models.JSONField(default=list)

    tag_keywords = models.JSONField(default=list)
    entity_map = models.JSONField(default=dict)
    dominant_items = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("note",),)
        indexes = [
            models.Index(name="reflective_tags_idx", fields=["tag_keywords"]),
        ]

    def clean(self):
        def clamp(v, lo, hi):
            try:
                v = float(v)
            except Exception:
                return lo
            return max(lo, min(hi, v))

        self.valence = clamp(self.valence, -1.0, 1.0)
        self.arousal = clamp(self.arousal, 0.0, 1.0)
        self.confidence = clamp(self.confidence, 0.0, 1.0)
        self.depth_0_1 = clamp(self.depth_0_1, 0.0, 1.0)
        self.clarity_0_1 = clamp(self.clarity_0_1, 0.0, 1.0)
        if not isinstance(self.entity_map, dict):
            self.entity_map = {}
        if not isinstance(self.dominant_items, dict):
            self.dominant_items = {}

    @property
    def top_lesson(self):
        idx = (self.dominant_items or {}).get("top_lesson_idx")
        items = self.lessons or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_reframe(self):
        idx = (self.dominant_items or {}).get("top_reframe_idx")
        items = self.reframes or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_growth_edge(self):
        idx = (self.dominant_items or {}).get("top_growth_edge_idx")
        items = self.growth_edges or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    def brief_context(self, include_quote=True):
        parts = []
        if self.top_lesson:
            parts.append(f"Lesson: {self.top_lesson.get('lesson','')}")
        if self.top_reframe:
            parts.append(f"Reframe: {self.top_reframe.get('from','')} → {self.top_reframe.get('to','')}")
        if self.top_growth_edge:
            parts.append(
                f"Growth edge: {self.top_growth_edge.get('strength','')} / {self.top_growth_edge.get('improvement_needed','')}"
            )
        if include_quote and self.quotes:
            parts.append(f'Quote: "{self.quotes[0].get("text","")}"')
        return "\n".join(parts)

    def __str__(self):
        return f"{self.note.note_title}"


class motivation_agent(models.Model):
    note = models.ForeignKey(
        "new_notes",
        on_delete=models.CASCADE,
        related_name="motivation_signal_pack",
        db_column="general_notes_id",
    )

    # Core metadata
    version = models.IntegerField(default=1)
    extraction_timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=10, default="en")
    source_length_chars = models.IntegerField(default=0)

    # Scalars
    valence = models.FloatField(default=0.0)
    arousal = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)
    drive_strength_0_1 = models.FloatField(default=0.0)
    clarity_0_1 = models.FloatField(default=0.0)
    feasibility_0_1 = models.FloatField(default=0.0)
    commitment_0_1 = models.FloatField(default=0.0)

    embedding = models.JSONField(null=True, blank=True)
    quotes = models.JSONField(default=list)
    spans = models.JSONField(default=list)

    goals = models.JSONField(default=list)
    anti_goals = models.JSONField(default=list)
    drivers = models.JSONField(default=list)
    identity_claims = models.JSONField(default=list)
    implementation_intentions = models.JSONField(default=list)
    next_actions = models.JSONField(default=list)
    time_blocks = models.JSONField(default=list)
    habits = models.JSONField(default=list)
    cues_triggers = models.JSONField(default=list)
    rewards = models.JSONField(default=list)
    accountability = models.JSONField(default=list)
    obstacles = models.JSONField(default=list)
    environment_design = models.JSONField(default=list)
    leverage_points = models.JSONField(default=list)
    progress_markers = models.JSONField(default=list)
    streaks = models.JSONField(default=list)
    fallback_plans = models.JSONField(default=list)
    pep_talk_lines = models.JSONField(default=list)
    readiness_state = models.JSONField(default=dict)

    tag_keywords = models.JSONField(default=list)
    entity_map = models.JSONField(default=dict)
    dominant_items = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("note",),)
        indexes = [
            models.Index(name="motivation_tags_idx", fields=["tag_keywords"]),
        ]

    def clean(self):
        def clamp(v, lo, hi):
            try:
                v = float(v)
            except Exception:
                return lo
            return max(lo, min(hi, v))

        self.valence = clamp(self.valence, -1.0, 1.0)
        self.arousal = clamp(self.arousal, 0.0, 1.0)
        self.confidence = clamp(self.confidence, 0.0, 1.0)
        self.drive_strength_0_1 = clamp(self.drive_strength_0_1, 0.0, 1.0)
        self.clarity_0_1 = clamp(self.clarity_0_1, 0.0, 1.0)
        self.feasibility_0_1 = clamp(self.feasibility_0_1, 0.0, 1.0)
        self.commitment_0_1 = clamp(self.commitment_0_1, 0.0, 1.0)
        if not isinstance(self.entity_map, dict):
            self.entity_map = {}
        if not isinstance(self.dominant_items, dict):
            self.dominant_items = {}

    @property
    def top_goal(self):
        idx = (self.dominant_items or {}).get("top_goal_idx")
        items = self.goals or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_action(self):
        idx = (self.dominant_items or {}).get("top_action_idx")
        items = self.next_actions or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_driver(self):
        idx = (self.dominant_items or {}).get("top_driver_idx")
        items = self.drivers or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    def brief_context(self, include_quote=True):
        parts = []
        if self.top_goal:
            g = self.top_goal
            parts.append(
                f"Goal: {g.get('description','')} (metric: {g.get('metric','')}, deadline: {g.get('deadline','~')})"
            )
        if self.top_driver:
            d = self.top_driver
            parts.append(f"Driver: {d.get('label','')} ({d.get('kind','')})")
        if self.top_action:
            a = self.top_action
            parts.append(
                f"Next action: {a.get('action','')} @ {a.get('context','')} ({a.get('duration_min',0)} min)"
            )
        if self.implementation_intentions:
            ii = self.implementation_intentions[0]
            parts.append(f"If {ii.get('if','...')} then {ii.get('then','...')} [{ii.get('context','')}]")
        if self.environment_design:
            ed = self.environment_design[0]
            parts.append(f"Environment: {ed.get('change','')} → {ed.get('effect','')}")
        if include_quote and self.quotes:
            parts.append(f'Quote: "{self.quotes[0].get("text","")}"')
        return "\n".join(parts)

    def __str__(self):
        return f"{self.note.note_title}"


class calm_agent(models.Model):
    """
    One per (note). Structured extraction for the 'Calm' mood.
    """
    note = models.ForeignKey(
        "new_notes",
        on_delete=models.CASCADE,
        related_name="calm_signal_pack",
        db_column="general_notes_id",
    )

    # Core metadata
    version = models.IntegerField(default=1)
    extraction_timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=10, default="en")
    source_length_chars = models.IntegerField(default=0)

    # Scalars
    valence = models.FloatField(default=0.0)
    arousal = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)
    serenity_0_1 = models.FloatField(default=0.0)
    safety_0_1 = models.FloatField(default=0.0)
    balance_0_1 = models.FloatField(default=0.0)
    clarity_0_1 = models.FloatField(default=0.0)

    embedding = models.JSONField(null=True, blank=True)
    quotes = models.JSONField(default=list)
    spans = models.JSONField(default=list)

    tranquil_moments = models.JSONField(default=list)
    soothing_activities = models.JSONField(default=list)
    calming_environments = models.JSONField(default=list)
    sensory_anchors = models.JSONField(default=list)
    stressors_reduced = models.JSONField(default=list)
    coping_strategies = models.JSONField(default=list)
    grounding_practices = models.JSONField(default=list)
    routines = models.JSONField(default=list)
    safe_people = models.JSONField(default=list)
    affirmations = models.JSONField(default=list)
    values_alignment = models.JSONField(default=list)
    releases = models.JSONField(default=list)
    recovery_signals = models.JSONField(default=list)
    calm_disturbances = models.JSONField(default=list)
    future_practices = models.JSONField(default=list)

    tag_keywords = models.JSONField(default=list)
    entity_map = models.JSONField(default=dict)
    dominant_items = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("note",),)
        indexes = [
            models.Index(name="calm_tags_idx", fields=["tag_keywords"]),
        ]

    def clean(self):
        def clamp(v, lo, hi):
            try:
                v = float(v)
            except Exception:
                return lo
            return max(lo, min(hi, v))

        self.valence = clamp(self.valence, -1.0, 1.0)
        self.arousal = clamp(self.arousal, 0.0, 1.0)
        self.confidence = clamp(self.confidence, 0.0, 1.0)
        self.serenity_0_1 = clamp(self.serenity_0_1, 0.0, 1.0)
        self.safety_0_1 = clamp(self.safety_0_1, 0.0, 1.0)
        self.balance_0_1 = clamp(self.balance_0_1, 0.0, 1.0)
        self.clarity_0_1 = clamp(self.clarity_0_1, 0.0, 1.0)
        if not isinstance(self.entity_map, dict):
            self.entity_map = {}
        if not isinstance(self.dominant_items, dict):
            self.dominant_items = {}

    @property
    def top_activity(self):
        idx = (self.dominant_items or {}).get("top_activity_idx")
        items = self.soothing_activities or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_anchor(self):
        idx = (self.dominant_items or {}).get("top_anchor_idx")
        items = self.sensory_anchors or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_routine(self):
        idx = (self.dominant_items or {}).get("top_routine_idx")
        items = self.routines or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    def brief_context(self, include_quote=True):
        parts = []
        if self.top_activity:
            parts.append(f"Soothing activity: {self.top_activity.get('activity','')}")
        if self.top_anchor:
            parts.append(
                f"Sensory anchor: {self.top_anchor.get('modality','')} – {self.top_anchor.get('detail','')}"
            )
        if self.top_routine:
            parts.append(
                f"Routine: {self.top_routine.get('routine','')} @ {self.top_routine.get('time','')}"
            )
        if self.releases:
            r = self.releases[0]
            parts.append(f"Released: {r.get('released','')} → relief {r.get('relief_0_1',0)}")
        if include_quote and self.quotes:
            parts.append(f'Quote: "{self.quotes[0].get("text","")}"')
        return "\n".join(parts)

    def __str__(self):
        return f"{self.note.note_title}"


class Dramatic_agent(models.Model):
    note = models.ForeignKey(
        "new_notes",
        on_delete=models.CASCADE,
        related_name="dramatic_signal_pack",
        db_column="general_notes_id",
    )

    # Core metadata
    version = models.IntegerField(default=1)
    extraction_timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=10, default="en")
    source_length_chars = models.IntegerField(default=0)

    # Scalars
    valence = models.FloatField(default=0.0)
    arousal = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)
    intensity_0_1 = models.FloatField(default=0.0)
    tension_0_1 = models.FloatField(default=0.0)
    stakes_0_1 = models.FloatField(default=0.0)
    pace_0_1 = models.FloatField(default=0.0)
    contrast_0_1 = models.FloatField(default=0.0)

    embedding = models.JSONField(null=True, blank=True)
    quotes = models.JSONField(default=list)
    spans = models.JSONField(default=list)

    settings = models.JSONField(default=list)
    characters = models.JSONField(default=list)
    stakes = models.JSONField(default=list)
    conflicts = models.JSONField(default=list)
    inciting_incident = models.JSONField(default=dict)
    escalations = models.JSONField(default=list)
    reversals = models.JSONField(default=list)
    turning_points = models.JSONField(default=list)
    climax = models.JSONField(default=dict)
    resolution = models.JSONField(default=dict)
    catharsis = models.JSONField(default=dict)
    themes = models.JSONField(default=list)
    motifs = models.JSONField(default=list)
    symbols = models.JSONField(default=list)
    imagery = models.JSONField(default=list)
    beat_sheet = models.JSONField(default=list)
    three_act_map = models.JSONField(default=dict)
    heros_journey = models.JSONField(default=dict)
    setup_payoff_links = models.JSONField(default=list)
    suspense_devices = models.JSONField(default=list)
    open_questions = models.JSONField(default=list)
    risks_or_concerns = models.JSONField(default=list)
    boundaries_to_respect = models.JSONField(default=list)

    tag_keywords = models.JSONField(default=list)
    entity_map = models.JSONField(default=dict)
    dominant_items = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("note",),)
        indexes = [
            models.Index(name="dramatic_tags_idx", fields=["tag_keywords"]),
        ]

    def clean(self):
        def clamp(v, lo, hi):
            try:
                v = float(v)
            except Exception:
                return lo
            return max(lo, min(hi, v))

        self.valence = clamp(self.valence, -1.0, 1.0)
        self.arousal = clamp(self.arousal, 0.0, 1.0)
        self.confidence = clamp(self.confidence, 0.0, 1.0)
        self.intensity_0_1 = clamp(self.intensity_0_1, 0.0, 1.0)
        self.tension_0_1 = clamp(self.tension_0_1, 0.0, 1.0)
        self.stakes_0_1 = clamp(self.stakes_0_1, 0.0, 1.0)
        self.pace_0_1 = clamp(self.pace_0_1, 0.0, 1.0)
        self.contrast_0_1 = clamp(self.contrast_0_1, 0.0, 1.0)
        if not isinstance(self.entity_map, dict):
            self.entity_map = {}
        if not isinstance(self.dominant_items, dict):
            self.dominant_items = {}

    @property
    def top_stake(self):
        idx = (self.dominant_items or {}).get("top_stake_idx")
        items = self.stakes or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_conflict(self):
        idx = (self.dominant_items or {}).get("top_conflict_idx")
        items = self.conflicts or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_reversal(self):
        idx = (self.dominant_items or {}).get("top_reversal_idx")
        items = self.reversals or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    def brief_context(self, include_quote=True):
        parts = []
        if self.inciting_incident:
            parts.append(f"Inciting: {self.inciting_incident.get('what_happened','')}")
        if self.top_stake:
            parts.append(
                f"Stake: {self.top_stake.get('description','')} (sev {self.top_stake.get('severity_0_1',0)})"
            )
        if self.top_conflict:
            parts.append(f"Conflict: {self.top_conflict.get('issue','')}")
        if self.top_reversal:
            parts.append(f"Reversal: {self.top_reversal.get('what_changed','')}")
        if self.climax:
            parts.append(f"Climax: {self.climax.get('moment','')} → {self.climax.get('result','')}")
        if self.resolution:
            parts.append(f"Resolution: {self.resolution.get('status','')}")
        if include_quote and self.quotes:
            parts.append(f'Quote: "{self.quotes[0].get("text","")}"')
        return "\n".join(parts)

    def __str__(self):
        return f"{self.note.note_title}"


class Funny_agent(models.Model):
    note = models.ForeignKey(
        "new_notes",
        on_delete=models.CASCADE,
        related_name="funny_signal_pack",
        db_column="general_notes_id",
    )

    # Core metadata
    version = models.IntegerField(default=1)
    extraction_timestamp = models.DateTimeField(default=timezone.now)
    language = models.CharField(max_length=10, default="en")
    source_length_chars = models.IntegerField(default=0)

    # Scalars
    valence = models.FloatField(default=0.0)
    arousal = models.FloatField(default=0.0)
    confidence = models.FloatField(default=0.0)
    surprise_0_1 = models.FloatField(default=0.0)
    warmth_0_1 = models.FloatField(default=0.0)

    embedding = models.JSONField(null=True, blank=True)
    quotes = models.JSONField(default=list)
    spans = models.JSONField(default=list)

    persona = models.JSONField(default=dict)
    audience = models.JSONField(default=dict)
    setups = models.JSONField(default=list)
    benign_violations = models.JSONField(default=list)
    wordplay = models.JSONField(default=list)
    amplifiers = models.JSONField(default=list)
    callbacks = models.JSONField(default=list)
    observations = models.JSONField(default=list)
    situational = models.JSONField(default=list)
    punchlines = models.JSONField(default=list)
    delivery = models.JSONField(default=dict)
    sensitivity_flags = models.JSONField(default=list)
    boundaries_to_respect = models.JSONField(default=list)
    redlines = models.JSONField(default=list)
    references = models.JSONField(default=list)

    tag_keywords = models.JSONField(default=list)
    entity_map = models.JSONField(default=dict)
    dominant_items = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("note",),)
        indexes = [
            models.Index(name="funny_tags_idx", fields=["tag_keywords"]),
        ]

    def clean(self):
        def clamp(v, lo, hi):
            try:
                v = float(v)
            except Exception:
                return lo
            return max(lo, min(hi, v))

        self.valence = clamp(self.valence, -1.0, 1.0)
        self.arousal = clamp(self.arousal, 0.0, 1.0)
        self.confidence = clamp(self.confidence, 0.0, 1.0)
        self.surprise_0_1 = clamp(self.surprise_0_1, 0.0, 1.0)
        self.warmth_0_1 = clamp(self.warmth_0_1, 0.0, 1.0)
        if not isinstance(self.entity_map, dict):
            self.entity_map = {}
        if not isinstance(self.dominant_items, dict):
            self.dominant_items = {}

    @property
    def top_setup(self):
        idx = (self.dominant_items or {}).get("top_setup_idx")
        items = self.setups or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_punch(self):
        idx = (self.dominant_items or {}).get("top_punch_idx")
        items = self.punchlines or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    @property
    def top_wordplay(self):
        idx = (self.dominant_items or {}).get("top_wordplay_idx")
        items = self.wordplay or []
        return items[idx] if (isinstance(idx, int) and 0 <= idx < len(items)) else None

    def brief_context(self, include_quote=True):
        parts = []
        if self.top_setup:
            parts.append(f"Setup: {self.top_setup.get('premise','')}")
        if self.top_wordplay:
            parts.append(
                f"Wordplay: {self.top_wordplay.get('hook','')} ({self.top_wordplay.get('type','')})"
            )
        if self.top_punch:
            parts.append(f"Punch candidate: {self.top_punch.get('line','')}")
        if self.callbacks:
            parts.append(f"Callback: {self.callbacks[0].get('reference','')}")
        if include_quote and self.quotes:
            parts.append(f'Quote: "{self.quotes[0].get("text","")}"')
        return "\n".join(parts)

    def __str__(self):
        return f"{self.note.note_title}"
