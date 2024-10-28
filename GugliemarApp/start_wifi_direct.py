import subprocess

def on_start_wifi_direct(self):
    try:
        result = subprocess.run(
            ['python', 'start_wifi_direct.py', 'ssid_value', 'password_value'],
            check=False,  # check=False にすることで例外をスローしない
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Standard Output: {result.stdout}")
        print(f"Standard Error: {result.stderr}")

        # subprocessのreturncodeを取得
        return_code = result.returncode

        if return_code == 0:
            print("Wi-Fi Direct setup succeeded!")
        elif return_code == 1:
            self.display_error_message("Wi-Fi Direct setup failed. Please check your input and try again.")
        elif return_code == 2:
            self.display_error_message("Failed to reconnect to home WiFi. Please try again.")
        else:
            self.display_error_message("An unknown error occurred.")

    except Exception as e:
        print(f"Unexpected error: {e}")
        self.display_error_message("An unexpected error occurred. Please try again.")