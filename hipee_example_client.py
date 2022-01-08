import sys
import asyncio
import time
import argparse
import logging
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from collections import OrderedDict
from hipee_messages import *

from bleak import BleakClient, BleakScanner

NOTIFY_CHARACTERISTIC_UUID = "0000FFF1-0000-1000-8000-00805F9B34FB"
WRITE_CHARACTERISTIC_UUID = "0000FFF2-0000-1000-8000-00805F9B34FB"

logger = logging.getLogger(__name__)


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
        await client.write_gatt_char(
            WRITE_CHARACTERISTIC_UUID, bytes(SetExtConfigDataRequest())
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
