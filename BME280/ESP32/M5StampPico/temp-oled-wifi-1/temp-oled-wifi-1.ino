/**
 * Copyright (c) 2022 Yoichi Tanibayashi
 */
#include <Wire.h>
#include <Adafruit_BME280.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_GFX.h>
#include "Adc1.h"
#include "NetMgr.h"
#include "Button.h"

const String VERSION_STR = "V0.2";

const int DISP_INTERVAL = 3000; // ms
const int GET_TEMP_INTERVAL = 6000; // ms

// OLED
const uint16_t DISP_W = 128;
const uint16_t DISP_H = 64;
Adafruit_SSD1306 disp(DISP_W, DISP_H, &Wire, -1);

// BME280
const uint8_t I2CADDR_BME280 = 0x76;
Adafruit_BME280 bme;
const float TEMP_OFFSET = -0.9;

// ADC
const adc1_channel_t ADC_CH = ADC1_CHANNEL_0; // GPIO36
Adc1 *adc1;
const float ADC_FACTOR = 2.0;
const adc_atten_t ADC_ATTEN = ADC_ATTEN_DB_11; // 11dB
const float ADC_V_MAX = 3.5; // <-- ADC_ATTEN_DB_11 (ATTEN_DB_0: 1.0V)

// WiFi
const String AP_SSID_HDR = "YT_CLOCK";
const unsigned int WIFI_RETRY_COUNT = 15;
NetMgr netMgr(AP_SSID_HDR, WIFI_RETRY_COUNT);

// Button
const uint8_t PIN_BTN0 = 39;
Button btn0 = Button(PIN_BTN0, "BTN0");
uint8_t intrPin0 = digitalPinToInterrupt(PIN_BTN0);
const unsigned long DEBOUNCE = 300; // ms

/**
 * RTC読込中に 割り込みがかかると落ちることがある
 * 設定ファイル読込中に 割り込みがかかると落ちることがある
 */
void IRAM_ATTR btn_intr_hdr() {
  static unsigned long prev_ms = 0;
  unsigned long        cur_ms = millis();

  if ( cur_ms - prev_ms < DEBOUNCE ) {
    return;
  }
  prev_ms = cur_ms;
}

/**
 *
 */
void enableIntr() {
  attachInterrupt(intrPin0, btn_intr_hdr, CHANGE);
}

/**
 *
 */
