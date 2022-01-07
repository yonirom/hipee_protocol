import sys
import asyncio
import struct
import time
import argparse
import logging
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from collections import OrderedDict

from bleak import BleakClient, BleakScanner

NOTIFY_CHARACTERISTIC_UUID = "0000FFF1-0000-1000-8000-00805F9B34FB"
WRITE_CHARACTERISTIC_UUID = "0000FFF2-0000-1000-8000-00805F9B34FB"

logger = logging.getLogger(__name__)


class Parameter:
    def __init__(self, name, size, default_value):
        self.name = name
        self.size = size
        self.default_value = default_value


class CommandMeta(type):
    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        for parameter in x.parameters:
            setattr(
                x,
                parameter.name,
                parameter.default_value()
                if callable(parameter.default_value)
                else parameter.default_value,
            )
        return x


class CommandBase(metaclass=CommandMeta):

    magic: int = 0x09

    parameters: List[Parameter] = []

    def __init__(self, data=None):
        if data:
            self.from_bytes(data)

    def hash(self, data: bytearray) -> int:
        return 256 - (sum(data) % 256)

    def __bytes__(self):
        data = bytearray()
        length = sum(a.size for a in self.parameters) + 1
        data.append(self.magic)
        data.append(length)
        data.append(self.command_id)
        for parameter in self.parameters:
            data.extend(
                getattr(self, parameter.name).to_bytes(
                    length=parameter.size, byteorder="big"
                )
            )
        data.append(self.hash(data))
        logger.debug(f"out: {self} {data.hex()}")
        return bytes(data)

    def __repr__(self):
        rv = f"Command: {self.__class__.__name__} {hex(self.command_id)} "
        for parameter in self.parameters:
            if hasattr(self, parameter.name + "_str"):
                value = getattr(self, parameter.name + "_str")()
                rv += f", {parameter.name}: {value}"
            else:
                rv += f", {parameter.name}: {getattr(self, parameter.name)}"
        return rv

    def validate(self, data: bytearray) -> bool:
        return not (sum(data) % 256)

    def gen_fmt_to_unpack(self):
        conv = {1: "b", 2: "H", 4: "I"}
        rv = ">"
        for parameter in self.parameters:
            rv += conv[parameter.size]
        return rv

    def from_bytes(self, data) -> None:
        if not self.validate(data):
            logger.warning("Checksum validation failed")
        fmt = self.gen_fmt_to_unpack()
        fields = struct.unpack(fmt, data[3:-1])
        assert len(fields) == len(self.parameters)
        for attribute, value in zip((a.name for a in self.parameters), fields):
            self.__setattr__(attribute, value)


class ErrorResponse(CommandBase):
    command_id: int = 0xFF

    parameters = [
        Parameter("unknown", 1, 0),
    ]


class HelloRequest(CommandBase):
    command_id: int = 0x01

    parameters: List[Parameter] = []


class HelloResponse(CommandBase):
    command_id: int = 0x02

    parameters = [
        Parameter("accepted", 1, 0),
    ]


class InitialDataRequest(CommandBase):
    command_id: int = 0x03

    parameters: List[Parameter] = []


class InitialDataResponse(CommandBase):

    command_id: int = 0x04

    def battery_percent_str(self):
        return f"{self.battery_percent}%"

    def version_str(self):
        return f"V0.{self.version}"

    parameters = [
        Parameter("battery_percent", 1, 0),
        Parameter("version", 2, 0),
        Parameter("space_remaining", 4, 0),
    ]


class SetTimeRequest(CommandBase):

    command_id: int = 0x05

    def current_time_str(self):
        return time.ctime(self.current_time)

    parameters = [Parameter("current_time", 4, lambda: round(time.time()))]


class SetTimeResponse(CommandBase):

    command_id: int = 0x06
    device_time: int = 0

    def device_time_str(self):
        return time.ctime(self.device_time)

    parameters = [Parameter("device_time", 4, 0)]


