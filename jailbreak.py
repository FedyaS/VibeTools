from websocket import create_connection
import time
ws = create_connection("wss://jailbreak.hackmit.org/ws/")
ws.settimeout(10)
print(ws.recv())  # 'user ID: '
ws.send_binary(bytes.fromhex("4665647961535f65626135363133390a"))  # 'FedyA5_eba56139\n'
time.sleep(1)
print(ws.recv())  # 'VAR: '
ws.send_binary(bytes.fromhex("50555a5a4c450a"))  # 'PUZZLE\n'
time.sleep(1)
print(ws.recv())  # 'VAL: '
ws.send_binary(bytes.fromhex("6265616e730a"))  # 'beans\n'
time.sleep(1)
try:
    print(ws.recv())  # Check for output
except Exception as e:
    print(f"Error: {e}")
ws.close()