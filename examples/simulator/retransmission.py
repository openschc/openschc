from __future__ import division
import math
import numpy as np
import random
import time


#first value of the bakcoff interval for retransmission, in s.
cw_min = 2
#Frame ToA in seconds
T = 0.104
#Fragment ToA in seconds
Tfrag = 0.05
#Duty cycle of 1%: if you send during 1 unit, you need to wait for 99
sleep = 100 #99
#Number of fragments per data packet
n_frag = 3
#Frequency at which a large packets (that need fragmentation) are generated, in seconds
freq = 120 # 120
#Nombre de trames
generation = 10000
G = 0.3
g = G/T

count = 0
collision = 0
somme = 0
count_packet_will_be_fragmented = 0
#Count the number of fragments of a packet we are sending
count_frag = 0
#Count the number of successfull packet transmission when it was fragmented (all fragments made it)
count_frag_success = 0
#Count the delay from the sending of the first fragment to the last for successfull transmission
time_fragment = []
#Index of the first time the first fragment was sent
time_first_fragment = 0

random.seed()

#tableau is the list of the interval of time between the beginning of each frame
tableau_temp = np.random.exponential((1/g), generation)
'''
rien = 0.0
tableau_temp = []
for i in range(100):
    rien += i
    tableau_temp.append(rien)
'''
#We build a table that contains
# [0] the time interval between the previous frame and the current one
# [1] the number of retransmission. 0 means never been transmitted
# [2] type of frame : 0 is normal and 1 is a fragment
tableau = []
local_somme = 0
#One way of filling the table
#for i in range(len(tableau_temp)):
#    j=i
#    while j < len(tableau_temp) and local_somme + tableau_temp[j] > freq:
#        #print("Yes new fragment :" + str(local_somme) + " and next interval = " + str(tableau_temp[j]))
#        count_packet_will_be_fragmented += 1
#        tableau.append((freq-local_somme, 0, 1))
#        local_somme = 0
#        j+=1
#    local_somme += tableau_temp[i]
#    tableau.append((tableau_temp[i], 0, 0))

#Another way to fill the table, by inserting all fragment of a packet:
for i in range(len(tableau_temp)):
    tableau.append((tableau_temp[i], 0, 0))

def insert(position, temps, retrans, isFrag):
    global tableau
    local_somme = 0
    #print("insert dans " + str(temps))
    #print("A new insert - position=" + str(position) + " et temps = " + str(temps))
    while position<len(tableau) and local_somme < temps:
        local_somme += tableau[position][0]
        position+=1
        #print(local_somme)
    #print("finish the while - position=" + str(position) + " et i-1 = " + str(tableau[position-1][0]) + " et i = " + str(tableau[position][0]) + " et somme = " + str(local_somme))
    position-=1
    if position<len(tableau)-1:
        #if isFrag == 0 :
        #    print("I insert a retransmission")
        #else:
        #    print("I can add one fragment")
        time1 = temps-(local_somme-tableau[position][0])
        time2 = local_somme - temps
        #print("local_somme = " + str(local_somme))
        #print("time1 = " + str(time1))
        #print("time2 = " + str(time2))
        tableau.insert(position, (time1, retrans, isFrag))
        tableau[position+1] = (time2, tableau[position+1][1], tableau[position+1][2])
    else:
        #print("We reached the size of the table")
        return -1
    return position+1

i = 0
j = 0 #count the number of fragment
m = 0
cond=True
while cond:
    #print("tour, i = " + str(i))
    i = insert(m, freq, 0, 1)
    m = i
    j=1
    if i > 0 :
        count_packet_will_be_fragmented+=1
        while j < n_frag:
            i = insert(i, sleep*Tfrag, 0, 1)
            if i < 0:
                j = n_frag
                count_packet_will_be_fragmented-=1
                cond = False
            j+=1
    else :
        #print("We reached the end of the table")
        cond = False


#for i in range(len(tableau)):
#    print(tableau[i])
#    print(tableau[i][2])

def print_table(i, end):
    global tableau
    global n_frag
    print("")
    total = 0
    n = 0
    while i < len(tableau) and i < end:
        total += tableau[i][0]
        print("i = " + str(i) + "\t" + str(tableau[i][0]) + "\t total = " + str(total) + "\t retrans = " + str(tableau[i][1]))
        if tableau[i][2] == 1:
            if n == 0:
                print(str(total) +  ": Debut d'un fragment")
            else : print(str(total) + ": Fragment i")
            n+=1
        #total = tableau[i][0]
            if n == n_frag:
                n = 0
        i+=1
    print("")

#time.sleep(10)

