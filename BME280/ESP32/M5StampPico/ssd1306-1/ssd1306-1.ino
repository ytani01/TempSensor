/**
 * Copyright (c) 2022 Yoichi Tanibayashi
 */
#include <Adafruit_BME280.h>
#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_GFX.h>

const int OLED_W = 128;
const int OLED_H = 64;
Adafruit_SSD1306 disp(OLED_W, OLED_H, &Wire, -1);

const uint8_t I2CADDR_BME280 = 0x76;
Adafruit_BME280 bme;

const uint8_t PIN_ADC = 36;
const float VOL_FACTOR = 2.0;
const float V_BASE = 3.3;
const float ADC_MAX = 4096.0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  delay(500);
  Serial.println("Start");

  if (!disp.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306: init failed");
    while (true) {}
  }

  bme.begin(I2CADDR_BME280);
  bme.setSampling(Adafruit_BME280::MODE_FORCED);  // !! IMPORTANT !!
} // setup()

void loop() {
  int v1 = analogRead(PIN_ADC);
  float vol = v1 * V_BASE * VOL_FACTOR / ADC_MAX;
  Serial.printf("%.2fV(%d) ", vol, v1);
  
  /*
  bme.begin(I2CADDR_BME280);
  bme.setSampling(Adafruit_BME280::MODE_FORCED);  // !! IMPORTANT !!
  */

  bme.takeForcedMeasurement();  // !! IMPORTANT !!
  float temp = bme.readTemperature();
  float hum = bme.readHumidity();
  float pressure = bme.readPressure() / 100.0;
  Serial.printf("%.2f %.1f %0.2f\n", temp, hum, pressure);  

  disp.clearDisplay();
  disp.setTextColor(WHITE);

  disp.setCursor(0, 0);

  disp.setTextSize(2);
  disp.printf("%4.1f", temp);
  disp.setTextSize(1);
  disp.printf("%c", (char)247);
  disp.setTextSize(2);
  disp.printf("C ");

  disp.printf("%2.0f%%\n", hum);

  disp.setTextSize(2);
  disp.printf("%6.1f", pressure);
  disp.setTextSize(1);
  disp.printf("hPa");
  disp.setTextSize(2);
  disp.printf(" \n");

  disp.printf("----------");
  disp.printf("%.2fV", vol);
  disp.display();

  delay(1000);
} // loop()
