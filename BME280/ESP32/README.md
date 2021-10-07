# BME280(I2C) and ESP32

## !! IMPORTANT !!

FORCEDモードにしないと、温度がかなり高めにでる!

```c++
:
#include <Adafruit_BME280.h>

const uint8_t I2CADDR_BME280 = 0x76;

Adafruit_BME280 bme;

void setup() {

  bme.begin(I2CADDR_BME280);
  bme.setSampling(Adafruit_BME280::MODE_FORCED);  // !! IMPORTANT !!

}

void loop() {

  bme.takeForcedMeasurement();  // !! IMPORTANT !!

  float temp = bme.readTemperature();
  float humidity = bme.readHumidity();
  
}
```
