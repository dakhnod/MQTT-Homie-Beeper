#!/usr/bin/python3 -u

from threading import Thread, Event
import RPi.GPIO as GPIO
import signal
import homie.device_base
import homie.node.node_base
import homie.node.property.property_base
import logging

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
        'MQTT_BROKER': '192.168.0.4'
    }

    device = homie.device_base.Device_Base(
        device_id='beeper',
        name='Beeper',
        mqtt_settings=config,
        extensions=['meta']
    )

    global property_sequence
    node_beeper = homie.node.node_base.Node_Base(
        device=device,
        id='beeper',
        name='Beeper',
        type_='beeper',
        retain=False
    )
    device.add_node(node_beeper)
    property_sequence = homie.node.property.property_base.Property_Base(
        node=node_beeper,
        id='sequence',
        name='Sequence',
        settable=True,
        retained=True,
        data_type='string',
        set_value=sequence_handler
    )
    node_beeper.add_property(property_sequence)
    device.start()


def sequence_handler(value):
    str_parse(str(value))


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
    if parts.__len__() == 0:
        return

    if parts.__len__() == 1:
        sequence_set([to_secs(parts[0])], 1)
        return

    _repeats = int(parts[0])
    _sequence = []

    for i in range(1, parts.__len__()):
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
