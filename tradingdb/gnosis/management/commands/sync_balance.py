from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django_eth_events.web3_service import Web3ServiceProvider

from tradingdb.chainevents.abis import abi_file_path, load_json_file
from tradingdb.relationaldb.models import (TournamentParticipant,
                                           TournamentParticipantBalance)


class Command(BaseCommand):
    help = 'Synchronizes balance from database and blockchain, hotfix for concurrency issue with user balance'

    def handle(self, *args, **options):
        users = TournamentParticipant.objects.all()
        self.style.SUCCESS('Synchronizing {} users'.format(users.count()))
        for user in users:

            # check blockchain balance
            web3_service = Web3ServiceProvider()
            web3 = web3_service.web3
            tournament_token_address = web3_service.make_sure_cheksumed_address(settings.TOURNAMENT_TOKEN)
            abi = load_json_file(abi_file_path('TournamentToken.json'))
            token_contract = web3.eth.contract(abi=abi, address=tournament_token_address)

            with transaction.atomic():
                locked_user = TournamentParticipant.objects.select_for_update().get(address=user.address)
                TournamentParticipantBalance.objects.get_or_create(participant=locked_user)
                user_address = web3.toChecksumAddress(locked_user.address)
                block_chain_balance = token_contract.functions.balanceOf(user_address).call()
                if block_chain_balance != locked_user.tournament_balance.balance:
                    self.stdout.write(self.style.SUCCESS(
                        'User {} had wrong balance, blockchain: {} | database: {}'.format(user_address,
                                                                                          block_chain_balance,
                                                                                          locked_user.tournament_balance.balance))
                    )
                    locked_user.tournament_balance.balance = block_chain_balance
                    locked_user.tournament_balance.save()

        self.stdout.write(self.style.SUCCESS('Finished synchronizing balances'))
