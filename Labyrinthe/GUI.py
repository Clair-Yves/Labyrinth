'''GUI stands for Graphical User Interface'''
import tkinter as tk
from threading import Thread
import select
import os


LabiMsgType="Labi:"
ChatMsgType="Chat:"
PlayersTurnMsgType="Turn:"
ChatWidth=30
ChatLabel="Chatting"
LabiLabel="The Maze"
InstruLabel="How to play"
YourTurnLabel="Your turn :"
ChatSubLabel="Send ->"
EndOfSessionMsg="StopSessionHereAndNow"

class GameWindow(Thread):
    '''GameWindow is both a tkinter widget for the players and a thread that is always listening to the Server
        Entry widgets of the Tkinter sends players input to the Server
        The server and the GameWindow know if the message is to be treated as a chat message, a turn input or a system message
        (like turn switch or end of session) with the message Type that is at the start of each message'''
    def __init__(self, LabiStringConstruct,ConnexionServer):
        self.LabiCharWidth, self.LabiLineHeight = readLabi(LabiStringConstruct)
        with open("instructions.txt", "r") as file:
            instructionsFileContent = file.read()
        self.InstructionCharWidth, self.InstructionLineHeight = readLabi(instructionsFileContent)
        height=max(self.LabiLineHeight,self.InstructionLineHeight)

        #-------- general main frames
        self._root = tk.Tk()
        self.GameFrame = tk.Frame(self.root)
        self.chatFrame = tk.Frame(self.root)
        self.labiFrame = tk.Frame(self.GameFrame)
        self.insrtuctionFrame=tk.Frame(self.GameFrame)#Not packed by default, only packed when it is your turn to play
        self.bottomInsrtuctionFrame = tk.Frame(self.insrtuctionFrame)
        self.topChatFrame = tk.Frame(self.chatFrame) # top frame used to make the scrollbar reach the top label
        self.bottomChatFrame = tk.Frame(self.chatFrame)

        self.labiFrame.config(bg='blue')
        self.chatFrame.config(bg='red')
        self.insrtuctionFrame.config(bg='green')

        self.chatFrame.pack(side='right', fill='y')
        self.GameFrame.pack(side='left', fill='y')
        self.labiFrame.pack(side='right', fill='y')
        self.topChatFrame.pack(side='top')
        self.bottomChatFrame.pack(side='bottom', fill='x')
        self.bottomInsrtuctionFrame.pack(side='bottom')

        # --- Display Labi, LabiFrame and Laby Entry
        self._playerInput = tk.StringVar()
        self.LabiLabel = tk.Label(self.labiFrame, text=LabiLabel)
        self.LabiLabel.pack(side='top')
        self.OtherPlayersTags=[]
        self.PlayerTag=""
        self.ExitTag=""
        self._labiString=LabiStringConstruct
        self.LabiTextWidget = tk.Text(self.labiFrame, width=self.LabiCharWidth, height=height)
        self.LabiTextWidget.insert(tk.END, self.LabiString)
        self.reset_and_apply_tagging()
        self.LabiTextWidget["state"] = "disabled"
        self.LabiTextWidget.pack(fill='both')

        # --------Display Chat and ChatEntry
        self.ChatScroll = tk.Scrollbar(self.chatFrame)
        self.ChatScroll.pack(side='right', fill='y')
        self.ChatLabel=tk.Label(self.topChatFrame, text=ChatLabel)
        self.ChatLabel.pack( fill='y')
        self.Chat = tk.Text(self.chatFrame, width=ChatWidth, height=height, yscrollcommand =self.ChatScroll.set)
        self.ChatScroll.config(command=self.Chat.yview)
        self.Chat["state"] = "disabled"
        self.Chat.pack(fill='y')
        self.ChatSubLabel=tk.Label(self.bottomChatFrame, text=ChatSubLabel)
        self.ChatSubLabel.pack(side='left')
        self._playerChat = tk.StringVar()
        self.ChatEntry = tk.Entry(self.bottomChatFrame, textvariable=self._playerChat)
        self.ChatEntry.bind('<Return>', self.send_player_ChatMsg)
        self.ChatEntry.pack(side='right', fill='y')


        #------ Display Instruction Text
        self.commandLabel = tk.Label(self.bottomInsrtuctionFrame, text=YourTurnLabel)
        self.commandLabel.pack(side='left')
        self.commandEntry = tk.Entry(self.bottomInsrtuctionFrame, textvariable=self._playerInput)
        self.commandEntry.pack()
        self.commandEntry.bind('<Return>', self.send_player_MoveInput)  # --- not packed at launch
        self.instructionLabel=tk.Label(self.insrtuctionFrame, text=InstruLabel)
        self.instructionLabel.pack(side='top')
        self.InstructionsPacked = [False]
        self.InstructionText=tk.Text(self.insrtuctionFrame, width=self.InstructionCharWidth, height=height)
        self.InstructionText.insert(tk.END,instructionsFileContent)
        self.InstructionText["state"] = "disabled"
        self.InstructionText.pack(fill='both')

        #----- connexion server
        self.ConnexionServer=ConnexionServer
        self.ContinueListening=True
        Thread.__init__(self)
        self.start() #run thread -> listening for the server

    def getPlayerInput(self):
        return self._playerInput.get()
    def setPlayerInput(self, newInput):
        self._playerInput.set(newInput)
    def getPlayerChat(self):
        return self._playerChat.get()
    def setPlayerChat(self,newChatMsg):
        self._playerChat.set(newChatMsg)
    PlayerInput=property(getPlayerInput,setPlayerInput)
    PlayerChat=property(getPlayerChat,setPlayerChat)

    def getRoot(self):
        return self._root

    root=property(getRoot)

    def run(self):
        while self.ContinueListening:
            try:
                socketReturn, wlist, xlist = select.select([self.ConnexionServer], [], [], 0.05)
                ServerMsg=socketReturn[0].recv(1024).decode()  # ex ->  Labi: OOOOOO... , or chat:playerName: Blablabla
                ServerMsgType, ServerMsgContent = decomposeMsg(ServerMsg)
                if ServerMsgType==LabiMsgType:
                    self.setLabiString(ServerMsgContent)
                if ServerMsgType==PlayersTurnMsgType:
                    self.ask_for_instructions_widgets_to_appear()
                if ServerMsgType==ChatMsgType:
                    self.add_to_chat(ServerMsgContent)

            except:
                pass

    def getLabiString(self):
        return self._labiString
    def setLabiString(self,newLabiStr):

        self._labiString=newLabiStr
        self.LabiTextWidget["state"] = "normal"
        self.LabiTextWidget.delete(1.0, tk.END)
        self.LabiTextWidget.insert(tk.END, self.LabiString)
        self.reset_and_apply_tagging()
        self.LabiTextWidget["state"] = "disabled"

    LabiString= property(getLabiString, setLabiString)

    def add_to_chat(self,newLine):
        self.Chat["state"] = "normal"
        self.Chat.insert(tk.END, newLine + "\n")
        self.LabiTextWidget["state"] = "disabled"

    def send_player_MoveInput(self, event):
        msgToServer=LabiMsgType+self.PlayerInput #concatenation of the message type (Labi:) and the player input typed in the labi entry widget
        self.ConnexionServer.send(msgToServer.encode())
        self.setPlayerInput("")

    def send_player_ChatMsg(self, event):
        chatMsgToBeSent=ChatMsgType+self.PlayerChat #concatenation of the message type (Chat:) and the player message typed in the chat entry widget
        self.ConnexionServer.send(chatMsgToBeSent.encode())
        self.setPlayerChat("")

    def ask_for_instructions_widgets_to_appear(self):
        '''Switch the Pack/Unpacked state of the labiInstruction Widget each time a PlayersTurnMsgType is received from the Server'''
        if not self.InstructionsPacked[0]:
            # self.commandWidget.pack(side='bottom', fill='y')
            self.insrtuctionFrame.pack(side='left', fill='y')
            self.InstructionsPacked[0] = True
        else:
            self.insrtuctionFrame.pack_forget()
            self.InstructionsPacked[0] = False

    def reset_and_apply_tagging(self):
        '''Creates and apply the tags on the maze display so players can see themselves (X) and others (x) easier'''

         #clearing all tags from LabiTextWidget
        self.LabiTextWidget.tag_delete(self.PlayerTag)
        for tag in self.OtherPlayersTags:
            self.LabiTextWidget.tag_delete(tag)
        self.OtherPlayersTags = []

        #Finding the tags in labistring
        charPerLine=self.LabiCharWidth
        i=0
        for char in self.LabiString:
            if char=="x":
                self.OtherPlayersTags.append(str(1+i//charPerLine)+"."+str(i%charPerLine))
            elif char=="X":
                self.PlayerTag=str(1+i//charPerLine)+"."+str(i%charPerLine)
            elif char=="U":
                self.ExitTag=str(1+i//charPerLine)+"."+str(i%charPerLine)
            elif char=="\n": #we do not count \n in the indexes
                i-=1
            i+=1

        #add and config the tags in the LabiTextWidget
        PlayerTagLine=int(self.PlayerTag[:self.PlayerTag.index(".")])
        PlayerTagColumn=int(self.PlayerTag[self.PlayerTag.index(".")+1:])
        PlayerTagNextIndex=str(PlayerTagLine)+"."+str(PlayerTagColumn+1)
        self.LabiTextWidget.tag_add(self.PlayerTag,self.PlayerTag,PlayerTagNextIndex)
        self.LabiTextWidget.tag_config(self.PlayerTag, background="yellow", foreground="blue")

        ExitTagLine=int(self.ExitTag[:self.ExitTag.index(".")])
        ExitTagColumn=int(self.ExitTag[self.ExitTag.index(".")+1:])
        ExitTagNextIndex=str(ExitTagLine)+"."+str(ExitTagColumn+1)
        self.LabiTextWidget.tag_add(self.ExitTag,self.ExitTag,ExitTagNextIndex)
        self.LabiTextWidget.tag_config(self.ExitTag, background="black", foreground="white")

        for tag in self.OtherPlayersTags:
            PlayerTagLine = int(tag[:tag.index(".")])
            PlayerTagColumn = int(tag[tag.index(".") + 1:])
            PlayerTagNextIndex = str(PlayerTagLine) + "." + str(PlayerTagColumn + 1)
            self.LabiTextWidget.tag_add(tag, tag, PlayerTagNextIndex)
            self.LabiTextWidget.tag_config(tag, background="red", foreground="black")

def readLabi(LabiString):
    '''return the number of characters per line and number of line of a labiString'''
    listeOfListes = []
    liste = []
    for char in LabiString:
        if char != '\n':
            liste.append(char)
        else:
            listeOfListes.append(liste)
            liste = []
    listeOfListes.append(liste)

    CharactersWidth = len(listeOfListes[0])
    LineHeight = len(listeOfListes)
    return CharactersWidth, LineHeight


def decomposeMsg(totalMsg):
    '''Returns a tuple composed of the MsgType and the content of the message in the GUI-Server exchanges'''
    MsgType = totalMsg[:totalMsg.index(":") + 1]
    MsgContent = totalMsg[totalMsg.index(":") + 1:]
    return MsgType,MsgContent

class ServerWindow():
    '''Small widget launched before the server to ask on which maze the game is going to take place'''
    def __init__(self):
        self.root = tk.Tk()
        self.mainFrame = tk.Frame(self.root, width=768, height=576, borderwidth=1)
        self.mainFrame.pack(side="bottom")

        self.label = tk.Label(self.root, text="Choose your maze :")
        self.label.config(bg='red')
        self.label.pack(side="top")

        self.finalChoice = tk.StringVar()
        self.choiceMade=tk.StringVar()
        self.choiceMade.set("not yet")
        choices = []
        mazeList = os.listdir("cartes/")
        for mazename in mazeList:
            name = mazename[::-1]
            name = name[:name.index("."):-1]
            choices.append(tk.Radiobutton(self.mainFrame, text=name, variable=self.finalChoice, value=name))

        for choice in choices:
            choice.pack(side="left")

        self.validateButton = tk.Button(self.mainFrame, text="Validate")
        self.validateButton.bind('<Button-1>', self.close_window)
        self.validateButton.pack(side="right")

    def close_window(self, event):
        '''The Validate button do not close the widget until a maze has been choosen'''
        if self.finalChoice.get() != "":
            self.root.destroy()


