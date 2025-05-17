import time
import pywifi

wifi = pywifi.PyWiFi()
try:
    iface = wifi.interfaces()[0]
except:
    print("未连接无线网卡或网卡编号设置错误，可前往config.py修改net_num")


def get_wifi_signal_strength():
    try:
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            iface.scan()
            time.sleep(1)
            scan_results = iface.scan_results()
            result = scan_results[0]
            signal = result.signal
            if signal >= -25:
                signal_percent = 100
            elif signal <= -95:
                signal_percent = 0
            else:
                signal_percent = int((signal - (-95)) / ((-25) - (-95)) * 100)
            print(f"信号强度为{signal_percent}%")
        print("WiFI已开启，但未连接")
    except:
        print("WiFI未开启")


get_wifi_signal_strength()