def backoff(retrans):
    global cw_min
    #later_ms = random.randrange(0, cw_min**(retrans + 1))
    later = random.uniform(0, cw_min**(retrans + 1))
    #print("In backoff, retrans = " + str(retrans) + " et borne sup : " + str(cw_min**(retrans + 1)) + " et random = " + str(later_ms))
    #later = later_ms / 1000 #to have it in s as the rest of the code.
    later += T #TODO: why I did that?
    #print(later)
    return later

#i is the index in the table of the frame that needs to be rescheduled for a later transmission
def schedule(i):
    global tableau
    #("Schedule")
    #we compute the time at which the retransmission will happen, ie. the ToA of the first attempt + the random time.
    retransmission = tableau[i][1]
    #print("retransmission : " + str(retransmission))
    later = backoff(retransmission)

    #Actually, we already waited tableau[i], we are intersted with the next delay
    if i>=len(tableau)-1: #Hope it is not > :)
        tableau.append((later, retransmission+1, tableau[i][2]))
    else :

        type_paquet = tableau[i][2]
        #debug
        #print("Later = " + str(later))
        #temp = 0
        #for j in range(i,len(tableau)):
        #    temp+=tableau[j]
        #    print (str(j) + " - " + str(tableau[j]) + " - " + str(temp))
        #OLD CODE - WORKING?
        #i+=1
        #if type_paquet == 0:
        #    while i < len(tableau) and tableau[i][0] < later:
        #        later-= tableau[i][0]
        #        i+=1
        #    tableau.insert(i-1, (later, retransmission+1, type_paquet))
        #    if i < len(tableau) - 1:
        #        tableau[i] = (tableau[i][0] - later, tableau[i][1], tableau[i][2])

        #END OF OLD code
        insert(i+1, later, retransmission+1, type_paquet)

    #print("Sortie - i = " + str(i) + "tab[i-1] = " + str(tableau[i-1]) + " - tab[i] = " + str(tableau[i]) )#+ " et tab[i+1] = " + str(tableau[i+1]))
    #if i+1 < len(tableau):
    #    print("Et tab[i+1] = " + str(tableau[i+1]))

#Not used anymore, was not tested.
def pop(position):
    global tableau

    #print("We want to remove a fragment isFrag = " + str(tableau[position][1]))
    if position < len(tableau) - 1:
        temp = tableau[position][0] + tableau[position+1][0]
    tableau.pop(position)
    tableau[position] = (temp, tableau[position][1], tableau[position][2])

def schedule_frag(position):
    global tableau
    global time_fragment
    global time_first_fragment
    pos = []

    #time_fragment.pop()
    retrans = tableau[position][1]
    total = 0
    #print("Time_first_fragment = " + str(time_first_fragment))
    for i in range(time_first_fragment, position):
        total += tableau[i][0]
    pos.append(position)

    later = backoff(retrans)
    #print("Time of the backoff: " + str(later) + " and retrans = " + str(retrans))
    #print("****" + str(position))
    total+=later
    #We check if the bakcoff will be before the next scheduled fragmented packet
    #print ("In schedule_Frag, we compare the time of the last fragment of the retransmission :" + str(total + n_frag * sleep * Tfrag) + " et freq = " + str(freq))

    if total + n_frag * sleep * Tfrag < freq:
        position = insert(position+1, later, retrans+1, 1)
        index = 1
        while position > 0  and index < n_frag :
            position = insert(position, sleep*Tfrag, retrans+1, 1)
            total += sleep*Tfrag
            index+=1
        if index != n_frag:
            print("WE FAILED TO SCHEDULE A FRAGMENT, SHOULDN'T HAPPEN")
            time_fragment.pop()
    else:
        #print("We failed to insert a new retransmission before freq, we cancel.")
        time_fragment.pop()

def deal_frag(position, total):
    global frag_collision
    global count_frag
    global stat
    global time_fragment
    global time_first_fragment
    global n_frag

    #print("Loss of a fragment - " + str(tableau[position]))
    if count_frag == 0:
        #If it is the first attempt, we log the beginning of time.
        if tableau[position][1] == 0:
            #print("retrans du fragment : " + str(tableau[position]) + " et retrans du precedant : " + str(tableau[position-1]))
            time_fragment.append(total)
            time_first_fragment = position
            #print("Start new fragment count at " + str(somme))
    #if frag_collision == False and count_frag != 0:
        #print("First Collision")
        #time_fragment.pop()
    if count_frag == n_frag - 1:
        #print("We reached the number of fragments in collision, let's start over")
        schedule_frag(position)
        count_frag = 0
        frag_collision = False
    else:
        #print("The fragment was not the last one")
        count_frag+=1
        frag_collision = True

