import random
import math

name = "SPAM SQUAD"



T_GUNPOWDER = 800


class MakePirateDecision:

    def __init__(self, pirate):



        self.pirate = pirate
        self.x, self.y = self.pirate.getPosition()
        self.deploy_point = self.pirate.getDeployPoint()
        self.getTeamSignal = self.pirate.getTeamSignal
        self.setTeamSignal = self.pirate.setTeamSignal

        self.MAPX = self.pirate.getDimensionX()
        self.MAPY = self.pirate.getDimensionY()


        self.ISLANDS= {1: 'island1',
                        2: 'island2',
                        3: 'island3'}
        

        self.ATKDIVIDE = 4
        self.TARGET_X =  5
        self.YT_ISLAND = 1

        
        self.sendsignal()
        recieved_signal = self.recievesignal()

        self.total_pirates = recieved_signal['pirates']
        self.Y_ISLAND = min(int(self.total_pirates/25) + 2,6)

        self.gunpowder = self.pirate.getTotalGunpowder()
        self.P_GUNPOWDER = 100
        self.T_GUNPOWDER = T_GUNPOWDER


    def plan(self):

        """
        Priotity..

        refresh if needed..
        pirtae.getsignal command
        pirtae.getTeamsignal --> attack_x, attak_y
        self.checkisland..
        pirtae.getTeamsignal --> random move        
        
        """
        received_signal = self.recievesignal()
        torefresh = received_signal['refresh']

        if torefresh == 10:
            self.refresh()


        move = self.follow_pirate_signal()
        if move != "" : 
            return move


        while  1:

            # Game starting point.. Intialize a signal with empty values..
            received_signal = self.recievesignal()
            # print(received_signal)
            if received_signal == {} : 
                self.sendsignal()
                continue
            # print(received_signal)

            # Check if the island is nearby and take a planned move..
            island_move = self.check_island()
            if island_move != "" : 
                move =  island_move
                break

            # Attack if any coordinates is locked for attack (Particulary for islands)..
            attack_x, attack_y = received_signal['attack_x'], received_signal['attack_y']
            if type(attack_x) == int and type(attack_y) == int and random.randint(1,self.ATKDIVIDE) == 1:
                
                tomove = self.attack_coordinate(received_signal)
                if tomove:
                    move =  self.moveTo(attack_x, attack_y)
                    break

            # Check if the sufficient no. of pirates reach at the target corner location or not?        
            if (self.x,self.y) == self.get_cordinate_from_quad(received_signal['current']):
                self.sendsignal(count = received_signal['count'] + 1)
                
            received_signal = self.recievesignal()
            
            if received_signal['count'] < self.TARGET_X:
                move = self.moveTo(*self.get_cordinate_from_quad(received_signal['current']))    # Move to the target location..
                break

            else:  self.get_new_target(received_signal)


        return move
    

    def refresh(self):

        """Refresh all the things assocoated to the pirate/team/map.."""
        self.pirate.setSignal("")


    def planorder(self):
        """Check deploy point and tell the order for attack of pirates.."""

        return {1:"3241",
                2: "4132",
                3:"1423",
                4: "2314"}[self.deploy_quad()]

    

    def attack_coordinate(self, received_signal):
        
        """Check that island has min no. of pirates and if not only then attack.."""
        attack_i = received_signal['attack_i']
        if received_signal[f'i{attack_i}'] < self.Y_ISLAND and self.gunpowder >= self.T_GUNPOWDER:
            return True
        else:
            self.sendsignal(attack_x = "", attack_y = "", attack_i = 0)
            return False



    def recievesignal(self):

        """
        
        Get a dict of arguments present in team signal..
       
        """

        signal = self.getTeamSignal()

        if signal == "": 
            return {}

        order_current , s_count , s_i1, s_i2, s_i3,  s_attack_x , s_attack_y, s_attack_i, s_island1_x , s_island1_y, s_island2_x, s_island2_y, s_island3_x, s_island3_y, s_pirates , s_refresh  = signal.split(",")

        s_order = order_current[0:4]
        s_current = order_current[4]
        s_count = int(s_count)

        s_i1 , s_i2 , s_i3 = int(s_i1), int(s_i2), int(s_i3)

        if s_attack_x != "" and s_attack_y != "" :
            s_attack_x, s_attack_y = int(s_attack_x), int(s_attack_y)
            
        if s_attack_i != "" :
            s_attack_i = int(s_attack_i)
            
        if s_island1_x != "" and s_island1_y != "" :
            s_island1_x, s_island1_y= int(s_island1_x), int(s_island1_y)

        if s_island2_x != "" and s_island2_y != "" :
            s_island2_x, s_island2_y= int(s_island2_x), int(s_island2_y)
        
        if s_island3_x != "" and s_island3_y != "" :
            s_island3_x, s_island3_y= int(s_island3_x), int(s_island3_y)

        s_pirates = int(s_pirates)
        s_refresh = int(s_refresh)


        return {"order" : s_order, 
                "current": s_current,
                "count" : s_count,
                'i0': 100000000000,
                'i1': s_i1,
                'i2': s_i2,
                'i3': s_i3,
                'attack_x': s_attack_x,
                'attack_y': s_attack_y,
                'attack_i': s_attack_i,
                'island1_x': s_island1_x,
                'island1_y': s_island1_y,
                'island2_x': s_island2_x,
                'island2_y': s_island2_y,
                'island3_x': s_island3_x,
                'island3_y': s_island3_y,
                'pirates' : s_pirates,
                'refresh' : s_refresh}
    


    def sendsignal(self, current = None, count = None, i1 = None, i2= None , i3 = None, attack_x = None, attack_y = None, attack_i = None, island1_x = None, island1_y = None, island2_x = None, island2_y = None, island3_x = None, island3_y = None, pirates = None, refresh = None):

        """
        Set signal through this function
        Only pass those arguments which you want to change..

        Format --> "order(4)current(1),count(2),i1(1),i2(1),i3(1),attack_x(2),attack_y(2),attack_i(1),island1_x(2),island1_y(2),island2_x(2),island2_y(2),island3_x(2),island3_y(2),pirates(2),refresh(1)"

        """

        old_signal = self.recievesignal()

        if old_signal == {}:

            order = self.planorder()
            current = order[0]

            i1 = i2 = i3 = 0
            attack_x = attack_y = ""
            attack_i = 0 
            island1_x = island1_y = island2_x = island2_y = island3_x = island3_y = ""

            pirates = 0
            refresh = 0

            signal = f"{order}{current},{0},{i1},{i2},{i3},{attack_x},{attack_y},{attack_i},{island1_x},{island1_y},{island2_x},{island2_y},{island3_x},{island3_y},{pirates},{refresh}"

        else:

            s_current, s_count, s_i1, s_i2, s_i3 , s_attack_x , s_attack_y, s_attack_i, s_island1_x , s_island1_y, s_island2_x, s_island2_y, s_island3_x, s_island3_y , s_pirates , s_refresh = old_signal['current'], old_signal['count'], old_signal['i1'], old_signal['i2'], old_signal['i3'] , old_signal['attack_x'], old_signal['attack_y'], old_signal['attack_i'] , old_signal['island1_x'], old_signal['island1_y'] , old_signal['island2_x'] , old_signal['island2_y'], old_signal['island3_x'], old_signal['island3_y'], old_signal['pirates'] , old_signal['refresh']

            if current: 
                s_current = current
                s_count = 0

            if count: s_count = count

            if type(i1) == int: s_i1 = i1 
            if type(i2) == int: s_i2 = i2 
            if type(i3) == int: s_i3 = i3

            if (type(attack_x) in (int,str)): s_attack_x = attack_x 
            if (type(attack_y) in (int,str)): s_attack_y = attack_y 
            if (type(attack_i) in (int,str)): s_attack_i = attack_i 
            
            
            if (type(island1_x) == int): s_island1_x = island1_x 
            if (type(island1_y) == int): s_island1_y = island1_y 
            if (type(island2_x) == int): s_island2_x = island2_x 
            if (type(island2_y) == int): s_island2_y = island2_y 
            if (type(island3_x) == int): s_island3_x = island3_x 
            if (type(island3_y) == int): s_island3_y = island3_y 

            if (type(pirates) == int): s_pirates = pirates
            if (type(refresh) == int): s_refresh = refresh


            signal = f"{old_signal['order']}{s_current},{s_count},{s_i1},{s_i2},{s_i3},{s_attack_x},{s_attack_y},{s_attack_i},{s_island1_x},{s_island1_y},{s_island2_x},{s_island2_y},{s_island3_x},{s_island3_y},{s_pirates},{s_refresh}"
       
        self.setTeamSignal(signal)            
        

    def deploy_quad(self):

        quads = {(0,0): 1,
                     (self.MAPX-1,0): 2,
                     (self.MAPX-1,self.MAPY-1): 3,
                     (0,self.MAPY-1): 4
                     }
                    
        return quads[self.deploy_point]
    
    
    def get_cordinate_from_quad(self, quad):
        
        return {"1": (0,0),
                "2":(self.MAPX-1,0),
                "3":(self.MAPX-1,self.MAPY-1),
                "4":(0,self.MAPY-1)}[quad]
    
    def get_new_target(self, received_signal):

        """
        Example - 3241

        """

        current = received_signal['current']
        order = received_signal['order']

        index = order.index(current)
        if index <= 2:
            index+=1 
        else:
            index = 0

        self.sendsignal(current = order[index]) 


    def moveTo(self,x, y):

        """This function aims to move all the pirates to a single location.. 
        Basically it will retrun direction in which pirate should move to achieve that coordinate.."""

        position = self.pirate.getPosition()
        if position[0] == x and position[1] == y:
            return 0
        if position[0] == x:
            return (position[1] < y) * 2 + 1
        if position[1] == y:
            return (position[0] > x) * 2 + 2
        if random.randint(1, 2) == 1:
            return (position[0] > x) * 2 + 2
        else:
            return (position[1] < y) * 2 + 1
        

    def islandmoves(self, island):

        possible_moves = []
        
        up , down , left , right = self.pirate.investigate_up(), self.pirate.investigate_down(), self.pirate.investigate_left(), self.pirate.investigate_right()

        if up[0] == island:
            possible_moves.append(1)
        if left[0] == island:
            possible_moves.append(4)
        if down[0] == island:
            possible_moves.append(3)
        if right[0] == island:
            possible_moves.append(2)

        if possible_moves == []:
            possible_moves.append(0)

        return possible_moves

        

    def follow_pirate_signal(self):

        """ This function basically aims to place the pirate to the coorect positon in the island...
        
            Signal format - "{n/y}{island_no}{move1}{move2}{move3}{stop-0}"
        
        """
        
        # Try to find coordinates of died pirate..


        signal = self.pirate.getSignal()
        recieved_signal = self.recievesignal()

        if signal:
            # print((self.pirate.getID(),signal))
            if signal[0] == "y":

                move = signal[2]
                if move != "0":
                    signal = "y" + signal[1] + signal[3:]
                    self.pirate.setSignal(signal)

                else:
                    # Think here..
                    # Move the pirte on each of the tiles of the island.. 
                    # But only when sufficient pirate and gunpowder is available..\

                    if self.gunpowder >= self.P_GUNPOWDER and recieved_signal[f"i{signal[1]}"] > self.YT_ISLAND:
                        move = random.choice(self.islandmoves(f'island{signal[1]}'))
                    
                return int(move)
            
            else:

                current = self.pirate.investigate_current()[0]
                if current != f'island{signal[1]}':
                    move = int(signal[2])
                    return move
                
                else:

                    # Check for max no. of pirates on island..

                    attack_i = signal[1]
                    if recieved_signal[f'i{attack_i}'] > self.Y_ISLAND:
                        self.pirate.setSignal("")
                        return ""
                

                    self.sendsignal(**{f'i{signal[1]}' : recieved_signal[f'i{signal[1]}'] + 1})
                    move = signal[3]
                    
                    remaining_moves = ""
                    if len(signal) > 4: remaining_moves = signal[3:]
                    elif signal[3] == "0": remaining_moves = "0"   
                    
                    signal = "y" + signal[1] + remaining_moves
                    self.pirate.setSignal(signal)

                    return move


        else : return ""



    def check_island_tile(self, number , island , tile1,tile2, signal1, signal2, signal3, attack_1, attack_2, attack_3 , recieved_signal):

        
        # Three cases.. 


        if tile1[0] == island and tile2[0] == island: 
            signal = signal1
           
            if number == 1: self.sendsignal(island1_x=  attack_1[0], island1_y= attack_1[1]) 
            if number == 2: self.sendsignal(attack_i = 2,island2_x=  attack_1[0], island2_y= attack_1[1]) 
            if number == 3: self.sendsignal(island3_x=  attack_1[0], island3_y= attack_1[1]) 

            if self.gunpowder >= self.T_GUNPOWDER:
                self.sendsignal(attack_x = attack_1[0], attack_y = attack_1[1], attack_i = number)

        elif tile1[0] == island: 
            signal = signal2

            if number == 1: self.sendsignal(island1_x=  attack_2[0], island1_y= attack_2[1]) 
            if number == 2: self.sendsignal(island2_x=  attack_2[0], island2_y= attack_2[1]) 
            if number == 3: self.sendsignal(island3_x=  attack_2[0], island3_y= attack_2[1]) 

            if self.gunpowder >= self.T_GUNPOWDER:
                self.sendsignal(attack_x = attack_2[0], attack_y = attack_2[1], attack_i = number)
        
        elif tile2[0] == island: 
            signal = signal3

            if number == 1: self.sendsignal(island1_x=  attack_3[0], island1_y= attack_3[1]) 
            if number == 2: self.sendsignal(island2_x=  attack_3[0], island2_y= attack_3[1]) 
            if number == 3: self.sendsignal(island3_x=  attack_3[0], island3_y= attack_3[1]) 

            if self.gunpowder >= self.T_GUNPOWDER:
                self.sendsignal(attack_x = attack_3[0], attack_y = attack_3[1], attack_i = number)

            

        signal = f"n{number}{signal}"
        
        # Check for gunpowder..
        # if self.gunpowder >= self.T_GUNPOWDER:
        # print((self.pirate.getID(),signal))
        self.pirate.setSignal(signal)         # Signal to pirate to follow remaining moves..
        



    def check_island(self):

        current , up , down , left , right , nw , ne , sw , se = self.pirate.investigate_current(), self.pirate.investigate_up(), self.pirate.investigate_down(), self.pirate.investigate_left(), self.pirate.investigate_right(), self.pirate.investigate_nw(), self.pirate.investigate_ne(), self.pirate.investigate_sw(), self.pirate.investigate_se()

        if current[0] != 'blank': 
            return ""

        recieved_signal = self.recievesignal()

        if up[0] != 'blank' and up[0] != 'wall':

            for number , island in self.ISLANDS.items():
               
                if up[0] == island and recieved_signal[f'i{number}'] < self.Y_ISLAND:
                    
                    self.check_island_tile(number , island, ne, nw, "10", "120", "140", (self.x + 2, self.y - 2), (self.x + 2, self.y - 2) , (self.x + 1, self.y - 2), recieved_signal) 
                    
                    return 1              # Move up...
                
        if left[0] != 'blank' and left[0] != 'wall':

            for number , island in self.ISLANDS.items():
               
                if left[0] == island and recieved_signal[f'i{number}'] < self.Y_ISLAND:
                    
                    self.check_island_tile(number , island, sw, nw, "40", "430", "410", (self.x - 2, self.y - 2), (self.x - 2, self.y - 1) , (self.x - 2 , self.y - 3), recieved_signal) 
                    
                    return 4              # Move left...
                
        if down[0] != 'blank' and down[0] != 'wall':

            for number , island in self.ISLANDS.items():
               
                if down[0] == island and recieved_signal[f'i{number}'] < self.Y_ISLAND:
                    
                    self.check_island_tile(number , island, se , sw, "30", "320", "340", (self.x - 2, self.y + 2), (self.x - 1, self.y + 2) , (self.x - 3 , self.y + 2), recieved_signal) 
                    
                    return 3              # Move down...
                
        if right[0] != 'blank' and right[0] != 'wall':

            for number , island in self.ISLANDS.items():
               
                if right[0] == island and recieved_signal[f'i{number}'] < self.Y_ISLAND:
                    
                    self.check_island_tile(number , island, ne , se, "20", "210", "230", (self.x + 2, self.y + 2), (self.x + 2, self.y + 1) , (self.x + 2, self.y + 3), recieved_signal) 
                    
                    return 2              # Move right...
                

        if nw[0] != 'blank' and nw[0] != 'wall':

            for number , island in self.ISLANDS.items():
               
                if nw[0] == island and recieved_signal[f'i{number}'] < self.Y_ISLAND:
                    return 1           # Move up...

        if ne[0] != 'blank' and ne[0] != 'wall':

            for number , island in self.ISLANDS.items():
               
                if ne[0] == island and recieved_signal[f'i{number}'] < self.Y_ISLAND:
                    return 1           # Move up...

        if sw[0] != 'blank' and sw[0] != 'wall':

            for number , island in self.ISLANDS.items():
               
                if sw[0] == island and recieved_signal[f'i{number}'] < self.Y_ISLAND:
                    return 3           # Move down...

        if se[0] != 'blank' and se[0] != 'wall':

            for number , island in self.ISLANDS.items():
               
                if se[0] == island and recieved_signal[f'i{number}'] < self.Y_ISLAND:
                    return 3           # Move down...
                
        return ""
                


