# PDC Struct IPC Example

This example demonstrates using PDC Struct to communicate between Python and C programs using Unix domain sockets.

## Overview

- `sensor_reader.c`: A C program that listens for sensor readings on a Unix domain socket
- `sensor_sender.py`: A Python program that sends sensor readings using PDC Struct
- Both programs use identical struct layouts to ensure binary compatibility

## Building

```bash
make
```

## Running

1. First, start the C program in one terminal:
```bash
./sensor_reader
```

2. Then, run the Python program in another terminal:
```bash
python sensor_sender.py
```

## How it Works

1. The C program creates a Unix domain socket and listens for connections
2. The Python program:
   - Creates SensorReading objects with sample data
   - Uses PDC Struct to serialize them to bytes
   - Sends the bytes over the socket
3. The C program:
   - Receives the bytes
   - Interprets them as a C struct
   - Prints the data
   - Sends back an acknowledgment
4. The Python program waits for acknowledgment after each send

## Key Points

- The C struct and Python StructModel must match exactly
- Both use `#pragma pack(1)` / `mode=StructMode.C_COMPATIBLE` for consistent layout
- Fixed-width integers ensure consistent sizes
- String field has fixed maximum size
- Little-endian byte order is used by both programs