i = 0
j = 0
somme = 0
frag_collision = False
#stat is a list of consecutive collisions. For example stat[0] gives the number of times there were collisions with 2 frames, stat[1] means collisions with 3 frames, and so on.
stat = [0]
#print (len(stat))
#while i < generation -1:
while i < len(tableau)-1:
    #print("")
    #time.sleep(1)
    #print(time_first_fragment)
    somme += tableau[i][0]
    #print(str(i) + " - " + str(somme))
    isFrag = tableau[i][2]
    #if the packet we deal with is a normal frame
    if (isFrag == 0 and tableau[i+1][0] < T) or (isFrag == 1 and tableau[i+1][0] < Tfrag):
        #Then both the current frame and the next one are in collision
        #print("COLLISION")
        if isFrag == 0:
            collision += 1
            schedule(i)
        else:
            #print("1st call: " + str(isFrag))
            deal_frag(i, somme)


        i+=1
        somme += tableau[i][0]
        #If this is again a classical frame:
        if tableau[i][2] == 0:
            collision +=1
            schedule(i)
            #If this is a fragment, we do the same as before.
        else:
            #print("2nd call: " + str(tableau[i][2]))
            deal_frag(i, somme)

            #If we hit the last frame, we count the collision in stat, and exit
            #if i >= len(tableau)-1:
            #    stat[0]+=1
            #    break
            #otherwise, we count the time, and check if there are more collisions
            #somme += tableau[i][0]
            #print(str(i) + " - " + str(somme))

        if (tableau[i+1][2] == 0 and tableau[i+1][0] > T) or (tableau[i+1][2] == 0 and tableau[i+1][0] > Tfrag):
            stat[0]+=1
            #j counts the number of consecutive packets that are in collision
        else:
            j = 2
            while i<len(tableau)-1 and ((tableau[i+1][2] == 0 and tableau[i+1][0] < T) or (tableau[i+1][2] == 1 and tableau[i+1][0] < Tfrag)):
                if tableau[i+1][2] == 0 :
                    collision+=1
                    schedule(i+1)
                    j+=1
                else: #This is a fragment
                    #print("Dans deep collsiion, isFrag = " + str(tableau[i+1][2]))
                    deal_frag(i+1, somme)


                i+=1
                somme += tableau[i][0]
                    #print(str(i) + " - " + str(somme))
                    #schedule(i) #XXX
                #if there was more than 2 frames in collisions, we log it
            if j>2:
                #print ("j =" +  str(j))
                while len(stat) < (j-1):
                    stat.append(0)
                stat[j-2] += 1

    else: # meaning that we are not in collision
        #print("SUCCESS")
        if isFrag == 0:
            count +=1
        else: #This is a fragment that was successfully sent.
            #print("")
            #print ("Fragment well received: " + str(tableau[i]))
            if count_frag == 0:
                #print("First fragment well received")
                if tableau[i][1] == 0:
                    #print("retrans du fragment : " + str(tableau[i]) + " et retrans du precedant : " + str(tableau[i-1]))
                    time_fragment.append(somme)
                    time_first_fragment = i
                    #print("Start new fragment count at " + str(somme))
                count_frag+=1
                frag_collision = False
            else :
                #print("Fragment well received count = " + str(count_frag))
                if count_frag == n_frag - 1:
                    #print("Was the last fragment")
                    if frag_collision == False:
                        #print("We received all the window well")
                        temp = time_fragment[len(time_fragment)-1]
                        time_fragment[len(time_fragment)-1] = somme - temp
                        count_frag = 0
                        count_frag_success += 1
                        #print("This packet had a delay of " + str(somme-temp))
                    else:
                        #print("We did not receive the window well, we re-initialize")
                        schedule_frag(i)
                        count_frag = 0
                        frag_collision = False
                else:
                    #print("was not the last frag, I just increase count")
                    count_frag +=1

    i+=1


nb_col = collision / somme
nb_succes = count / somme
S = nb_succes * T

avg = 0
for i in range(len(time_fragment)):
    avg += time_fragment[i]
avg = avg/len(time_fragment)

#if we are in a middle of a window of fragments, we remove the last registered time, which is only the record of the starting of the fragments
if count_frag != 0:
    time_fragment.pop()

#print_table(0, len(tableau))

print("Number of fragmented packets: " + str(count_packet_will_be_fragmented))
print("Number of successfull packet that were fragmented: " + str(count_frag_success))
print("Time of the fragmented packets: in theory should be around " + str(n_frag * Tfrag + (n_frag-1) * sleep * Tfrag) + " and in practice: ")
print("Average of time needed to send a fragmented data:" + str(avg))
print(time_fragment)
print("Nombre de collisions : " + str(collision) + " - soit " + str(nb_col) + " trames par seconde")
print("Nombre de trames recues : " + str(count) + " - soit " + str(nb_succes) + " trames par seconde")
print("S = " + str(S))
print("Theoriquement, on devrait avoir S=" + str(G*math.exp(-2*G)))
print("** Stat sur les collisions **")
for i in range(0,len(stat)):
    print("Collision entre " + str(i+2) + " trames : " + str(stat[i]))
