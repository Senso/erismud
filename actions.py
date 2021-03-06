import tables, ConfigParser
from model import Select, Update
from common import C
import template as tpl

#cu = tables.cu

Update = Update()
Select = Select()

config = ConfigParser.ConfigParser()
config.read("eris.conf")

class Actions():

    def __init__(self, sessions):
        self.sessions = sessions
        global Effects
        Effects = EffectsC(self.sessions)

    def do_chat(self, session, line):
        c = C(session)
        self.everybody = Select.getAllPlayers()
        self.talker = c.B_WHITE(session.pname)
        for i in self.everybody:
            self.listen = self.sessions.get(i[0])
            if self.listen == None:
                pass
            else:
                self.lbracket = c.B_GREEN("[")
                self.rbracket = c.B_GREEN("]")
                self.listen.push("%s%s%s %s" % (self.lbracket, self.talker, self.rbracket, line))

    def do_description(self, session, line):
        Update.setDescription(session.p_id, line)
        session.push(tpl.DESC_SET)

    def do_drop(self, session, line):
        try:
            self.drop = Select.getItemInstance(session.p_id, line.lower())

            self.drop = Update.dropItem(session.is_in, self.drop[0])
            #self.msg = session.pname + " dropped " + line + "."
            #self.RoomBroadcast(session, session.is_in, self.msg)
            session.push(tpl.DROP % (session.pname, line))
        except: session.push(tpl.DROP_CANT)

    def do_emote(self, session, line):
        if line == '' : session.push(tpl.EMOTE_DEFAULT)
        else:
            self.emote = ">" + line + "<"
            Effects.RoomBroadcast(session, session.is_in, self.emote)
            session.push(tpl.EMOTE % (session.pname, self.emote))

    def do_get(self, session, line):
        self.objonfloor = Select.getItem(session.is_in, line.lower())

        try:
            Update.setItemOwner(session.p_id, self.objonfloor[0])
            session.push(tpl.GET % line)
        except:
            session.push(tpl.NOT_HERE)

    def do_give(self, session, line):
        if not line: session.push(tpl.SYNTAX_GIVE)
        else:
            self.argu = line.lower()
            #if not self.argu.strip(): session.push("> ")
            self.parts = line.split(' ', 3)

            if self.parts[1] == "to":
                try:
                    self.itom = Select.getItemInstance(session.p_id, self.parts[0].lower()) # Given item info

                    # Check if given to a player.
                    self.transf = Select.getPlayerInRoom(session.is_in, self.parts[2].lower())

                    # Check if given to a mob.
                    self.mob = Select.getNpcInRoom(session.is_in, self.parts[2].lower())

                    if self.transf:
                        Update.setItemOwner(self.transf[0], self.itom[0])
                        session.push(tpl.GIVE % (self.parts[0],self.parts[2]))
                        # the following line is commented out -- not sure if I'll tell the whole room + it doesn't work
                        #self.RoomBroadcast(session, session.is_in, " gives %s to %s" % (self.parts[0],self.parts[2]))
                        
                    elif self.mob:
                        Update.setItemNpcOwner(self.mob[0], self.itom[0])
                        session.push(tpl.GIVE % (self.parts[0],self.parts[2]))
                        #Effects.RoomBroadcast(session, session.is_in, " gives %s to %s" % (self.parts[0], self.parts[2]))
                    else: session.push(tpl.PLAYER_NOT_FOUND)

                except: session.push(tpl.SYNTAX_GIVE)

            else: session.push(tpl.SYNTAX_GIVE)

    def do_go(self, session, line):
        if not line: session.push(tpl.DONT_GO)
        else:
            try:
                self.isexit = Select.getExit(session.is_in, line.lower())
            except:
                session.push(tpl.NO_EXIT)

            try:
                # Actually move
                Update.setLocation(session.p_id , self.isexit[1])
                #Effects.RoomBroadcast(session, session.is_in, " leaves %s." % str(self.isexit[2]))
                session.is_in = self.isexit[1]
                #Effects.RoomBroadcast(session, session.is_in, " enters the room.")
                self.do_look(session, '') # Force a look, to be replaced by something nicer.

            except:
                session.push(tpl.CANT_MOVE)

    def do_help(self, session, line):
        if not line: # help command alone
            self.allh = Select.getAllHelp()
            self.allhelp = []
            for i in self.allh:
                self.allhelp.append(i[0])

            self.allhelp.sort()
            self.counter = 0
            for i in self.allhelp:
                self.counter += 1

            #Make 2 columns of help files
            self.counter = self.counter / 2
            self.counter = int(self.counter)
            self.first = self.allhelp[:self.counter]
            self.second = self.allhelp[self.counter:]
            session.push(tpl.HELP_TOPICS)
            for x, y in map(None, self.first, self.second):
                if x == None:
                    x = ' '
                    session.push(str(x).ljust(15) + str(y).ljust(10) + "\r\n")
                else: session.push(str(x).ljust(15) + str(y).ljust(10) + "\r\n")

        else: #If help <foo>
            try:
                self.helper = Select.getHelp(command)
                session.push("Help for %s: \r\n" % (line,))
                self.docu = self.helper[1].split('\\n')
                for i in self.docu:
                    session.push("%s \r\n" % (i,))
                session.push("\r\n")
            except:
                session.push(tpl.NO_HELP)

    def do_inv(self, session, line):
        c = C(session)

        self.owned = Select.getInventory(session.p_id)
        self.owned = c.flatten(self.owned)
        session.push(c.B_WHITE(tpl.INVENTORY))

        self.stufa = {}
        for i in self.owned:
            self.stufa[i] = self.owned.count(i)

        for i in self.stufa:
            if self.stufa[i] > 1:
                c.B_GREEN(str(i))
                session.push("%s (%s)\r\n" % (c.B_GREEN(str(i)),str(self.stufa[i])))
            else:
                session.push("%s\r\n" % (c.B_GREEN(str(i)),))

    def do_look(self, session, line):
        c = C(session)
        if not line: # Looking at the room itself
            self.descr = Select.getRoomDesc(session.is_in)
            session.push("%s \r\n" % (c.CYAN(self.descr[0]),))                  # short desc
            session.push("%s \r\n" % self.descr[1].replace('\\n', '\r\n'))      # long desc

            # Players in the room.
            self.look_com = Select.getPlayersInRoom(session.is_in)
            session.push("%s %s" % (session.BOLD, session.RED))
            for i in self.look_com:
                if str(i[0].capitalize()) == session.pname: pass
                else: session.push("%s \r\n" % str(i[0].capitalize()))
            session.push("%s" % session.RESET)

            #Get list of NPCs in the room.
            self.mobonfloor = Select.getNpcsInRoom(session.is_in)

            #Get list of objects in the room.
            self.objonfloor = Select.getItemsInRoom(session.is_in, session.p_id)

            if self.mobonfloor != []:
                for i in self.mobonfloor:
                    session.push("%s%s%s %s\r\n" % (session.BOLD, session.MAGENTA, str(i[0]), session.RESET))

            if self.objonfloor != []:
                comma = False
                for i in self.objonfloor:
                    if not i[0] or not i[1]: pass
                    elif i[2] > 1:
                        if comma:
                            session.push(", ")
                        session.push("%s%s%s%s (%s)" % (session.BOLD,session.GREEN,str(i[0]),session.RESET,str(i[2])))
                        comma = True
                    else:
                        if comma:
                            session.push(", ")
                        session.push("%s%s%s%s" % (session.BOLD,session.GREEN,str(i[0]),session.RESET))
                        comma = True
                session.push("\r\n")

            # List exits
            session.push("%s%s%s " % (session.BOLD,session.CYAN, tpl.EXITS))
            self.tmpgoto = Select.getExitsInRoom(session.is_in)
            for i in self.tmpgoto:
                session.push("%s " % i[0])
            session.push("%s\r\n" % session.RESET)

        else: # Looking at something specific
            #Check if looked-at player is there
            self.peeps = Select.getPlayerDesc(session.is_in, line.lower())

            #Get list of items possessed by player or in the room
            self.obj = Select.getItemsOnPlayer(session.p_id, line.lower())
            
            #Get list of items in the room
            self.obj2 = Select.getItemsInRoom(session.is_in, session.p_id, line.lower())

            #Get list of mobs in the room.
            self.mobonfloor = Select.getNpcsInRoom(session.is_in, line.lower())

            try:
                if self.peeps: #Looking at a player
                    session.push("%s \r\n" % self.peeps[1].replace('\\n', '\r\n'))
                    #Effects.RoomBroadcast(session, session.is_in,tpl.LOOKS_AT + line)

                elif self.obj: #An object in your inventory
                    session.push("%s \r\n" % self.obj[1].replace('\\n', '\r\n'))
                    
                elif self.obj2: #An object on the floor
                    session.push("%s \r\n" % self.obj2[1].replace('\\n', '\r\n'))

                elif self.mobonfloor: #A mob/NPC
                    self.mobinv = Select.getItemsOnNpc(self.mobonfloor[0])
                    
                    self.descri = self.mobonfloor[2].split('\\n') # Print the description
                    for i in self.descri:
                        session.push(str(i) + "\r\n")

                    if self.mobinv: # Print the mob's inventory
                        self.stuff = []
                        self.stufa = {}
                        session.push(c.B_WHITE(tpl.INVENTORY))

                        for i in self.mobinv:
                            self.item_name = i[2]
                            self.stuff.append(item_name)
                            self.stufa[self.item_name] = self.stuff.count(self.item_name)
                        for i in self.stufa:
                            if self.stufa[i] > 1:
                                session.push("%s (%s)\r\n" % (str(i), str(self.stufa[i])))
                            else:
                                session.push("%s \r\n" % str(i))
                    else: pass

                else: session.push(tpl.CANT_SEE)

            except: session.push(tpl.CANT_SEE)

    def do_say(self, session, line):
        if not line: pass
        session.push(tpl.YOU_SAY % line)
        Effects.RoomBroadcast(session, session.is_in, tpl.SAYS % line)

    def do_setansi(self, session, arg):
        if arg == "on":
            session.BLACK, session.RED, session.GREEN = '\033[30m', '\033[31m', '\033[32m'
            session.YELLOW, session.BLUE, session.MAGENTA = '\033[33m', '\033[34m', '\033[35m'
            session.CYAN, session.WHITE = '\033[36m', '\033[37m'
            session.RESET, session.BOLD = '\033[0;0m', '\033[1m'
            Update.setColors(session.p_id, arg)
        elif arg == "off": # Empty strings.
            session.BLACK, session.RED, session.GREEN, session.YELLOW, session.BLUE = '','','','',''
            session.MAGENTA, session.CYAN, session.WHITE, session.RESET, session.BOLD = '','','','',''
            Update.setColors(session.p_id, arg)
        else: session.push("Syntax:\r\nsetansi [off|on]\r\n")

    # def do_skills(self, session, line):
        # cu.execute("select * from skills where p_id = ?", (session.p_id,))
        # self.ski = cu.fetchone()
        # session.push("Your skills are:\r\n")
        # session.push("Loiter: "+str(self.ski[1])+"\r\n"+
                    # "Whistle: "+str(self.ski[2])+"\r\n"+
                    # "Spam: "+str(self.ski[2])+"\r\n")

    # def do_stats(self, session, line):
        # cu.execute("select names,str,stm,dex,agl,int,wil,prs,per,app from pnames where p_id = ?", [session.p_id])
        # self.stats = cu.fetchone()
        # session.push(session.BOLD+session.WHITE+"Stats for " + str(self.stats[0].capitalize()) +session.RESET+"\r\n")
        # session.push("STR: " + str(self.stats[1]) + "\r\n")
        # session.push("STM: " + str(self.stats[2]) + "\r\n")
        # session.push("DEX: " + str(self.stats[3]) + "\r\n")
        # session.push("AGL: " + str(self.stats[4]) + "\r\n")
        # session.push("INT: " + str(self.stats[5]) + "\r\n")
        # session.push("WIL: " + str(self.stats[6]) + "\r\n")
        # session.push("PRS: " + str(self.stats[7]) + "\r\n")
        # session.push("PER: " + str(self.stats[8]) + "\r\n")
        # session.push("APP: " + str(self.stats[9]) + "\r\n")

    def do_who(self, session, line):
        c = C(session)
        session.push("The following players are logged on:\r\n")
        self.whoin = Select.getAllPlayerNames()
        for i in self.whoin:
            session.push("%s\r\n" % (c.B_RED(i[0].capitalize()),))
        session.push("\r\n")

    # Shortcuts
    def do_n(self, session, line): self.do_go(session, 'north')
    def do_s(self, session, line): self.do_go(session, 'south')
    def do_w(self, session, line): self.do_go(session, 'west')
    def do_e(self, session, line): self.do_go(session, 'east')
    def do_u(self, session, line): self.do_go(session, 'up')
    def do_d(self, session, line): self.do_go(session, 'down')
    def do_se(self, session, line): self.do_go(session, 'southeast')
    def do_sw(self, session, line): self.do_go(session, 'southwest')
    def do_nw(self, session, line): self.do_go(session, 'northwest')
    def do_ne(self, session, line): self.do_go(session, 'northeast')
    do_north = do_n
    do_south = do_s
    do_west = do_w
    do_east = do_e
    do_up = do_u
    do_down = do_d
    do_i = do_inv
    do_l = do_look
    
    
class EffectsC:

    def __init__(self, sessions):
        self.sessions = sessions

    def RoomBroadcast(self, session, inroom, line):
        "By calling this method, 'line' is sent to all players in 'inroom'."
        c = C(session)

        self.local = Select.getAllPlayersInLoc(inroom)
        self.pnamer = c.B_WHITE(session.pname)
        if not line:
            pass
        else:
            for i in self.local:
                self.tmpses = self.sessions.get(i[0]) # sessions dict
                if not self.tmpses: # Player is not logged in
                    pass
                elif self.tmpses.p_id == session.p_id: # Is the player
                    pass
                else:
                    self.tmpses.push("%s %s\r\n" % (self.pnamer,line))


