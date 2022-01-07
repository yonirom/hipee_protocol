# Hipee / Posture UP BLE Protocol

An attempt at describing the Hipee Posture UP BLE protocol

Unexplored:

* Offline record upload
* Game Modes
* OTA Upgrade (TI)


## BLE Connection

```name "JZ-" or "jiaozi-"```

## Relevant service UUID
```0000FFF0-0000-1000-8000-00805F9B34FB```

## Relevant Charicreistic UUID
```
Notify - 0000fff1-0000-1000-8000-00805f9b34fb
Write - 0000fff2-0000-1000-8000-00805f9b34fb
```

## Command Format

All communication is big endian.

```
[0x09 , PARAMETER_LENGTH, CMDID,  PARAMETER_DATA, CHECKSUM]
```

## Checksum Calculation

Last byte must satisfy that the sum of all bytes in message % 256 == 0

```
ba += bytearray([256 - (sum(ba) % 256)])
```


## Command Types

| CMDID | DIR  | DESCRIPTION
| ----- | ---- | -----------
| 0x01  | W    | Request User device confirmation
| 0x02  | R    | User Confirmed Device
| 0x03  | W    | Request info - Power Level , Remaining Space, Version
| 0x04  | R    | Reply with Power Level, Remaining Space, version
| 0x05  | W    | Set the device time
| 0x06  | R    | Returns the newly set time
| 0x46  | W    | Get Device Configuration
| 0x47  | R    | Returns the device configuration
| 0x50  | W    | Write Additional (?) config information TBD
| 0x51  | R    | Read additional config information
| 0x30  | W    | Set Device Configuration
| 0x31  | R    | return Device Configuration
| 0x32  | W    | Reset current position to zero
| 0x33  | W    | Current zero position information
| 0x34  | W    | enable/disable Live position update
| 0x35  | R    | Live position information
| 0x44  | W    | Request battery charge state/status
| 0x45  | R    | Respond with battery charge state/status
| 0x50  | W    | Extra Config Data (??)
| 0x51  | R    | Extra Config Data (??)


## Command Details

<<<<<<< Updated upstream
### CMD ID: 0x01
Parameter Length: 0

### CMD ID: 0x02
Parameter Length: 1
=======
CMD ID: 0x01
Parameter Length: 0

CMD ID: 0x02
Parameter Length: 1
Parameters:
>>>>>>> Stashed changes

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      |bool - was device confirmed by user

### CMD ID: 0x03
Parameter Length: 0

### CMD ID: 0x04
Parameter Length: 7

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Battery in percent
| 01   | 2      | Version
| 03   | 2      | Storage space remaining on device out of 1024


### CMD ID: 0x05
Parameter Length: 4

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 4      | The current time in seconds since the Epoch. ```hex(round(time.time()))```


### CMD ID: 0x06
Parameter Length: 4

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 4      | The current time stored on the device in seconds since the Epoch

### CMD ID: 0x46
Parameter Length: 0

### CMD ID: 0x47
Parameter Length: 15

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Shakemode - 0x1 short, 0x0 long
| 01   | 1      | Shake Power
| 02   | 1      | back forward angle 0 upto 90
| 03   | 1      | back sideways angle -90 upto 90 (??)
| 04   | 1      | hardcoded 1
| 05   | 1      | hardcoded 244
| 06   | 1      | hardcoded 7
| 07   | 1      | hardcoded 208
| 08   | 2      | Sitting time in seconds
| 0a   | 1      | special num (??)
| 0b   | 1      | delay reminder before shake
| 0c   | 1      | Do not disturb
| 0d   | 1      | workforerake (??)
| 0e   | 1      | hardcoded 15


### CMD ID 0x34
Parameter Length: 3

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 2      | time in milliseconds between each posture notification
| 02   | 1      | bool - start/stop sending live updates

### CMD ID 0x35
Parameter Length: 15

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Shakemode - 0x1 short, 0x0 long
| 01   | 1      | Shake Power
| 02   | 1      | back forward angle 0 upto 90
| 03   | 1      | back sideways angle -90 upto 90 (??)
| 04   | 1      | hardcoded 1
| 05   | 1      | hardcoded 244
| 06   | 1      | hardcoded 7
| 07   | 1      | hardcoded 208
| 08   | 2      | Sitting time in seconds
| 0a   | 1      | special num (??)
| 0b   | 1      | delay reminder before shake
| 0c   | 1      | Do not disturb
| 0d   | 1      | workforerake (??)
| 0e   | 1      | hardcoded 15
