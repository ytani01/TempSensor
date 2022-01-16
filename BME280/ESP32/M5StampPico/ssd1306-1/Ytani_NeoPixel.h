//
// Copyright (c) 2021 Yoichi Tanibayashi
//
#ifndef YTANI_NEOPIXEL_H
#define YTANI_NEOPIXEL_H

#include <Adafruit_NeoPixel.h>

/**
 *
 */
class Ytani_NeoPixel {
public:
  uint8_t pixels_n = 0;
  uint8_t pin;

  Ytani_NeoPixel(uint8_t n, uint8_t pin);
  void clear() { this->_pixels.clear(); }
  void show() { this->_pixels.show(); interrupts();}
  void setColor(int led_i, uint32_t col) { this->_pixels.setPixelColor(led_i, col); }
  void setColor(int led_i, uint8_t r, uint8_t g, uint8_t b) {
    this->_pixels.setPixelColor(led_i, r, g, b); }
  uint32_t getColor(int led_i) { return this->_pixels.getPixelColor(led_i); }
  uint32_t color(uint8_t r, uint8_t g, uint8_t b) { return this->_pixels.Color(r, g, b); }

  /**
   * @param hue 0-65535(0xffff)
   * @param sat 0-255
   * @param val 0-255
   */
  uint32_t colorHSV(uint16_t hue, uint8_t sat, uint8_t val);
  void setColorHSV(int led_i, uint16_t hue, uint8_t sat, uint8_t val);
  void setColorHSVdeg(int led_i, uint16_t hue_deg, uint8_t sat, uint8_t val);

protected:
  Adafruit_NeoPixel _pixels;
};
#endif // YTANI_NEOPIXEL_H
