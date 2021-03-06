# MQTT-Homie-Beeper

This service allows you to play patterns on a connected Buzzer or LED via GPIO.
It is controlled through MQTT and follows Homie4, can be used in OpenHAB2 etc.

## Installation

You can just run the beeper.py script, as long as the user can access GPIO.

If you want to run the script as a service, follow these steps:

First, clone this repo.

Second, edit the path in the unit file (.service) to match the final script location.

Then, either copy or link the service file to /etc/systemd/system.

After that, you may want to autostart the service by "systemctl enable beeper".

Start the service with "systemctl start beeper".

Most likely, you will have to change the pin in the script, just search "25".

## Usage

invoke the logic by either posting a string to the mqtt topic "homie/beeper/beeper/sequence/set"
or posting the sequence string to the homie property.

If the sequence is a single digit, a tone with the length of that digit in milliseconds is played.
It the sequence is more than one digit, the first digit is the repitition count, all other digits are alternating beeps and pauses.

## Sequence examples
|Sequence|Result|
|--------|------|
|100|bep|
|200|beep|
|400|beeeep|
|1 100 100|bep bep |
|3 100 200|bep  bep  bep  |
|1 100 100 300 200 100 100|bep beeep  bep|  
