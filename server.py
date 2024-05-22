import socket
import threading
import json
from datetime import datetime
import os

class MessageManager:
    def __init__(self, file_name='messages.json'):
        self.file_name = file_name
        self.messages = self.load_messages()

    def load_messages(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_messages(self):
        with open(self.file_name, 'w') as file:
            json.dump(self.messages, file, indent=4)

    def add_message(self, sender, recipient, message):
        room_id = f"{sender}-{recipient}" if sender < recipient else f"{recipient}-{sender}"
        if room_id not in self.messages:
            self.messages[room_id] = []
        new_message = {
            'date': datetime.now().isoformat(),
            'sender': sender,
            'message': message
        }
        self.messages[room_id].append(new_message)
        self.save_messages()


    def get_chatrooms_for_user(self, username):
        chatrooms = []
        for room_id in self.messages:
            if username in room_id:
                chatrooms.append(room_id)
        return chatrooms
    
    def get_messages_for_chatroom(self, room_id):
        if room_id in self.messages:
            a=sorted(self.messages[room_id], key=lambda x: x['date'])
            print(a)
            return a
        return []
    
    def search_messages_in_chatrooms(self, username, query):
        results = []
        for room_id in self.messages:
            if username in room_id:
                for msg in self.messages[room_id]:
                    if query.lower() in msg['message'].lower():
                        results.append(msg)
        a=sorted(results, key=lambda x: x['date'])
        print(a)
        return a

    

def handle_client(connection, address, manager):
    try:
        data = b""
        while True:
            part = connection.recv(1024)
            data += part
            if len(part) < 1024:
                break
        request = json.loads(data.decode())
        if data and request['type'] != 'login':
            if request['type'] == 'send_message':
                manager.add_message(request['sender'], request['recipient'], request['message'])
                response = {'status': 'success', 'message': 'Mesaj kaydedildi.'}
            elif request['type'] == 'get_chatrooms':
                chatrooms = manager.get_chatrooms_for_user(request['username'])
                response = {'status': 'success', 'chatrooms': chatrooms}
            elif request['type'] == 'get_messages':
                messages = manager.get_messages_for_chatroom(request['room_id'])
                response = {'status': 'success', 'messages': messages}
            elif request['type'] == 'search_messages':
                messages = manager.search_messages_in_chatrooms(request['username'], request['query'])
                response = {'status': 'success', 'messages': messages}
            connection.sendall(json.dumps(response).encode())
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        connection.sendall(json.dumps({'status': 'error', 'message': 'JSON format hatası.'}).encode())
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    finally:
        connection.close()

def start_server(host='localhost', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Sunucu {host} üzerinde {port} portunu dinliyor...")

    manager = MessageManager()

    while True:
        client_socket, addr = server_socket.accept()
        print(f"{addr} adresinden bir bağlantı kabul edildi")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, manager))
        client_thread.start()



# def start_server(host='localhost', port=12345):
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((host, port))
#     server_socket.listen()

#     print(f"Sunucu {host} üzerinde {port} portunu dinliyor...")

#     while True:
#         client_socket, addr = server_socket.accept()
#         print(f"{addr} adresinden bir bağlantı kabul edildi")
#         client_socket.sendall("Sunucuya bağlandınız!".encode())
#         client_socket.close()

if __name__ == '__main__':
    start_server()
