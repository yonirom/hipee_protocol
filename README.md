# Hipee / Posture UP BLE Protocol

An attempt at describing the Hipee Posture UP BLE protocol

Unexplored:

* Offline record upload
* Game Modes
* OTA Upgrade (TI)


## BLE Connection

```
name "JZ-" or "jiaozi-"
```

## Relevant service UUID
```
0000FFF0-0000-1000-8000-00805F9B34FB
```

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
| 0x30  | W    | Set Device Configuration
| 0x31  | R    | return Device Configuration
| 0x32  | W    | Reset current position to zero
| 0x33  | W    | Current zero position information
| 0x34  | W    | enable/disable Live position update
| 0x35  | R    | Live position information
| 0x44  | W    | Request battery charge state/status
| 0x45  | R    | Respond with battery charge state/status
| 0x46  | W    | Get Device Configuration
| 0x47  | R    | Returns the device configuration
| 0x50  | W    | Set button double tap options
| 0x51  | R    | Reply to set double tap options, unknown
| 0xff  | R    | Error response


## Command Details

### CMD ID: 0x01
Parameter Length: 0

### CMD ID: 0x02
Parameter Length: 1

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Bool - was device confirmed by user

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

### CMD ID: 0x30
Parameter Length: 14

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Shake mode (0=Long, 1=Short)
| 01   | 1      | Shake power < 100 (over 100 will cause device reboot)
| 02   | 1      | Shake reminder for forward back angle in degrees
| 03   | 1      | Shake reminder for sideways back angle in degrees (does not trigger shake)
| 04   | 1      | Unknown - constant value 1
| 05   | 1      | Unknown - constant value 244
| 06   | 1      | Unknown - constant value 7
| 07   | 1      | Unknown - constant value 208
| 08   | 1      | Sitting time in seconds for log sit reminder
| 09   | 1      | Special number (unknown)
| 0A   | 1      | Shake delay reminder in seconds
| 0B   | 1      | Do not disturb (suppress shakes)
| 0C   | 1      | Exercise angle reminder
| 0D   | 1      | Unknown - constant value 15

### CMD ID: 0x31
Parameter Length: 4

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 4      | Device time

### CMD ID: 0x32
Parameter Length: 0

### CMD ID: 0x33
Parameter Length: 3

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Left right angle
| 01   | 1      | Front back angle with a 90 degree offset (?)
| 02   | 1      | Front back angle

### CMD ID 0x34
Parameter Length: 3

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 2      | Time in milliseconds between each posture notification
| 02   | 1      | Bool - start/stop sending live updates

### CMD ID 0x35
Parameter Length: 16

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 4      | Current time
| 04   | 1      | Back forward angle
| 05   | 1      | Back left right angle
| 06   | 2      | Number of shake alerts
| 08   | 2      | Long sit counter (?)
| 0A   | 1      | Mode (?)
| 0B   | 1      | Do not disturb
| 0C   | 4      | Daily challenge progress

### CMD ID 0x44
Parameter Length: 0

### CMD ID 0x45
Parameter Length: 2

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Battery level in percent
| 01   | 1      | Charge state in (0=Charging, 1=Full, 2=Discharging)

### CMD ID: 0x46
Parameter Length: 0

### CMD ID: 0x47
Parameter Length: 15

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Shake mode (0=Long, 1=Short)
| 01   | 1      | Shake power < 100 (over 100 will cause device reboot)
| 02   | 1      | Shake reminder for forward back angle in degrees (0-90)
| 03   | 1      | Shake reminder for sideways back angle in degrees (does not trigger shake)
| 04   | 1      | unknown - constant value 1
| 05   | 1      | Unknown - constant value 244
| 06   | 1      | Unknown - constant value 7
| 07   | 1      | Unknown - constant value 208
| 08   | 1      | Sitting time in seconds for log sit reminder
| 09   | 1      | Special number (unknown)
| 0A   | 1      | Shake delay reminder in seconds
| 0B   | 1      | Do not disturb (suppress shakes)
| 0C   | 1      | Exercise angle reminder
| 0D   | 1      | Unknown - constant value 15

### CMD ID: 0x50
Parameter Length: 4

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Enable / Disable do not disturb double tap
| 01   | 1      | unknown - constant value  0
| 02   | 1      | Minutes after disabling double tap to reenable shake alerts
| 03   | 1      | unknown - constant value  1

### CMD ID: 0x51
Parameter Length: 5

| Byte | Length | Value |
| ---- | ------ | ----- |
| 00   | 1      | Unknown (?)
| 01   | 1      | Unknown (?)
| 02   | 1      | Unknwon (?)
| 03   | 1      | Unknwon (?)
| 04   | 1      | Unknwon (?)
