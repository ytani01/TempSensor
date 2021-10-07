/**
 *
 * SDA: GPIO21
 * SCL: GPIO22
 *
 */
#include <Adafruit_BME280.h>

const float OFFSET_TEMP = -0.53;  // ??

const unsigned long DELAY_MSEC = 2000;

const uint8_t I2CADDR_BME280 = 0x76;

Adafruit_BME280 bme;

/**
 *
 */
void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }

  bme.begin(I2CADDR_BME280);
  bme.setSampling(Adafruit_BME280::MODE_FORCED);  // !! IMPORTANT !!
  
} // setup()

/**
 *
 */
void loop() {
  bme.takeForcedMeasurement();  // !! IMPORTANT !!
  float temp = bme.readTemperature() + OFFSET_TEMP;
  float humidity = bme.readHumidity();

  //Serial.printf("%f, %f\n", temp, humidity);
  Serial.printf("%.2f\n", temp);

  delay(DELAY_MSEC);
} // loop()
