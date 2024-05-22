import sys
import socket
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit,QListWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.label = QLabel('Kullanıcı Adınız:', self)
        self.lineEditUsername = QLineEdit(self)
        self.buttonLogin = QPushButton('Giriş Yap', self)
        self.buttonLogin.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.lineEditUsername)
        layout.addWidget(self.buttonLogin)
        self.setLayout(layout)

        self.setWindowTitle('Chat Uygulaması Giriş')
        self.setGeometry(300, 300, 300, 150)

    def login(self):
        username = self.lineEditUsername.text()
        self.connect_to_server(username)
        self.main_window = MainWindow(username)
        self.main_window.show()
        self.close()
        
    def connect_to_server(self, username):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            data = json.dumps({
             'type': 'login',  
            'sender': username
        })
            client_socket.sendall(data.encode())
            response = client_socket.recv(1024).decode()
            client_socket.close()
            return response == "Giriş başarılı"
        except Exception as e:
            print(f'Bağlantı hatası: {e}')
            return False

class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Chat Uygulaması Ana Ekran')
        self.setGeometry(300, 300, 400, 300)

        self.buttonSendMessage = QPushButton('Mesaj Gönder', self)
        self.buttonSendMessage.clicked.connect(self.openChatWindow)

        self.buttonViewMessage = QPushButton('Sohbetlerim', self)
        self.buttonViewMessage.clicked.connect(self.openChatroomsWindow)

        self.buttonSearchMessage = QPushButton('Mesaj Ara', self)
        self.buttonSearchMessage.clicked.connect(self.openSearchMessagesWindow)

        layout = QVBoxLayout()
        layout.addWidget(self.buttonSendMessage)
        layout.addWidget(self.buttonViewMessage)
        layout.addWidget(self.buttonSearchMessage)
        self.setLayout(layout)

    def openChatWindow(self):
        self.chat_window = ChatWindow(self.username)
        self.chat_window.show()

    def openChatroomsWindow(self):
        self.chatrooms_window = ChatroomsWindow(self.username)
        self.chatrooms_window.show()
    
    def openSearchMessagesWindow(self):
        self.search_messages_window = SearchMessagesWindow(self.username)
        self.search_messages_window.show()

class ChatWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.labelMessage = QLabel('Mesajınız:', self)
        self.lineEditMessage = QLineEdit(self)
        self.lineEditRecipient = QLineEdit(self)
        self.labelRecipient = QLabel('Alıcı Kullanıcı Adı:', self)
        self.buttonSendMessage = QPushButton('Mesaj Gönder', self)
        self.buttonSendMessage.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.labelRecipient)
        layout.addWidget(self.lineEditRecipient)
        layout.addWidget(self.labelMessage)
        layout.addWidget(self.lineEditMessage)
        layout.addWidget(self.buttonSendMessage)
        self.setLayout(layout)

        self.setWindowTitle('Chat Uygulaması Mesajlaşma')
        self.setGeometry(300, 300, 400, 200)


    def send_message(self):
        message = self.lineEditMessage.text()
        recipient = self.lineEditRecipient.text()
        data = json.dumps({
            'type': 'send_message',
            'sender': self.username,
            'recipient': recipient,
            'message': message
        })
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            client_socket.sendall(data.encode())
            response = client_socket.recv(1024).decode()
            print(response)
            client_socket.close()
        except Exception as e:
            print(f'Bağlantı hatası: {e}')



class ChatroomsWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sohbet Odalarım')
        self.setGeometry(300, 300, 400, 300)
        self.layout = QVBoxLayout()
        
        self.chatrooms_list = QListWidget(self)
        self.chatrooms_list.clicked.connect(self.on_chatroom_selected)

        self.messages_display = QListWidget(self)
        
        self.layout.addWidget(self.chatrooms_list)
        self.layout.addWidget(self.messages_display)
        self.setLayout(self.layout)
        
        self.load_chatrooms()


    def load_chatrooms(self):
        # Sunucudan chatroom listesini al
        chatrooms = self.get_chatrooms(self.username)
        for room in chatrooms:
            self.chatrooms_list.addItem(room)

    def on_chatroom_selected(self, index):
        room_id = self.chatrooms_list.item(index.row()).text()
        # Sunucudan oda için mesajları al
        messages = get_messages_for_chatroom(room_id)
        self.messages_display.clear()
        for msg in messages:
            display_text = f"{msg['date']} - {msg['sender']}: {msg['message']}"
            self.messages_display.addItem(display_text)

    def get_chatrooms(self, username):
    # Sunucuya bağlan ve chatrooms isteğini gönder
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            request = json.dumps({
                'type': 'get_chatrooms',
                'username': username
            })
            client_socket.sendall(request.encode())
            
            # Sunucudan yanıt al
            response = client_socket.recv(4096).decode()
            response_data = json.loads(response)
            client_socket.close()
            
            if response_data['status'] == 'success':
                return response_data['chatrooms']
            else:
                print("Error fetching chatrooms:", response_data['message'])
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return []

def get_messages_for_chatroom(room_id):
    # Sunucuya bağlan ve mesajlar için isteğini gönder
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 12345))
        request = json.dumps({
            'type': 'get_messages',
            'room_id': room_id
        })
        client_socket.sendall(request.encode())
        
        # Sunucudan yanıt al
        response = client_socket.recv(4096).decode()
        response_data = json.loads(response)
        client_socket.close()
        
        if response_data['status'] == 'success':
            return response_data['messages']
        else:
            print("Error fetching messages:", response_data['message'])
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return []

class SearchMessagesWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Message Search')
        self.setGeometry(300, 300, 400, 300)
        layout = QVBoxLayout()
        
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText('Enter message to search...')
        self.search_button = QPushButton('Search', self)
        self.search_button.clicked.connect(self.perform_search)
        
        self.results_display = QListWidget(self)
        
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results_display)
        self.setLayout(layout)
        
    def perform_search(self):
        search_query = self.search_input.text()
        results = self.search_messages(self.username, search_query)
        self.results_display.clear()
        for msg in results:
            display_text = f"{msg['date']} - {msg['sender']}: {msg['message']}"
            self.results_display.addItem(display_text)

    def search_messages(self,username, query):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            request = json.dumps({
                'type': 'search_messages',
                'username': username,
                'query': query
            })
            client_socket.sendall(request.encode())
            
            response = client_socket.recv(4096).decode()
            response_data = json.loads(response)
            client_socket.close()
            
            if response_data['status'] == 'success':
                return response_data['messages']
            else:
                print("Error searching messages:", response_data['message'])
        except Exception as e:
            print(f"An error occurred: {e}")
        return []


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
