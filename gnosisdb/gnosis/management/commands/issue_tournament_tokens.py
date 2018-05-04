from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django_eth_events.web3_service import Web3Service

from chainevents.abis import abi_file_path, load_json_file


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

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get('users'):
            web3_service = Web3Service()
            web3 = web3_service.web3

            users = [web3_service.make_sure_cheksumed_address(user) for user in options['users'].split(",")]
            amount = options['amount']
            self.stdout.write(
                self.style.SUCCESS('Preparing to issue {} tokens for user{} {}'.format(amount,
                                                                                       's' if len(users) > 1 else '',
                                                                                       options['users'])
                                   )
            )

            tournament_token_address = web3_service.make_sure_cheksumed_address(settings.TOURNAMENT_TOKEN)
            abi = load_json_file(abi_file_path('TournamentToken.json'))
            token_contract = web3.eth.contract(abi=abi,
                                               address=tournament_token_address)
            gas = settings.ISSUANCE_GAS
            gas_price = settings.ISSUANCE_GAS_PRICE
            ethereum_default_account = web3_service.make_sure_cheksumed_address(settings.ETHEREUM_DEFAULT_ACCOUNT)

            if getattr(settings, 'ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY'):
                # https://web3py.readthedocs.io/en/stable/web3.eth.account.html?highlight=enable_unaudited_featured#not-acceptable-for-production
                tx = token_contract.functions.issue(users, amount).buildTransaction(
                    {
                        'nonce': web3.eth.getTransactionCount(ethereum_default_account),
                        'gasPrice': gas_price,
                        'gas': gas,
                    }
                )
                signed_tx = web3.eth.account.signTransaction(tx,
                                                             private_key=settings.ETHEREUM_DEFAULT_ACCOUNT_PRIVATE_KEY)
                tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            else:
                tx_hash = token_contract.functions.issue(users, amount).transact(
                    {
                        'from': ethereum_default_account,
                        'gasPrice': gas_price,
                        'gas': gas,
                    }
                )

            self.stdout.write(self.style.SUCCESS('Sent transaction {}'.format(tx_hash.hex())))
        else:
            self.stdout.write(
                self.style.ERROR('python manage.py issue_tournament_tokens '
                                 '<0xchecksum_address,0xchecksum_address2...> 100')
            )
