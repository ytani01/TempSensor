/**
 * Copyright (c) 2022 Yoichi Tanibayashi
 */
#include <Wire.h>
#include <Adafruit_BME280.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_GFX.h>
#include "Adc1.h"

// OLED
const int OLED_W = 128;
const int OLED_H = 64;
Adafruit_SSD1306 disp(OLED_W, OLED_H, &Wire, -1);

// BME280
const uint8_t I2CADDR_BME280 = 0x76;
Adafruit_BME280 bme;
const float TEMP_OFFSET = -0.5;

// ADC
const adc1_channel_t ADC_CH = ADC1_CHANNEL_0; // GPIO36
Adc1 *adc1;
const float ADC_FACTOR = 2.0;
const adc_atten_t ADC_ATTEN = ADC_ATTEN_DB_11; // 11dB
const float ADC_V_MAX = 3.5; // <-- ADC_ATTEN_DB_11 (ATTEN_DB_0: 1.0V)

/**
 *
 */
float adc_get_vol() {
  int adv_val = adc1->get();
  float vol = adv_val * ADC_V_MAX * ADC_FACTOR / adc1->max_val;
  return vol;
}

/**
 *
 */
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

  adc1 = new Adc1(ADC_CH, ADC_ATTEN, ADC_WIDTH_BIT_9);
} // setup()

/**
 *
 */
void loop() {
  /**
   * get vol
   */
  float vol = adc_get_vol();
  Serial.printf("%.2fV ", vol);
  
  /**
   * get temp, hum, pressure
   */
  bme.takeForcedMeasurement();  // !! IMPORTANT !!
  float temp = bme.readTemperature() + TEMP_OFFSET;
  float hum = bme.readHumidity();
  float pressure = bme.readPressure() / 100.0;
  Serial.printf("%.2f(%.1f) %.1f %0.2f\n", temp, TEMP_OFFSET, hum, pressure);  

  /**
   * display
   */
  disp.clearDisplay();
  disp.setTextColor(WHITE);

  disp.setCursor(0, 0);

  disp.setTextSize(2);
  disp.printf("%4.1f", temp);
  disp.setTextSize(1);
  disp.printf("%cC ", (char)247);

  disp.setTextSize(2);
  disp.printf("%2.0f", hum);
  disp.setTextSize(1);
  disp.printf("%%");

  disp.setTextSize(2);
  disp.println();

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