class MakeTeamDecision(MakePirateDecision):

    def __init__(self, team):

        self.team = team
        self.getTeamSignal = self.team.getTeamSignal
        self.deploy_point = self.team.getDeployPoint()
        self.setTeamSignal = self.team.setTeamSignal

        
        self.MAPX = self.team.getDimensionX()
        self.MAPY = self.team.getDimensionY()

        self.TARGET_X =  5
        self.ISLANDS= {1: 'island1',
                        2: 'island2',
                        3: 'island3'}
        

        self.gunpowder = self.team.getTotalGunpowder()
        self.T_GUNPOWDER = T_GUNPOWDER

        self.sendsignal()
        self.sendsignal(pirates= int(self.team.getTotalPirates()))
       
        self.Y_ISLAND = min(int(self.team.getTotalPirates()/25) + 2,6)

        self.track_list = self.team.trackPlayers()
        self.capturelist = self.trackisland(self.track_list)

        self.T1_WALL = 0
        self.T2_WALL = 0
        self.wall = self.team.getTotalWood()



    def update_pirate_counts(self):

        counts = {'i1':0, 'i2':0, 'i3':0}

        for signal in self.team.getListOfSignals() :
            
            # Signal format - "{n/y}{island_no}{move1}{move2}{move3}{stop-0}"

            if signal and signal[0] == "y":

                island_number = int(signal[1])
                counts[f'i{island_number}'] += 1

        self.sendsignal(**counts) 


    def trackisland(self, current_list):

        island_capture = []
        actual = []


        for i in current_list[:3]:

            actual.append(i)

            if i == '':
                island_capture.append(0)
            else:
                island_capture.append(1)

        return island_capture
    

    def make_wall(self):

        if int(self.team.getCurrentFrame()) < (int(self.MAPX)*1.41):
            return

        my_captures = self.track_list[0:3]
        recieved_signal = self.recievesignal()

        for i in range(len(my_captures)):
            if my_captures[i] == 'myCapturing' and self.wall >= self.T1_WALL :

                if recieved_signal[f"i{i+1}"] >= self.Y_ISLAND or self.gunpowder < self.T_GUNPOWDER:
                    self.team.buildWalls(i+1)
                

        for i in range(len(my_captures)):
            if my_captures[i] == 'myCaptured' and self.wall >= self.T2_WALL :
                self.team.buildWalls(i+1)


    def check_refresh(self):
        
        """
        0 --> nothing
        10 --> refresh mode on but not refreshed
        11 - refreshed, don't refresh again..        
        """

        recieved_signal = self.recievesignal()

        if (self.team.getCurrentFrame() >=  2500):

            if recieved_signal['refresh'] == 11:
                return
            elif recieved_signal['refresh'] == 10:
                self.sendsignal(refresh = 11)
                return
            
            # Refresh the map..

            count = 0

            for i in self.capturelist:
                if i == 1:
                    count += 1
            if count > 1:
                return 
            self.sendsignal(refresh = 10)              # 10 --> Refresh
            return

        
        

    def plan(self):
        
        self.make_wall()

        self.update_pirate_counts()
        recieved_signal = self.recievesignal()

        for i in range(len(self.capturelist)):

            if self.capturelist[i] == 0:
                island_x, island_y = recieved_signal[f"island{i+1}_x"], recieved_signal[f"island{i+1}_y"]
                if island_x != "" and island_y != ""  and self.gunpowder >= self.T_GUNPOWDER:
                    self.sendsignal(attack_x = island_x, attack_y = island_y, attack_i = i + 1)
                    break

        self.check_refresh()



def ActPirate(pirate):

    # Try avoiding error - use try except block..
    try:
        decision_maker = MakePirateDecision(pirate)
        move = decision_maker.plan()
        return move
    except Exception:
        return random.randint(0,4)



def ActTeam(team):
    
    # Try avoiding error - use try except block..
    try:
        decision_maker = MakeTeamDecision(team) 
        decision_maker.plan()
    except Exception:
        pass