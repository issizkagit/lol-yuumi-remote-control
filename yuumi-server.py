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
        valid_keys = [
            config.get('Keys', key) 
            for key in ['spell_q', 'spell_w', 'spell_e', 'spell_r', 'spell_d', 'spell_f', 
                       'open_shop', 'tab_info', 'go_to_base', 
                       'level_up_q', 'level_up_w', 'level_up_e', 'level_up_r']
        ]

        if spell_action in valid_keys:
            if safe_key_press(spell_action):
                return jsonify({'success': True})
            return jsonify({'error': 'Key press failed'}), 500
        return jsonify({'error': 'Invalid spell action'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/click', methods=['POST'])
def handle_click():
    try:
        mouse_x = request.json['mouse_x']
        mouse_y = request.json['mouse_y']
        button = request.json['button']

        # Koordinat dönüşümü
        game_x = int((mouse_x / client_game_resolution[0]) * yuumi_game_resolution[0])
        game_y = int((mouse_y / client_game_resolution[1]) * yuumi_game_resolution[1])

        # Koordinatları ekran sınırları içinde tutma
        game_x = max(0, min(game_x, yuumi_game_resolution[0]))
        game_y = max(0, min(game_y, yuumi_game_resolution[1]))

        # Fare hareketini ve tıklamayı gerçekleştirme
        pyautogui.moveTo(game_x, game_y, duration=0.1)
        if button == 'left':
            pyautogui.click()
        elif button == 'right':
            pyautogui.rightClick()
        else:
            return jsonify({'error': 'Invalid mouse button'}), 400

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/level', methods=['POST'])
def handle_level():
    try:
        ability = request.json['ability']
        valid_level_keys = [config.get('Keys', key) for key in ['level_up_q', 'level_up_w', 'level_up_e', 'level_up_r']]
        
        if ability in valid_level_keys:
            if safe_key_press(ability):
                return jsonify({'success': True})
            return jsonify({'error': 'Key press failed'}), 500
        return jsonify({'error': 'Invalid ability'}), 400

    except Exception as e:
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