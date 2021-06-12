import argparse

from . import OppleDevice
from . import OppleLightDevice


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='"get" "set" or "search"')
    parser.add_argument('-a', '--address', help='device ip address', default='255.255.255.255')
    parser.add_argument('-p', '--power', help='light power status, "on" or "off"')
    parser.add_argument('-b', '--brightness', help='light brightness, 10 <= x <= 255')
    parser.add_argument('-c', '--ct', help='light color temperature, 2700 <= x <= 6500')

    args = parser.parse_args()

    if args.action == 'search':
        for device in OppleDevice.search():
            print("%s\t%s\t%s\t%s" % (device.id, device.ip, device.mac, device.name))

    elif args.action == 'set':
        if args.address is None:
            return print('IP address is empty.')

        device = OppleLightDevice.OppleLightDevice(ip=args.address)

        if args.power is None and args.brightness is None and args.ct is None:
            return print('nothing to change.')

        if args.power is not None:
            if args.power != 'on' and args.power != 'off':
                return print('power can only be "on" or "off"')
            device.power_on = args.power == 'on'

        if args.brightness is not None:
            try:
                value = int(args.brightness)
            except (TypeError, ValueError):
                return print("brightness value is illegal")

            if value < 0 or value > 255:
                return print("brightness is out of range")
            device.brightness = value

        if args.ct is not None:
            try:
                value = int(args.ct)
            except (TypeError, ValueError):
                return print("color temperature value is illegal")

            if value < 2700 or value > 6500:
                return print("color temperature is out of range")
            device.color_temperature = value

        print("Light %s" % device.ip)
        if args.power is not None:
            print("Power:\t\t\t%s" % "on" if device.power_on else "off")
        if args.brightness is not None:
            print("Brightness:\t\t%s" % device.brightness)
        if args.ct is not None:
            print("Color Temperature:\t%s" % device.color_temperature)
    else:
        if args.address is None:
            print('IP address is empty.')
            exit(0)

        device = OppleLightDevice.OppleLightDevice(ip=args.address)

        if device.is_online:
            print("Light %s\nPower:\t\t\t%s\nBrightness:\t\t%s\nColor Temperature:\t%s"
                  % (device.ip, "on" if device.power_on else "off", device.brightness, device.color_temperature))
        else:
            print("Light %s is offline." % device.ip)


if __name__ == "__main__":
    main()
    exit(0)
