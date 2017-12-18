from django.core.management.base import BaseCommand
from web3 import Web3, HTTPProvider
from django.conf import settings
from gnosisdb.chainevents.abis import abi_file_path, load_json_file
from relationaldb.models import TournamentParticipant
from django.db import transaction


class Command(BaseCommand):
    help = 'Synchronizes balance from database and blockchain, hotfix for concurrency issue with user balance'

    def handle(self, *args, **options):
        users = TournamentParticipant.objects.all()
        self.style.SUCCESS('Synchronizing {} users'.format(users.count()))
        for user in users:

            # check blockchain balance
            protocol = 'https' if settings.ETHEREUM_NODE_SSL else 'http'
            provider_uri = '{}://{}:{}'.format(
                protocol,
                settings.ETHEREUM_NODE_HOST,
                settings.ETHEREUM_NODE_PORT,
            )
            rpc_provider = HTTPProvider(provider_uri)
            web3 = Web3(rpc_provider)
            abi = load_json_file(abi_file_path('TournamentToken.json'))
            token = web3.eth.contract(abi=abi, address=settings.TOURNAMENT_TOKEN)

            with transaction.atomic():
                locked_user = TournamentParticipant.objects.select_for_update().get(address=user.address)
                block_chain_balance = token.call().balanceOf(locked_user.address)
                if block_chain_balance != locked_user.balance:
                    self.stdout.write(self.style.SUCCESS(
                        'User {} had wrong balance, blockchain: {} | database: {}'.format(locked_user.address, block_chain_balance, locked_user.balance)))
                    locked_user.balance = block_chain_balance
                    locked_user.save()

        self.stdout.write(self.style.SUCCESS('Finished synchronizing balances'))