void disableIntr() {
  detachInterrupt(intrPin0);
}

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
void display(float temp, float hum, float pres, float vol, mode_t netmgr_mode) {
  static int count = 0;
  const String PROGRESS_CHR = "|\x2F-\x5C";

  count++;
  count %= PROGRESS_CHR.length();

  const uint16_t CH_W = 6;
  const uint16_t CH_H = 8;
  const uint16_t LINE_W = 1;

  disp.clearDisplay();
  disp.setTextColor(WHITE);
  disp.setTextWrap(false);

  disp.fillRect(0,0, DISP_W, DISP_H, WHITE);
  disp.fillRect(LINE_W, LINE_W,
                DISP_W - LINE_W * 2, DISP_H - LINE_W * 2,
                BLACK);

  temp = round(temp * 10) / 10;
  int temp1 = int(temp);
  int temp2 = int((temp - int(temp)) * 10);
  hum = round(hum);
  pres = round(pres);
  vol = round(vol * 10) / 10;
  
  const uint16_t MARGIN1_X = 3;
  const uint16_t MARGIN1_Y = 2;

  const uint16_t X1 = LINE_W + MARGIN1_X;
  const uint16_t Y1 = LINE_W + MARGIN1_Y;

  disp.setCursor(X1, Y1);
  disp.setTextSize(4);
  disp.printf("%2d", temp1);

  const uint16_t X2 = X1 + CH_W * 4 * 2;
  
  disp.setCursor(X2 - 6,
                 Y1 + CH_H * 2 - 2);
  disp.setTextSize(2);
  disp.printf(".%1d", temp2);

  disp.setCursor(X2 + CH_W - 1, Y1);
  disp.setTextSize(1);
  disp.printf("%cC ", (char)247);

  const uint16_t X3 = X2 + CH_W * 2 * 2 - 2 ;

  const uint16_t LINE1_X = X3 - 4;
  const uint16_t LINE1_Y = LINE_W + MARGIN1_Y + CH_W * 4 + LINE_W + 5;
  // disp.drawLine(LINE1_X, 0,  LINE1_X, LINE1_Y, WHITE);

  disp.setCursor(X3, Y1);
  disp.setTextSize(4);
  disp.printf("%.0f", hum);

  const uint16_t X4 = X3 + CH_W * 4 * 2 - 2;

  disp.setCursor(X4, Y1 + CH_H * 3 - 3);
  disp.setTextSize(1);
  disp.printf("%%");

  disp.drawLine(0, LINE1_Y, DISP_W, LINE1_Y, WHITE);

  const uint16_t X5 = X1 + CH_W * 9 + 3;
  const uint16_t Y5 = LINE1_Y + MARGIN1_Y + 1;

  disp.setCursor(X5, Y5);
  disp.setTextSize(2);
  disp.printf("%.0f", pres);

  const uint16_t X6 = X5 + CH_W * 2 * 4;
  const uint16_t Y6 = Y5 + CH_H - 1;

  disp.setCursor(X6, Y6);
  disp.setTextSize(1);
  disp.printf("hPa");

  const uint16_t LINE2_Y = Y6 + CH_H + 1;

  disp.drawLine(0, LINE2_Y, DISP_W, LINE2_Y, WHITE);

  const uint16_t Y7 = LINE2_Y + 2;

  disp.setCursor(X1, Y7);
  disp.setTextSize(1);
  disp.printf("%.1fv", vol);

  const uint16_t X_VERSION = DISP_W - CH_W * 4 - 2;
  const uint16_t Y_VERSION = Y7;
  disp.setCursor(X_VERSION, Y_VERSION);
  disp.print(VERSION_STR);

  const uint16_t X_PROGRESS = X1 + CH_W * 4 + 2;
  const uint16_t Y_PROGRESS = Y7;
  disp.setCursor(X_PROGRESS, Y_PROGRESS);
  disp.setTextSize(1);
  disp.printf("%c", PROGRESS_CHR[count]);

  String net_stat;
  if ( netmgr_mode == NetMgr::MODE_WIFI_ON ) {
    net_stat = WiFi.SSID();
  } else if ( netmgr_mode == NetMgr::MODE_AP_LOOP ) {
    net_stat = "[AP mode]";
  } else {
    net_stat = "...";
  }
  const uint16_t X_NET = X_PROGRESS + CH_W + 2;
  const uint16_t Y_NET = Y7;
  disp.setCursor(X_NET, Y_NET);
  disp.setTextSize(1);
  disp.printf("%s", net_stat);
  
  disp.display();
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
  // disp.ssd1306_command(SSD1306_SETCONTRAST);
  // disp.ssd1306_command(0x8F); // デフォルト
  // disp.dim(true); // 少し暗くなる

  bme.begin(I2CADDR_BME280);
  bme.setSampling(Adafruit_BME280::MODE_FORCED);  // !! IMPORTANT !!
  //bme.setSampling(Adafruit_BME280::MODE_NORMAL);

  adc1 = new Adc1(ADC_CH, ADC_ATTEN, ADC_WIDTH_BIT_9);

  enableIntr();
} // setup()

/**
 *
 */
void loop() {
  static unsigned long prev_get_ms = 0;
  static unsigned long prev_disp_ms = 0;
  static mode_t prev_netmgr_mode = NetMgr::MODE_NULL;
  static float temp, hum, pres, vol;
  mode_t netmgr_mode;
  bool disp_force = false;
  unsigned long cur_ms = millis();

  // Button
  if ( btn0.get() ) {
    btn0.print();
    if ( btn0.is_long_pressed() ) {
      Serial.println("reboot ..\n");
      // display(99.9, 99, 9999, 9.9, prev_netmgr_mode);
      disp.clearDisplay();
      disp.display();
      delay(1000);
      ESP.restart();
    }
  }

  // NetMgr
  netmgr_mode = netMgr.loop();
  if ( netmgr_mode != prev_netmgr_mode ) {
    prev_netmgr_mode = netmgr_mode;

    Serial.printf("netmgr_mode=0x%02X\n", netmgr_mode);
    disp_force = true;
  }

  // get data (temp, vol, ...)
  if ( cur_ms - prev_get_ms >= GET_TEMP_INTERVAL
       || prev_get_ms == 0
       || cur_ms < prev_get_ms ) {
    prev_get_ms = cur_ms;
    
    /**
     * get vol
     */
    vol = adc_get_vol();
  
    /**
     * get temp, hum, pressure
     */
    bme.takeForcedMeasurement();  // !! IMPORTANT !!
    temp = bme.readTemperature() + TEMP_OFFSET;
    hum = bme.readHumidity();
    pres = bme.readPressure() / 100.0;
    Serial.printf("%.3fV %.3f(%.1f) %.2f %0.3f\n",
                  vol, temp, TEMP_OFFSET, hum, pres);
  }
  
  // Display
  if ( disp_force
       || cur_ms - prev_disp_ms >= DISP_INTERVAL
       || prev_disp_ms == 0
       || cur_ms < prev_disp_ms ) {
    prev_disp_ms = cur_ms;
    disp_force = false;

    display(temp, hum, pres, vol, netmgr_mode);
  }

  delayMicroseconds(1);
} // loop()
