import tables
cu = tables.cu

class Select:
    def getAllPlayers(self):
        cu.execute("select id from players where location > 0")
        return cu.fetchall()
    
    def getAllPlayerNames(self):
        cu.execute("select name from players where location > 0")
        return cu.fetchall()
    
    def getAllPlayersInLoc(self, where):
        cu.execute("select id from players where location = ?", (where,))
        return cu.fetchall()
    
    def getPlayerInRoom(self, session, player):
        cu.execute("select id from players where name = ? and location = ?", (player, session.is_in))
        return cu.fetchone()
    
    def getPlayerDesc(self, session, player):
        cu.execute("select id,description,location,name from players \
            where name = ? and location = ?", (player, session.is_in))
        return cu.fetchone()
    
    def getItemsOnPlayer(self, session, item):
        cu.execute("select o.name, o.description from objects o, obj_instances oi where \
                    o.id = oi.o_id and o.name = ? and oi.owner = ?", (session.p_id, item))
        return cu.fetchone()
    
    def getItemsOnNpc(self, session, npc):
        cu.execute("select oi.o_id,o.id,o.name,oi.npc_owner \
                    from obj_instances oi,objects where oi.o_id = o.id\
                    and oi.npc_owner = ?", (npc,))
        return cu.fetchall()
    
    def getNpcInRoom(self, session, npc):
        cu.execute("select ni.id from npc_instances ni where ni.location = ? and \
                    ni.n_id = (select id from npcs where name = ?)", (session.is_in, npc)
        self.mob = cu.fetchone()
    
    def getItem(self, session, item):
        cu.execute("select id,o_id from obj_instances where location=? and owner is NULL and \
        o_id = (select id from objects where name = ?)", (int(session.is_in), item))
        return cu.fetchone()
    
    def getExit(self, session, exit):
        cu.execute("select origin, dest, exit from links where origin = ? and exit = ?", (session.is_in, exit))
        return cu.fetchone()
    
    def getHelp(self, command):
        cu.execute("select command, doc from helps where command = ?", (command,))
        return cu.fetchone()
    
    def getAllHelp(self):
        cu.execute("select command from helps")
        return cu.fetchall()
    
    def getInventory(self, session):
        cu.execute("select o.name from objects o, obj_instances oi where oi.owner = ? and o.id = oi.o_id", (session.p_id,))
        return cu.fetchall()
    
    def getRoomDesc(self, session):
        cu.execute("select s_desc,l_desc from rooms where id = ?", (session.is_in,))
        return cu.fetchone()
    
    def getRoom(self, rid):
        cu.execute("select id from rooms where id = ?", (rid,))
        return cu.fetchone()
        
    def getPlayersInRoom(self, session):
        cu.execute("select name from players where location = ?", (session.is_in,))
        return cu.fetchall()
    
    def getNpcsInRoom(self, session, named = None):
        if not named:
            cu.execute("select name from npcs where id in (select n_id from npc_instances where location = ?)", (session.is_in,))
            return cu.fetchall()
        else:
            cu.execute("select ni.id, npcs.name, npcs.description from npc_instances ni,npcs where \
                       npcs.id = ni.n_id and npcs.name = ? and ni.location = ?", (named, session.is_in))
            return cu.fetchone()
    
    def getItemsInRoom(self, session, named = None):
        if not named:
            cu.execute("select o.name,oi.o_id,count(*) from objects o,obj_instances oi where o.id = oi.o_id and oi.location = ?", (session.is_in,))
            return cu.fetchall()
        else:
            cu.execute("select o.name, o.description from objects o, obj_instances oi where \
                       o.id = oi.o_id and o.name = ? and oi.location = ?", (session.p_id, named, session.is_in))
            return cu.fetchone()
    
    def getExitsInRoom(self, session):
        cu.execute("select exit from links where origin = ?", (session.is_in,))
        return cu.fetchall()
    
    def getItemInstance(self, session, object):
        cu.execute("select oi.id, o.name from obj_instances oi, objects o \
                    where oi.owner = ? and o.name = ? and o.id = oi.o_id", (session.p_id, object))
        return cu.fetchone()
    
    def getBannedPlayers(self):
        cu.execute("select id, name from players where banned = 1")
        return cu.fetchall()
    
    def getAllRooms(self):
        cu.execute("select id, s_desc from rooms")
        return cu.fetchall()
    
    def getLink(self, id):
        cu.execute("select id from links where id = ?", (id, ))
        return cu.fetchonce()
    
    def getLocation(self):
        cu.execute("select id,name,location,ip_addr from players where location > 0")
        return cu.fetchall()
    
    def getAllItems(self):
        cu.execute("select id,name,description from objects")
        return cu.fetchall()
    
    def getItemNameId(self, item):
        cu.execute("select id, name from objects where id = ? or where name = ?", (item, item))
        return cu.fetchone()
    
    def getNpc(self, npc):
        cu.execute("select id,name from npcs where name = ?", (npc,))
        return cu.fetchone()
    
    def listObjectInstances(self):
        cu.execute("select id,o_id,owner,location from obj_instances")
        return cu.fetchall()
    
    
class Update:
    
    def setDescription(self, session, line):
        cu.execute("update players set description = ? where id = ?", (line, session.p_id))
        return cu.rowcount
        
    def setItemOwner(self, session, new_owner, obj_id):
        cu.execute("update obj_instances set owner = ?, location = NULL, npc_owner = NULL where id = ?", (new_owner, obj_id))
        return cu.rowcount

    def setItemNpcOwner(self, session, new_owner, obj_id):
        cu.execute("update obj_instances set npc_owner = ?, location = NULL, owner = NULL where id = ?", (new_owner, obj_id))
        return cu.rowcount
        
    def dropItem(self, session, obj_id):
        cu.execute("update obj_instances set owner = NULL, location = ?, npc_owner = NULL where id = ?", (session.is_in, obj_id))
        return cu.rowcount
        
    def setLocation(self, session, where):
        cu.execute("update players set location = ? where id = ?", (where, session.p_id))
        return cu.rowcount
        
    def setColors(self, session, color):
        cu.execute("update players set colors = ? where id = ?", (color, session.p_id))
        return cu.rowcount
        
    def banPlayer(self, player):
        cu.execute("update players set banned = 1 where name = ?", (player,))
        return cu.rowcount
        
    def unbanPlayer(self, player):
        cu.execute("update players set banned = 0 where name = ?", (player,))
        return cu.rowcount
        
    def setShortDesc(self, room, desc):
        cu.execute("update rooms set s_desc = ? where id = ?", (desc, room))
        return cu.rowcount

    def setShortDesc(self, room, desc):
        cu.execute("update rooms set l_desc = ? where id = ?", (desc, room))
        return cu.rowcount
        
    def setLocation(self, room, pid):
        cu.execute("update players set location = ? where id = ?", (room, p_id))
        return cu.rowcount
        
    def setItemDescription(self, item, desc):
        cu.execute("update objects set description = ? where name = ?", (desc, item))
        return cu.rowcount
    
    def setNpcDesc(self, npc, desc):
        cu.execute("update npcs set description = ? where id = ?", (desc, npc))
        return cu.rowcount
        
        
class Insert:
    
    def addRoom(self):
        cu.execute("insert into rooms(id, s_desc, l_desc) values (NULL,'A room','Set the description.')")
        return cu.lastrowid
    
    def addLink(self, orig, exit, dir):
        cu.execute("insert into links(id, origin, dest, exit) values (NULL, ?, ?, ?)", (orig, exit, dir))
        
    def addItem(self, name):
        cu.execute("insert into objects(id,name,description) values (NULL, ?, 'Set description')", (name,))
        return cu.lastrowid
    
    def addNpc(self, name):
        cu.execute("insert into npcs(id,name,description) values (NULL, ?, 'Set description.')", (name,))
        return cu.lastrowid
    
    def cloneItem(self, item, pid, time):
        cu.execute("insert into obj_instances(id,o_id,owner,creation) values (NULL, ?, ?,?)", (item, pid, time))
        
    def cloneNpc(self, npc, pid, item):
        cu.execute("insert into npc_instances(id,n_id,location,creation) values (NULL,?,?,?)", (npc, pid, item))
        
class Delete:
    
    def deleteRoom(self, id):
        cu.execute("delete from rooms where id = ?", (id,))
        return cu.rowcount

    def deleteLink(self, id):
        cu.execute("delete from links where origin = ? or dest = ?", (id,))
        return cu.rowcount
        
    def deleteLinkById(self, id):
        cu.execute("delete from links where id = ?", (id,))
        return cu.rowcount
        
    def deleteItem(self, item):
        cu.execute("delete from obj_instances where o_id = ?", (item,)
        cu.execute("delete from objects where id = ?", (item,))
        return cu.rowcount
                   
    def deleteObject(self, object):
        cu.execute("delete from obj_instances where id = ?", (object,))
        return cu.rowcount
    
    def deleteNpc(self, npc):
        cu.execute("delete from npcs where id = ?", (npc,))
        
    def deleteNpcInst(self, npc):
        cu.execute("delete from npc_instances where id = ?", (npc,))
        return cu.rowcount
    
    
    
        