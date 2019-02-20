import StartServer as Server
import GUI


continueMsg=True
port=Server.port
name=input("Your player name :")

ConnexionServer, labiStr =Server.connect_to_server(name,port)
GameWindow=GUI.GameWindow(labiStr, ConnexionServer)
GameWindow.root.mainloop()
GameWindow.ContinueListening=False
ConnexionServer.send((":"+GUI.EndOfSessionMsg).encode())

ConnexionServer.close()