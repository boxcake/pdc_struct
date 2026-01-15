# IoT Devices

This example demonstrates using PDC Struct to decode data from I2C sensors on a Raspberry Pi. We'll read from a BME280 temperature/humidity/pressure sensor and parse its binary register data.

## BME280 Sensor Overview

The [BME280](https://www.bosch-sensortec.com/products/environmental-sensors/humidity-sensors-bme280/) is a popular environmental sensor that communicates over I2C or SPI. It returns raw ADC values in a packed binary format that must be decoded using calibration data.

**Key registers:**

| Register | Address | Size | Content |
|----------|---------|------|---------|
| Calibration | 0x88-0xA1 | 26 bytes | Temperature/pressure calibration |
| Calibration | 0xE1-0xE7 | 7 bytes | Humidity calibration |
| Data | 0xF7-0xFE | 8 bytes | Raw ADC readings |

## Defining the Register Structures

### Calibration Data

The BME280 stores factory calibration values that we need to decode the raw readings:

```python
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import Int8, UInt8, Int16, UInt16


class BME280CalibrationTP(StructModel):
    """Temperature and Pressure calibration data (registers 0x88-0xA1)."""

    # Temperature calibration
    dig_T1: UInt16 = Field(description="Temperature coefficient 1")
    dig_T2: Int16 = Field(description="Temperature coefficient 2")
    dig_T3: Int16 = Field(description="Temperature coefficient 3")

    # Pressure calibration
    dig_P1: UInt16 = Field(description="Pressure coefficient 1")
    dig_P2: Int16 = Field(description="Pressure coefficient 2")
    dig_P3: Int16 = Field(description="Pressure coefficient 3")
    dig_P4: Int16 = Field(description="Pressure coefficient 4")
    dig_P5: Int16 = Field(description="Pressure coefficient 5")
    dig_P6: Int16 = Field(description="Pressure coefficient 6")
    dig_P7: Int16 = Field(description="Pressure coefficient 7")
    dig_P8: Int16 = Field(description="Pressure coefficient 8")
    dig_P9: Int16 = Field(description="Pressure coefficient 9")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN  # BME280 uses little-endian
    )


class BME280CalibrationH(StructModel):
    """Humidity calibration data (registers 0xE1-0xE7)."""

    dig_H2: Int16 = Field(description="Humidity coefficient 2")
    dig_H3: UInt8 = Field(description="Humidity coefficient 3")
    # H4 and H5 share bytes and need special handling
    dig_H4_H5_raw: bytes = Field(
        json_schema_extra={"struct_length": 3},
        description="Raw bytes for H4/H5 (needs bit manipulation)"
    )
    dig_H6: Int8 = Field(description="Humidity coefficient 6")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

    @property
    def dig_H4(self) -> int:
        """Extract H4 from shared bytes (12-bit value)."""
        raw = self.dig_H4_H5_raw
        return (raw[0] << 4) | (raw[1] & 0x0F)

    @property
    def dig_H5(self) -> int:
        """Extract H5 from shared bytes (12-bit value)."""
        raw = self.dig_H4_H5_raw
        return (raw[2] << 4) | ((raw[1] >> 4) & 0x0F)
```

### Raw Sensor Data

The sensor returns 8 bytes of raw ADC data:

```python
class BME280RawData(StructModel):
    """Raw ADC data from registers 0xF7-0xFE.

    Data is packed as:
    - Pressure: 20-bit unsigned (3 bytes)
    - Temperature: 20-bit unsigned (3 bytes)
    - Humidity: 16-bit unsigned (2 bytes)
    """

    press_msb: UInt8 = Field(description="Pressure MSB [19:12]")
    press_lsb: UInt8 = Field(description="Pressure LSB [11:4]")
    press_xlsb: UInt8 = Field(description="Pressure XLSB [3:0] in upper nibble")
    temp_msb: UInt8 = Field(description="Temperature MSB [19:12]")
    temp_lsb: UInt8 = Field(description="Temperature LSB [11:4]")
    temp_xlsb: UInt8 = Field(description="Temperature XLSB [3:0] in upper nibble")
    hum_msb: UInt8 = Field(description="Humidity MSB [15:8]")
    hum_lsb: UInt8 = Field(description="Humidity LSB [7:0]")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Data registers are big-endian
    )

    @property
    def raw_pressure(self) -> int:
        """Get 20-bit raw pressure value."""
        return (self.press_msb << 12) | (self.press_lsb << 4) | (self.press_xlsb >> 4)

    @property
    def raw_temperature(self) -> int:
        """Get 20-bit raw temperature value."""
        return (self.temp_msb << 12) | (self.temp_lsb << 4) | (self.temp_xlsb >> 4)

    @property
    def raw_humidity(self) -> int:
        """Get 16-bit raw humidity value."""
        return (self.hum_msb << 8) | self.hum_lsb
```

## Reading from the Sensor

### Using smbus2 on Raspberry Pi

```python
import smbus2

BME280_ADDRESS = 0x76  # or 0x77 depending on SDO pin


class BME280:
    """BME280 sensor driver using PDC Struct for data parsing."""

    def __init__(self, bus_number: int = 1, address: int = BME280_ADDRESS):
        self.bus = smbus2.SMBus(bus_number)
        self.address = address
        self._load_calibration()

    def _read_registers(self, start: int, length: int) -> bytes:
        """Read multiple registers from the sensor."""
        return bytes(self.bus.read_i2c_block_data(
            self.address, start, length
        ))

    def _load_calibration(self):
        """Load calibration data from sensor."""
        # Read temperature/pressure calibration (0x88-0xA1, 26 bytes)
        # Note: We only need 24 bytes for our struct
        tp_data = self._read_registers(0x88, 24)
        self.calib_tp = BME280CalibrationTP.from_bytes(tp_data)

        # Read H1 separately (single byte at 0xA1)
        self.dig_H1 = self._read_registers(0xA1, 1)[0]

        # Read humidity calibration (0xE1-0xE7, 7 bytes)
        h_data = self._read_registers(0xE1, 7)
        self.calib_h = BME280CalibrationH.from_bytes(h_data)

        print(f"Calibration loaded:")
        print(f"  T1={self.calib_tp.dig_T1}, T2={self.calib_tp.dig_T2}, T3={self.calib_tp.dig_T3}")

    def read_raw(self) -> BME280RawData:
        """Read raw ADC values from sensor."""
        data = self._read_registers(0xF7, 8)
        return BME280RawData.from_bytes(data)

    def read(self) -> tuple[float, float, float]:
        """Read compensated temperature, pressure, and humidity.

        Returns:
            Tuple of (temperature_celsius, pressure_pa, humidity_percent)
        """
        raw = self.read_raw()

        # Apply compensation formulas (from BME280 datasheet)
        temp, t_fine = self._compensate_temperature(raw.raw_temperature)
        pressure = self._compensate_pressure(raw.raw_pressure, t_fine)
        humidity = self._compensate_humidity(raw.raw_humidity, t_fine)

        return temp, pressure, humidity

    def _compensate_temperature(self, adc_T: int) -> tuple[float, int]:
        """Compensate raw temperature reading."""
        c = self.calib_tp

        var1 = (adc_T / 16384.0 - c.dig_T1 / 1024.0) * c.dig_T2
        var2 = ((adc_T / 131072.0 - c.dig_T1 / 8192.0) ** 2) * c.dig_T3
        t_fine = int(var1 + var2)
        temperature = t_fine / 5120.0

        return temperature, t_fine

    def _compensate_pressure(self, adc_P: int, t_fine: int) -> float:
        """Compensate raw pressure reading."""
        c = self.calib_tp

        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * c.dig_P6 / 32768.0
        var2 = var2 + var1 * c.dig_P5 * 2.0
        var2 = var2 / 4.0 + c.dig_P4 * 65536.0
        var1 = (c.dig_P3 * var1 * var1 / 524288.0 + c.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * c.dig_P1

        if var1 == 0:
            return 0

        pressure = 1048576.0 - adc_P
        pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
        var1 = c.dig_P9 * pressure * pressure / 2147483648.0
        var2 = pressure * c.dig_P8 / 32768.0
        pressure = pressure + (var1 + var2 + c.dig_P7) / 16.0

        return pressure

    def _compensate_humidity(self, adc_H: int, t_fine: int) -> float:
        """Compensate raw humidity reading."""
        h = self.calib_h

        var_H = t_fine - 76800.0
        if var_H == 0:
            return 0

        var_H = (adc_H - (h.dig_H4 * 64.0 + h.dig_H5 / 16384.0 * var_H)) * \
                (h.dig_H2 / 65536.0 * (1.0 + h.dig_H6 / 67108864.0 * var_H * \
                (1.0 + h.dig_H3 / 67108864.0 * var_H)))

        var_H = var_H * (1.0 - self.dig_H1 * var_H / 524288.0)

        return max(0.0, min(100.0, var_H))
```

## Example Usage

```python
def main():
    # Initialize sensor
    sensor = BME280()

    print("\nReading sensor data...")
    print(f"Raw data struct size: {BME280RawData.struct_size()} bytes")
    print(f"Raw data format: {BME280RawData.struct_format_string()}\n")

    # Read and display values
    for i in range(5):
        temp, pressure, humidity = sensor.read()

        print(f"Reading {i + 1}:")
        print(f"  Temperature: {temp:.2f}°C")
        print(f"  Pressure: {pressure / 100:.2f} hPa")
        print(f"  Humidity: {humidity:.2f}%")
        print()

        time.sleep(1)


if __name__ == "__main__":
    import time
    main()
```

## Output

```
Calibration loaded:
  T1=27504, T2=26435, T3=-1000

Reading sensor data...
Raw data struct size: 8 bytes
Raw data format: >BBBBBBBB

Reading 1:
  Temperature: 23.45°C
  Pressure: 1013.25 hPa
  Humidity: 45.32%
```

## Why PDC Struct for IoT?

### Without PDC Struct

```python
# Manual byte unpacking (error-prone)
def read_calibration_manual(data: bytes):
    dig_T1 = int.from_bytes(data[0:2], 'little', signed=False)
    dig_T2 = int.from_bytes(data[2:4], 'little', signed=True)
    dig_T3 = int.from_bytes(data[4:6], 'little', signed=True)
    # ... 20+ more fields
    return dig_T1, dig_T2, dig_T3, ...
```

### With PDC Struct

- **Self-documenting** - Field names and descriptions in the model
- **Type-safe** - Proper signed/unsigned handling via `Int16`/`UInt16`
- **Validated** - Pydantic validates all values automatically
- **Maintainable** - Easy to update when sensor registers change
- **Testable** - Create mock sensor data easily for testing

## Testing Without Hardware

You can test your parsing logic without the actual sensor:

```python
def test_raw_data_parsing():
    """Test parsing of raw sensor data."""
    # Simulated raw data bytes
    test_data = bytes([
        0x50, 0x00, 0x00,  # Pressure (20-bit)
        0x80, 0x00, 0x00,  # Temperature (20-bit)
        0x80, 0x00,        # Humidity (16-bit)
    ])

    raw = BME280RawData.from_bytes(test_data)

    assert raw.raw_pressure == 0x50000
    assert raw.raw_temperature == 0x80000
    assert raw.raw_humidity == 0x8000

    print("✓ Raw data parsing test passed")


def test_calibration_parsing():
    """Test parsing of calibration data."""
    # Create known calibration values
    calib = BME280CalibrationTP(
        dig_T1=27504,
        dig_T2=26435,
        dig_T3=-1000,
        dig_P1=36477,
        dig_P2=-10685,
        dig_P3=3024,
        dig_P4=2855,
        dig_P5=140,
        dig_P6=-7,
        dig_P7=15500,
        dig_P8=-14600,
        dig_P9=6000,
    )

    # Round-trip through bytes
    data = calib.to_bytes()
    restored = BME280CalibrationTP.from_bytes(data)

    assert restored.dig_T1 == calib.dig_T1
    assert restored.dig_T2 == calib.dig_T2
    assert restored.dig_P9 == calib.dig_P9

    print("✓ Calibration parsing test passed")


if __name__ == "__main__":
    test_raw_data_parsing()
    test_calibration_parsing()
```

## Other I2C Sensors

The same pattern works for other I2C devices:

| Sensor | Data Size | Use Case |
|--------|-----------|----------|
| BME280 | 8 bytes | Temperature, humidity, pressure |
| MPU6050 | 14 bytes | Accelerometer, gyroscope |
| ADS1115 | 2 bytes | ADC readings |
| SHT31 | 6 bytes | Temperature, humidity |
| BMP280 | 6 bytes | Temperature, pressure |

## Requirements

```bash
# On Raspberry Pi
pip install pdc-struct smbus2

# Enable I2C
sudo raspi-config  # Interface Options → I2C → Enable
```

## Hardware Setup

Connect the BME280 to your Raspberry Pi:

| BME280 Pin | Raspberry Pi Pin |
|------------|------------------|
| VCC | 3.3V (Pin 1) |
| GND | Ground (Pin 6) |
| SDA | GPIO 2 / SDA (Pin 3) |
| SCL | GPIO 3 / SCL (Pin 5) |

Verify the sensor is detected:
```bash
i2cdetect -y 1
# Should show 76 or 77
```
