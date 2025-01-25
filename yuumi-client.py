import sys
import requests
import threading
import pyautogui
import win32api
import win32con
import time
import configparser

running = True

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

yuumi_pc_ip = config.get('General', 'yuumi_server_ip')
server_port = config.get('General', 'yuumi_server_port')
click_url = f'http://{yuumi_pc_ip}:{server_port}/click'
spell_url = f'http://{yuumi_pc_ip}:{server_port}/spell'
level_url = f'http://{yuumi_pc_ip}:{server_port}/level'

alt_pressed = False
action_delay = 0.5
last_action_time = 0

try:
    print('Trying to connect...')
    requests.get(f'http://{yuumi_pc_ip}:{server_port}')
    print('Connected to Yuumi PC')
except requests.exceptions.ConnectionError:
    print('\033[91m' + 'Failed to connect to Yuumi PC. Please check the server IP and try running the script again.' + '\033[0m')
    sys.exit()

def send_request(url, json_data):
    try:
        response = requests.post(url, json=json_data, timeout=5.0)
        if response.status_code != 200:
            print(f"Error: Server returned {response.status_code}")
            print(f"Response: {response.json()}")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except Exception as e:
        print(f"Error sending request: {str(e)}")

# Setup key bindings
spell_keys = {
    config.get('Keys', 'spell_q'): 'q',
    config.get('Keys', 'spell_w'): 'w',
    config.get('Keys', 'spell_e'): 'e',
    config.get('Keys', 'spell_r'): 'r',
    config.get('Keys', 'spell_d'): 'd',
    config.get('Keys', 'spell_f'): 'f',
    config.get('Keys', 'open_shop'): 'p',
    config.get('Keys', 'tab_info'): 'o',
    config.get('Keys', 'go_to_base'): 'b',
}

level_keys = {
    config.get('Keys', 'level_up_q'): 'q',
    config.get('Keys', 'level_up_w'): 'w',
    config.get('Keys', 'level_up_e'): 'e',
    config.get('Keys', 'level_up_r'): 'r'
}

def check_key_press():
    global alt_pressed, last_action_time
    
    while running:
        # Alt tuşu kontrolü
        if win32api.GetAsyncKeyState(win32con.VK_MENU) & 0x8000:
            if not alt_pressed:
                alt_pressed = True
                print('ALT key pressed')
        else:
            if alt_pressed:
                alt_pressed = False
                print('ALT key released')

        # Diğer tuşların kontrolü
        if alt_pressed:
            # Spell tuşlarını kontrol et
            for key, action in spell_keys.items():
                if win32api.GetAsyncKeyState(ord(key.upper())) & 0x8000:
                    print(f'{key} key pressed (spell)')
                    spell_data = {'action': action}
                    send_request(spell_url, spell_data)
                    time.sleep(0.1)

            # Level yükseltme tuşlarını kontrol et
            for key, ability in level_keys.items():
                if win32api.GetAsyncKeyState(ord(key.upper())) & 0x8000:
                    print(f'{key} key pressed (level up {ability})')
                    level_data = {'ability': ability}
                    send_request(level_url, level_data)
                    time.sleep(0.1)

            # Fare tıklamalarını kontrol et
            if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                current_time = time.time()
                if current_time - last_action_time >= action_delay:
                    x, y = pyautogui.position()
                    print(f'left button clicked at ({x}, {y})')
                    click_data = {'mouse_x': x, 'mouse_y': y, 'button': 'left'}
                    send_request(click_url, click_data)
                    last_action_time = current_time
                    time.sleep(0.1)

            if win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000:
                current_time = time.time()
                if current_time - last_action_time >= action_delay:
                    x, y = pyautogui.position()
                    print(f'right button clicked at ({x}, {y})')
                    click_data = {'mouse_x': x, 'mouse_y': y, 'button': 'right'}
                    send_request(click_url, click_data)
                    last_action_time = current_time
                    time.sleep(0.1)

        time.sleep(0.01)  # CPU kullanımını azaltmak için

print("Client is running. Press ALT + key to control Yuumi.")

# Start key checking thread
key_thread = threading.Thread(target=check_key_press, daemon=True)
key_thread.start()

# Main loop
while running:
    time.sleep(1)
