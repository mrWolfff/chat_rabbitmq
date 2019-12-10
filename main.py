from appJar import gui
import pika
import time
import threading

def threadReceive():
    thread = threading.Thread(target=receive)
    thread.daemon = True
    thread.start()
    
def enter_public(button):
    user = app.getEntry("user")
    host = app.getEntry("host")
    if user == "":
        app.infoBox("Usuario Vazio", "Nome do usuario vazio ou nulo, por favor, insira um nome!", parent=None)
        app.go()
    else:
        app.hide()
        app.disableEnter()
        app.startSubWindow("ChatPublic")
        app.setBg("yellow")
        app.setSize(500, 400)
        app.setFont(12)
        app.addTextArea("textArea", 0, 0, 5)
        app.setTextAreaWidth("textArea", 40)
        app.addEntry("textSend", 1, 0, 2)
        app.setFocus("textSend")
        app.addButtons(["Enviar"], send_public, 2, 0, 1)
        app.addButtons(["Exit"], pressExit, 2, 1, 1)
        threadReceive()
        app.setTextArea("textArea", user + " entrou!" , end=True, callFunction=True)
        app.setTextArea("textArea", "\n", end=True, callFunction=True)
        app.enableEnter(send_public)
        app.go(startWindow="ChatPublic")

def enter_private(button):
    user = app.getEntry("user")
    host = app.getEntry("host")
    if user == "":
        app.infoBox("Usuario Vazio", "Nome do usuario vazio ou nulo, por favor, insira um nome!", parent=None)
        app.go()
    else:
        if host == "":
            host = 'localhost'
        app.hide()
        app.disableEnter()
        app.startSubWindow("Chat")
        app.setBg("orange")
        app.setSize(500, 400)
        app.setFont(12)
        app.addLabelEntry("to_user", 0, 0, 2)
        app.addTextArea("textArea", 2, 0, 5)
        app.setTextAreaWidth("textArea", 40)
        app.addEntry("textSend", 4, 0, 2)
        app.setFocus("textSend")
        app.addButtons(["Enviar"], send_private, 5, 0, 1)
        app.addButtons(["Exit"], pressExit, 5, 1, 1)
        threadReceive()
        app.setTextArea("textArea", user + " entrou!" , end=True, callFunction=True)
        app.setTextArea("textArea", "\n", end=True, callFunction=True)
        app.enableEnter(send_private)
        app.go(startWindow="Chat")
        
def pressExit(button):
    app.stop()
    
def send_public():
    user = app.getEntry("user")
    host = app.getEntry("host")
    message = app.getEntry("textSend")
    if host == '':
        host = 'localhost'
    if message == '':
        pass
    message = user + ": " + message
    app.clearEntry("textSend", callFunction=True)
    try: 
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.exchange_declare(exchange='direct', exchange_type='fanout') 
        channel.basic_publish(exchange='direct', routing_key='', body=message)    
    except Exception as exception:
        print("ERRO: ")
    
def send_private():
    user = app.getEntry("user")
    host = app.getEntry("host")
    message = app.getEntry("textSend")
    if host == '':
        host = 'localhost'
    if message == '':
        pass
    if app.getEntry("to_user") != "":
        message = user + ": " + message
        to_user = app.getEntry("to_user")
        app.clearEntry("textSend", callFunction=True)
        try: 
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
            channel = connection.channel()
            channel.queue_declare(queue=to_user)
            channel.basic_publish(exchange='', routing_key=to_user, body=message, properties = pika.BasicProperties(delivery_mode=2,))
            app.setTextArea("textArea", message, end=True, callFunction=True)
            app.setTextArea("textArea", "\n", end=True, callFunction=True)
        except Exception as exception:
            print("ERRO: {}", exception)
    else:
        app.infoBox("Usuario Vazio", "Insira o nome do usuario que voce deseja enviar a mensagem!", parent=None)
        
              
def receive():
    user = app.getEntry("user")
    host = app.getEntry("host")
    if host == '':
        host = 'localhost'
    try:
        to_user = app.getEntry("to_user")
        try:    
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
            channel = connection.channel()
            channel.queue_declare(queue=user)
            channel.basic_consume(queue=user, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except Exception as exception:
            print("Erro: {}", exception)   
    except:    
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
            channel.exchange_declare(exchange='direct', exchange_type='fanout')
            queue_name = channel.queue_declare(queue='').method.queue
            channel.queue_bind(exchange='direct', queue=queue_name)
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except Exception as exception:
            print("Erro: {}", exception)
                
def callback(ch, method, properties, body):
    print(">> %r" % body)
    time.sleep(body.count(b'.'))
    app.setTextArea("textArea", body, end=True, callFunction=True)
    app.setTextArea("textArea", "\n", end=True, callFunction=True)
    
app = gui("Login", "500x400")
app.setBg("grey")
app.setFont(14)
app.startLabelFrame("Login")
app.addLabelEntry("user", 0, 0, 3)
app.addLabelEntry("host", 1, 0, 3)
app.setFocus("user")
app.addButtons(["Entrar"], enter_private, 4, 0, 1)
app.addButtons(["Entrar Publico"], enter_public, 4, 1, 1)
app.addButtons(["Sair"], pressExit, 4, 2, 1)
app.enableEnter(enter_public)
app.stopLabelFrame()
app.go()