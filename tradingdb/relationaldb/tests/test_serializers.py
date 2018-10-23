from time import mktime

from django.conf import settings
from django.test import TestCase
from django_eth_events.utils import normalize_address_without_0x
from django_eth_events.web3_service import Web3Service, Web3ServiceProvider
from eth_tester import EthereumTester
from web3.providers.eth_tester import EthereumTesterProvider

from chainevents.abis import abi_file_path, load_json_file
from ipfs.ipfs import Ipfs

from ..models import (OutcomeToken, OutcomeTokenBalance,
                      ScalarEventDescription, TournamentParticipant,
                      TournamentParticipantBalance)
from ..serializers import (CategoricalEventSerializer,
                           CentralizedOracleInstanceSerializer,
                           CentralizedOracleSerializer,
                           GenericTournamentParticipantEventSerializerTimestamped,
                           IPFSEventDescriptionDeserializer,
                           MarketSerializerTimestamped,
                           OutcomeTokenInstanceSerializer,
                           OutcomeTokenIssuanceSerializer,
                           OutcomeTokenRevocationSerializer,
                           OutcomeTokenTransferSerializer,
                           ScalarEventSerializer,
                           TournamentTokenIssuanceSerializer,
                           TournamentTokenTransferSerializer,
                           UportTournamentParticipantSerializerEventSerializerTimestamped)
from .factories import (CategoricalEventDescriptionFactory,
                        CategoricalEventFactory, CentralizedOracleFactory,
                        EventFactory, MarketFactory,
                        OutcomeTokenBalanceFactory, OutcomeTokenFactory,
                        ScalarEventDescriptionFactory, ScalarEventFactory,
                        TournamentParticipantBalanceFactory)
from .utils import tournament_token_bytecode


