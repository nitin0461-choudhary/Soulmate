from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from authentication.models import Login_model
from .models import (
    new_notes,
    general_agent,
    Happy_agent,
    Hopeful_agent,
    Reflective_agent,
    motivation_agent,
    calm_agent,
    Dramatic_agent,
    Funny_agent
)
import os,re,json
from dotenv import load_dotenv

from .prompts import General_mood_extractor
from openai import AzureOpenAI
from .prompts_combine import Master_combine
from .prompts_mood_schema import mood_schema
from .prompts_format import format
from .prompts_mood import Mood
import numpy as np

load_dotenv()


# ----------------- Custom Decorator -----------------
def login_required_custom(view_func):
    """Custom decorator to ensure the user is logged in"""
    def wrapper(request, *args, **kwargs):
        if 'User_id' not in request.session:
            return redirect('login_page')  # Redirect to login page if not logged in
        return view_func(request, *args, **kwargs)
    return wrapper


# ----------------- Static Pages -----------------
def home(req):
    return render(req, 'application/home.html')


def about(req):
    return render(req, 'application/about.html')


# ----------------- Add Note -----------------
# @login_required_custom
def get_client():
    client=AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("API_VERSION"),
        azure_endpoint=os.getenv("ENDPOINT_URL")
    )
    return client


@login_required_custom
def add_note(request):
    import os, json, re
    from datetime import datetime
    # from django.utils import timezone
    # from django.shortcuts import render, redirect
    from django.db import models as djm
    from .models import (
        new_notes, general_agent, Happy_agent, Hopeful_agent,
        Reflective_agent, motivation_agent, calm_agent,
        Dramatic_agent, Funny_agent
    )
    from .prompts import General_mood_extractor
    # from openai import AzureOpenAI

    def get_client():
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("API_VERSION"),
            azure_endpoint=os.getenv("ENDPOINT_URL"),
        )

    def _strip_code_fences(s: str) -> str:
        if not s:
            return s
        m = re.match(r"```(?:json)?\s*(.*?)\s*```", s, flags=re.DOTALL | re.IGNORECASE)
        return m.group(1) if m else s

    def _filter_fields_for_model(model_cls, data_dict: dict) -> dict:
        field_names = {
            f.name for f in model_cls._meta.get_fields()
            if getattr(f, "concrete", False) and not getattr(f, "many_to_many", False)
        }
        field_names.discard("id")
        field_names.discard("pk")
        field_names.discard("note")  # we set FK separately
        return {k: v for k, v in (data_dict or {}).items() if k in field_names}

    def _coerce_types_for_model(model_cls, data: dict) -> dict:
        """Coerce incoming JSON into the Django field types, fixing placeholders like '~'."""
        if not data:
            return {}
        coerced = dict(data)
        for f in model_cls._meta.get_fields():
            if not getattr(f, "concrete", False) or getattr(f, "many_to_many", False):
                continue
            name = f.name
            if name not in coerced or name == "note":
                continue
            val = coerced[name]

            # Handle DateTimeField
            if isinstance(f, djm.DateTimeField):
                if isinstance(val, str):
                    v = val.strip()
                    ok = True
                    if v in ("~", "", "N/A", "null", "None"):
                        ok = False
                    else:
                        try:
                            # accept ISO strings; add timezone if missing
                            dt = datetime.fromisoformat(v)
                            if dt.tzinfo is None:
                                dt = timezone.make_aware(dt, timezone.get_current_timezone())
                            coerced[name] = dt
                        except Exception:
                            ok = False
                    if not ok:
                        coerced[name] = timezone.now()
                elif not isinstance(val, datetime):
                    coerced[name] = timezone.now()

            # Handle FloatField
            elif isinstance(f, djm.FloatField):
                try:
                    coerced[name] = float(val)
                except Exception:
                    coerced[name] = f.default if f.default is not djm.NOT_PROVIDED else 0.0

            # Handle IntegerField
            elif isinstance(f, djm.IntegerField):
                try:
                    coerced[name] = int(val)
                except Exception:
                    coerced[name] = f.default if f.default is not djm.NOT_PROVIDED else 0

            # Char/Text: ensure string
            elif isinstance(f, (djm.CharField, djm.TextField)):
                if val is None:
                    coerced[name] = ""
                else:
                    coerced[name] = str(val)

            # JSONField: leave as-is (must be JSON-serializable)
            elif isinstance(f, djm.JSONField):
                # If model returned code-fenced text accidentally, fallback safely
                if isinstance(val, str) and val.strip() in ("~", ""):
                    coerced[name] = {} if f.default == dict else ([] if f.default == list else None)
                # else: trust as JSON-compatible
            # Other fields: leave as-is

        return coerced

    # -------------- view logic --------------
    user_id = request.session.get('User_id')
    if not user_id:
        return redirect('login_page')

    user = Login_model.objects.get(id=user_id)

    if request.method == "POST":
        title = (request.POST.get('title') or "").strip()
        description = (request.POST.get('description') or "").strip()

        if title and description:
            note = new_notes.objects.create(
                user_notes=user,
                note_title=title,
                note_description=description
            )

            raw_text = f"Title:{note.note_title}\nDescription:{note.note_description}\n"
            now = timezone.now()
            class_mood = General_mood_extractor(note.id, now, raw_text)

            moods = {
                "General":    (general_agent,     class_mood.General_instruction),
                "Happy":      (Happy_agent,       class_mood.Happy_instruction),
                "Hopeful":    (Hopeful_agent,     class_mood.Hopeful_instruction),
                "Reflective": (Reflective_agent,  class_mood.Reflective_instruction),
                "Motivation": (motivation_agent,  class_mood.Motivation_instruction),
                "Calm":       (calm_agent,        class_mood.Calm_instruction),
                "Dramatic":   (Dramatic_agent,    class_mood.Dramatic_instruction),
                "Funny":      (Funny_agent,       class_mood.Funny_instruction),
            }

            client = get_client()
            deployment = os.getenv("DEPLOYMENT_NAME")

            for mood_name, (model_class, mood_prompt) in moods.items():
                resp = client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "system", "content": class_mood.prompt},
                        {"role": "user", "content": mood_prompt},
                    ],
                )

                raw = resp.choices[0].message.content or ""
                text = _strip_code_fences(raw)

                # Parse JSON payload; if invalid, fallback to minimal record
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    payload = {
                        "abstract": text,
                        "source_length_chars": len(text),
                        "extraction_timestamp": now.isoformat(),
                        "language": "en",
                        "tag_keywords": ["fallback"],
                    }

                filtered = _filter_fields_for_model(model_class, payload)
                sanitized = _coerce_types_for_model(model_class, filtered)
                print("sanitized=",sanitized)
                obj = model_class.objects.create(note=note, **sanitized)
                print(f"[{mood_name}] saved id={obj.id}")

    notes = new_notes.objects.filter(user_notes=user).order_by('-date')
    return render(request, 'application/add_note.html', {'notes': notes})


