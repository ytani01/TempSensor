# SHT-31
SHT-31 sensor

# Appendix

## A1. /boot/config.txt を使う方法
このライブラリと共存はできない

### A1.1 /boot/config.txt
```
deoverlay=i2c-sensor,sht3x,addr=0x45
```

### A1.2 ディレクトリ・ファイル名
/sys/bus/i2c/devices/1-0045/hwmon/hwmon0/
* temp1_input: 温度 * 1000
* humidity1_input: 湿度 * 1000

### A1.3 Source code
https://github.com/torvalds/linux/blob/master/drivers/hwmon/sht3x.c
