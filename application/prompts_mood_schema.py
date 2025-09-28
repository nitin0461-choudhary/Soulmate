class mood_schema:
    def __init__(self):
        self.General={
  "mood_name": "General",
  "version": 1,
  "description": "Neutral, context-preserving extraction for the 'General' mood. Canonical, style-free source of truth.",
  "fields": {
    "version": { "type": "integer", "default": 1, "description": "Schema/payload version." },
    "extraction_timestamp": { "type": "string", "format": "date-time", "description": "When this extraction was produced." },
    "language": { "type": "string", "description": "BCP-47 or 2-letter code of detected language; default 'en'." },
    "source_length_chars": { "type": "integer", "min": 0, "description": "Length of source note text in characters." },

    "valence": { "type": "number", "min": -1.0, "max": 1.0, "description": "Overall pleasantness (-1..+1)." },
    "arousal": { "type": "number", "min": 0.0, "max": 1.0, "description": "Emotional intensity (0..1)." },
    "confidence": { "type": "number", "min": 0.0, "max": 1.0, "description": "Extractor confidence (0..1)." },
    "certainty_0_1": { "type": "number", "min": 0.0, "max": 1.0, "description": "Estimated factual certainty (0..1)." },
    "importance_0_1": { "type": "number", "min": 0.0, "max": 1.0, "description": "Overall importance of the note (0..1)." },

    "embedding": {
      "type": ["array", "object", "null"],
      "items": { "type": "number" },
      "description": "Optional vector embedding or provider-specific payload."
    },

    "quotes": {
      "type": "array",
      "description": "Short verbatim quotes with offsets and purpose.",
      "items": {
        "type": "object",
        "properties": {
          "text": { "type": "string" },
          "start": { "type": "integer", "min": 0 },
          "end": { "type": "integer", "min": 0 },
          "purpose": { "type": "string", "enum": ["fact", "decision", "task", "reference", "other"] }
        },
        "required": ["text"]
      }
    },

    "spans": {
      "type": "array",
      "description": "Evidence spans for traceability.",
      "items": {
        "type": "object",
        "properties": {
          "span_id": { "type": "string" },
          "start": { "type": "integer", "min": 0 },
          "end": { "type": "integer", "min": 0 },
          "text": { "type": "string" }
        },
        "required": ["span_id", "text"]
      }
    },

    "abstract": { "type": "string", "description": "Short neutral summary (~80–120 words)." },

    "key_facts": {
      "type": "array",
      "description": "Atomic, mood-neutral facts.",
      "items": {
        "type": "object",
        "properties": {
          "fact": { "type": "string" },
          "evidence_ref": { "type": "string", "description": "span_id or quote ref" },
          "certainty_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
          "timestamp": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|~)$" }
        },
        "required": ["fact"]
      }
    },

    "entities": {
      "type": "object",
      "description": "Recognized entities grouped by type.",
      "properties": {
        "people": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "role": { "type": ["string", "null"] },
              "span_ref": { "type": ["string", "null"] }
            },
            "required": ["name"]
          }
        },
        "orgs": { "$ref": "#/definitions/entityItemArray" },
        "places": { "$ref": "#/definitions/entityItemArray" },
        "objects": { "$ref": "#/definitions/entityItemArray" }
      },
      "additionalProperties": "false"
    },

    "timeline": {
      "type": "array",
      "description": "Ordered events.",
      "items": {
        "type": "object",
        "properties": {
          "when": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|~)$" },
          "event": { "type": "string" },
          "detail": { "type": ["string", "null"] },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["event"]
      }
    },

    "topics": {
      "type": "array",
      "description": "Neutral tags and scores.",
      "items": {
        "type": "object",
        "properties": {
          "topic": { "type": "string" },
          "score_0_1": { "type": "number", "min": 0.0, "max": 1.0 }
        },
        "required": ["topic"]
      }
    },

    "open_questions": {
      "type": "array",
      "description": "Unknowns or clarifications needed.",
      "items": {
        "type": "object",
        "properties": {
          "question": { "type": "string" },
          "info_needed": { "type": ["string", "null"] },
          "owner": { "type": "string", "enum": ["self", "other", "unknown"] },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["question"]
      }
    },

    "decisions": {
      "type": "array",
      "description": "Decisions made or pending.",
      "items": {
        "type": "object",
        "properties": {
          "status": { "type": "string", "enum": ["made", "pending"] },
          "decision": { "type": "string" },
          "by": { "type": "string", "enum": ["self", "team", "manager", "other", "unknown"] },
          "rationale": { "type": ["string", "null"] },
          "date": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|~)$" },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["status", "decision"]
      }
    },

    "actions": {
      "type": "array",
      "description": "Actionable tasks.",
      "items": {
        "type": "object",
        "properties": {
          "task": { "type": "string" },
          "owner": { "type": "string", "enum": ["self", "other"] },
          "status": { "type": "string", "enum": ["todo", "doing", "done"] },
          "due": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|\\d{2}:\\d{2}|~)$" },
          "effort_min": { "type": ["integer", "null"], "min": 0 },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["task", "owner", "status"]
      }
    },

    "risks": {
      "type": "array",
      "description": "Neutral risks/blockers.",
      "items": {
        "type": "object",
        "properties": {
          "risk": { "type": "string" },
          "severity_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
          "likelihood_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
          "mitigation": { "type": ["string", "null"] },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["risk"]
      }
    },

    "metrics": {
      "type": "array",
      "description": "Explicit metrics or counts mentioned.",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "value": { "type": "string" },
          "unit": { "type": ["string", "null"] },
          "timeframe": { "type": ["string", "null"] },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["name", "value"]
      }
    },

    "references": {
      "type": "array",
      "description": "External links or artifacts.",
      "items": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["link", "doc", "image", "email", "other"] },
          "title": { "type": ["string", "null"] },
          "url_or_id": { "type": ["string", "null"] },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["kind"]
      }
    },

    "constraints": {
      "type": "array",
      "description": "Explicit constraints.",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["time", "budget", "policy", "tech", "dependency", "other"] },
          "detail": { "type": "string" },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["type", "detail"]
      }
    },

    "assumptions": {
      "type": "array",
      "description": "Assumptions stated in the note.",
      "items": {
        "type": "object",
        "properties": {
          "assumption": { "type": "string" },
          "support": { "type": ["string", "null"] },
          "risk_if_wrong": { "type": ["string", "null"] },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["assumption"]
      }
    },

    "comparisons": {
      "type": "array",
      "description": "Comparative statements.",
      "items": {
        "type": "object",
        "properties": {
          "axis": { "type": "string", "enum": ["before_after", "expected_actual", "self_other", "other"] },
          "before": { "type": ["string", "null"] },
          "after": { "type": ["string", "null"] },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["axis"]
      }
    },

    "mood_hints": {
      "type": "object",
      "description": "Optional crosslinks to other moods (free-form).",
      "additionalProperties": "true"
    },

    "tag_keywords": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Flat keyword tags."
    },

    "entity_map": {
      "type": "object",
      "description": "Flat quick map for entities (free-form).",
      "additionalProperties": "true"
    },

    "dominant_items": {
      "type": "object",
      "description": "Indices pointing to dominant items (optional).",
      "properties": {
        "top_fact_idx": { "type": ["integer", "null"], "min": 0 },
        "top_task_idx": { "type": ["integer", "null"], "min": 0 },
        "top_decision_idx": { "type": ["integer", "null"], "min": 0 }
      }
    }
  },
  "definitions": {
    "entityItemArray": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "span_ref": { "type": ["string", "null"] }
        },
        "required": ["name"]
      }
    }
  },
  "requirements": {
    "arrays_are_tight": "true",
    "quotes_max": 6,
    "quote_length_max_chars": 140,
    "date_format": "YYYY-MM-DD or '~' when unknown",
    "clamp_rules": {
      "valence": [-1.0, 1.0],
      "arousal": [0.0, 1.0],
      "confidence": [0.0, 1.0],
      "certainty_0_1": [0.0, 1.0],
      "importance_0_1": [0.0, 1.0],
      "score_0_1": [0.0, 1.0],
      "severity_0_1": [0.0, 1.0],
      "likelihood_0_1": [0.0, 1.0]
    }
  }
}
        self.Happy={
  "mood_name": "Happy",
  "version": 1,
  "description": "Positive, appreciative, and outcome-focused extraction for the 'Happy' mood.",
  "fields": {
    "version": { "type": "integer", "default": 1 },
    "extraction_timestamp": { "type": "string", "format": "date-time" },
    "language": { "type": "string", "default": "en" },
    "source_length_chars": { "type": "integer", "min": 0 },

    "valence": { "type": "number", "min": -1.0, "max": 1.0 },
    "arousal": { "type": "number", "min": 0.0, "max": 1.0 },
    "confidence": { "type": ["number","object"], "min": 0.0, "max": 1.0, "description": "Model uses number; DB may store JSON—accept either." },

    "embedding": { "type": ["array","object","null"], "items": { "type": "number" } },

    "quotes": {
      "type": "array",
      "items": { "$ref": "#/definitions/quoteItem" }
    },
    "spans": {
      "type": "array",
      "items": { "$ref": "#/definitions/spanItem" }
    },

    "positive_events": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "what_happened": { "type": "string" },
          "who": { "type": ["string","null"] },
          "where": { "type": ["string","null"] },
          "when": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|~)$" },
          "why_it_matters": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["what_happened"]
      }
    },

    "outcomes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "result": { "type": "string" },
          "metric": { "type": ["string","null"] },
          "value": { "type": ["string","null"] },
          "timeframe": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["result"]
      }
    },

    "graditude": {
      "type": "array",
      "description": "Note: field name is 'graditude' per model.",
      "items": {
        "type": "object",
        "properties": {
          "target": { "type": "string" },
          "reason": { "type": ["string","null"] },
          "intensity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["target"]
      }
    },

    "pleasant_emotions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "intensity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "trigger": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["label"]
      }
    },

    "strengths": {
      "type": "array",
      "items": { "$ref": "#/definitions/namedItem" }
    },

    "social_ties": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "person": { "type": "string" },
          "relationship": { "type": ["string","null"] },
          "support_type": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["person"]
      }
    },

    "growth": {
      "type": "array",
      "items": { "$ref": "#/definitions/namedWithDetail" }
    },

    "future_positives": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "anticipation": { "type": "string" },
          "target_date": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|~)$" },
          "confidence_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["anticipation"]
      }
    },

    "activities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "category": { "type": "string" },
          "description": { "type": ["string","null"] },
          "duration_min": { "type": ["integer","null"], "min": 0 },
          "enjoyment_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["category"]
      }
    },

    "sensory": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "modality": { "type": "string", "enum": ["sight","sound","smell","taste","touch","other"] },
          "description": { "type": "string" },
          "pleasantness_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["modality","description"]
      }
    },

    "humor": {
      "type": "array",
      "items": { "$ref": "#/definitions/namedWithDetail" }
    },

    "comparatives": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "axis": { "type": "string", "enum": ["before_after","expected_actual","self_other","other"] },
          "before": { "type": ["string","null"] },
          "after": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["axis"]
      }
    },

    "obstacles_overcome": {
      "type": "array",
      "items": { "$ref": "#/definitions/namedWithDetail" }
    },

    "values_alignment": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "value": { "type": "string" },
          "evidence": { "type": ["string","null"] },
          "alignment_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["value"]
      }
    },

    "artifacts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["photo","video","note","link","other"] },
          "title": { "type": ["string","null"] },
          "url_or_id": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["kind"]
      }
    },

    "state_metrics": {
      "type": "object",
      "additionalProperties": {
        "type": ["number","string","null"]
      },
      "description": "Free-form positive-state metrics, e.g., energy, calmness, satisfaction."
    },

    "risks_or_concers": {
      "type": "array",
      "description": "Note: field name is 'risks_or_concers' per model.",
      "items": {
        "type": "object",
        "properties": {
          "risk": { "type": "string" },
          "severity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "likelihood_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "mitigation": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["risk"]
      }
    },

    "boundaries_to_respect": {
      "type": "array",
      "items": { "$ref": "#/definitions/namedWithDetail" }
    },

    "tag_keywords": { "type": "array", "items": { "type": "string" } },
    "entity_map": { "type": "object", "additionalProperties": "true" },

    "dominant_items": {
      "type": "object",
      "properties": {
        "top_event_idx": { "type": ["integer","null"], "min": 0 },
        "top_outcome_idx": { "type": ["integer","null"], "min": 0 },
        "top_emotion_idx": { "type": ["integer","null"], "min": 0 }
      }
    }
  },
  "definitions": {
    "quoteItem": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "purpose": { "type": ["string","null"], "enum": ["fact","decision","task","reference","other","null"] }
      },
      "required": ["text"]
    },
    "spanItem": {
      "type": "object",
      "properties": {
        "span_id": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "text": { "type": "string" }
      },
      "required": ["span_id","text"]
    },
    "namedItem": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "evidence_ref": { "type": ["string","null"] }
      },
      "required": ["name"]
    },
    "namedWithDetail": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "detail": { "type": ["string","null"] },
        "evidence_ref": { "type": ["string","null"] }
      },
      "required": ["name"]
    }
  },
  "requirements": {
    "arrays_are_tight": "true",
    "quotes_max": 6,
    "quote_length_max_chars": 140,
    "date_format": "YYYY-MM-DD or '~' when unknown",
    "clamp_rules": {
      "valence": [-1.0, 1.0],
      "arousal": [0.0, 1.0],
      "intensity_0_1": [0.0, 1.0],
      "confidence": [0.0, 1.0],
      "alignment_0_1": [0.0, 1.0],
      "severity_0_1": [0.0, 1.0],
      "likelihood_0_1": [0.0, 1.0],
      "enjoyment_0_1": [0.0, 1.0]
    }
  }
}
        self.Hopeful={
  "mood_name": "Hopeful",
  "version": 1,
  "description": "Deep, structured extraction for the 'Hopeful' mood: goals, pathways, supports, blockers, milestones, commitments, and hope signals.",
  "fields": {
    "version": { "type": "integer", "default": 1 },
    "extraction_timestamp": { "type": "string", "format": "date-time" },
    "language": { "type": "string", "default": "en" },
    "source_length_chars": { "type": "integer", "min": 0 },

    "valence": { "type": "number", "min": -1.0, "max": 1.0 },
    "arousal": { "type": "number", "min": 0.0, "max": 1.0 },
    "confidence": { "type": "number", "min": 0.0, "max": 1.0 },

    "agency_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
    "clarity_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
    "feasibility_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
    "optimism_0_1": { "type": "number", "min": 0.0, "max": 1.0 },

    "embedding": { "type": ["array","object","null"], "items": { "type": "number" } },

    "quotes": { "type": "array", "items": { "$ref": "#/definitions/quoteItem" } },
    "spans":  { "type": "array", "items": { "$ref": "#/definitions/spanItem" } },

    "goals": {
      "type": "array",
      "description": "Goals & aspirations the note points toward.",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["short_term","long_term","vision"] },
          "description": { "type": "string" },
          "why_it_matters": { "type": ["string","null"] },
          "time_horizon": { "type": "string", "enum": ["today","this_week","this_month","quarter","year","later"] },
          "priority_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["type","description"]
      }
    },

    "pathways": {
      "type": "array",
      "description": "Multiple routes/strategies toward goals.",
      "items": {
        "type": "object",
        "properties": {
          "step": { "type": "string" },
          "rationale": { "type": ["string","null"] },
          "resources_needed": { "type": "array", "items": { "type": "string" } },
          "effort_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "dependency": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["step"]
      }
    },

    "supports": {
      "type": "array",
      "description": "People, tools, environments, habits that support progress.",
      "items": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["person","team","mentor","tool","environment","habit"] },
          "name_or_desc": { "type": "string" },
          "strength_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "availability": { "type": "string", "enum": ["now","soon","uncertain"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["kind","name_or_desc"]
      }
    },

    "blockers": {
      "type": "array",
      "description": "Risks/obstacles and initial mitigations.",
      "items": {
        "type": "object",
        "properties": {
          "obstacle": { "type": "string" },
          "severity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "likelihood_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "mitigation": { "type": ["string","null"] },
          "owner": { "type": "string", "enum": ["self","other","unknown"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["obstacle"]
      }
    },

    "milestones": {
      "type": "array",
      "description": "Progress markers / what success looks like.",
      "items": {
        "type": "object",
        "properties": {
          "marker": { "type": "string" },
          "metric": { "type": ["string","null"] },
          "target_date": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|~)$" },
          "confidence_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["marker"]
      }
    },

    "commitments": {
      "type": "array",
      "description": "Explicit intent / next actions.",
      "items": {
        "type": "object",
        "properties": {
          "action": { "type": "string" },
          "deadline": { "type": "string" },
          "effort_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "risk_if_skipped": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["action"]
      }
    },

    "small_wins": {
      "type": "array",
      "description": "Wins already achieved to seed hope.",
      "items": {
        "type": "object",
        "properties": {
          "win": { "type": "string" },
          "evidence_quote": { "type": ["string","null"] },
          "impact_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["win"]
      }
    },

    "reframes": {
      "type": "array",
      "description": "Perspective shifts that increase hope.",
      "items": {
        "type": "object",
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "proof_quote": { "type": ["string","null"] },
          "strengthened_value": { "type": ["string","null"] }
        },
        "required": ["from","to"]
      }
    },

    "values_alignment": {
      "type": "array",
      "description": "Why the path matters to the user.",
      "items": {
        "type": "object",
        "properties": {
          "value": { "type": "string", "enum": ["mastery","family","health","creativity","service","autonomy","community","faith","adventure","other"] },
          "alignment_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["value"]
      }
    },

    "contingencies": {
      "type": "array",
      "description": "Plan B/C options.",
      "items": {
        "type": "object",
        "properties": {
          "trigger": { "type": "string" },
          "alternative_path": { "type": "string" },
          "cost_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["trigger","alternative_path"]
      }
    },

    "uncertainties": {
      "type": "array",
      "description": "Unknowns and information gaps.",
      "items": {
        "type": "object",
        "properties": {
          "question": { "type": "string" },
          "information_needed": { "type": ["string","null"] },
          "owner": { "type": "string", "enum": ["self","other","unknown"] }
        },
        "required": ["question"]
      }
    },

    "hopeful_emotions": {
      "type": "array",
      "description": "Emotional signals specific to hope.",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string", "enum": ["hope","anticipation","confidence","curiosity","other"] },
          "intensity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "trigger_ref": { "type": ["string","null"] }
        },
        "required": ["label"]
      }
    },

    "visualizations": {
      "type": "array",
      "description": "Vivid future imagery.",
      "items": {
        "type": "object",
        "properties": {
          "image": { "type": "string" },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["image"]
      }
    },

    "invitations": {
      "type": "array",
      "description": "External validation/opportunities.",
      "items": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["invite","offer","referral","warm_intro","acceptance"] },
          "details": { "type": "string" },
          "likelihood_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["kind","details"]
      }
    },

    "tag_keywords": { "type": "array", "items": { "type": "string" } },
    "entity_map": { "type": "object", "additionalProperties": "true" },

    "dominant_items": {
      "type": "object",
      "properties": {
        "top_goal_idx": { "type": ["integer","null"], "min": 0 },
        "top_pathway_idx": { "type": ["integer","null"], "min": 0 },
        "top_support_idx": { "type": ["integer","null"], "min": 0 }
      }
    }
  },
  "definitions": {
    "quoteItem": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "purpose": { "type": ["string","null"], "enum": ["fact","decision","task","reference","other","null"] }
      },
      "required": ["text"]
    },
    "spanItem": {
      "type": "object",
      "properties": {
        "span_id": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "text": { "type": "string" }
      },
      "required": ["span_id","text"]
    }
  },
  "requirements": {
    "date_format": "YYYY-MM-DD or '~' when unknown",
    "clamp_rules": {
      "valence": [-1.0, 1.0],
      "arousal": [0.0, 1.0],
      "confidence": [0.0, 1.0],
      "agency_0_1": [0.0, 1.0],
      "clarity_0_1": [0.0, 1.0],
      "feasibility_0_1": [0.0, 1.0],
      "optimism_0_1": [0.0, 1.0],
      "intensity_0_1": [0.0, 1.0],
      "severity_0_1": [0.0, 1.0],
      "likelihood_0_1": [0.0, 1.0],
      "alignment_0_1": [0.0, 1.0]
    },
    "quotes_max": 6,
    "quote_length_max_chars": 140,
    "arrays_are_tight": "true"
  }
}
        self.Reflective={
  "mood_name": "Reflective",
  "version": 1,
  "description": "Structured extraction for the 'Reflective' mood: lessons, reframes, patterns, growth edges, and future adjustments.",
  "fields": {
    "version": { "type": "integer", "default": 1 },
    "extraction_timestamp": { "type": "string", "format": "date-time" },
    "language": { "type": "string", "default": "en" },
    "source_length_chars": { "type": "integer", "min": 0 },

    "valence": { "type": "number", "min": -1.0, "max": 1.0 },
    "arousal": { "type": "number", "min": 0.0, "max": 1.0 },
    "confidence": { "type": "number", "min": 0.0, "max": 1.0 },

    "depth_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
    "clarity_0_1": { "type": "number", "min": 0.0, "max": 1.0 },

    "embedding": { "type": ["array","object","null"], "items": { "type": "number" } },

    "quotes": { "type": "array", "items": { "$ref": "#/definitions/quoteItem" } },
    "spans":  { "type": "array", "items": { "$ref": "#/definitions/spanItem" } },

    "events_recalled": {
      "type": "array",
      "description": "Key events referenced in reflection.",
      "items": {
        "type": "object",
        "properties": {
          "event": { "type": "string" },
          "timeframe": { "type": ["string","null"] },
          "impact": { "type": ["string","null"] },
          "valence": { "type": "string", "enum": ["positive","negative","mixed"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["event","valence"]
      }
    },

    "lessons": {
      "type": "array",
      "description": "Lessons extracted from the reflection.",
      "items": {
        "type": "object",
        "properties": {
          "lesson": { "type": "string" },
          "domain": { "type": "string", "enum": ["work","relationships","self","health","learning","other"] },
          "generalizable": { "type": "boolean" },
          "evidence_quote": { "type": ["string","null"] }
        },
        "required": ["lesson","domain","generalizable"]
      }
    },

    "mistakes": {
      "type": "array",
      "description": "Mistakes & acknowledgments.",
      "items": {
        "type": "object",
        "properties": {
          "mistake": { "type": "string" },
          "realization": { "type": ["string","null"] },
          "severity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "repair_action": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["mistake"]
      }
    },

    "reframes": {
      "type": "array",
      "description": "Perspective shifts.",
      "items": {
        "type": "object",
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "trigger": { "type": ["string","null"] },
          "value_strengthened": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["from","to"]
      }
    },

    "patterns": {
      "type": "array",
      "description": "Patterns noticed across time.",
      "items": {
        "type": "object",
        "properties": {
          "theme": { "type": "string" },
          "frequency": { "type": ["string","null"] },
          "trigger": { "type": ["string","null"] },
          "span_refs": { "type": "array", "items": { "type": "string" } }
        },
        "required": ["theme"]
      }
    },

    "values_alignment": {
      "type": "array",
      "description": "Values alignment or misalignment.",
      "items": {
        "type": "object",
        "properties": {
          "value": { "type": "string", "enum": ["honesty","family","growth","health","creativity","service","community","faith","other"] },
          "alignment": { "type": "string", "enum": ["aligned","conflicted"] },
          "evidence_quote": { "type": ["string","null"] }
        },
        "required": ["value","alignment"]
      }
    },

    "growth_edges": {
      "type": "array",
      "description": "Strengths & growth edges.",
      "items": {
        "type": "object",
        "properties": {
          "strength": { "type": "string", "enum": ["resilience","patience","empathy","curiosity","discipline","other"] },
          "example": { "type": ["string","null"] },
          "improvement_needed": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["strength"]
      }
    },

    "open_questions": {
      "type": "array",
      "description": "Self-inquiry questions raised.",
      "items": {
        "type": "object",
        "properties": {
          "question": { "type": "string" },
          "category": { "type": "string", "enum": ["purpose","decision","relationship","identity","career","other"] },
          "unresolved": { "type": "boolean" }
        },
        "required": ["question","category","unresolved"]
      }
    },

    "turning_points": {
      "type": "array",
      "description": "Small or big shifts.",
      "items": {
        "type": "object",
        "properties": {
          "trigger": { "type": "string" },
          "realization": { "type": ["string","null"] },
          "impact": { "type": "string", "enum": ["short_term","long_term"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["trigger","impact"]
      }
    },

    "comparisons": {
      "type": "array",
      "description": "Before vs after, self vs others, expectation vs reality.",
      "items": {
        "type": "object",
        "properties": {
          "axis": { "type": "string", "enum": ["past_vs_present","self_vs_others","expectation_vs_reality"] },
          "before": { "type": ["string","null"] },
          "after": { "type": ["string","null"] },
          "insight": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["axis"]
      }
    },

    "gratitude": {
      "type": "array",
      "description": "Gratitude / appreciation within reflection.",
      "items": {
        "type": "object",
        "properties": {
          "target": { "type": "string", "description": "person|event|circumstance" },
          "reason": { "type": ["string","null"] },
          "quote": { "type": ["string","null"] }
        },
        "required": ["target"]
      }
    },

    "regrets": {
      "type": "array",
      "description": "Regrets & closure signals.",
      "items": {
        "type": "object",
        "properties": {
          "regret": { "type": "string" },
          "acceptance_level_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "next_step": { "type": ["string","null"] }
        },
        "required": ["regret"]
      }
    },

    "future_adjustments": {
      "type": "array",
      "description": "Intended changes for the future.",
      "items": {
        "type": "object",
        "properties": {
          "change": { "type": "string" },
          "why": { "type": ["string","null"] },
          "confidence_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["change"]
      }
    },

    "tag_keywords": { "type": "array", "items": { "type": "string" } },
    "entity_map": { "type": "object", "additionalProperties": "true" },

    "dominant_items": {
      "type": "object",
      "properties": {
        "top_lesson_idx": { "type": ["integer","null"], "min": 0 },
        "top_reframe_idx": { "type": ["integer","null"], "min": 0 },
        "top_growth_edge_idx": { "type": ["integer","null"], "min": 0 }
      }
    }
  },
  "definitions": {
    "quoteItem": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "purpose": { "type": ["string","null"] }
      },
      "required": ["text"]
    },
    "spanItem": {
      "type": "object",
      "properties": {
        "span_id": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "text": { "type": "string" }
      },
      "required": ["span_id","text"]
    }
  },
  "requirements": {
    "date_format": "YYYY-MM-DD or '~' when unknown",
    "arrays_are_tight": "true",
    "quotes_max": 6,
    "quote_length_max_chars": 140,
    "clamp_rules": {
      "valence": [-1.0, 1.0],
      "arousal": [0.0, 1.0],
      "confidence": [0.0, 1.0],
      "depth_0_1": [0.0, 1.0],
      "clarity_0_1": [0.0, 1.0],
      "severity_0_1": [0.0, 1.0],
      "acceptance_level_0_1": [0.0, 1.0],
      "confidence_0_1": [0.0, 1.0]
    }
  }
}
        self.Motivation={
  "mood_name": "Motivation",
  "version": 1,
  "description": "Deep, structured extraction for the 'Motivation' mood: drivers, commitments, executable next steps, timeboxing, and reinforcement.",
  "fields": {
    "version": { "type": "integer", "default": 1 },
    "extraction_timestamp": { "type": "string", "format": "date-time" },
    "language": { "type": "string", "default": "en" },
    "source_length_chars": { "type": "integer", "min": 0 },

    "valence": { "type": "number", "min": -1.0, "max": 1.0 },
    "arousal": { "type": "number", "min": 0.0, "max": 1.0 },
    "confidence": { "type": "number", "min": 0.0, "max": 1.0 },

    "drive_strength_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
    "clarity_0_1":        { "type": "number", "min": 0.0, "max": 1.0 },
    "feasibility_0_1":    { "type": "number", "min": 0.0, "max": 1.0 },
    "commitment_0_1":     { "type": "number", "min": 0.0, "max": 1.0 },

    "embedding": { "type": ["array","object","null"], "items": { "type": "number" } },

    "quotes": { "type": "array", "items": { "$ref": "#/definitions/quoteItem" } },
    "spans":  { "type": "array", "items": { "$ref": "#/definitions/spanItem" } },

    "goals": {
      "type": "array",
      "description": "Targets (SMART/WOOP compatible).",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["outcome","performance","learning","habit"] },
          "description": { "type": "string" },
          "why_it_matters": { "type": ["string","null"] },
          "metric": { "type": ["string","null"] },
          "target_value": { "type": ["string","null"] },
          "deadline": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|~)$" },
          "priority_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["type","description"]
      }
    },

    "anti_goals": {
      "type": "array",
      "description": "Avoid states (clarify focus).",
      "items": {
        "type": "object",
        "properties": {
          "description": { "type": "string" },
          "reason": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["description"]
      }
    },

    "drivers": {
      "type": "array",
      "description": "Motivational drivers (intrinsic/extrinsic).",
      "items": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["intrinsic","extrinsic"] },
          "label": { "type": "string", "enum": ["mastery","autonomy","purpose","recognition","reward","fear_of_loss","deadline","other"] },
          "evidence_quote": { "type": ["string","null"] },
          "strength_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["kind","label"]
      }
    },

    "identity_claims": {
      "type": "array",
      "description": "Identity statements.",
      "items": {
        "type": "object",
        "properties": {
          "claim": { "type": "string" },
          "proof_quote": { "type": ["string","null"] },
          "salience_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["claim"]
      }
    },

    "implementation_intentions": {
      "type": "array",
      "description": "If-then + timeboxing.",
      "items": {
        "type": "object",
        "properties": {
          "if": { "type": "string" },
          "then": { "type": "string" },
          "context": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["if","then"]
      }
    },

    "next_actions": {
      "type": "array",
      "description": "Granular, executable tasks.",
      "items": {
        "type": "object",
        "properties": {
          "action": { "type": "string" },
          "context": { "type": ["string","null"] },
          "size": { "type": "string", "enum": ["micro","small","normal"] },
          "owner": { "type": "string", "enum": ["self","other"] },
          "effort_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "duration_min": { "type": ["integer","null"], "min": 0 },
          "due": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|\\d{2}:\\d{2}|~)$" },
          "blockers_ref": { "type": "array", "items": { "type": "string" } },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["action","owner"]
      }
    },

    "time_blocks": {
      "type": "array",
      "description": "Calendar commitments.",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "start": { "type": "string", "format": "date-time" },
          "end": { "type": "string", "format": "date-time" },
          "location": { "type": ["string","null"] },
          "pomodoro": { "type": ["integer","null"], "enum": [25,50,"null"] }
        },
        "required": ["label","start","end"]
      }
    },

    "habits": {
      "type": "array",
      "description": "Habits & routines for automaticity.",
      "items": {
        "type": "object",
        "properties": {
          "habit": { "type": "string" },
          "cue": { "type": "string", "enum": ["time","location","preceding_action","other"] },
          "frequency": { "type": "string", "enum": ["daily","weekly","custom"] },
          "streak_days": { "type": ["integer","null"], "min": 0 },
          "confidence_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["habit","cue","frequency"]
      }
    },

    "cues_triggers": {
      "type": "array",
      "description": "Cues & triggers.",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["time","location","tool","social","emotion","calendar","notification","other"] },
          "detail": { "type": "string" },
          "strength_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["type","detail"]
      }
    },

    "rewards": {
      "type": "array",
      "description": "Rewards & reinforcement.",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["intrinsic","extrinsic"] },
          "reward": { "type": "string" },
          "timing": { "type": "string", "enum": ["immediate","end_of_block","end_of_day"] },
          "safety_checked": { "type": "boolean" }
        },
        "required": ["type","reward","timing","safety_checked"]
      }
    },

    "accountability": {
      "type": "array",
      "description": "People/systems for accountability.",
      "items": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["person","team","public_commit","bot","streak_counter"] },
          "who_or_what": { "type": "string" },
          "cadence": { "type": "string", "enum": ["daily","weekly","adhoc"] },
          "contact": { "type": ["string","null"], "enum": ["email","dm","in_person","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["kind","who_or_what","cadence"]
      }
    },

    "obstacles": {
      "type": "array",
      "description": "Obstacles & friction points.",
      "items": {
        "type": "object",
        "properties": {
          "obstacle": { "type": "string" },
          "type": { "type": "string", "enum": ["skill_gap","unclear_spec","distraction","tooling","fear","logistics","other"] },
          "severity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "likelihood_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["obstacle"]
      }
    },

    "environment_design": {
      "type": "array",
      "description": "Friction reducers & enablers.",
      "items": {
        "type": "object",
        "properties": {
          "change": { "type": "string" },
          "effect": { "type": ["string","null"] },
          "setup_time_min": { "type": ["integer","null"], "min": 0 }
        },
        "required": ["change"]
      }
    },

    "leverage_points": {
      "type": "array",
      "description": "80/20 highest impact actions.",
      "items": {
        "type": "object",
        "properties": {
          "action": { "type": "string" },
          "why_high_impact": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["action"]
      }
    },

    "progress_markers": {
      "type": "array",
      "description": "Markers & metrics for progress.",
      "items": {
        "type": "object",
        "properties": {
          "marker": { "type": "string" },
          "metric": { "type": ["string","null"] },
          "baseline": { "type": ["string","null"] },
          "target": { "type": ["string","null"] },
          "due": { "type": "string", "pattern": "^(\\d{4}-\\d{2}-\\d{2}|~)$" }
        },
        "required": ["marker"]
      }
    },

    "streaks": {
      "type": "array",
      "description": "Momentum via streaks/history.",
      "items": {
        "type": "object",
        "properties": {
          "label": { "type": "string" },
          "current": { "type": ["integer","null"], "min": 0 },
          "best": { "type": ["integer","null"], "min": 0 },
          "last_date": { "type": ["string","null"], "pattern": "^(\\d{4}-\\d{2}-\\d{2})$" }
        },
        "required": ["label"]
      }
    },

    "fallback_plans": {
      "type": "array",
      "description": "Plan B options.",
      "items": {
        "type": "object",
        "properties": {
          "trigger": { "type": "string" },
          "fallback": { "type": "string" },
          "cost_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["trigger","fallback"]
      }
    },

    "pep_talk_lines": {
      "type": "array",
      "description": "Short energizing lines (grounded in quotes).",
      "items": {
        "type": "object",
        "properties": {
          "line": { "type": "string" },
          "evidence_quote": { "type": ["string","null"] }
        },
        "required": ["line"]
      }
    },

    "readiness_state": {
      "type": "object",
      "description": "Energy & wellbeing preconditions.",
      "properties": {
        "sleep_ok": { "type": ["boolean","null"] },
        "fuel_ok": { "type": ["boolean","null"] },
        "mood": { "type": ["string","null"], "enum": ["ok","low","high","null"] },
        "time_of_day": { "type": ["string","null"], "enum": ["morning","afternoon","evening","null"] }
      }
    },

    "tag_keywords": { "type": "array", "items": { "type": "string" } },
    "entity_map": { "type": "object", "additionalProperties":" true" },

    "dominant_items": {
      "type": "object",
      "properties": {
        "top_goal_idx": { "type": ["integer","null"], "min": 0 },
        "top_action_idx": { "type": ["integer","null"], "min": 0 },
        "top_driver_idx": { "type": ["integer","null"], "min": 0 }
      }
    }
  },
  "definitions": {
    "quoteItem": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "purpose": { "type": ["string","null"] }
      },
      "required": ["text"]
    },
    "spanItem": {
      "type": "object",
      "properties": {
        "span_id": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "text": { "type": "string" }
      },
      "required": ["span_id","text"]
    }
  },
  "requirements": {
    "date_format": "YYYY-MM-DD or '~' (or HH:MM for 'due' time)",
    "arrays_are_tight": "true",
    "quotes_max": 6,
    "quote_length_max_chars": 140,
    "clamp_rules": {
      "valence": [-1.0, 1.0],
      "arousal": [0.0, 1.0],
      "confidence": [0.0, 1.0],
      "drive_strength_0_1": [0.0, 1.0],
      "clarity_0_1": [0.0, 1.0],
      "feasibility_0_1": [0.0, 1.0],
      "commitment_0_1": [0.0, 1.0],
      "strength_0_1": [0.0, 1.0],
      "effort_0_1": [0.0, 1.0],
      "confidence_0_1": [0.0, 1.0],
      "severity_0_1": [0.0, 1.0],
      "likelihood_0_1": [0.0, 1.0]
    }
  }
}
        self.Calm={
  "mood_name": "Calm",
  "version": 1,
  "description": "Structured extraction for the 'Calm' mood: serenity, safety, soothing practices, routines, and balance.",
  "fields": {
    "version": { "type": "integer", "default": 1 },
    "extraction_timestamp": { "type": "string", "format": "date-time" },
    "language": { "type": "string", "default": "en" },
    "source_length_chars": { "type": "integer", "min": 0 },

    "valence": { "type": "number", "min": -1.0, "max": 1.0 },
    "arousal": { "type": "number", "min": 0.0, "max": 1.0 },
    "confidence": { "type": "number", "min": 0.0, "max": 1.0 },

    "serenity_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
    "safety_0_1":   { "type": "number", "min": 0.0, "max": 1.0 },
    "balance_0_1":  { "type": "number", "min": 0.0, "max": 1.0 },
    "clarity_0_1":  { "type": "number", "min": 0.0, "max": 1.0 },

    "embedding": { "type": ["array","object","null"], "items": { "type": "number" } },

    "quotes": { "type": "array", "items": { "$ref": "#/definitions/quoteItem" } },
    "spans":  { "type": "array", "items": { "$ref": "#/definitions/spanItem" } },

    "tranquil_moments": {
      "type": "array",
      "description": "Calm moments or situations.",
      "items": {
        "type": "object",
        "properties": {
          "moment": { "type": "string" },
          "when": { "type": ["string","null"] },
          "where": { "type": ["string","null"] },
          "with": { "type": ["string","null"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["moment"]
      }
    },

    "soothing_activities": {
      "type": "array",
      "description": "Activities/rituals that soothe.",
      "items": {
        "type": "object",
        "properties": {
          "activity": { "type": "string", "enum": ["meditation","tea","walk","bath","reading","music","nature","other"] },
          "duration_min": { "type": ["integer","null"], "min": 0 },
          "frequency": { "type": "string", "enum": ["daily","weekly","adhoc"] },
          "enjoyment_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["activity","frequency"]
      }
    },

    "calming_environments": {
      "type": "array",
      "description": "Places/environments that induce calm.",
      "items": {
        "type": "object",
        "properties": {
          "place": { "type": "string" },
          "qualities": { "type": "array", "items": { "type": "string" } },
          "sensory_details": { "type": "array", "items": { "type": "string" } },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["place"]
      }
    },

    "sensory_anchors": {
      "type": "array",
      "description": "Soothing sensory anchors.",
      "items": {
        "type": "object",
        "properties": {
          "modality": { "type": "string", "enum": ["sound","sight","smell","touch","taste","other"] },
          "detail": { "type": "string" },
          "valence_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["modality","detail"]
      }
    },

    "stressors_reduced": {
      "type": "array",
      "description": "Stressors reduced/removed.",
      "items": {
        "type": "object",
        "properties": {
          "stressor": { "type": "string" },
          "how_reduced": { "type": ["string","null"] },
          "relief_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["stressor"]
      }
    },

    "coping_strategies": {
      "type": "array",
      "description": "Healthy coping techniques.",
      "items": {
        "type": "object",
        "properties": {
          "strategy": { "type": "string", "enum": ["deep breathing","journaling","walk","pause","reframing","other"] },
          "effectiveness_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["strategy"]
      }
    },

    "grounding_practices": {
      "type": "array",
      "description": "Mindfulness/body/prayer/gratitude practices.",
      "items": {
        "type": "object",
        "properties": {
          "practice": { "type": "string" },
          "frequency": { "type": "string", "enum": ["daily","weekly","adhoc"] },
          "stability_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["practice","frequency"]
      }
    },

    "routines": {
      "type": "array",
      "description": "Predictable routines that create calm.",
      "items": {
        "type": "object",
        "properties": {
          "routine": { "type": "string" },
          "time": { "type": ["string","null"], "pattern": "^(\\d{2}:\\d{2})$" },
          "frequency": { "type": "string", "enum": ["daily","weekly","adhoc"] },
          "comfort_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["routine","frequency"]
      }
    },

    "safe_people": {
      "type": "array",
      "description": "People that create social safety.",
      "items": {
        "type": "object",
        "properties": {
          "person": { "type": "string" },
          "relationship": { "type": "string", "enum": ["friend","partner","family","mentor","other"] },
          "warmth_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "quote": { "type": ["string","null"] }
        },
        "required": ["person"]
      }
    },

    "affirmations": {
      "type": "array",
      "description": "Stabilizing self-talk/affirmations.",
      "items": {
        "type": "object",
        "properties": {
          "line": { "type": "string" },
          "tone": { "type": "string", "enum": ["gentle","accepting","spiritual","other"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["line"]
      }
    },

    "values_alignment": {
      "type": "array",
      "description": "Values supported by calm state.",
      "items": {
        "type": "object",
        "properties": {
          "value": { "type": "string", "enum": ["health","family","balance","spirituality","growth","other"] },
          "alignment_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_quote": { "type": ["string","null"] }
        },
        "required": ["value"]
      }
    },

    "releases": {
      "type": "array",
      "description": "Letting go / forgiveness / closure.",
      "items": {
        "type": "object",
        "properties": {
          "released": { "type": "string", "enum": ["anger","resentment","worry","other"] },
          "how": { "type": ["string","null"] },
          "relief_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["released"]
      }
    },

    "recovery_signals": {
      "type": "array",
      "description": "Indicators of rest/recovery.",
      "items": {
        "type": "object",
        "properties": {
          "signal": { "type": "string", "enum": ["slept well","felt light","reduced tension","other"] },
          "intensity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["signal"]
      }
    },

    "calm_disturbances": {
      "type": "array",
      "description": "Risks/disturbances to calm.",
      "items": {
        "type": "object",
        "properties": {
          "disturbance": { "type": "string" },
          "severity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "likelihood_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["disturbance"]
      }
    },

    "future_practices": {
      "type": "array",
      "description": "Intentions to maintain calm.",
      "items": {
        "type": "object",
        "properties": {
          "practice": { "type": "string" },
          "commitment": { "type": ["string","null"] },
          "confidence_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["practice"]
      }
    },

    "tag_keywords": { "type": "array", "items": { "type": "string" } },
    "entity_map": { "type": "object", "additionalProperties": "true" },

    "dominant_items": {
      "type": "object",
      "properties": {
        "top_activity_idx": { "type": ["integer","null"], "min": 0 },
        "top_anchor_idx": { "type": ["integer","null"], "min": 0 },
        "top_routine_idx": { "type": ["integer","null"], "min": 0 }
      }
    }
  },
  "definitions": {
    "quoteItem": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "purpose": { "type": ["string","null"] }
      },
      "required": ["text"]
    },
    "spanItem": {
      "type": "object",
      "properties": {
        "span_id": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "text": { "type": "string" }
      },
      "required": ["span_id","text"]
    }
  },
  "requirements": {
    "date_format": "YYYY-MM-DD or '~' (for times use HH:MM where applicable)",
    "arrays_are_tight": "true",
    "quotes_max": 6,
    "quote_length_max_chars": 140,
    "clamp_rules": {
      "valence": [-1.0, 1.0],
      "arousal": [0.0, 1.0],
      "confidence": [0.0, 1.0],
      "serenity_0_1": [0.0, 1.0],
      "safety_0_1": [0.0, 1.0],
      "balance_0_1": [0.0, 1.0],
      "clarity_0_1": [0.0, 1.0],
      "enjoyment_0_1": [0.0, 1.0],
      "relief_0_1": [0.0, 1.0],
      "effectiveness_0_1": [0.0, 1.0],
      "alignment_0_1": [0.0, 1.0],
      "intensity_0_1": [0.0, 1.0],
      "likelihood_0_1": [0.0, 1.0],
      "confidence_0_1": [0.0, 1.0]
    }
  }
}
        self.Dramatic={
  "mood_name": "Dramatic",
  "version": 1,
  "description": "Structured extraction for the 'Dramatic' mood: stakes, conflict, reversals, vivid beats, pacing, and payoff—grounded by quotes/spans.",
  "fields": {
    "version": { "type": "integer", "default": 1 },
    "extraction_timestamp": { "type": "string", "format": "date-time" },
    "language": { "type": "string", "default": "en" },
    "source_length_chars": { "type": "integer", "min": 0 },

    "valence": { "type": "number", "min": -1.0, "max": 1.0 },
    "arousal": { "type": "number", "min": 0.0, "max": 1.0 },
    "confidence": { "type": "number", "min": 0.0, "max": 1.0 },

    "intensity_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
    "tension_0_1":   { "type": "number", "min": 0.0, "max": 1.0 },
    "stakes_0_1":    { "type": "number", "min": 0.0, "max": 1.0 },
    "pace_0_1":      { "type": "number", "min": 0.0, "max": 1.0 },
    "contrast_0_1":  { "type": "number", "min": 0.0, "max": 1.0 },

    "embedding": { "type": ["array","object","null"], "items": { "type": "number" } },

    "quotes": { "type": "array", "items": { "$ref": "#/definitions/quoteItem" } },
    "spans":  { "type": "array", "items": { "$ref": "#/definitions/spanItem" } },

    "settings": {
      "type": "array",
      "description": "Setting & atmosphere.",
      "items": {
        "type": "object",
        "properties": {
          "place": { "type": ["string","null"] },
          "time": { "type": ["string","null"] },
          "atmosphere": { "type": "string", "enum": ["tense","somber","electric","hopeful","other"] },
          "span_ref": { "type": ["string","null"] }
        }
      }
    },

    "characters": {
      "type": "array",
      "description": "Cast of characters and roles.",
      "items": {
        "type": "object",
        "properties": {
          "name_or_role": { "type": "string", "enum": ["self","mentor","critic","teammate","manager","antagonist","ally","other"] },
          "traits": { "type": "array", "items": { "type": "string" } },
          "motivation": { "type": ["string","null"] },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["name_or_role"]
      }
    },

    "stakes": {
      "type": "array",
      "description": "What could be won/lost.",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["reputation","relationship","deadline","health","opportunity","money","other"] },
          "description": { "type": "string" },
          "severity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "urgency_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["type","description"]
      }
    },

    "conflicts": {
      "type": "array",
      "description": "Internal/external conflicts.",
      "items": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["internal","interpersonal","systemic","logistical","other"] },
          "issue": { "type": "string" },
          "opposing_forces": { "type": "array", "items": { "type": "string" } },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["kind","issue"]
      }
    },

    "inciting_incident": {
      "type": "object",
      "description": "Inciting incident / problem statement.",
      "properties": {
        "what_happened": { "type": ["string","null"] },
        "why_it_matters": { "type": ["string","null"] },
        "span_ref": { "type": ["string","null"] }
      }
    },

    "escalations": {
      "type": "array",
      "description": "Rising complications.",
      "items": {
        "type": "object",
        "properties": {
          "complication": { "type": "string" },
          "effect": { "type": "string", "enum": ["raises stakes","narrows options","adds time pressure","other"] },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["complication","effect"]
      }
    },

    "reversals": {
      "type": "array",
      "description": "Reversals & revelations.",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["reversal","revelation","red_herring"] },
          "what_changed": { "type": "string" },
          "impact_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["type","what_changed"]
      }
    },

    "turning_points": {
      "type": "array",
      "description": "Key decisions/turns.",
      "items": {
        "type": "object",
        "properties": {
          "decision": { "type": "string" },
          "reason": { "type": ["string","null"] },
          "cost": { "type": ["string","null"] },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["decision"]
      }
    },

    "climax": {
      "type": "object",
      "description": "Peak tension.",
      "properties": {
        "moment": { "type": ["string","null"] },
        "action": { "type": ["string","null"] },
        "result": { "type": ["string","null"] },
        "span_ref": { "type": ["string","null"] }
      }
    },

    "resolution": {
      "type": "object",
      "description": "Outcome and immediate aftermath.",
      "properties": {
        "status": { "type": ["string","null"], "enum": ["win","loss","mixed","open","null"] },
        "after_effects": { "type": ["string","null"] },
        "lesson_hint": { "type": ["string","null"] },
        "span_ref": { "type": ["string","null"] }
      }
    },

    "catharsis": {
      "type": "object",
      "description": "Emotional release.",
      "properties": {
        "feeling": { "type": ["string","null"], "enum": ["relief","pride","grief","awe","bittersweet","other","null"] },
        "intensity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
        "quote": { "type": ["string","null"] }
      }
    },

    "themes": {
      "type": "array",
      "description": "Thematic elements.",
      "items": {
        "type": "object",
        "properties": {
          "theme": { "type": "string", "enum": ["resilience","fairness","trust","ambition","belonging","integrity","fate_vs_choice","other"] },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["theme"]
      }
    },

    "motifs": {
      "type": "array",
      "description": "Recurring images/ideas.",
      "items": {
        "type": "object",
        "properties": {
          "motif": { "type": "string" },
          "meaning": { "type": ["string","null"] },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["motif"]
      }
    },

    "symbols": {
      "type": "array",
      "description": "Symbolic objects.",
      "items": {
        "type": "object",
        "properties": {
          "symbol": { "type": "string" },
          "represents": { "type": ["string","null"] },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["symbol"]
      }
    },

    "imagery": {
      "type": "array",
      "description": "Imagery & sensory vividness.",
      "items": {
        "type": "object",
        "properties": {
          "modality": { "type": "string", "enum": ["sight","sound","smell","touch","taste","other"] },
          "detail": { "type": "string" },
          "valence_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["modality","detail"]
      }
    },

    "beat_sheet": {
      "type": "array",
      "description": "Narrative beats.",
      "items": {
        "type": "object",
        "properties": {
          "beat": { "type": "string", "enum": ["setup","inciting","rising","reversal","dark_night","climax","resolution","other"] },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["beat"]
      }
    },

    "three_act_map": {
      "type": "object",
      "description": "Three-act structure mapping.",
      "properties": {
        "act1": { "type": ["string","null"] },
        "act2": { "type": ["string","null"] },
        "act3": { "type": ["string","null"] }
      }
    },

    "heros_journey": {
      "type": "object",
      "description": "Hero’s Journey mapping.",
      "properties": {
        "call_to_adventure": { "type": ["string","null"] },
        "tests_allies_enemies": { "type": ["string","null"] },
        "ordeal": { "type": ["string","null"] },
        "return": { "type": ["string","null"] }
      }
    },

    "setup_payoff_links": {
      "type": "array",
      "description": "Setups that later pay off.",
      "items": {
        "type": "object",
        "properties": {
          "setup_span": { "type": "string" },
          "payoff_span": { "type": "string" },
          "note": { "type": ["string","null"] }
        },
        "required": ["setup_span","payoff_span"]
      }
    },

    "suspense_devices": {
      "type": "array",
      "description": "Pacing & suspense techniques.",
      "items": {
        "type": "object",
        "properties": {
          "device": { "type": "string", "enum": ["ticking_clock","dramatic_irony","cliffhanger","misdirection","other"] },
          "where": { "type": ["string","null"] },
          "strength_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["device"]
      }
    },

    "open_questions": {
      "type": "array",
      "description": "Open questions that keep tension (safe for user).",
      "items": {
        "type": "object",
        "properties": {
          "question": { "type": "string" },
          "importance_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["question"]
      }
    },

    "risks_or_concerns": {
      "type": "array",
      "description": "Safety & boundaries topics to treat carefully.",
      "items": {
        "type": "object",
        "properties": {
          "topic": { "type": "string", "enum": ["self-harm","violence","abuse","phobia","other"] },
          "severity_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["topic"]
      }
    },

    "boundaries_to_respect": {
      "type": "array",
      "description": "Explicit boundaries/constraints for safe narration.",
      "items": { "type": "string" }
    },

    "tag_keywords": { "type": "array", "items": { "type": "string" } },
    "entity_map": { "type": "object", "additionalProperties": "true" },

    "dominant_items": {
      "type": "object",
      "properties": {
        "top_stake_idx": { "type": ["integer","null"], "min": 0 },
        "top_conflict_idx": { "type": ["integer","null"], "min": 0 },
        "top_reversal_idx": { "type": ["integer","null"], "min": 0 }
      }
    }
  },
  "definitions": {
    "quoteItem": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "purpose": { "type": ["string","null"] }
      },
      "required": ["text"]
    },
    "spanItem": {
      "type": "object",
      "properties": {
        "span_id": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "text": { "type": "string" }
      },
      "required": ["span_id","text"]
    }
  },
  "requirements": {
    "date_format": "YYYY-MM-DD or '~' when unknown",
    "arrays_are_tight": "true",
    "quotes_max": 6,
    "quote_length_max_chars": 140,
    "clamp_rules": {
      "valence": [-1.0, 1.0],
      "arousal": [0.0, 1.0],
      "confidence": [0.0, 1.0],
      "intensity_0_1": [0.0, 1.0],
      "tension_0_1": [0.0, 1.0],
      "stakes_0_1": [0.0, 1.0],
      "pace_0_1": [0.0, 1.0],
      "contrast_0_1": [0.0, 1.0],
      "severity_0_1": [0.0, 1.0],
      "urgency_0_1": [0.0, 1.0],
      "impact_0_1": [0.0, 1.0],
      "importance_0_1": [0.0, 1.0],
      "strength_0_1": [0.0, 1.0],
      "valence_0_1": [0.0, 1.0]
    }
  }
}
        self.Funny={
  "mood_name": "Funny",
  "version": 1,
  "description": "Structured extraction for the 'Funny' mood: setups, benign violations, wordplay, callbacks, punchlines, timing, and safety controls.",
  "fields": {
    "version": { "type": "integer", "default": 1 },
    "extraction_timestamp": { "type": "string", "format": "date-time" },
    "language": { "type": "string", "default": "en" },
    "source_length_chars": { "type": "integer", "min": 0 },

    "valence": { "type": "number", "min": -1.0, "max": 1.0 },
    "arousal": { "type": "number", "min": 0.0, "max": 1.0 },
    "confidence": { "type": "number", "min": 0.0, "max": 1.0 },
    "surprise_0_1": { "type": "number", "min": 0.0, "max": 1.0 },
    "warmth_0_1":  { "type": "number", "min": 0.0, "max": 1.0 },

    "embedding": { "type": ["array","object","null"], "items": { "type": "number" } },

    "quotes": { "type": "array", "items": { "$ref": "#/definitions/quoteItem" } },
    "spans":  { "type": "array", "items": { "$ref": "#/definitions/spanItem" } },

    "persona": {
      "type": "object",
      "description": "Speaker persona to steer tone.",
      "properties": {
        "speaker": { "type": "string", "enum": ["self","narrator","other"] },
        "traits": { "type": "array", "items": { "type": "string" } },
        "self_deprecating_ok": { "type": ["boolean","null"] }
      }
    },

    "audience": {
      "type": "object",
      "description": "Audience knowledge and taboos.",
      "properties": {
        "familiar_with": { "type": "array", "items": { "type": "string" } },
        "taboos": { "type": "array", "items": { "type": "string" } },
        "friendliness_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
      }
    },

    "setups": {
      "type": "array",
      "description": "Premises to hang jokes on.",
      "items": {
        "type": "object",
        "properties": {
          "premise": { "type": "string" },
          "context": { "type": "string", "enum": ["work","home","travel","tech","social","other"] },
          "evidence_ref": { "type": ["string","null"] },
          "tension_seed": { "type": ["string","null"] }
        },
        "required": ["premise"]
      }
    },

    "benign_violations": {
      "type": "array",
      "description": "Incongruities / rule-bending framed as harmless.",
      "items": {
        "type": "object",
        "properties": {
          "violation": { "type": "string" },
          "benign_reason": { "type": ["string","null"] },
          "sensitivity_risk_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "evidence_ref": { "type": ["string","null"] }
        },
        "required": ["violation"]
      }
    },

    "wordplay": {
      "type": "array",
      "description": "Puns / homophones / double meanings.",
      "items": {
        "type": "object",
        "properties": {
          "hook": { "type": "string" },
          "type": { "type": "string", "enum": ["pun","double_entendre","malapropism","portmanteau","other"] },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["hook","type"]
      }
    },

    "amplifiers": {
      "type": "array",
      "description": "Hyperbole, understatement, analogies.",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["hyperbole","understatement","analogy","other"] },
          "line": { "type": "string" },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["type","line"]
      }
    },

    "callbacks": {
      "type": "array",
      "description": "Running gags / references.",
      "items": {
        "type": "object",
        "properties": {
          "reference": { "type": "string" },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["reference"]
      }
    },

    "observations": {
      "type": "array",
      "description": "Observational humor beats.",
      "items": {
        "type": "object",
        "properties": {
          "topic": { "type": "string" },
          "line": { "type": "string" },
          "evidence_ref": { "type": ["string","null"] },
          "relatability_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["topic","line"]
      }
    },

    "situational": {
      "type": "array",
      "description": "Physical/situational comedy bits.",
      "items": {
        "type": "object",
        "properties": {
          "scene": { "type": "string" },
          "prop": { "type": ["string","null"] },
          "awkwardness_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["scene"]
      }
    },

    "punchlines": {
      "type": "array",
      "description": "Short snappy punchline candidates.",
      "items": {
        "type": "object",
        "properties": {
          "line": { "type": "string" },
          "built_from": { "type": "array", "items": { "type": "string" } },
          "spice": { "type": "string", "enum": ["dry","silly","deadpan","witty","other"] },
          "safety_checked": { "type": "boolean" }
        },
        "required": ["line","safety_checked"]
      }
    },

    "delivery": {
      "type": "object",
      "description": "Timing & delivery notes.",
      "properties": {
        "style": { "type": "string", "enum": ["deadpan","playful","wry","animated","other"] },
        "beats": { "type": "array", "items": { "type": "string" } },
        "max_line_len": { "type": ["integer","null"], "min": 1 }
      }
    },

    "sensitivity_flags": {
      "type": "array",
      "description": "Potentially sensitive topics to watch.",
      "items": {
        "type": "object",
        "properties": {
          "topic": { "type": "string", "enum": ["body","religion","politics","trauma","identity","health","other"] },
          "risk_0_1": { "type": ["number","null"], "min": 0.0, "max": 1.0 }
        },
        "required": ["topic"]
      }
    },

    "boundaries_to_respect": {
      "type": "array",
      "description": "Soft boundaries to keep humor kind.",
      "items": { "type": "string" }
    },

    "redlines": {
      "type": "array",
      "description": "Hard no topics (never cross).",
      "items": { "type": "string" }
    },

    "references": {
      "type": "array",
      "description": "Cultural/context references (light and safe).",
      "items": {
        "type": "object",
        "properties": {
          "kind": { "type": "string", "enum": ["pop","tech","work","internet","other"] },
          "item": { "type": "string" },
          "recency": { "type": "string", "enum": ["old","current"] },
          "span_ref": { "type": ["string","null"] }
        },
        "required": ["kind","item","recency"]
      }
    },

    "tag_keywords": { "type": "array", "items": { "type": "string" } },
    "entity_map": { "type": "object", "additionalProperties": "true" },

    "dominant_items": {
      "type": "object",
      "properties": {
        "top_setup_idx": { "type": ["integer","null"], "min": 0 },
        "top_punch_idx": { "type": ["integer","null"], "min": 0 },
        "top_wordplay_idx": { "type": ["integer","null"], "min": 0 }
      }
    }
  },
  "definitions": {
    "quoteItem": {
      "type": "object",
      "properties": {
        "text": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "purpose": { "type": ["string","null"] }
      },
      "required": ["text"]
    },
    "spanItem": {
      "type": "object",
      "properties": {
        "span_id": { "type": "string" },
        "start": { "type": ["integer","null"], "min": 0 },
        "end": { "type": ["integer","null"], "min": 0 },
        "text": { "type": "string" }
      },
      "required": ["span_id","text"]
    }
  },
  "requirements": {
    "arrays_are_tight": "true",
    "quotes_max": 6,
    "quote_length_max_chars": 140,
    "date_format": "YYYY-MM-DD or '~' when unknown",
    "clamp_rules": {
      "valence": [-1.0, 1.0],
      "arousal": [0.0, 1.0],
      "confidence": [0.0, 1.0],
      "surprise_0_1": [0.0, 1.0],
      "warmth_0_1": [0.0, 1.0],
      "sensitivity_risk_0_1": [0.0, 1.0],
      "relatability_0_1": [0.0, 1.0],
      "awkwardness_0_1": [0.0, 1.0]
    },
    "safety_rules": [
      "Prefer self-deprecating or observational humor; avoid punching down.",
      "Respect 'boundaries_to_respect' and never cross 'redlines'.",
      "If uncertainty about sensitivity exists, drop or soften the line."
    ]
  }
}