class TestSerializers(TestCase):

    def setUp(self):
        self.ipfs = Ipfs()

    def test_create_centralized_oracle(self):
        oracle = CentralizedOracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address,
                },
                {
                    'name': 'ipfsHash',
                    'value': oracle.event_description.ipfs_hash[1:-7] + ''
                }
            ]
        }
        oracle.delete()
        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        # ipfs_hash not saved to IPFS
        self.assertFalse(s.is_valid(), s.errors)
        # oracle.event_description
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolutionDate': oracle.event_description.resolution_date.isoformat(),
            'outcomes': ['Yes', 'No']
        }

        # save event_description to IPFS
        ipfs_hash = self.ipfs.post(event_description_json)
        oracle_event.get('params')[2]['value'] = ipfs_hash

        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_centralized_oracle_scalar_event_with_outcomes(self):
        oracle = CentralizedOracleFactory()

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address,
                },
                {
                    'name': 'ipfsHash',
                    'value': 'something unknown'
                }
            ]
        }
        # remove test oracle before creating it again
        oracle.delete()
        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        # ipfs_hash not saved to IPFS
        self.assertFalse(s.is_valid(), s.errors)
        # oracle.event_description
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolutionDate': oracle.event_description.resolution_date.isoformat(),
            'outcomes': [],
            'unit': 'unit',
            'decimals': 2
        }

        # save event_description to IPFS
        ipfs_hash = self.ipfs.post(event_description_json)
        oracle_event.get('params')[2]['value'] = ipfs_hash

        s = CentralizedOracleSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

        self.assertEqual(ScalarEventDescription.objects.filter(ipfs_hash=instance.event_description.ipfs_hash).count(), 1)

    def test_event_description_different_outcomes(self):

        oracle = CentralizedOracleFactory()

        oracle.event_description.outcomes = ['Yes', 'No', 'Third']
        oracle.event_description.save()

        event = CategoricalEventFactory(oracle=oracle)

        # Categorical Event with different outcomes

        block = {
            'number': event.creation_block,
            'timestamp': mktime(event.creation_date_time.timetuple())
        }

        categorical_event = {
            'address': event.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event.creator
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'outcomeCount',
                    'value': 2
                },
                {
                    'name': 'categoricalEvent',
                    'value': event.address,
                }
            ]
        }

        event.delete()

        s = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertFalse(s.is_valid())
        categorical_event['params'][3]['value'] = 3
        s2 = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertTrue(s2.is_valid(), s.errors)
        instance = s2.save()
        self.assertIsNotNone(instance)

    def test_create_scalar_with_categorical_description(self):

        event_description = CategoricalEventDescriptionFactory()
        oracle = CentralizedOracleFactory(event_description=event_description)

        # Scalar Event with different outcomes
        event = ScalarEventFactory()

        block = {
            'number': event.creation_block,
            'timestamp': mktime(event.creation_date_time.timetuple())
        }

        scalar_event = {
            'address': event.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event.creator
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'upperBound',
                    'value': event.upper_bound
                },
                {
                    'name': 'lowerBound',
                    'value': event.lower_bound
                },
                {
                    'name': 'scalarEvent',
                    'value': event.address,
                }
            ]
        }

        event.delete()
        s = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertFalse(s.is_valid())
        scalar_event['params'][3]['value'] = 3
        scalar_descripion = ScalarEventDescriptionFactory()
        oracle.event_description = scalar_descripion
        oracle.save()
        s2 = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertTrue(s2.is_valid(), s.errors)
        instance = s2.save()
        self.assertIsNotNone(instance)

    def test_create_scalar_event(self):
        event = ScalarEventFactory()
        event_description = ScalarEventDescriptionFactory()
        oracle = CentralizedOracleFactory(event_description=event_description)

        block = {
            'number': event.creation_block,
            'timestamp': mktime(event.creation_date_time.timetuple())
        }

        scalar_event = {
            'address': event.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event.collateral_token
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'upperBound',
                    'value': 1
                },
                {
                    'name': 'lowerBound',
                    'value': 0
                }
            ]
        }
        event.delete()
        s = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        scalar_event.get('params').append({
            'name': 'scalarEvent',
            'value': event.address
        })

        s = ScalarEventSerializer(data=scalar_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_categorical_event(self):
        event = CategoricalEventFactory()
        oracle = CentralizedOracleFactory()

        block = {
            'number': event.creation_block,
            'timestamp': mktime(event.creation_date_time.timetuple())
        }

        categorical_event = {
            'address': event.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': event.creator
                },
                {
                    'name': 'collateralToken',
                    'value': event.collateral_token
                },
                {
                    'name': 'oracle',
                    'value': oracle.address
                },
                {
                    'name': 'outcomeCount',
                    'value': 2
                }
            ]
        }
        event.delete()
        s = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        categorical_event.get('params').append({
            'name': 'categoricalEvent',
            'value': event.address
        })

        s = CategoricalEventSerializer(data=categorical_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_market(self):
        oracle = CentralizedOracleFactory()
        event = CategoricalEventFactory(oracle=oracle)
        market = MarketFactory()

        block = {
            'number': market.creation_block,
            'timestamp': mktime(market.creation_date_time.timetuple())
        }

        market_dict = {
            'address': market.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': market.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address,
                },
                {
                    'name': 'marketMaker',
                    'value': market.market_maker
                },
                {
                    'name': 'fee',
                    'value': market.fee
                },
                {
                    'name': 'market',
                    'value': market.address
                }
            ]
        }
        market.delete()

        s = MarketSerializerTimestamped(data=market_dict, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        market_dict.get('params').append({
            'name': 'eventContract',
            'value': market.address
        })

        market_dict.get('params').append({
            'name': 'fee',
            'value': market.fee
        })

        s = MarketSerializerTimestamped(data=market_dict, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        market_dict.get('params')[-2]['value'] = event.address

        s = MarketSerializerTimestamped(data=market_dict, block=block)
        self.assertFalse(s.is_valid(), s.errors)

        marketMaker = [x for x in market_dict.get('params') if x.get('name') == 'marketMaker'][0]
        marketMaker.update({'value': normalize_address_without_0x(settings.LMSR_MARKET_MAKER)})

        s = MarketSerializerTimestamped(data=market_dict, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_categorical_event_description(self):
        event_description = CategoricalEventDescriptionFactory()
        event_description.delete()
        categorical_event_description_json = {
            'title': event_description.title,
            'description': event_description.description,
            'resolution_date': event_description.resolution_date.isoformat(),
            'outcomes': event_description.outcomes
        }
        ipfs_hash = self.ipfs.post(categorical_event_description_json)
        serializer = IPFSEventDescriptionDeserializer(data={'ipfs_hash': ipfs_hash})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNotNone(serializer.save())

    def test_create_scalar_event_description(self):
        event_description = ScalarEventDescriptionFactory()
        event_description.delete()
        scalar_event_description_json = {
            'title': event_description.title,
            'description': event_description.description,
            'resolution_date': event_description.resolution_date.isoformat(),
            'unit': event_description.unit,
            'decimals': event_description.decimals,
        }
        ipfs_hash = self.ipfs.post(scalar_event_description_json)
        serializer = IPFSEventDescriptionDeserializer(data={'ipfs_hash': ipfs_hash})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIsNotNone(serializer.save())

    def test_create_centralized_oracle_instance(self):
        oracle = CentralizedOracleFactory()
        oracle.delete()
        # oracle.event_description
        event_description_json = {
            'title': oracle.event_description.title,
            'description': oracle.event_description.description,
            'resolutionDate': oracle.event_description.resolution_date.isoformat(),
            'outcomes': oracle.event_description.outcomes
        }

        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        oracle_event = {
            'address': oracle.factory,
            'params': [
                {
                    'name': 'creator',
                    'value': oracle.creator
                },
                {
                    'name': 'centralizedOracle',
                    'value': oracle.address,
                },
                {
                    'name': 'ipfsHash',
                    'value': oracle.event_description.ipfs_hash
                }
            ]
        }

        s = CentralizedOracleInstanceSerializer(data=oracle_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_create_outcome_token_instance(self):
        outcome_token = OutcomeTokenFactory()
        event = ScalarEventFactory()

        outcome_token_event = {
            'address': event.address,
            'params': [
                {
                    'name': 'outcomeToken',
                    'value': outcome_token.address,
                },
                {
                    'name': 'index',
                    'value': outcome_token.index
                }
            ]
        }
        outcome_token.delete()

        s = OutcomeTokenInstanceSerializer(data=outcome_token_event)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        self.assertIsNotNone(instance)

    def test_issuance_outcome_token(self):
        outcome_token = OutcomeTokenFactory()
        event = EventFactory()

        issuance_event = {
            'name': 'Issuance',
            'address': outcome_token.address,
            'params': [
                {
                    'name': 'owner',
                    'value': event.address
                },
                {
                    'name': 'amount',
                    'value': 20,
                }
            ]
        }

        s = OutcomeTokenIssuanceSerializer(data=issuance_event)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()

        balance = OutcomeTokenBalance.objects.get(owner=event.address)
        self.assertEqual(balance.balance, 20)
        self.assertIsNotNone(instance)

        self.assertEqual(OutcomeToken.objects.get(address=outcome_token.address).total_supply,
                         outcome_token.total_supply + 20)

    def test_revocation_outcome_token(self):
        balance = OutcomeTokenBalanceFactory()
        balance.balance = 20
        balance.save()

        issuance_event = {
            'name': 'Revocation',
            'address': balance.outcome_token.address,
            'params': [
                {
                    'name': 'owner',
                    'value': balance.owner
                },
                {
                    'name': 'amount',
                    'value': 20,
                }
            ]
        }

        s = OutcomeTokenRevocationSerializer(data=issuance_event)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()

        self.assertEqual(OutcomeTokenBalance.objects.get(owner=balance.owner).balance, 0)
        self.assertIsNotNone(instance)

        self.assertEqual(OutcomeToken.objects.get(address=balance.outcome_token.address).total_supply,
                         balance.outcome_token.total_supply - 20)

    def test_transfer_outcome_token(self):
        outcome_token_balance = OutcomeTokenBalanceFactory()
        event = EventFactory()
        outcome_token_balance.balance = 20
        outcome_token_balance.save()

        transfer_event = {
            'name': 'Transfer',
            'address': outcome_token_balance.outcome_token.address,
            'params': [
                {
                    'name': 'from',
                    'value': outcome_token_balance.owner
                },
                {
                    'name': 'to',
                    'value': event.address
                },
                {
                    'name': 'value',
                    'value': outcome_token_balance.balance,
                }
            ]
        }

        s = OutcomeTokenTransferSerializer(data=transfer_event)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()

        self.assertEqual(OutcomeTokenBalance.objects.get(owner=outcome_token_balance.owner).balance, 0)
        self.assertIsNotNone(instance)
        self.assertEqual(instance.owner, event.address)
        self.assertEqual(instance.balance, 20)

    def test_save_generic_tournament_participant(self):
        oracle = CentralizedOracleFactory()
        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        contract_address = "d833215cbcc3f914bd1c9ece3ee7bf8b14f841bb"
        registrant_address = "90f8bf6a479f320ead074411a4b0e7944ea8c9c1"
        registrant_address2 = "80f8bf6a479f320ead074411a4b0e7944ea8c9c2"
        registered_mainnet_address = "ffcf8fdee72ac11b5c542428b35eef5769c409f0"

        participant_event = {
            "address": contract_address,
            "name": "AddressRegistration",
            "params": [
                {
                    "name": "registrant",
                    "value": registrant_address,
                },
                {
                    "name": "registeredMainnetAddress",
                    "value": registered_mainnet_address,
                }
            ]
        }
        s = GenericTournamentParticipantEventSerializerTimestamped(data=participant_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(TournamentParticipant.objects.all().count(), 0)
        instance = s.save()

        self.assertEqual(TournamentParticipant.objects.all().count(), 1)
        self.assertEqual(TournamentParticipant.objects.first().tournament_balance.balance, 0)
        self.assertIsNotNone(instance)
        self.assertEqual(instance.address, registrant_address)
        self.assertEqual(instance.mainnet_address, registered_mainnet_address)

        web3_service = Web3Service(provider=EthereumTesterProvider(EthereumTester()))
        web3 = web3_service.web3
        checksumed_registrant_address2 = web3.toChecksumAddress('0x' + registrant_address2)
        tournament_token_abi = load_json_file(abi_file_path('TournamentToken.json'))

        # create tournament token
        tournament_token = web3.eth.contract(abi=tournament_token_abi, bytecode=tournament_token_bytecode)
        tx_hash = tournament_token.constructor().transact()
        tournament_token_address = web3.eth.getTransactionReceipt(tx_hash).get('contractAddress')
        self.assertIsNotNone(tournament_token_address)
        # Get token instance
        token_contract = web3.eth.contract(abi=tournament_token_abi, address=tournament_token_address)
        # Issue tokens
        tokens_amount = 100
        tx_hash = token_contract.functions.issue([checksumed_registrant_address2], tokens_amount).transact(
            {
                'from': web3.eth.coinbase
            }
        )
        blockchain_balance = token_contract.functions.balanceOf(checksumed_registrant_address2).call()
        self.assertEqual(blockchain_balance, tokens_amount)

        # Save participant 2
        oracle = CentralizedOracleFactory()
        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        participant_with_tokens_event = {
            "address": contract_address,
            "name": "AddressRegistration",
            "params": [
                {
                    "name": "registrant",
                    "value": checksumed_registrant_address2[2:],
                },
                {
                    "name": "registeredMainnetAddress",
                    "value": registered_mainnet_address,
                }
            ]
        }

        # Mocks
        with self.settings(TOURNAMENT_TOKEN=tournament_token_address):
            # Mock Web3Service __new__ method to retrieve the same web3 instance used to deploy the contract
            Web3ServiceProvider.instance = web3_service
            s = GenericTournamentParticipantEventSerializerTimestamped(data=participant_with_tokens_event, block=block)
            self.assertTrue(s.is_valid(), s.errors)
            instance = s.save()
            self.assertEqual(TournamentParticipant.objects.all().count(), 2)
            self.assertEqual(TournamentParticipant.objects.first().tournament_balance.balance, tokens_amount)

    def test_save_uport_tournament_participant(self):
        oracle = CentralizedOracleFactory()
        block = {
            'number': oracle.creation_block,
            'timestamp': mktime(oracle.creation_date_time.timetuple())
        }

        identity = 'ebe4dd7a4a9e712e742862719aa04709cc6d80a6'

        participant_event = {
            'name': 'IdentityCreated',
            'address': 'abbcd5b340c80b5f1c0545c04c987b87310296ae',
            'params': [
                {
                    'name': 'identity',
                    'value': identity
                },
                {
                    'name': 'creator',
                    'value': '50858f2c7873fac9398ed9c195d185089caa7967'
                },
                {
                    'name': 'owner',
                    'value': '8f357b2c8071c2254afbc65907997f9adea6cc78',
                },
                {
                    'name': 'recoveryKey',
                    'value': 'b67c2d2fcfa3e918e3f9a5218025ebdd12d26212'
                }
            ]
        }

        s = UportTournamentParticipantSerializerEventSerializerTimestamped(data=participant_event, block=block)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(TournamentParticipant.objects.all().count(), 0)
        instance = s.save()

        self.assertEqual(TournamentParticipant.objects.all().count(), 1)
        self.assertIsNotNone(instance)
        self.assertEqual(instance.address, identity)

    def test_tournament_issuance(self):
        participant_balance = TournamentParticipantBalanceFactory()
        participant = participant_balance.participant
        participant_event = {
            'name': 'Issuance',
            'address': 'not needed',
            'params': [
                {
                    'name': 'owner',
                    'value': participant.address
                },
                {
                    'name': 'amount',
                    'value': 123
                }
            ]
        }
        self.assertEqual(TournamentParticipantBalance.objects.get(participant=participant.address).balance, participant_balance.balance)
        s = TournamentTokenIssuanceSerializer(data=participant_event)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(TournamentParticipantBalance.objects.get(participant=participant.address).balance, participant_balance.balance)
        instance = s.save()

        self.assertIsNotNone(instance)
        self.assertEqual(instance.participant.address, participant.address)
        self.assertEqual(instance.balance, participant_balance.balance + 123)

    def test_tournament_token_transfer(self):
        # Test the token transfer serializer
        participant_balance1 = TournamentParticipantBalanceFactory()
        participant1 = participant_balance1.participant
        participant_balance2 = TournamentParticipantBalanceFactory()
        participant2 = participant_balance2.participant

        transfer_event = {
            'name': 'Transfer',
            'address': 'not needed',
            'params': [
                {
                    'name': 'from',
                    'value': participant1.address
                },
                {
                    'name': 'to',
                    'value': participant2.address
                },
                {
                    'name': 'value',
                    'value': 150,
                }
            ]
        }

        transfer_serializer = TournamentTokenTransferSerializer(data=transfer_event)
        self.assertTrue(transfer_serializer.is_valid(), transfer_serializer.errors)
        instance = transfer_serializer.save()
        self.assertEqual(TournamentParticipantBalance.objects.get(participant=participant2.address).balance.__float__(), float(participant_balance2.balance+150))
        self.assertEqual(TournamentParticipantBalance.objects.get(participant=participant1.address).balance.__float__(), float(participant_balance1.balance-150))
