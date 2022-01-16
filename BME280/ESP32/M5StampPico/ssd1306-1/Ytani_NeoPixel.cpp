/**
 * Copyright (c) 2021 Yoichi Tanibayashi
 */
#include "Ytani_NeoPixel.h"

/**
 *
 * @param[in] n number of LEDs
 * @param[in] pin GPIO pin number
 */
Ytani_NeoPixel::Ytani_NeoPixel(uint8_t n, uint8_t pin) {
  Serial.println("n=" + String(n));
  this->pixels_n = n;
  this->pin = pin;
  this->_pixels = Adafruit_NeoPixel(n, pin, NEO_GRB + NEO_KHZ800);
  this->_pixels.begin();
  this->_pixels.setBrightness(255);
} // Ytani_NeoPixel::Ytani_NeoPixel()

/**
 * @fn
 *
 * @param[in] hue 0-65535(0xffff)
 * @param[in] sat 0-255
 * @param[in] val 0-255
 * @return uint32_t RGB Color
 */
uint32_t Ytani_NeoPixel::colorHSV(uint16_t hue, uint8_t sat, uint8_t val) {
    return this->_pixels.ColorHSV(hue, sat, val);
} // Ytani_NeoPixel::colorHSV()

/**
 * @fn
 *
 * @param[in] led_i  index of the LED
 * @param[in] hue  0-0xffff
 * @param[in] sat  0-0xff
 * @param[in] val  0-0xff
 */
void Ytani_NeoPixel::setColorHSV(int led_i, uint16_t hue, uint8_t sat, uint8_t val) {
  this->setColor(led_i, this->colorHSV(hue, sat, val));
} // Ytani_NeoPixel::setColorHSV()

/**
 * @fn
 *
 * @param[in] led_i  index of the LED
 * @param[in] hue  0-359 (in degree)
 * @param[in] sat  0-0xff
 * @param[in] val  0-0xff
 */
void Ytani_NeoPixel::setColorHSVdeg(int led_i, uint16_t hue_deg, uint8_t sat, uint8_t val) {
  hue_deg %= 360;
  this->setColorHSV(led_i, (uint16_t)(0x10000L * hue_deg / 360), sat, val);
} // Ytani_NeoPixel::setColorHSVdeg()