class SetConfigDataRequest(CommandBase):
    command_id: int = 0x30

    parameters = [
        Parameter("shake_mode", 1, 1),
        Parameter("shake_power", 1, 50),  # Max power is 100 or deive will reboot
        Parameter("back_forward_angle_reminder", 1, 5),
        Parameter("back_sideways_angle_reminder", 1, 0),
        Parameter("unknown_hc_1", 1, 1),
        Parameter("unknown_hc_244", 1, 244),
        Parameter("unknown_hc_7", 1, 7),
        Parameter("unknown_hc_208", 1, 208),
        Parameter("sitting_time_seconds", 2, 0),
        Parameter("special_num", 1, 0),
        Parameter("shake_delay_reminder", 1, 2),
        Parameter("do_not_disturb", 1, 0),
        Parameter("exercise_angle_reminder", 1, 30),
        Parameter("unknown_hc_15", 1, 0),
    ]


class SetConfigDataResponse(CommandBase):
    command_id: int = 0x31

    def device_time_str(self):
        return time.ctime(self.device_time)

    parameters = [
        Parameter("device_time", 4, 0),
    ]


class SetStandardRequest(CommandBase):
    command_id: int = 0x32

    parameters: List[Parameter] = []


class SetStandardResponse(CommandBase):
    command_id: int = 0x33

    parameters = [
        Parameter("left_right_angle", 1, 0),
        Parameter("front_back_angle_90_deg_offset", 1, 0),
        Parameter("from_back_angle", 1, 0),
    ]


class GetLiveUpdateRequest(CommandBase):
    command_id: int = 0x34

    parameters = [
        Parameter("delay_milliseconds", 2, 20),
        Parameter("enable_stream", 1, 1),
    ]


class LiveUpdateResponse(CommandBase):

    command_id: int = 0x35

    parameters = [
        Parameter("current_time", 4, 0),
        Parameter("back_forward_angle", 1, 0),
        Parameter("back_left_right_angle", 1, 0),
        Parameter("error_num", 2, 0),
        Parameter("long_sit_ready", 2, 0),
        Parameter("mode", 1, 0),
        Parameter("do_not_disturb", 1, 0),
        Parameter("challenge_progress", 4, 0),
    ]


class GetBatteryStateRequest(CommandBase):
    command_id: int = 0x44

    parameters: List[Parameter] = []


class GetBatteryStateResponse(CommandBase):
    command_id: int = 0x45

    charge_state: int = 0  # 0 Charging, 1 Full, 2 In Use

    def charge_state_str(self):
        return ["Charging", "Full", "Discharging"][self.charge_state]

    parameters = [Parameter("battery_percent", 1, 0), Parameter("charge_state", 1, 0)]


class GetConfigDataRequest(CommandBase):
    command_id: int = 0x46

    parameters: List[Parameter] = []


class GetConfigDataResponse(CommandBase):
    command_id: int = 0x47

    parameters = [
        Parameter("shake_mode", 1, 0),
        Parameter("shake_power", 1, 0),
        Parameter("back_forward_angle_reminder", 1, 0),
        Parameter("back_sideways_angle_reminder", 1, 0),
        Parameter("unknown_hc_1", 1, 0),
        Parameter("unknown_hc_244", 1, 0),
        Parameter("unknown_hc_7", 1, 0),
        Parameter("unknown_hc_208", 1, 0),
        Parameter("sitting_time_seconds", 2, 0),
        Parameter("special_num", 1, 0),
        Parameter("shake_delay_reminder", 1, 0),
        Parameter("do_not_disturb", 1, 0),
        Parameter("exercise_angle_reminder", 1, 0),
        Parameter("unknown_hc_15", 1, 0),
    ]


class SetExtConfigDataRequest(CommandBase):
    command_id: int = 0x50

    parameters = [
        Parameter("allow_double_tap", 1, 0),
        Parameter("unknown_hc_0", 1, 0),
        Parameter("auto_restore_double_tap_time_minutes", 2, 0),
        Parameter("unknown_hc_1", 1, 1),
    ]


