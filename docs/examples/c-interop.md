# C Interoperability

This example demonstrates exchanging binary data between Python and C programs using PDC Struct. Both programs share the same struct definition, enabling seamless communication via pipes, sockets, or shared memory.

## Use Case: Sensor Data Pipeline

A Python program collects sensor readings and sends them to a C program for processing. The struct layout must be identical in both languages.

## The Shared Struct Definition

### Python Side (PDC Struct)

```python
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16

MAX_LOCATION = 16


class SensorReading(StructModel):
    """Sensor reading - must match C struct exactly."""

    sensor_id: UInt16 = Field(description="Unique sensor identifier")
    temperature: float = Field(
        description="Temperature in Celsius",
        json_schema_extra={"struct_format": "f"}  # 32-bit float
    )
    humidity: float = Field(
        description="Relative humidity percentage",
        json_schema_extra={"struct_format": "f"}  # 32-bit float
    )
    timestamp: int = Field(description="Unix timestamp")
    location: str = Field(
        max_length=MAX_LOCATION,
        json_schema_extra={"struct_length": MAX_LOCATION},
        description="Sensor location"
    )

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )
```

### C Side

```c
#include <stdint.h>

#define MAX_LOCATION 16

// Must match Python struct exactly
#pragma pack(push, 1)
struct sensor_reading {
    uint16_t sensor_id;
    float temperature;
    float humidity;
    int64_t timestamp;
    char location[MAX_LOCATION];
};
#pragma pack(pop)
```

!!! warning "Struct Packing"
    Use `#pragma pack(1)` in C to disable padding. PDC Struct's `C_COMPATIBLE` mode produces tightly packed data with no padding bytes.

## Memory Layout

Both definitions produce identical binary layout:

| Offset | Size | Field | C Type | Python Type |
|--------|------|-------|--------|-------------|
| 0 | 2 | sensor_id | uint16_t | UInt16 |
| 2 | 4 | temperature | float | float (32-bit) |
| 6 | 4 | humidity | float | float (32-bit) |
| 10 | 8 | timestamp | int64_t | int |
| 18 | 16 | location | char[16] | str |

**Total: 34 bytes**

Verify in Python:
```python
print(f"Struct size: {SensorReading.struct_size()} bytes")
print(f"Format: {SensorReading.struct_format_string()}")
# Output:
# Struct size: 34 bytes
# Format: <Hffq16s
```

## Communication via Unix Socket

### Python Sender

```python
import socket
import time

SOCKET_PATH = "/tmp/sensor_socket"


def send_reading(reading: SensorReading) -> bool:
    """Send a sensor reading to the C program."""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCKET_PATH)

        # Send the packed struct
        sock.sendall(reading.to_bytes())

        # Wait for acknowledgment
        ack = sock.recv(4)
        success = int.from_bytes(ack, byteorder="little") == 1

        sock.close()
        return success

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
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
    ]

    print("Sending sensor readings to C program...")

    for reading in readings:
        print(f"\nSensor {reading.sensor_id} @ {reading.location}")
        print(f"  Temp: {reading.temperature}°C, Humidity: {reading.humidity}%")

        if send_reading(reading):
            print("  ✓ Acknowledged")
        else:
            print("  ✗ Failed")

        time.sleep(0.5)


if __name__ == "__main__":
    main()
```

### C Receiver

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <stdint.h>

#define SOCKET_PATH "/tmp/sensor_socket"
#define MAX_LOCATION 16

#pragma pack(push, 1)
struct sensor_reading {
    uint16_t sensor_id;
    float temperature;
    float humidity;
    int64_t timestamp;
    char location[MAX_LOCATION];
};
#pragma pack(pop)

void print_reading(struct sensor_reading *r) {
    printf("Sensor Reading Received:\n");
    printf("  ID: %d\n", r->sensor_id);
    printf("  Temperature: %.2f°C\n", r->temperature);
    printf("  Humidity: %.2f%%\n", r->humidity);
    printf("  Timestamp: %ld\n", r->timestamp);
    printf("  Location: %s\n", r->location);
    printf("\n");
}

