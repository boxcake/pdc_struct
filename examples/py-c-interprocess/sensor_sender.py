"""
Example demonstrating PDC Struct interoperating with C code.
Sends sensor readings to a C program over a Unix domain socket.
"""

import socket
import time
from typing import Optional
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16

SOCKET_PATH = "/tmp/sensor_socket"
MAX_LOCATION = 16


class SensorReading(StructModel):
    """Sensor reading structure - must match C struct exactly"""

    sensor_id: UInt16 = Field(description="Unique sensor identifier")
    temperature: float = Field(
        description="Temperature in Celsius",
        json_schema_extra={'struct_format': 'f'}  # Use 32-bit float
    )
    humidity: float = Field(
        description="Relative humidity percentage",
        json_schema_extra={'struct_format': 'f'}  # Use 32-bit float
    )
    timestamp: int = Field(description="Unix timestamp")
    location: str = Field(
        max_length=MAX_LOCATION,
        struct_length=MAX_LOCATION,  # Ensure full buffer size
        description="Sensor location string"
    )

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,  # Must match C struct exactly
        byte_order=ByteOrder.LITTLE_ENDIAN
    )


def send_reading(reading: SensorReading) -> bool:
    """Send a sensor reading to the C program."""
    try:
        # Connect to Unix domain socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCKET_PATH)

        # Send reading
        sock.sendall(reading.to_bytes())

        # Wait for acknowledgment
        ack = sock.recv(4)
        success = int.from_bytes(ack, byteorder='little') == 1

        sock.close()
        return success

    except Exception as e:
        print(f"Error sending reading: {e}")
        return False


def main():
    """Send some sample sensor readings."""
    readings = [
        SensorReading(
            sensor_id=1,
            temperature=23.5,
            humidity=45.2,
            timestamp=int(time.time()),
            location="Lab 1"
        ),
        SensorReading(
            sensor_id=2,
            temperature=25.1,
            humidity=52.8,
            timestamp=int(time.time()),
            location="Lab 2"
        ),
        SensorReading(
            sensor_id=3,
            temperature=19.8,
            humidity=62.3,
            timestamp=int(time.time()),
            location="Outside"
        )
    ]

    print("Python program sending sensor readings...")

    for reading in readings:
        print(f"\nSending: Sensor {reading.sensor_id} @ {reading.location}")
        if send_reading(reading):
            print("Successfully sent and acknowledged")
        else:
            print("Failed to send reading")
        time.sleep(1)  # Wait between readings


if __name__ == "__main__":
    main()