# ----------------- Delete Note -----------------
@login_required_custom
def delete_note(request, note_id):
    user_id = request.session['User_id']
    new_notes.objects.filter(id=note_id, user_notes_id=user_id).delete()
    return redirect('add_note')


# ----------------- AI Agent -----------------

def combine_master(extra_input1,mood_prompt_expanded1,mood_schema_json1,format_prompt_expanded1):
    client=get_client()
    prompts=Master_combine(mood_prompt_expanded1,mood_schema_json1,format_prompt_expanded1,extra_input1)
    # prompts.extra_input=extra_input1
    # prompts.mood_prompt_expanded=mood_prompt_expanded1
    # prompts.mood_schema_json=mood_schema_json1
    # prompts.format_prompt_expanded=format_prompt_expanded1
    response=client.chat.completions.create(
                    model=os.getenv("DEPLOYMENT_NAME"),
                    messages=[
                       {"role": "system", "content":prompts.prompt},
        
                    ]
                )
    result=response.choices[0].message.content
    print("combine prompt=",result)
    return result
    
def embeded_return(text:str):
    AZURE_OPENAI_KEY=os.getenv("AZURE_OPENAI_API_KEY")    
    AZURE_OPENAI_VERSION=os.getenv("API_VERSION")
    AZURE_OPENAI_ENDPOINT=os.getenv("EMBEDED_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT=os.getenv("EMBEDED_OPENAI_DEPLOYMENT")
    client=AzureOpenAI(
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,

    )
    response=client.embeddings.create(
        input=text,
        model=AZURE_OPENAI_DEPLOYMENT,
    )
    return response.data[0].embedding
def _l2norm(mat:np.ndarray) ->np.ndarray:
    return mat/(np.linalg.norm(mat,axis=1,keepdims=True)+1e-12)
def  rank_bycosine(query_text:str,docs,top_k=1):
    top_k=1
    print("docs is rank_bucosine=",docs)
    print("query_tex=",query_text)

    q=np.array(embeded_return(query_text),dtype=np.float32)[None,:]
    D=np.array([embeded_return(t) for t in docs],dtype=np.float32)
    qn=_l2norm(q)
    Dn=_l2norm(D)
    sims=(Dn @qn.T).ravel()
    top_idx=np.argpartition(-sims,top_k)[:top_k]
    top_idx=top_idx[np.argsort(-sims[top_idx])]
    print("here")
    results=[docs[i] for i in top_idx]
    print("final results=",results)
    return results
def serialize_mood_entry(entry) -> str:
    """Turn a mood entry model instance into a text snippet for embedding."""
    # Prefer the model’s brief_context if available
    bc = getattr(entry, "brief_context", None)
    if callable(bc):
        txt = bc(include_quote=True)
        if txt and txt.strip():
            return txt

    # Fallbacks: stitch together common fields
    parts = []
    try:
        parts.append(f"Note: {entry.note.note_title}")
        if getattr(entry.note, "note_description", None):
            parts.append(f"Desc: {entry.note.note_description}")
    except Exception:
        pass

    for attr in ("abstract", "key_facts", "actions", "decisions", "goals",
                 "positive_events", "outcomes", "pleasant_emotions", "lessons"):
        if hasattr(entry, attr):
            val = getattr(entry, attr)
            if isinstance(val, str) and val.strip():
                parts.append(val)
            elif isinstance(val, list) and val:
                # take a couple of items to keep prompt compact
                parts.append(str(val[:3]))

    return "\n".join(p for p in parts if p).strip() or f"entry_id={entry.id}"

@login_required_custom
def ai_agent(request):
    user_id = request.session['User_id']
    notes = new_notes.objects.filter(user_notes_id=user_id)
    output_text = None

    if request.method == "POST":
        mood = request.POST.get('mood')
        selected_note_ids = [int(x) for x in request.POST.getlist('selected_notes') if x.strip()]
        extra_details = request.POST.get('extra_details', '')
        output_format = request.POST.get('output_format', 'paragraph')
        mood_schema1=mood_schema()
        # Map mood to model
        mood1=Mood()
        mood_models = {
                "General": (general_agent, "gen_info",mood_schema1.General,mood1.General_detail),
                "Happy": (Happy_agent, "hap_info",mood_schema1.Happy,mood1.Happy_detail),
                "Hopeful": (Hopeful_agent, "hop_info",mood_schema1.Happy,mood1.Hopeful_detail),
                "Reflective": (Reflective_agent, "ref_info",mood_schema1.Reflective,mood1.Reflective_detail),
                "Motivation": (motivation_agent, "mot_info",mood_schema1.Motivation,mood1.Motivation_detail),
                "Calm": (calm_agent, "calm_info",mood_schema1.Calm,mood1.Calm_detail),
                "Dramatic": (Dramatic_agent, "dram_info",mood_schema1.Dramatic,mood1.Dramatic_detail),
                "Funny": (Funny_agent, "fun_info",mood_schema1.Funny,mood1.Funny_detail)
        }
        
                          
        formated=format()
        formating={
             "paragraph":formated.Paragraph_detail,
             "story":formated.Story_detail,
             "poem":formated.Poem_detail,
             "letter":formated.Letter_detail,
             "journal_entry":formated.Journal_entry_detail,
             "summary":formated.Summary_detail
        }
        print(f"Selected mood :   {mood}")

        mood_mode = mood_models[mood]
        format_prompt_expanded=formating[output_format]
        mood_schema_json=mood_models[mood][2]
        mood_prompt_expanded=mood_models[mood][3]
        mood_model=mood_models[mood][0]
        combine_master_schema=combine_master(extra_details, mood_prompt_expanded,mood_schema_json,format_prompt_expanded)
        # Resolve the notes queryset (helps catch mismatches early)
        selected_notes_qs = new_notes.objects.filter(
         user_notes_id=user_id, id__in=selected_note_ids
        )
        print("combine mater schema=",combine_master_schema)
# Use the ORM field name ("note") or "note_id" — NOT db_column
        mood_entries = mood_model.objects.filter(note__in=selected_notes_qs)
# (equivalent): mood_entries = mood_model.objects.filter(note_id__in=selected_note_ids)
       # notes_text = " ".join(getattr(entry, field_name) for entry in mood_entries)
        print("mood_entries=",mood_entries)
        docs_texts = [serialize_mood_entry(e) for e in mood_entries]
        print("docs_text=",docs_texts)
        final_chunks=rank_bycosine(combine_master_schema,docs_texts,len(docs_texts))
        if isinstance(final_chunks,list):
            context_text="\n\n".join(str(x) for x in final_chunks)
        else:
            context_text=str(final_chunks)    
        context_text+= mood_prompt_expanded
        context_text+="format="   
        context_text+=format_prompt_expanded

        # TODO: Add TTS output here if needed
        client=get_client()    
        response=client.chat.completions.create(
                    model=os.getenv("DEPLOYMENT_NAME"),
                    messages=[
                       {"role": "system", "content": "You are a helpful writing assistant."},
                        {"role": "user", "content": f"Use the following context to produce the requested output:\n\n{context_text}\n"}
    
                    ]
                )
        output_text=response.choices[0].message.content
    return render(request, 'application/ai_agent.html', {
        'notes': notes,
        'output_text': output_text
    })
