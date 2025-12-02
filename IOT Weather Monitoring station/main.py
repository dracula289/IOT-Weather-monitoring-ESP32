import network
import time
from machine import Pin, I2C
import dht
import ssd1306
import urequests

# --- 1. CONFIGURATION ---
SSID = "Wokwi-GUEST"
PASSWORD = ""
API_KEY = "1JBRZS3NCQFEVGOH" 

# --- 2. HARDWARE SETUP ---
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
sensor = dht.DHT22(Pin(15))
fan = Pin(13, Pin.OUT) 

# --- SELF TEST: Blink 3 Times ---
print("System Starting... Watch LED...")
for i in range(3):
    fan.value(1) # ON
    time.sleep(0.3)
    fan.value(0) # OFF
    time.sleep(0.3)
print("LED Test Done.")

# --- 3. WIFI CONNECT ---
def connect_wifi():
    oled.fill(0)
    oled.text("Connecting WiFi...", 0, 0)
    oled.show()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.1)
    oled.fill(0)
    oled.text("WiFi Connected!", 0, 0)
    oled.show()
    print("WiFi Connected! Starting Loop...")
    time.sleep(1)

# --- 4. MAIN LOOP ---
connect_wifi()

while True:
    try:
        # A. Read Sensor
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        
        # --- SIMPLE PRINT (Bulletproof) ---
        print(">>> Reading Sensor:", temp, "C", hum, "%")

        # B. Fan Logic (Threshold = 20C)
        if temp > 20: 
            fan.value(1)
            status = "FAN: ON"
            print("   Fan Status: ON (Hot)")
        else:
            fan.value(0)
            status = "FAN: OFF"
            print("   Fan Status: OFF (Cool)")

        # C. Update Screen
        oled.fill(0)
        oled.text("IOT SYSTEM", 20, 0)
        oled.text("Temp: " + str(temp) + " C", 0, 20)
        oled.text("Hum: " + str(hum) + " %", 0, 35)
        oled.text(status, 0, 50)
        oled.show()

        # D. Send to Cloud
        print("   Sending to Cloud...", end="")
        url = "http://api.thingspeak.com/update?api_key=" + API_KEY + "&field1=" + str(temp) + "&field2=" + str(hum)
        response = urequests.get(url)
        print(" Done! Code:", response.text)
        response.close()

    except Exception as e:
        print("Error:", e)
    
    # E. Wait
    print("   Waiting 16s...")
    time.sleep(16)