import random
import crc16
from . import const

MESSAGE_OFFSET = const.MESSAGE_OFFSET


class Message(object):

    def __init__(self, device, data=bytearray()):
        self.device = device
        self.data = bytearray(data)
        self.body = data[MESSAGE_OFFSET['BODY']:]

    def get(self, offset, length=4, value_type=None, header=False):
        if not header:
            offset += MESSAGE_OFFSET['BODY']

        value = self.data[offset: offset + length]

        if value_type == int:
            return int.from_bytes(value, 'big')
        else:
            return value

    def set(self, value, offset, length=4, header=False):
        if not header:
            offset += MESSAGE_OFFSET['BODY']

        self.data[offset: offset + length] = value.to_bytes(length, 'big')

    def set_checksum(self):
        crc = crc16.crc16xmodem(bytes(self.data[0x64:]))
        self.set(crc, MESSAGE_OFFSET['CHECK_SUM'], header=True)

    def encrypt(self):
        if self.device is None or not self.device.is_init:
            return

        password = bytearray(20)
        mac = self.device.mac_raw

        for i in range(0, 20):
            password[i] = mac[i % mac.__len__()]

        for i, v in enumerate(self.body):
            self.data[i + MESSAGE_OFFSET['BODY']] = v ^ password[i % password.__len__()]

    def decrypt(self):
        return self.encrypt()

    def get_request_sn(self):
        return self.data[MESSAGE_OFFSET['REQ_SERIAL_NUM']: MESSAGE_OFFSET['REQ_SERIAL_NUM'] + 4]

    def get_response_sn(self):
        return self.data[MESSAGE_OFFSET['RES_SERIAL_NUM']: MESSAGE_OFFSET['RES_SERIAL_NUM'] + 4]

    def to_bytes(self):
        return bytes(self.data)


def build_message(msg_type, body=None, device=None):
    sn = random.randint(1, 1000)
    body = bytearray() if body is None else bytearray(body)
    data = bytearray(MESSAGE_OFFSET['BODY']) + body

    message = Message(device, data)

    message.set(0x03F2, MESSAGE_OFFSET['L2_TYPE'], header=True)
    message.set(0x2775, MESSAGE_OFFSET['L3_VERSION'], header=True)
    message.set(0x0001, MESSAGE_OFFSET['L3_ID'], header=True)
    message.set(0x0002, MESSAGE_OFFSET['OFFSET'], header=True)
    message.set(0x0003, MESSAGE_OFFSET['TTL'], header=True)
    message.set(0x0005, MESSAGE_OFFSET['L3_CHECKSUM'], header=True)
    message.set(0x0001, MESSAGE_OFFSET['DEST_OBJ_TYPE'], header=True)
    message.set(0x6A68, MESSAGE_OFFSET['SRC_ID'], header=True)

    message.set(sn, MESSAGE_OFFSET['REQ_SERIAL_NUM'], header=True)
    message.set(msg_type, MESSAGE_OFFSET['MSG_TYPE'], header=True)
    message.set(body.__len__() + 0x68, MESSAGE_OFFSET['PKG_LENGTH'], header=True)
    message.set(body.__len__() + 0x18, MESSAGE_OFFSET['MSG_LENGTH'], header=True)

    if device and device.is_init:
        message.set(device.server_port, MESSAGE_OFFSET['DEST_PORT'], header=True)
        message.set(device.id, MESSAGE_OFFSET['DEST_ID'], header=True)

    message.set_checksum()
    message.encrypt()

    return message


def parse_message(data, device=None):
    message = Message(device, data)
    message.decrypt()
    return message
