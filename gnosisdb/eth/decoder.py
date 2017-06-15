from ethereum.utils import sha3
from utils import Singleton
from eth_abi import decode_abi
from ethereum.utils import remove_0x_head
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


class Decoder(Singleton):

    methods = {}

    def add_abi(self, abi):
        added = 0
        for item in abi:
            if item.get(u'name'):
                method_header = None
                if item.get(u'inputs'):
                    # Generate methodID and link it with the abi
                    method_header = "{}({})".format(item[u'name'],
                                                    ','.join(map(lambda input: input[u'type'], item[u'inputs'])))
                else:
                    method_header = "{}()".format(item[u'name'])

                method_id = sha3(method_header).encode('hex')
                self.methods[method_id] = item
                added += 1
        return added

    def remove_abi(self, abis):
        for item in abis:
            if item.get(u'name'):
                # Generate methodID and link it with the abi
                method_header = "{}({})".format(item[u'name'],
                                                ','.join(map(lambda input: input[u'type'], item[u'inputs'])))
                method_id = sha3(method_header).encode('hex')
                if self.methods.get(method_id):
                    del self.methods[method_id]

    def decode_logs(self, logs):
        decoded = []
        for log in logs:
            method_id = log[u'topics'][0][2:]
            logger.info('method_id {}'.format(method_id))
            logger.info('methods {}'.format(self.methods))
            if self.methods.get(method_id):
                method = self.methods[method_id]
                logger.info('method {}'.format(method))
                decoded_params = []
                data_i = 0
                topics_i = 1
                data_types = []

                # get param types from properties not indexed
                for param in method[u'inputs']:
                    if not param[u'indexed']:
                        data_types.append(param[u'type'])

                decoded_data = decode_abi(data_types, log[u'data'])

                for param in method[u'inputs']:
                    decoded_p = {
                        u'name': param[u'name']
                    }
                    logger.info('param: {} {}'.format(param, decoded_p))
                    if param[u'indexed']:
                        decoded_p[u'value'] = log[u'topics'][topics_i]
                        topics_i += 1
                    else:
                        decoded_p[u'value'] = decoded_data[data_i]
                        data_i += 1

                    if u'[]' in param[u'type']:
                        if u'int' in param[u'type']:
                            decoded_p[u'value'] = list([long(account, 16) for account in decoded_p[u'value']])
                        elif u'address' in param[u'type']:
                            decoded_p[u'value'] = list([remove_0x_head(account) for account in decoded_p[u'value']])
                        else:
                            decoded_p[u'value'] = list(decoded_p[u'value'])
                    elif u'int' in param[u'type']:
                        decoded_p[u'value'] = long(decoded_p[u'value'])
                    elif u'address' == param[u'type']:
                        address = remove_0x_head(decoded_p[u'value'])
                        logger.info('address, length {}'.format(len(address)))
                        if len(address) == 40:
                            decoded_p[u'value'] = address
                        elif len(address) == 64:
                            decoded_p[u'value'] = decoded_p[u'value'][26::]

                    decoded_params.append(decoded_p)
                decoded.append({
                    u'params': decoded_params,
                    u'name': method[u'name'],
                    u'address': remove_0x_head(log[u'address'])
                })

        return decoded
