import configparser
import keyboard
import pyautogui
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Fare hareketlerini daha güvenli hale getirmek için
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1

# Read the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get values from the config file
yuumi_server_ip = config.get('General', 'yuumi_server_ip')
yuumi_server_port = config.getint('General', 'yuumi_server_port')
yuumi_game_resolution = tuple(map(int, config.get('General', 'yuumi_game_resolution').split(', ')))
client_game_resolution = tuple(map(int, config.get('General', 'client_game_resolution').split(', ')))
yuumi_controls_key_press_duration = config.getfloat('General', 'yuumi_controls_key_press_duration')

# Duration for key presses
key_press_duration = yuumi_controls_key_press_duration

def safe_key_press(key):
    """Güvenli tuş basma işlemi"""
    try:
        keyboard.press(key)
        time.sleep(key_press_duration)
        keyboard.release(key)
        return True
    except Exception as e:
        print(f"Tuş basma hatası ({key}): {str(e)}")
        return False

@app.route('/spell', methods=['POST'])
def handle_spell():
    try:
        spell_action = request.json['action']
        print(f'Casting spell: {spell_action}')
        
        # Doğrudan tuşu basıyoruz
        keyboard.press(spell_action)
        time.sleep(key_press_duration)
        keyboard.release(spell_action)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error in handle_spell: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/click', methods=['POST'])
def handle_click():
    try:
        # Get the mouse coordinates from the request
        mouse_x = request.json['mouse_x']
        mouse_y = request.json['mouse_y']
        button = request.json['button']

        # Convert the mouse coordinates from main PC screen resolution to League of Legends game resolution
        game_x = int((mouse_x / client_game_resolution[0]) * yuumi_game_resolution[0])
        game_y = int((mouse_y / client_game_resolution[1]) * yuumi_game_resolution[1])

        # Move the mouse to the specified position and click
        pyautogui.moveTo(game_x, game_y)
        if button == 'left':
            pyautogui.click()
        elif button == 'right':
            pyautogui.rightClick()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error in handle_click: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/level', methods=['POST'])
def handle_level():
    try:
        ability = request.json['ability']
        print(f'Leveling up ability: {ability}')
        
        keyboard.press(ability)
        time.sleep(key_press_duration)
        keyboard.release(ability)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f'Error in handle_level: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def handle_connect():
    return jsonify({'status': 'Server is running'})

if __name__ == '__main__':
    try:
        print(f"Yuumi Server başlatılıyor... {yuumi_server_ip}:{yuumi_server_port}")
        app.run(host=yuumi_server_ip, port=yuumi_server_port, threaded=True)
    except Exception as e:
        print(f"Server başlatma hatası: {str(e)}")