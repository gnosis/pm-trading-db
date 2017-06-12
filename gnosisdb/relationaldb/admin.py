from django.contrib import admin
from .models import UltimateOracle, CentralizedOracle
from .models import EventDescription, ScalarEventDescription, CategoricalEventDescription
from .models import OutcomeToken
from .models import Event, Market

admin.site.register(Market)
admin.site.register(Event)
admin.site.register(OutcomeToken)
admin.site.register(UltimateOracle)
admin.site.register(CentralizedOracle)
admin.site.register(EventDescription)
admin.site.register(ScalarEventDescription)
admin.site.register(CategoricalEventDescription)
