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
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

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
@login_required_custom
def add_note(request):
    user_id = request.session['User_id']
    user = Login_model.objects.get(id=user_id)

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')

        if title.strip() and description.strip():
            # Save main note
            note = new_notes.objects.create(
                user_notes=user,
                note_title=title,
                note_description=description
            )

            # Process with LLM for all moods
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",


                google_api_key=os.getenv("GOOGLE_API_KEY")
            )

            moods = {
                "General": (general_agent, "gen_info"),
                "Happy": (Happy_agent, "hap_info"),
                "Hopeful": (Hopeful_agent, "hop_info"),
                "Reflective": (Reflective_agent, "ref_info"),
                "Motivation": (motivation_agent, "mot_info"),
                "Calm": (calm_agent, "calm_info"),
                "Dramatic": (Dramatic_agent, "dram_info"),
                "Funny": (Funny_agent, "fun_info")
            }
            print("Model output =")
            for mood_name, (model_class, field_name) in moods.items():
                prompt = PromptTemplate(
                    input_variables=["desc"],
                    template=f"Rewrite the following note in a {mood_name} tone: {{desc}}"
                )
                chain = LLMChain(llm=llm, prompt=prompt)
                mood_output = chain.run(desc=description)

                model_class.objects.create(
                    general_notes=note,
                    **{field_name: mood_output}
                )
                print(f"for Mood:  {mood_name}")
                print(f"{ mood_output}\n")

    notes = new_notes.objects.filter(user_notes=user).order_by('-date')
    return render(request, 'application/add_note.html', {'notes': notes})


# ----------------- Delete Note -----------------
@login_required_custom
def delete_note(request, note_id):
    user_id = request.session['User_id']
    new_notes.objects.filter(id=note_id, user_notes_id=user_id).delete()
    return redirect('add_note')


# ----------------- AI Agent -----------------
@login_required_custom
def ai_agent(request):
    user_id = request.session['User_id']
    notes = new_notes.objects.filter(user_notes_id=user_id)
    output_text = None

    if request.method == "POST":
        mood = request.POST.get('mood')
        selected_note_ids = request.POST.getlist('selected_notes')
        extra_details = request.POST.get('extra_details', '')
        output_format = request.POST.get('output_format', 'paragraph')

        # Map mood to model
        mood_models = {
            "General": (general_agent, "gen_info"),
            "Happy": (Happy_agent, "hap_info"),
            "Hopeful": (Hopeful_agent, "hop_info"),
            "Reflective": (Reflective_agent, "ref_info"),
            "Motivation": (motivation_agent, "mot_info"),
            "Calm": (calm_agent, "calm_info"),
            "Dramatic": (Dramatic_agent, "dram_info"),
            "Funny": (Funny_agent, "fun_info")
        }
        print(f"Selected mood :   {mood}")
        mood_model, field_name = mood_models[mood]

        mood_entries = mood_model.objects.filter(
            general_notes_id__in=selected_note_ids
        )
        notes_text = " ".join(getattr(entry, field_name) for entry in mood_entries)

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",


            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        prompt = PromptTemplate(
            input_variables=["format", "notes", "extra"],
            template="Create a {format} using these mood-specific notes: {notes} also write in mentioned language English . Additional details: {extra}"
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        output_text = chain.run(format=output_format, notes=notes_text, extra=extra_details)

        # TODO: Add TTS output here if needed

    return render(request, 'application/ai_agent.html', {
        'notes': notes,
        'output_text': output_text
    })
