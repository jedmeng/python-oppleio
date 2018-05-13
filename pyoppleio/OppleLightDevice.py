from . import const, OppleDevice

MESSAGE_TYPE     = const.MESSAGE_TYPE
QUERY_RES_OFFSET = const.QUERY_RES_OFFSET


class OppleLightDevice(OppleDevice.OppleDevice):
    def __init__(self, ip='', message=None):
        self._isPowerOn = False
        self._brightness = 0
        self._colorTemperature = 0
        super().__init__(ip, message)

    def init(self, message):
        super(OppleLightDevice, self).init(message)
        self.update()

    def update(self):
        if not self.is_init:
            self.async_init()

        if not self.is_init:
            return

        message = self.send('QUERY', reply=True)
        if message:
            self._isPowerOn = message.get(QUERY_RES_OFFSET['POWER_ON'], 1, int)
            self._brightness = message.get(QUERY_RES_OFFSET['BRIGHT'], 1, int)
            self._colorTemperature = message.get(QUERY_RES_OFFSET['COLOR_TEMP'], 2, int)

    def set(self, message_type, value, check=None, _time=3):
        if _time == 0:
            return False

        if check():
            return True

        self.send(message_type, value)

        if check:
            self.update()
            if not check():
                return self.set(message_type, value, check, _time-1)

        return True

    @property
    def power_on(self):
        return self._isPowerOn

    @power_on.setter
    def power_on(self, value):
        value = 1 if value else 0

        def check():
            return self.power_on == (value == 1)

        self.set('POWER_ON', value.to_bytes(1, 'big'), check)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        value = max(0, value)
        value = min(255, value)

        def check():
            return self.brightness == value

        self.set('BRIGHTNESS', value.to_bytes(1, 'big'), check)

    @property
    def color_temperature(self):
        return self._colorTemperature

    @color_temperature.setter
    def color_temperature(self, value):
        value = max(2700, value)
        value = min(6500, value)

        def check():
            return self.color_temperature == value

        self.set('COLOR_TEMP', value.to_bytes(2, 'big'), check)
