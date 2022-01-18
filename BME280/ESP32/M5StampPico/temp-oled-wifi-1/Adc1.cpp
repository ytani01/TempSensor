/**
 * (c) 2021 Yoichi Tanibayashi
 */
#include "Adc1.h"

/**
 *
 */
unsigned long Adc1::bitWidth2maxVal(adc_bits_width_t width) {
  unsigned long max_val = 0;
  
  switch (width) {  // XXX
  case ADC_WIDTH_BIT_9:
    max_val = 511;
    break;
  default:
    max_val = 0;
    break;
  } // switch

  return max_val;
} // Adc1::bitWidth2maxVal()

/**
 * constructor
 */
Adc1::Adc1(adc1_channel_t adc_ch, adc_atten_t adc_atten,
                               adc_bits_width_t width) {
  this->adc_ch = adc_ch;
  this->adc_atten = adc_atten;
  this->max_val = bitWidth2maxVal(width);
  Serial.printf("%s> adc_ch=%d, adc_atten=%d, max_val=%d\n",
                "Adc1::Adc1",
                this->adc_ch, this->adc_atten, this->max_val);
  
  adc1_config_width(width);
  adc1_config_channel_atten(this->adc_ch, this->adc_atten);
} // Adc1()

/**
 *
 */
int Adc1::get() {
  esp_err_t ret;
  int val;

  val = adc1_get_raw(this->adc_ch);
  return val;
} // Adc1::get()