int main() {
    int server_fd, client_fd;
    struct sockaddr_un addr;
    struct sensor_reading reading;

    // Remove existing socket
    unlink(SOCKET_PATH);

    // Create socket
    server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("socket");
        exit(1);
    }

    // Bind
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        perror("bind");
        exit(1);
    }

    // Listen
    if (listen(server_fd, 5) == -1) {
        perror("listen");
        exit(1);
    }

    printf("C program listening on %s\n", SOCKET_PATH);
    printf("Expecting struct size: %lu bytes\n\n", sizeof(reading));

    while (1) {
        client_fd = accept(server_fd, NULL, NULL);
        if (client_fd == -1) {
            perror("accept");
            continue;
        }

        // Read the struct
        ssize_t bytes = read(client_fd, &reading, sizeof(reading));
        if (bytes == sizeof(reading)) {
            print_reading(&reading);

            // Send acknowledgment
            uint32_t ack = 1;
            write(client_fd, &ack, sizeof(ack));
        } else {
            printf("Error: received %zd bytes, expected %lu\n",
                   bytes, sizeof(reading));
        }

        close(client_fd);
    }

    return 0;
}
```

## Running the Example

### Compile and Start the C Program

```bash
gcc -o sensor_reader sensor_reader.c
./sensor_reader
```

Output:
```
C program listening on /tmp/sensor_socket
Expecting struct size: 34 bytes
```

### Run the Python Sender

In another terminal:
```bash
python sensor_sender.py
```

Output:
```
Sending sensor readings to C program...

Sensor 1 @ Lab 1
  Temp: 23.5°C, Humidity: 45.2%
  ✓ Acknowledged

Sensor 2 @ Lab 2
  Temp: 25.1°C, Humidity: 52.8%
  ✓ Acknowledged
```

The C program will display:
```
Sensor Reading Received:
  ID: 1
  Temperature: 23.50°C
  Humidity: 45.20%
  Timestamp: 1705329600
  Location: Lab 1
```

## Windows: Named Pipes

On Windows, use named pipes instead of Unix sockets:

### Python (Windows)

```python
import win32pipe
import win32file

PIPE_NAME = r"\\.\pipe\sensor_pipe"


def send_reading_windows(reading: SensorReading) -> bool:
    """Send reading via Windows named pipe."""
    try:
        handle = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_WRITE,
            0, None,
            win32file.OPEN_EXISTING,
            0, None
        )
        win32file.WriteFile(handle, reading.to_bytes())
        win32file.CloseHandle(handle)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

### C (Windows)

```c
#include <windows.h>
#include <stdio.h>

#define PIPE_NAME "\\\\.\\pipe\\sensor_pipe"

int main() {
    HANDLE pipe;
    struct sensor_reading reading;
    DWORD bytes_read;

    pipe = CreateNamedPipe(
        PIPE_NAME,
        PIPE_ACCESS_INBOUND,
        PIPE_TYPE_BYTE | PIPE_WAIT,
        1, 0, sizeof(reading), 0, NULL
    );

    printf("Waiting for connection...\n");

    while (1) {
        ConnectNamedPipe(pipe, NULL);

        if (ReadFile(pipe, &reading, sizeof(reading), &bytes_read, NULL)) {
            print_reading(&reading);
        }

        DisconnectNamedPipe(pipe);
    }

    return 0;
}
```

## Key Points

1. **Matching layouts** - Use `#pragma pack(1)` in C and `C_COMPATIBLE` mode in Python
2. **Byte order** - Both sides must use the same endianness (usually little-endian on x86)
3. **Fixed strings** - C strings are fixed-length char arrays; use `struct_length` in Python
4. **Float precision** - Specify `struct_format: 'f'` for 32-bit floats (C `float`)

## Debugging Tips

Print the hex dump to verify both sides produce identical bytes:

```python
data = reading.to_bytes()
print(f"Hex: {data.hex()}")
print(f"Len: {len(data)} bytes")
```

```c
unsigned char *p = (unsigned char *)&reading;
printf("Hex: ");
for (int i = 0; i < sizeof(reading); i++) {
    printf("%02x", p[i]);
}
printf("\n");
```

## Full Example

See the complete working example in the repository:
[`examples/py-c-interprocess/`](https://github.com/boxcake/pdc_struct/tree/main/examples/py-c-interprocess)
