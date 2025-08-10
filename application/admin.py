from django.contrib import admin
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

admin.site.register(new_notes)
admin.site.register(general_agent)
admin.site.register(Happy_agent)
admin.site.register(Hopeful_agent)
admin.site.register(Reflective_agent)
admin.site.register(motivation_agent)
admin.site.register(calm_agent)
admin.site.register(Dramatic_agent)
admin.site.register(Funny_agent)


# Register your models here.
