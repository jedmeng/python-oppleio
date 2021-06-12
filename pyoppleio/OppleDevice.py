import socket
import re

from . import const, Message

MESSAGE_TYPE = const.MESSAGE_TYPE
SEARCH_RES_OFFSET = const.SEARCH_RES_OFFSET


class OppleDevice(object):
    def __init__(self, ip='', message=None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', 0))
        self.socket.settimeout(2)

        self.id = 0
        self.port = 0
        self.version = 0
        self.name = ''
        self.ip = ip
        self.ip_raw = ()
        self.mac = ''
        self.mac_raw = ()
        self.server_port = self.socket.getsockname()[1]
        self.is_init = False
        self.is_online = False

        if message:
            self.init(message)
        else:
            self.async_init()

    def init(self, message):
        self.id = message.get(SEARCH_RES_OFFSET['ID_LOW'], 4, value_type=int)
        self.port = message.get(SEARCH_RES_OFFSET['PORT'], 2, value_type=int)
        self.version = message.get(SEARCH_RES_OFFSET['VERSION'], 4, value_type=int)
        self.name = re.sub(r'@*$', '', str(message.get(SEARCH_RES_OFFSET['NAME'], 0xE), 'gbk'))
        self.ip_raw = message.get(SEARCH_RES_OFFSET['IP'], 4)
        self.mac_raw = message.get(SEARCH_RES_OFFSET['MAC'], 6)

        self.ip = '.'.join(map(lambda x: str(x), self.ip_raw))
        self.mac = ':'.join(map(lambda x: hex(x)[2:], self.mac_raw))

        self.is_init = True
        self.is_online = True

    def async_init(self):
        self.port = const.BROADCAST_PORT
        message = self.send('SEARCH', reply=True)
        if message:
            self.init(message)

    def send(self, message_type, data=None, reply=False):
        message = Message.build_message(MESSAGE_TYPE[message_type], data, self)
        self.socket.sendto(message.data, (self.ip, self.port))

        if reply:
            while True:
                try:
                    data, address = self.socket.recvfrom(1024)
                    incoming_message = Message.parse_message(data, self)

                    if message.get_request_sn() != incoming_message.get_response_sn():
                        continue

                    self.is_online = True
                    return incoming_message

                except socket.timeout:
                    self.is_online = False
                    return None


def search():
    message = Message.build_message(MESSAGE_TYPE['SEARCH'])
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(message.to_bytes(), ('255.255.255.255', const.BROADCAST_PORT))
    s.settimeout(2)

    from . import OppleLightDevice

    device_list = []

    while True:
        try:
            data, address = s.recvfrom(1024)
            message = Message.parse_message(data)

            if message.get(SEARCH_RES_OFFSET['CLASS_SKU'], 4, value_type=int) == 0x100010E:
                device = OppleLightDevice.OppleLightDevice(message=message)
            else:
                break

            device_list.append(device)
            yield device
        except socket.timeout:
            break

    return device_list
