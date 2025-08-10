from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import JsonResponse
from authentication.models import Login_model
from authentication.decorators import login_required_custom
from .models import Note
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pyttsx3

load_dotenv()

@login_required_custom
def add_note(request):
    user = Login_model.objects.get(id=request.session['User_id'])

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title and content:
            Note.objects.create(user=user, title=title, content=content)
            return redirect('add_note')

    notes = Note.objects.filter(user=user).order_by('-created_at')
    return render(request, "notes/add_note.html", {"notes": notes, "user": user})


@login_required_custom
def ai_agent(request):
    user = Login_model.objects.get(id=request.session['User_id'])
    notes = Note.objects.filter(user=user)

    if request.method == "POST":
        mood = request.POST.get("mood")
        selected_note_ids = request.POST.getlist("selected_notes")
        extra_info = request.POST.get("extra_info")

        selected_notes = Note.objects.filter(id__in=selected_note_ids, user=user)
        notes_text = "\n".join([n.content for n in selected_notes])

        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        prompt = PromptTemplate.from_template(
            "You are a supportive AI companion. The user is in a {mood} mood. "
            "Use the following notes:\n{notes}\n"
            "And consider this extra info: {extra_info}\n"
            "Create a warm and engaging response."
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.invoke({"mood": mood, "notes": notes_text, "extra_info": extra_info})
        ai_text = result["text"]

        # Text-to-speech
        engine = pyttsx3.init()
        engine.say(ai_text)
        engine.runAndWait()

        return render(request, "notes/ai_agent.html", {
            "notes": notes,
            "ai_text": ai_text,
            "mood": mood
        })

    return render(request, "notes/ai_agent.html", {"notes": notes})

