from django.contrib import admin
from .models import CentralizedOracle
from .models import EventDescription, ScalarEventDescription, CategoricalEventDescription
from .models import OutcomeToken, OutcomeTokenBalance
from .models import Market, CategoricalEvent, ScalarEvent
from .models import BuyOrder, SellOrder
from .models import TournamentParticipant
from .models import TournamentWhitelistedCreator

admin.site.register(Market)
admin.site.register(CategoricalEvent)
admin.site.register(ScalarEvent)
admin.site.register(OutcomeToken)
admin.site.register(CentralizedOracle)
admin.site.register(EventDescription)
admin.site.register(ScalarEventDescription)
admin.site.register(CategoricalEventDescription)
admin.site.register(OutcomeTokenBalance)
admin.site.register(BuyOrder)
admin.site.register(SellOrder)
admin.site.register(TournamentParticipant)
admin.site.register(TournamentWhitelistedCreator)
