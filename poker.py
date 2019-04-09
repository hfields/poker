from localpokergui import Application as LocalApp
from localpokerchips import Table as LocalTable
from fbpokerbot import *
from discordpokerbot import *
from tkinter import *
from tkinter.messagebox import *
import asyncio

email = ""
password = ""
TOKEN = ""
channelId = ""
FACEBOOK = 1
DISCORD = 2

def main():
    # Grab info from logininfo.txt
    global email, password, TOKEN, channelId
    f = open("logininfo.txt", "r")
    info = f.readlines()
    email = info[0][:-1]
    password = info[1][:-1]
    TOKEN = info[2][:-1]
    channelId = info[3]

    # Initialize the startup options window
    startup = Tk()
    startup.geometry("800x450")
    gui = IntVar()
    online = IntVar()

    # Create radio buttons for GUI/Terminal selection
    Label(startup, 
            text="""Terminal view or GUI?""",
            justify = LEFT,
            padx = 20).grid(row=0, column=0)
    
    Radiobutton(startup, 
                text="GUI",
                padx = 20, 
                variable=gui,
                value=0).grid(row=0, column=1)
    Radiobutton(startup, 
                text="Terminal",
                padx = 20, 
                variable=gui, 
                value=1).grid(row=0, column=2)

    # Create radio buttons for local/online selection
    Label(startup, 
            text="""Play locally or online?""",
            justify = LEFT,
            padx = 20).grid(row=1, column=0)
    Radiobutton(startup, 
                text="Local",
                padx = 20, 
                variable=online, 
                value=0).grid(row=1, column=1)
    Radiobutton(startup, 
                text="Online (Facebook)",
                padx = 20, 
                variable=online, 
                value=FACEBOOK).grid(row=1, column=2)
    Radiobutton(startup, 
                text="Online (Discord)",
                padx = 20, 
                variable=online, 
                value=DISCORD).grid(row=1, column=3)

    Label(startup, text="Names of players (separate with a comma and a space)").grid(row=2)
    e1 = Entry(startup)

    e1.grid(row=2, column=1)

    Label(startup, text="Number of starting chips?").grid(row=3)
    e2 = Entry(startup)

    e2.grid(row=3, column=1)

    Label(startup, text="Small blind (big blind will be double the small blind)?").grid(row=4)
    e3 = Entry(startup)

    e3.grid(row=4, column=1)

    Button(startup, 
        text="Continue", 
        fg="red",
        command= lambda window=startup, : checkEntries(e1.get(), e2.get(), e3.get(), gui.get(), online.get(), window)).grid(row=5, column = 3)

    startup.mainloop()

def checkEntries(playerNames, chips, smallBlind, gui, online, window):
    """ Takes in names of players, starting chips, small blind, variables for gui and online modes, 
    and the startup window and performs error checking on the first three inputs before passing
    everything along to the next step depending on gui and online."""

    players = playerNames.split(", ")
    playLen = len(players)
    errorMessage = ""

    if playLen < 2:
        errorMessage += "Not enough players! Please provide more names.\n"

    elif playLen != len(set(players)):
        errorMessage += "Duplicate player names detected! Please remove duplicates.\n"

    try:
        if int(chips) < 2:
            errorMessage += "Not enough starting chips! Please choose a higher number of starting chips.\n"
    except:
        errorMessage += "Please enter a valid positive integer for starting chips.\n"

    try:
        if 2 * int(smallBlind) > int(chips):
            errorMessage += "Big blind cannot be greater than the amount of chips each player starts with.\n"
    except:
        errorMessage += "Please enter a valid positive integer for the small blind.\n"

    if errorMessage != "":
        showerror("Error!", errorMessage)

    else:    
        if online:
            findIds(players, chips, smallBlind, gui, online, window)

        else:
            startGame(players, int(chips), int(smallBlind), gui, online, window)

def findIds(players, chips, smallBlind, gui, online, window):
    # Stop the startup window
    window.destroy()

    # If facebook is being used, select profiles with tkinter windows
    if online == FACEBOOK:
        # Create a new window for selecting facebook profiles
        select = Tk()
        select.geometry("600x450")

        # Create a header label, a PokerBot instance and find possible profiles for the players
        Label(select, 
                text="""Select Online IDs for players""",
                justify = LEFT,
                padx = 20).pack()

        client = FBPokerBot(email = email, password = password)
        idSuggestions = client.findIds(players)

        # Create empty lists for dropdown StringVars
        selectedProfiles = []

        # Iterate through the idSuggestions and create dropdowns for each player
        for player in idSuggestions.keys():
            selectedProfile = StringVar()
            selectedProfiles += [selectedProfile]

            Label(select, 
                text=player,
                justify = LEFT,
                padx = 20).pack()

            dropdown = OptionMenu(select, selectedProfile, *idSuggestions[player])
            dropdown.pack()

        # Create a button to proceed when profiles have been selected
        Button(select, 
            text="Continue", 
            fg="red",
            command= lambda window=select, : startOnline(selectedProfiles, client, window)).pack(side = "bottom")

    elif online == DISCORD:
        # Initialize the poker table
        table = Table()

        # Get the players and blinds
        table.getPlayers(names = players, chips = int(chips))
        table.getBlinds(smallBlind = int(smallBlind))
        
        # Create a PokerBot instance. The bot will then find Ids and start the game
        client = DiscordPokerBot(token = TOKEN, channelId = channelId, names = players, table = table)

def startOnline(profiles, client, window):
    window.destroy()

    ids = list(map(lambda x: x.get()[-17:-3], profiles))

    # Create the top level window
    top = Tk()
    top.geometry("1200x450")

    # Start the game
    client.startGame(top, ids)

def startGame(players, chips, smallBlind, gui, online, window):
    """ Starts a local GUI game."""
    # Stop the startup window
    window.destroy()

    # Initialize the poker table
    table = LocalTable()

    # Get the players and blinds
    table.getPlayers(names=players, chips=chips)
    table.getBlinds(smallBlind=smallBlind)

    # Create the top level window
    top = Tk()
    top.geometry("1200x450")

    LocalApp(master=top, table=table)

    top.mainloop()

if __name__ == "__main__":
    main()