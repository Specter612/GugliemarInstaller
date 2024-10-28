import sys
import socket
import time
import pywifi
from pywifi import PyWiFi, const, Profile

UDP_IP = "192.168.4.1"
UDP_PORT = 21089
CONFIG_FILE = 'home_credentials.txt'

def load_credentials():
    try:
        with open(CONFIG_FILE, 'r') as file:
            lines = file.readlines()
            if len(lines) >= 2:
                return lines[0].strip(), lines[1].strip()
            else:
                raise ValueError("Invalid format in home_credentials.txt")
    except FileNotFoundError:
        # ファイルが見つからない場合はデフォルトのSSIDとパスワードを返す
        return "30F772B5723C", "2211590813763"

def save_credentials(ssid, password):
    with open(CONFIG_FILE, 'w') as file:
        file.write(f"{ssid}\n{password}")

def connect_to_wifi(ssid, password):
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]

    iface.scan()
    time.sleep(2)

    results = iface.scan_results()
    profile = Profile()
    profile.ssid = ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password

    iface.remove_all_network_profiles()
    iface.add_network_profile(profile)

    iface.connect(profile)
    time.sleep(2)

    status = iface.status()
    print(f"Connection status for {ssid}: {status}")  # ステータスを出力
    if status == const.IFACE_CONNECTED:
        print(f"Successful connection to {ssid}")
        return True
    else:
        print(f"Failed to connect to {ssid}. Status: {status}")
        return False

def send_udp_message(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        binary_message = message.to_bytes(2, byteorder='little')
        sock.sendto(binary_message, (ip, port))
        print("Send message")

def main():
    print(f"Received arguments: {sys.argv}")
    if len(sys.argv) != 3:
        print("Usage: python wifi_direct_program.py <SSID> <PASSWORD>")
        return 3  # エラーコード1を返す

    direct_ssid = sys.argv[1]
    direct_password = sys.argv[2]

    # HOME_SSID と HOME_PASSWORD を設定ファイルから読み込み
    home_ssid, home_password = load_credentials()

    # Wi-Fi Directに接続
    if not connect_to_wifi(direct_ssid, direct_password):
        print("code 1: Direct WiFi connection failed")
        return 3  # エラーコード1を返す

    time.sleep(1)
    send_udp_message(UDP_IP, UDP_PORT, 2002)

    # 元のWi-Fiに接続
    if not connect_to_wifi(home_ssid, home_password):
        print("code 2: Home WiFi reconnection failed")
        return 2  # エラーコード2を返す
    
    print("Success: WiFi connections were successful")
    return 1  # 成功ステータスを返す

if __name__ == "__main__":
    result_code = main()
    home_ssid, home_password = load_credentials()  # 設定ファイルから読み込み
    connect_to_wifi(home_ssid, home_password)
    print(f"Exit code: {result_code}")
    # プログラムの終了を行わないようにする
