from django.contrib import admin

from .models import (BuyOrder, CategoricalEvent, CategoricalEventDescription,
                     CentralizedOracle, EventDescription, Market, OutcomeToken,
                     OutcomeTokenBalance, ScalarEvent, ScalarEventDescription,
                     SellOrder, TournamentParticipant,
                     TournamentWhitelistedCreator)

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
