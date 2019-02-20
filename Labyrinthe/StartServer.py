import socket
import select
from threading import Thread
import time
import FrontEnd as FE
import GUI

host=''
port=12800

WinningMsg=" is the WINNER !!!\n\n"
LeavingMsg= " <has left the game>\n"
BeginGameCommand= "C"
GameStartMsg= " < Game Started >"

def get_a_running_server(SingletonClasse):
    runningServersInstance={}
    def get_instance(anything):
        if SingletonClasse not in runningServersInstance:
            runningServersInstance[SingletonClasse]=SingletonClasse(anything)
        return runningServersInstance[SingletonClasse]
    return get_instance

class Server():
    ''' implementation of the server for the labyrinthe game'''
    def __init__(self):
        self._connexion=socket.socket()
        self._host=host
        self._port = port
        self._clients_dico = {} # dictionnary of keys : client socket, value : player name -> first msg send

@get_a_running_server
class RunningLabiServer(Thread):
    '''Object containing the server, a Labyrinthe object from BackEnd and other usefull inforamtion for the game
        PlayerWindows widget are communicating with the RunningLabiServer'''
    def __init__(self, mazeName):
        # creating a RunningLabiServer instance starts the Thread-Server, we never starts it manually
        self.Begun = False
        self.EndOfGame=False
        Thread.__init__(self)
        self.server=Server()
        self.ActivePlayer="" #contains the client socket of the active player (the player who can play his turn)
        self.Connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Connexion.bind((self.Host, self.Port))
        self.Connexion.listen(5)
        print("Server started")
        print("Please do NOT close this window")
        self._labi = FE.labi(mazeName)
        self.start()

    def getLabi(self):
        return self._labi
    def _getConnexion(self):
        return self.server._connexion
    def _setConnexion(self,socket):
        self.server._connexion=socket
    def _getHost(self):
        return self.server._host
    def _getPort(self):
        return self.server._port
    def _getClientsDico(self):
        return self.server._clients_dico
    def add_to_ClientsDico(self,client,name):
        self.ClientsDico[client]=name

    Labi=property(getLabi)
    Connexion=property(_getConnexion,_setConnexion)
    Host = property(_getHost)
    Port = property(_getPort)
    ClientsDico = property(_getClientsDico)

    def run(self):
        #Always listen for new connection and to players input andact accordingly
        server_running=True
        while server_running:
            if not self.Begun:
                self.admit_newPlayers()
            server_running=self.listen_and_respond_to_Players()

    def admit_newPlayers(self):
        '''Add players to the player base dictionnary as long as the game hasn't started'''
        client_connexions, wlist, xlist = select.select([self.Connexion], [], [], 0.05)

        for new_clients in client_connexions:
            client, infos_client = new_clients.accept()
            name_client = client.recv(1024).decode()
            self.add_to_ClientsDico(client, name_client)
            self.Labi.addPlayer(name_client)
            self.send_labiStr_to_allClients()
            if len(list(self.ClientsDico.keys()))==1:
                self.ActivePlayer=client
                self.send_Turn_to_ActivePlayer()

    def listen_and_respond_to_Players(self):
        '''Read the messages send by the playerBase dictionnary and acts accordingly'''
        ContinueRunning=True
        try:
            clients_sending, wlist, xlist = select.select(self.ClientsDico.keys(), [], [], 0.05)
        except:
            pass
        else:
            for client in clients_sending:
                TotalMsg = client.recv(1024).decode()
                clientMsgType, msgClient = GUI.decomposeMsg(TotalMsg)
                if msgClient == GUI.EndOfSessionMsg:
                    ContinueRunning=self.leavingPlayerActions(client)
                if clientMsgType == GUI.LabiMsgType and msgClient.upper() == BeginGameCommand:
                    if self.Begun==False:
                        self.Begun=True
                        self.send_in_all_chats(GameStartMsg, client)
                elif clientMsgType == GUI.LabiMsgType and self.Begun==True:
                    self.makePlayerMove(msgClient,client)
                elif clientMsgType == GUI.ChatMsgType:
                    self.send_in_all_chats(msgClient,client)
        return ContinueRunning

    def leavingPlayerActions(self, client):
        '''When a player leaves his GameWindow widget he is removed from the player base dictionnary and his socket is closed,
            The Server is stopped if no players remain'''
        ContinueRunning = True
        if len(list(self.ClientsDico.keys())) == 1:
            ContinueRunning = False
            self.close()
        else:
            self.send_in_all_chats(LeavingMsg, client)
            client.close()
            self.Labi.removePlayer(self.ClientsDico[client])
            if self.ActivePlayer == client:
                self.nextPlayerTurn()
                self.send_Turn_to_ActivePlayer()
            del self.ClientsDico[client]
            if not self.EndOfGame:
                self.send_labiStr_to_allClients()
        return ContinueRunning

    def nextPlayerTurn(self):
        '''Send a TurnMsgType to the adequate players so that only one player can play at any time, taking turns'''
        listPlayers=list(self.ClientsDico.keys())
        indexActivePlayer=listPlayers.index(self.ActivePlayer)
        if indexActivePlayer+1==len(listPlayers):
            indexActivePlayer=-1
        self.ActivePlayer=listPlayers[indexActivePlayer+1]


    def makePlayerMove(self, inputJouer, client):
        '''Impact the Server's Labi with the player input from his Labi Entry's widget'''
        nomClient = self.ClientsDico[client]
        mvt = FE.nextMvt(inputJouer)
        if mvt is not False:
            FE.move(self.Labi, nomClient, mvt)
            self.send_labiStr_to_allClients()
            if len(list(self.ClientsDico.keys())) > 1:
                self.send_Turn_to_ActivePlayer()
                self.nextPlayerTurn()
                self.send_Turn_to_ActivePlayer()
            if self.Labi.getPlayerPos(self.ClientsDico[client])==self.Labi.Exit:
                self.send_Turn_to_ActivePlayer()
                self.sendWinnerMsg(client)

    def send_labiStr_to_allClients(self):
        '''Send the LabiString to all players to be on page
            Each player receives a specific LabiString with their own position being marked by a 'X' and opponent with a 'x' '''
        for anyClient in self.ClientsDico.keys():
            stringToBeSend=GUI.LabiMsgType+self.Labi.labi_to_LabiString_for_playerName(self.ClientsDico[anyClient])
            anyClient.send(stringToBeSend.encode())

    def send_Turn_to_ActivePlayer(self):
        time.sleep(0.1)
        self.ActivePlayer.send(GUI.PlayersTurnMsgType.encode())

    def send_in_all_chats(self,msgClient,client):
        '''Send the chat message to all clients for their chat to display'''
        for anyClient in self.ClientsDico.keys():
            stringToBeSend=GUI.ChatMsgType+self.ClientsDico[client]+":"+msgClient
            anyClient.send(stringToBeSend.encode())

    def sendWinnerMsg(self, WinnerClient):
        '''Send a winning message to all chats'''
        self.EndOfGame=True
        for anyClient in self.ClientsDico.keys():
            stringToBeSend=GUI.LabiMsgType+self.ClientsDico[WinnerClient]+WinningMsg+self.Labi.labi_to_LabiString_for_playerName(self.ClientsDico[anyClient])
            anyClient.send(stringToBeSend.encode())

    def close(self):
        for client in self.ClientsDico.keys():
            client.close()
        self.Connexion.close()
        print("server closed..")
        time.sleep(2)


def connect_to_server(nameJoueur, portConn):
    '''Return the ConnexionToServer socket and a first labiString '''
    ConnexionToServer=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ConnexionToServer.connect(('localhost',portConn))
        ConnexionToServer.send(nameJoueur.encode())

        ServerMsg = ConnexionToServer.recv(1024).decode()
        labiStr = ServerMsg[ServerMsg.index(":") + 1:]
        return ConnexionToServer, labiStr
    except:
        print("Start the server before connecting to it")
        time.sleep(3)
        return None

if __name__ =="__main__":
    #Create the 'Choose your maze' prompt and starts the server
    serverWindow=GUI.ServerWindow()
    serverWindow.root.mainloop()
    print("You are playing on : "+serverWindow.finalChoice.get())
    ARunningServer=RunningLabiServer(serverWindow.finalChoice.get())