class SetExtConfigDataResponse(CommandBase):
    command_id: int = 0x51

    parameters = [
        Parameter("unknown1", 1, 1),
        Parameter("unknown2", 1, 0),
        Parameter("unknown3", 1, 0),
        Parameter("unknown4", 1, 0),
        Parameter("unknown5", 1, 0),
    ]


def parseCommand(data) -> Optional[CommandBase]:
    commands = {
        0x1: HelloRequest,
        0x2: HelloResponse,
        0x3: InitialDataRequest,
        0x4: InitialDataResponse,
        0x5: SetTimeRequest,
        0x6: SetTimeResponse,
        0x30: SetConfigDataRequest,
        0x31: SetConfigDataResponse,
        0x32: SetStandardRequest,
        0x33: SetStandardResponse,
        0x34: GetLiveUpdateRequest,
        0x35: LiveUpdateResponse,
        0x44: GetBatteryStateRequest,
        0x45: GetBatteryStateResponse,
        0x46: GetConfigDataRequest,
        0x47: GetConfigDataResponse,
        0x50: SetExtConfigDataRequest,
        0x51: SetExtConfigDataResponse,
        0xFF: ErrorResponse,
    }

    if data[2] not in commands:
        return None
    logger.debug(f"Creating command object {commands[data[2]]}")
    return commands[data[2]](data)


def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    logger.debug(f"{sender} {data.hex()}")
    command = parseCommand(data)
    if command:
        logger.info(command)
    else:
        logger.warning("Command type not Implanted for message {data.hex()}")


async def start(address):
    async with BleakClient(address) as client:
        logger.info(f"Connected to {address}")

        await client.start_notify(NOTIFY_CHARACTERISTIC_UUID, notification_handler)

        await client.write_gatt_char(WRITE_CHARACTERISTIC_UUID, bytes(HelloRequest()))
        await asyncio.sleep(3)
        await client.write_gatt_char(
            WRITE_CHARACTERISTIC_UUID, bytes(InitialDataRequest())
        )
        await asyncio.sleep(3.0)
        await client.write_gatt_char(WRITE_CHARACTERISTIC_UUID, bytes(SetTimeRequest()))
        await asyncio.sleep(3.0)
        await client.write_gatt_char(
            WRITE_CHARACTERISTIC_UUID, bytes(SetConfigDataRequest())
        )
        await asyncio.sleep(3.0)
        await client.write_gatt_char(
            WRITE_CHARACTERISTIC_UUID, bytes(GetBatteryStateRequest())
        )
        await asyncio.sleep(3.0)
        await client.write_gatt_char(
            WRITE_CHARACTERISTIC_UUID, bytes(GetConfigDataRequest())
        )
        await asyncio.sleep(3.0)
        await client.write_gatt_char(
            WRITE_CHARACTERISTIC_UUID, bytes(SetStandardRequest())
        )
        await asyncio.sleep(10.0)
        await client.write_gatt_char(
            WRITE_CHARACTERISTIC_UUID, bytes(GetLiveUpdateRequest())
        )

        await asyncio.sleep(150.0)
        await client.stop_notify(char_uuid)


async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        logger.info(d)


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s  %(message)s"))
    logger.addHandler(ch)

    parser = argparse.ArgumentParser(
        description="Hippe BLE API Example",
        epilog="*Make sure hipee is not connected to phone app",
    )
    parser.add_argument(
        "mac",
        metavar="UUID or MAC",
        nargs="?",
        type=str,
        help="Hipee Bluetooth UUID/MAC",
    )
    parser.add_argument(
        "--scan", dest="scan", action="store_const", const=True, help="scan BLE devices"
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_const",
        const=True,
        help="scan BLE devices",
    )

    args = parser.parse_args()

    if not (args.scan or args.mac):
        parser.print_help()
        sys.exit(1)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    asyncio.run(scan() if args.scan else start(args.mac))
