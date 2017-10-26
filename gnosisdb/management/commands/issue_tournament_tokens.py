from django.core.management.base import BaseCommand
from web3 import Web3, HTTPProvider
from django.conf import settings
from gnosisdb.chainevents.abis import abi_file_path, load_json_file
import requests
import binascii

class Command(BaseCommand):
    help = 'Cleans the Relational Database and sets up all required configuration'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            'user',
        )

        parser.add_argument(
            'amount',
            type=int,
        )

    def handle(self, *args, **options):
        if options.get('user'):
            user = options['user']
            amount = options['amount']
            self.stdout.write(self.style.SUCCESS('Preparing to issue {} tokens for user {}'.format(amount, user)))
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

            data = token.encodeABI(fn_name='issue', args=[[user], amount])
            key = settings.ETHEREUM_PRIVATE_KEY
            account = self.web3.eth.account.privateKeyToAccount(key).address
            nonce = self.web3.eth.getTransactionCount(account=account)
            transaction = {
                'to': settings.TOURNAMENT_TOKEN,
                'value': 0,
                'data': data,
                'chainId': 4,
                'gasPrice': 10000000,
                'gas': 1000000,
                'nonce': nonce
            }

            signed = self.web3.eth.account.signTransaction(transaction, key)
            data = { "jsonrpc":"2.0","method":"eth_sendRawTransaction","params":["0x" + binascii.hexlify(str(signed.rawTransaction))], "id":1 }
            r = requests.post(provider_uri, json = data)
            self.stdout.write(self.style.SUCCESS(str(r.status_code)))
            self.stdout.write(self.style.SUCCESS(r.reason))
            self.stdout.write(self.style.SUCCESS('Sent transaction {}'.format(binascii.hexlify(signed.hash))))
        else:
            self.stdout.write(self.style.ERROR('python manage.py issue_tournament_tokens --user <0xaddress> --amount 100'))
