from django.core.management.base import BaseCommand
from web3 import Web3, HTTPProvider
from django.conf import settings
from gnosisdb.chainevents.abis import abi_file_path, load_json_file


class Command(BaseCommand):
    help = 'Cleans the Relational Database and sets up all required configuration'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            'users',
        )

        parser.add_argument(
            'amount',
            type=int,
        )

    def handle(self, *args, **options):
        if options.get('users'):
            users = options['users'].split(",")
            amount = options['amount']
            self.stdout.write(self.style.SUCCESS('Preparing to issue {} tokens for users {}'.format(amount, options['users'])))
            protocol = 'https' if settings.ETHEREUM_NODE_SSL else 'http'
            provider_uri = '{}://{}:{}'.format(
                protocol,
                settings.ETHEREUM_NODE_HOST,
                settings.ETHEREUM_NODE_PORT,
            )
            rpc_provider = HTTPProvider(provider_uri)

            self.web3 = Web3(rpc_provider)
            abi = load_json_file(abi_file_path('TournamentToken.json'))
            token = self.web3.eth.contract(abi=abi, address=settings.TOURNAMENT_TOKEN)
            tx = token.transact(
                {
                    'from': settings.ETHEREUM_DEFAULT_ACCOUNT,
                    'gasPrice': 50000000000,
                    'gas': 2000000
                }
            ).issue(users, amount)
            self.stdout.write(self.style.SUCCESS('Sent transaction {}'.format(tx)))
        else:
            self.stdout.write(
                self.style.ERROR('python manage.py issue_tournament_tokens <0xaddress,0xaddress2...> 100')
            )
