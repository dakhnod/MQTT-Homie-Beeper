#!/usr/bin/python3 -u

from threading import Thread, Event
import RPi.GPIO as GPIO
import signal
import logging
import homie

# logging.basicConfig(level=logging.DEBUG)

repeats = 0
sequence = []
current_position = 0
gpio_last = False
should_stop = False

interrupt = Event()

property_sequence = None


def mqtt_init():
    config = {
        'HOST': 'localhost',
        'DEVICE_ID': 'beeper',
        'DEVICE_NAME': 'Beeper',
        'TOPIC': 'homie'
    }

    device = homie.Device(config)
    node_beeper = device.addNode('beeper', 'Beeper', 'beeper')
    property_sequence = node_beeper.addProperty('sequence', 'Sequence', datatype='string')
    property_sequence.settable(sequence_handler)
    device.setFirmware('python', '1.0')
    device.setup()


def sequence_handler(property, value):
    try:
        str_parse(str(value))
    except:
        print(f'error parsing string "{value}"')
        pass


def gpio_init():
    print('gpio init')
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25, GPIO.OUT)


def gpio_set(state):
    print('setting gpio %s' % state)
    GPIO.output(25, GPIO.LOW if state else GPIO.HIGH)


def loop_beeps():
    global current_position, repeats, gpio_last
    while True:
        try:
            if sequence is not None:
                delay = sequence[current_position]
                current_position = current_position + 1

                gpio_last = not gpio_last
                gpio_set(gpio_last)

                print('delaying %f secs' % delay)
                interrupt.wait(delay)
                if should_stop:
                    return
                interrupt.clear()
        except IndexError:
            current_position = 0
            repeats = repeats - 1
            repeats = max(0, repeats)

        if repeats == 0 or sequence is None:
            gpio_set(False)
            print('waiting for next sequence')
            interrupt.wait()
            if should_stop:
                return
            interrupt.clear()


def sequence_set(_sequence, _repeats):
    global sequence, repeats, gpio_last
    sequence = _sequence
    repeats = _repeats
    gpio_last = False
    interrupt.set()


def to_secs(secs):
    return int(secs) / 1000


def str_parse(sequence_str):
    parts = sequence_str.split(' ')

    print(parts)

    parts_count = len(parts)


    if parts_count == 0:
        return

    _repeats = 1
    sequence_start = 0
    print(f'count: {parts_count}')
    if parts_count == 1:
        # handle only one beep, should work by default
        pass
    elif parts_count % 2 == 1:
        print(f'repeats: {_repeats}')
        _repeats = int(parts[0])
        sequence_start = 1


    _sequence = []

    for i in range(sequence_start, parts_count):
        _sequence.append(to_secs(parts[i]))
    sequence_set(_sequence, _repeats)


def stop(sgnum, frame):
    GPIO.cleanup()
    global should_stop
    should_stop = True
    interrupt.set()

    exit()


def main():
    mqtt_init()
    gpio_init()
    gpio_set(False)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    loop_beeps()


if __name__ == '__main__':
    main()
