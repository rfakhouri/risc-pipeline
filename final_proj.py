##Filname: final_proj.py
##Class: EE577A
##Authors: Michael Chu and Nikhil Narang

#!/usr/bin/python
import re
from collections import deque

def add_clk(x):
    x[0] = x[0] + 2.5

def add_mult(x):
    x[0] = x[0] + 1

def clear_mult(x):
    val = x[0]
    x[0] = x[0] - val

#decimal to binary
def d2b(n):
    bStr = ''
    if n < 0: raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1    
    return bStr

#hex to binary
def h2b(hex):
    return d2b(int(hex,16))

#binary to hex
def b2h(binary):
    binary = binary.replace("B","")
    num = hex(int(binary,2))
    hexint = num[2:].upper()
    if len(hexint) < 2:
        hexint = '0' + hexint
    return hexint + 'H'
    

#2's compliment
def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

#Reverse Bits
def reverse_bits(bits):
    return bits[::-1]

def flip_bits(b_string):
    ib_string = ""
    for bit in b_string:
        if bit == "1":
            ib_string += "0"
        else:
            ib_string += "1"
    return ib_string

##-------------------------------------------------------------------------------
def STOREI(input, dict, vecfile, clk, mem_flag, dictfile, dict_write, mul_count, mul_val, mul_flag):
    #print input
    input = input.replace("#","") #clean the string to remove all #
    word = input.split() #split the string into individual words

    #If the value is binary, make it HEX
    if (("B" in word[0] and len(word[0]) > 5) and len(word) == 2):
        word[0] = b2h(word[0])
    elif (("B" in word[1] and len(word[1]) > 5) and len(word) >= 3):
        word[1] = b2h(word[1])
 
    if len(word) == 2: #if the line only contains a word name, and the value (e.g. 40H #0010)
        hex_int = int(word[1], 16)  #convert word into hex value
        dict[word[0]] = hex(hex_int)    #create a map between word and hex val
        if dict_write == 1:
            dictfile.write("0\n")
    elif word[0] == '1' and len(word) == 3: #if the line includes a "1" at the front (e.g. 1 40H #0010)
        hex_int = int(word[2], 16)
        dict[word[1]] = hex(hex_int)
        if dict_write == 1:
            dictfile.write("0\n")        
    elif len(word) > 3: #if the line requires bursting (e.g. 2 40H #0010 #0011)
        #print "in burst write 0\n"
        dict[word[1]] = hex(int(word[2],16)) #assigns the first word name the first value (e.g. 40H : 0010)
        hex_int = int(word[1].replace("H",""), 16) #convert hex string to hex int so we can increment (e.g. 40H --> 41H)
        if dict_write == 1:
            dictfile.write("0\n")
            if mul_flag == 1:
                add_mult(mul_count)
        for i in range(1,int(word[0])): #loops through "burst" operation
            #print dict_write
            #print mul_count
            if dict_write == 1 and mul_count[0] < 4:
                #print "in burst still 0\n"   
                dictfile.write("0\n")
                if mul_flag == 1:
                    add_mult(mul_count)
            elif mul_count[0] == 4 and mul_flag == 1:
                dictfile.write(mul_val)
                mul_count[0] = 0
                mul_flag = 0 #if mul_flag == 0, we'd just write 0's to dictfile
                
            new_int = hex(hex_int + 0x1) + 'H' #increments the word name and then converts it to a string 
            dict[new_int[2:]] = hex(int(word[2+i],16)) #assigns the incremented hex string a value (e.g. 41H : 0011)
    #print dict
    mul_list = [mul_flag, mul_count]
    
    #Vecfile Logic
    if len(word) == 2:
        bin_i = h2b(word[1])
        while len(bin_i) < 16:
            bin_i = '0' + bin_i
        IMM_15_12 = hex(int(bin_i[:4],2))[2:]
        IMM_11_8 = hex(int(bin_i[4:8],2))[2:]
        IMM_7_4 = hex(int(bin_i[8:12],2))[2:]
        IMM_3_0 = hex(int(bin_i[12:],2))[2:]

        bin_b = h2b(word[0].replace("H",""))
        while len(bin_b) < 16:
            bin_b = '0' + bin_b

        MEM_5_4 = hex(int(bin_b[10:12],2))[2:]
        MEM_3_0 = hex(int(bin_b[12:],2))[2:]

        if mem_flag == 1: #prior SW
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI, prior SW\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 0 1 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
        elif mem_flag == 2: #prior LW
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI, prior LW\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
            clk_bar = clk_bar + 0.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 1 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
        else: #normal
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
            
    elif word[0] == '1' and len(word) == 3:
        bin_i = h2b(word[2])
        while len(bin_i) < 16:
            bin_i = '0' + bin_i
        IMM_15_12 = hex(int(bin_i[:4],2))[2:]
        IMM_11_8 = hex(int(bin_i[4:8],2))[2:]
        IMM_7_4 = hex(int(bin_i[8:12],2))[2:]
        IMM_3_0 = hex(int(bin_i[12:],2))[2:]

        bin_b = h2b(word[1].replace("H",""))
        while len(bin_b) < 16:
            bin_b = '0' + bin_b

        MEM_5_4 = hex(int(bin_b[10:12],2))[2:]
        MEM_3_0 = hex(int(bin_b[12:],2))[2:]

        if mem_flag == 1: #prior SW
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI, prior SW\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 0 1 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
        elif mem_flag == 2: #prior LW
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI, prior LW\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
            clk_bar = clk_bar + 0.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 1 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")

        else:
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")            
    elif len(word) > 3:
        bin_i = h2b(word[2])
        while len(bin_i) < 16:
            bin_i = '0' + bin_i
        IMM_15_12 = hex(int(bin_i[:4],2))[2:]
        IMM_11_8 = hex(int(bin_i[4:8],2))[2:]
        IMM_7_4 = hex(int(bin_i[8:12],2))[2:]
        IMM_3_0 = hex(int(bin_i[12:],2))[2:]
        
        new_int = hex(hex_int + 0x1)
        bin_b = h2b(word[1].replace("H",""))
        while len(bin_b) < 16:
            bin_b = '0' + bin_b

        MEM_5_4 = hex(int(bin_b[10:12],2))[2:]
        MEM_3_0 = hex(int(bin_b[12:],2))[2:]

        if mem_flag == 1: #prior SW
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI, prior SW\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 0 1 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
        elif mem_flag == 2:
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI, prior LW\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
            clk_bar = clk_bar + 0.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 1 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
        else: #normal
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0+" "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
            
        for i in range(i, int(word[0])):
            bin_i = h2b(word[2+i])
            while len(bin_i) < 16:
                bin_i = '0' + bin_i

            IMM_15_12 = hex(int(bin_i[:4],2))[2:]
            IMM_11_8 = hex(int(bin_i[4:8],2))[2:]
            IMM_7_4 = hex(int(bin_i[8:12],2))[2:]
            IMM_3_0 = hex(int(bin_i[12:],2))[2:]

            new_int = hex(hex_int + 0x1) #increments the word name and then converts it to a string 
            bin_b = h2b(new_int)
            while len(bin_b) < 16:
                bin_b = '0' + bin_b

            MEM_5_4 = hex(int(bin_b[10:12],2))[2:]
            MEM_3_0 = hex(int(bin_b[12:],2))[2:]

            #all prior ones are SW thus:
            add_clk(clk)
            vecfile.write(str(clk[0]) + "\t1 1 0 1 0 0 0 0 0 0 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0 + " " + IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +" ; STOREI, prior SW\n")
            clk_bar = clk[0] + 1.25
            vecfile.write(str(clk_bar) + "\t1 0 1 1 0 0 0 1 0 1 0 0 0 0 7 0 7 0 " + MEM_5_4 + " " + MEM_3_0 + " " + IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0 +"\n")
    return mul_list #return dict_flag value for others to use
##---------------------------------------------------------------------------------------------------------------------------------------------------    
def STORE(input, dict, reg, vecfile, clk, mem_flag, dictfile, dict_write):
    input = input.replace("$","")
    word = input.split()

    #If the value is binary, make it HEX
    if "B" in word[0] and len(word[0]) > 5:
        word[0] = b2h(word[0])
    
    dict[word[0]] = reg[int(word[1])]
    #print dict
    if dict_write == 1:
        dictfile.write("0\n")
        
    #Vecfile Logic
    bin_b = h2b(word[0].replace("H",""))
    while len(bin_b) < 16:
        bin_b = '0' + bin_b

    #Find RD_ADDR_BAR
    b_string = d2b(int(word[1]))
    ib_string = flip_bits(b_string)

    rd_addr_bar = hex(int(ib_string,2))[2:]
    MEM_ADDR_5_4 = hex(int(bin_b[10:12],2))[2:]
    MEM_ADDR_3_0 = hex(int(bin_b[12:],2))[2:]

    #Output to Vec File
    if mem_flag == 1:
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 0 0 0 0 0 0 0 0 7 " + word[1]+" "+rd_addr_bar+" 0 " + MEM_ADDR_5_4 + " " + MEM_ADDR_3_0 + " 0 0 0 0 ; SW, prior SW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 0 1 0 1 0 0 0 0 7 " + word[1]+" "+rd_addr_bar+" 0 " + MEM_ADDR_5_4 + " " + MEM_ADDR_3_0 + " 0 0 0 0\n")
    elif mem_flag == 2:
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 0 0 0 0 0 0 0 0 7 " + word[1]+" "+rd_addr_bar+" 0 " + MEM_ADDR_5_4 + " " + MEM_ADDR_3_0 + " 0 0 0 0 ; SW, prior LW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 0 1 0 0 0 0 0 0 7 " + word[1]+" "+rd_addr_bar+" 0 " + MEM_ADDR_5_4 + " " + MEM_ADDR_3_0 + " 0 0 0 0\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 0 1 1 0 0 0 0 0 7 " + word[1]+" "+rd_addr_bar+" 0 " + MEM_ADDR_5_4 + " " + MEM_ADDR_3_0 + " 0 0 0 0\n")
        
    else:
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 0 0 0 0 0 0 0 0 7 " + word[1]+" "+rd_addr_bar+" 0 " + MEM_ADDR_5_4 + " " + MEM_ADDR_3_0 + " 0 0 0 0 ; STORE\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 0 0 0 0 0 0 0 0 7 " + word[1]+" "+rd_addr_bar+" 0 " + MEM_ADDR_5_4 + " " + MEM_ADDR_3_0 + " 0 0 0 0\n")
        
##--------------------------------------------------------------------------------------------------------------------------------------------------- 
def LOAD(input, dict, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$","")
    word = input.split()
    
    #If the value is binary, make it HEX
    if "B" in word[1] and len(word[1]) > 5:
        word[1] = b2h(word[1])

    if word[0] != "0":
        reg[int(word[0])] = dict[word[1]]

    #print reg

    #if first 2 chars are 0x
    if str(dict[word[1]])[:2] == "0x":
        dictfile.write(dict[str(word[1])][2:] + "\n")
    else:
        dictfile.write(dict[str(word[1])] + "\n")

    bin_b = h2b(word[1].replace("H",""))
    while len(bin_b) < 16:
        bin_b = '0' + bin_b

    #Vecfile Logic
    MEM_ADDR_5_4 = hex(int(bin_b[10:12],2))[2:]
    MEM_ADDR_3_0 = hex(int(bin_b[12:],2))[2:]

    #Output Logic
    if mem_flag == 1: #prior SW    
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 1 0 1 1 0 0 0 0 0 0 0 7 0 7 "+word[0]+" "+MEM_ADDR_5_4+" "+MEM_ADDR_3_0+" 0 0 0 0 ; LW, prior SW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 1 0 1 1 1 0 1 0 0 0 0 7 0 7 "+word[0]+" "+MEM_ADDR_5_4+" "+MEM_ADDR_3_0+" 0 0 0 0\n")
    elif mem_flag == 2: #prior LW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 1 0 1 1 0 0 0 0 0 0 0 7 0 7 "+word[0]+" "+MEM_ADDR_5_4+" "+MEM_ADDR_3_0+" 0 0 0 0 ; LW, prior LW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 1 0 1 1 1 0 0 0 0 0 0 7 0 7 "+word[0]+" "+MEM_ADDR_5_4+" "+MEM_ADDR_3_0+" 0 0 0 0\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar) + "\t1 0 1 1 0 1 1 1 1 0 0 0 0 0 7 0 7 "+word[0]+" "+MEM_ADDR_5_4+" "+MEM_ADDR_3_0+" 0 0 0 0\n")        
    else: #normal
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 1 0 1 1 0 0 0 0 0 0 0 7 0 7 "+word[0]+" "+MEM_ADDR_5_4+" "+MEM_ADDR_3_0+" 0 0 0 0 ; LW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 1 0 1 1 0 0 0 0 0 0 0 7 0 7 "+word[0]+" "+MEM_ADDR_5_4+" "+MEM_ADDR_3_0+" 0 0 0 0\n")    
##---------------------------------------------------------------------------------------------------------------------------------------------------    
def AND(input, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$", "")
    word = input.split()
    a = int(reg[int(word[1])], 16)
    b = int(reg[int(word[2])], 16)
    if word[0] != "0":
        reg[int(word[0])] = hex(a&b)
    
    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")    

    #Vecfile Logic
    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    b2_string = d2b(int(word[2]))
    while len(b2_string) < 3:
        b2_string = '0' + b2_string
    ib_string2 = flip_bits(b2_string)
    rd_addr_bar2 = hex(int(ib_string2,2))[2:]

    if mem_flag == 1: #prior SW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 1 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; AND, prior SW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 1 0 1 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    elif mem_flag == 2: #Prior LW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 1 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; AND, prior LW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 0 0 1 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 1 0 0 1 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")        
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 1 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; AND\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 0 0 0 0 1 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")    
##---------------------------------------------------------------------------------------------------------------------------------------------------
def ANDI(input, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$", "")
    input = input.replace("#", "")
    input = input.replace("H", "")
    word = input.split()
    a = int(reg[int(word[1])], 16)
    b = (int(word[2], 16))

    if word[0] != "0":
        reg[int(word[0])] = hex(a&b)

    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")    

    #print reg
    #Convert hexadecimal value to Binary
    bin_b = h2b(word[2])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
        
    #Vecfile Logic
    IMM_15_12 = hex(int(bin_b[:4],2))[2:]
    IMM_11_8 = hex(int(bin_b[4:8],2))[2:]
    IMM_7_4 = hex(int(bin_b[8:12],2))[2:]
    IMM_3_0 = hex(int(bin_b[12:],2))[2:]

    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    if mem_flag == 1: #Prior SW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 1 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; ANDI, prior SW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 1 0 1 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
    elif mem_flag == 2: #Prior LW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 1 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; ANDI, prior LW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 0 0 1 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 1 0 0 1 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")        
    else: #Normal 
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 1 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; ANDI\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 0 0 0 0 1 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n") 

    
##---------------------------------------------------------------------------------------------------------------------------------------------------
def XOR(input, reg, vecfile, clk, mem_flag, dictfile):
    input = input.replace("$", "")
    word = input.split()
    a = int(reg[int(word[1])], 16)
    b = int(reg[int(word[2])], 16)

    if word[0] != "0":
        reg[int(word[0])] = hex(a^b)
        
    #print reg

    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")
    #Vecfile Logic

    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    b2_string = d2b(int(word[2]))
    while len(b2_string) < 3:
        b2_string = '0' + b2_string
    ib_string2 = flip_bits(b2_string)
    rd_addr_bar2 = hex(int(ib_string2,2))[2:]

    if mem_flag == 1: #prior SW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 8 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; XOR, prior SW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 1 0 0 8 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    elif mem_flag == 2: #prior LW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 8 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; XOR, prior LW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 0 0 0 8 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 1 0 0 0 8 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
        
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 8 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; XOR\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 0 0 0 0 0 8 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
##---------------------------------------------------------------------------------------------------------------------------------------------------
def XORI(input, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$", "")
    input = input.replace("#", "")
    word = input.split()
    a = int(reg[int(word[1])], 16)
    b = (int(word[2], 16))

    if word[0] != "0":
        reg[int(word[0])] = hex(a^b)
    #print reg

    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")
        
    #Convert hexadecimal value to Binary
    bin_b = h2b(word[2])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b

    #Vecfile Logic
    IMM_15_12 = hex(int(bin_b[:4],2))[2:]
    IMM_11_8 = hex(int(bin_b[4:8],2))[2:]
    IMM_7_4 = hex(int(bin_b[8:12],2))[2:]
    IMM_3_0 = hex(int(bin_b[12:],2))[2:]

    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    if mem_flag == 1: #Prior is SW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 8 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; XORI, prior SW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 1 0 0 8 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
    elif mem_flag == 2: #Prior is LW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 8 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; XORI, prior LW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 0 0 0 8 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 1 0 0 0 8 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")        
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 8 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; XORI\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 0 0 0 0 0 8 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")

##---------------------------------------------------------------------------------------------------------------------------------------------------
def NOP(vecfile, clk, mem_flag, dictfile, dict_write, NOP_flag):
    #print "NOP"

    if dict_write == 1 and NOP_flag == 0:
        dictfile.write("0\n")

    if mem_flag == 1: #Prior Instr is a STORE/STOREI
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 0 0 0 0 0 0 0 0 0 0 7 0 7 0 0 0 0 0 0 0 ; NOP, prior instr SW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) +"\t1 0 1 0 0 0 0 1 0 1 0 0 0 0 7 0 7 0 0 0 0 0 0 0\n")
    elif mem_flag == 2: #Prior Instr is a LOAD
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 0 0 0 0 0 0 0 0 0 0 7 0 7 0 0 0 0 0 0 0 ; NOP, prior instr LW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) +"\t1 0 1 0 0 0 0 1 0 0 0 0 0 0 7 0 7 0 0 0 0 0 0 0\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar) +"\t1 0 1 0 0 0 0 1 1 0 0 0 0 0 7 0 7 0 0 0 0 0 0 0\n")
    else: #Normal Instr
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 0 0 0 0 0 0 0 0 0 0 7 0 7 0 0 0 0 0 0 0 ; NOP\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) +"\t1 0 1 0 0 0 0 0 0 0 0 0 0 0 7 0 7 0 0 0 0 0 0 0\n")

##---------------------------------------------------------------------------------------------------------------------------------------------------
def ADD(input, reg, vecfile, clk, mem_flag, dictfile):
    #Back-End Logic:
    input = input.replace("$", "")
    word = input.split()
    
    #Check for 2's Comp
    bin_a = h2b(reg[int(word[1])])
    while len(bin_a) < 16:
        bin_a = '0' + bin_a
    val_a = twos_comp(int(bin_a,2), len(bin_a))

    bin_b = h2b(reg[int(word[2])])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
    val_b = twos_comp(int(bin_b,2), len(bin_b))

    val = hex((val_a+val_b) & (2**16-1)) #12 bit 2's comp
    #Perform 2's Comp Addition
    if word[0] != "0":
        reg[int(word[0])] = val

    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")
        
    #VecFile Logic
    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    b2_string = d2b(int(word[2]))
    while len(b2_string) < 3:
        b2_string = '0' + b2_string
    ib_string2 = flip_bits(b2_string)
    rd_addr_bar2 = hex(int(ib_string2,2))[2:]
    
    if mem_flag == 1: #prior is SW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 2 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; ADD, prior SW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 1 0 2 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    elif mem_flag == 2: #prior is LW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 2 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; ADD, prior LW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 0 0 2 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 1 0 0 2 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 2 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; ADD\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 0 0 0 0 2 0 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    
##---------------------------------------------------------------------------------------------------------------------------------------------------
def ADDI(input, reg, vecfile, clk, mem_flag, dictfile):
    #Back-End Logic:    
    input = input.replace("$", "")
    input = input.replace("#", "")
    word = input.split()

    #Check for 2's Comp
    bin_a = h2b(reg[int(word[1])])
    while len(bin_a) < 16:
        bin_a = '0' + bin_a
    val_a = twos_comp(int(bin_a,2), len(bin_a))

    bin_b = h2b(word[2])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
    val_b = twos_comp(int(bin_b,2), len(bin_b))

    #Perform 2's Comp Addition
    val = hex((val_a+val_b) & (2**16-1)) #12 bit 2's comp
    if word[0] != "0":
        reg[int(word[0])] = val

    
    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")
        
    #Convert hexadecimal value to Binary
    bin_b = h2b(word[2])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b

    #Vecfile Logic
    IMM_15_12 = hex(int(bin_b[:4],2))[2:]
    IMM_11_8 = hex(int(bin_b[4:8],2))[2:]
    IMM_7_4 = hex(int(bin_b[8:12],2))[2:]
    IMM_3_0 = hex(int(bin_b[12:],2))[2:]

    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    #Output to Vector File
    if mem_flag == 1: #Prior is SW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 2 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; ADDI, prior SW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 1 0 2 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
    elif mem_flag == 2: #Prior is LW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 2 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; ADDI, prior LW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 0 0 2 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar)+"\t1 0 1 0 1 0 1 1 1 0 0 2 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 2 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; ADDI \n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 0 0 0 0 2 0 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")

##--------------------------------------------------------------------------------------------------------------------------------------------------- 
def MUL(input, reg, vecfile, clk, mem_flag, dictfile):
    input = input.replace("$","")
    word = input.split()
    a = int(reg[int(word[1])], 16)
    b = int(reg[int(word[2])], 16)

    #Only takes Lower 6-bits of Register Value
    #1st, convert to Binary
    bin_a = h2b(reg[int(word[1])])
    bin_b = h2b(reg[int(word[2])])
    while len(bin_a) < 16:
        bin_a = '0' + bin_a
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
    
    #2nd, take last 6 bits of binary
    val_a = twos_comp(int(bin_a[10:],2), len(bin_a[10:]))
    val_b = twos_comp(int(bin_b[10:],2), len(bin_b[10:]))

    val = hex((val_a*val_b) & (2**12-1)) #12 bit 2's comp

    if val_a < 0 or val_b < 0:
        val = "0xf" + val[2:]
        
    if word[0] != "0":
        reg[int(word[0])] = val

    dictfile.write("0\n")
        
    #Vecfile Logic
    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    b2_string = d2b(int(word[2]))
    while len(b2_string) < 3:
        b2_string = '0' + b2_string
    ib_string2 = flip_bits(b2_string)
    rd_addr_bar2 = hex(int(ib_string2,2))[2:]

    if mem_flag == 1: #prior was SW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 4 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; MUL, prior SW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 1 0 0 4 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    elif mem_flag == 2: #prior was LW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 4 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; MUL, prior LW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 0 0 0 4 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 1 0 0 0 4 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 4 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; MUL\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 0 0 0 0 0 4 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")

    return val
##---------------------------------------------------------------------------------------------------------------------------------------------------
def MULI(input, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$", "")
    input = input.replace("#", "")
    input = input.replace("H", "")
    word = input.split()

    bin_a = h2b(reg[int(word[1])])
    bin_b = h2b(word[2])
    while len(bin_a) < 16:
        bin_a = '0' + bin_a
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
   
    #2nd, take last 6 bits of binary
    val_a = twos_comp(int(bin_a[10:],2), len(bin_a[10:]))
    val_b = twos_comp(int(bin_b[10:],2), len(bin_b[10:]))
    val = hex((val_a*val_b) & (2**12-1)) #12 bit 2's comp
    print h2b(val)
    if h2b(val)[:1] == '1':
        val = "0xf" + val[2:]
        
    if word[0] != "0":
        reg[int(word[0])] = val

    dictfile.write("0\n")

    #Vecfile Logic
    IMM_5_4 = hex(int(bin_b[10:12],2))[2:]
    IMM_3_0 = hex(int(bin_b[12:],2))[2:]

    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    #Output to Vector File
    if mem_flag == 1: #prior SW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 4 "+word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 "+IMM_5_4+" "+IMM_3_0+" ; MULI, prior SW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 1 0 0 4 "+word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 "+IMM_5_4+" "+IMM_3_0+"\n")
    elif mem_flag == 2: #prior LW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 4 "+word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 "+IMM_5_4+" "+IMM_3_0+" ; MULI, prior LW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 0 0 0 4 "+word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 "+IMM_5_4+" "+IMM_3_0+"\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 1 0 0 0 4 "+word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 "+IMM_5_4+" "+IMM_3_0+"\n")
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 4 "+word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 "+IMM_5_4+" "+IMM_3_0+" ; MULI\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 0 0 0 0 0 4 "+word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 "+IMM_5_4+" "+IMM_3_0+"\n")
    return val

##---------------------------------------------------------------------------------------------------------------------------------------------------   
def MAX(input, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$","")
    word = input.split()
    
    bin_a = h2b(reg[int(word[1])])
    while len(bin_a) < 16:
        bin_a = '0' + bin_a
    val_a = twos_comp(int(bin_a,2), len(bin_a))

    print reg[int(word[2])]
    bin_b = h2b(reg[int(word[2])])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
    val_b = twos_comp(int(bin_b,2), len(bin_b))

    #Perform 2's Comp MAX
    if word[0] != "0":
        if val_a >= val_b:
            reg[int(word[0])] = reg[int(word[1])]
            print val_a
        elif val_a < val_b:
            reg[int(word[0])] = reg[int(word[2])]
            print val_b

    #print reg
    print reg[int(word[0])]
    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")
        
    #Vecfile Logic
    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    b2_string = d2b(int(word[2]))
    while len(b2_string) < 3:
        b2_string = '0' + b2_string
    ib_string2 = flip_bits(b2_string)
    rd_addr_bar2 = hex(int(ib_string2,2))[2:]

    if mem_flag == 1: #Prior was SW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 2 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; MAX, prior SW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 1 0 0 2 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    elif mem_flag == 2: #Prior was LW
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 2 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; MAX, prior LW\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 0 0 0 0 2 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 1 1 0 0 0 2 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0]) + "\t1 1 0 0 1 0 1 0 0 0 0 0 2 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0 ; MAX\n")
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar) + "\t1 0 1 0 1 0 1 0 0 0 0 0 2 " + word[1]+" "+rd_addr_bar+" "+word[2]+" "+rd_addr_bar2+" "+word[0]+" 0 0 0 0 0 0\n")
    
##---------------------------------------------------------------------------------------------------------------------------------------------------
def MAXI(input, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$","")
    input = input.replace("#", "")
    word = input.split()

    bin_a = h2b(reg[int(word[1])])
    while len(bin_a) < 16:
        bin_a = '0' + bin_a
    val_a = twos_comp(int(bin_a,2), len(bin_a))

    bin_b = h2b(word[2])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
    val_b = twos_comp(int(bin_b,2), len(bin_b))

    if word[0] != "0":
        if val_a >= val_b:
            reg[int(word[0])] = reg[int(word[1])]
        elif val_a < val_b:
            reg[int(word[0])] = hex(val_b & (2**16-1))
            
    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")
    #Vecfile Logic
    IMM_15_12 = hex(int(bin_b[:4],2))[2:]
    IMM_11_8 = hex(int(bin_b[4:8],2))[2:]
    IMM_7_4 = hex(int(bin_b[8:12],2))[2:]
    IMM_3_0 = hex(int(bin_b[12:],2))[2:]

    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    #Output to Vector File
    if mem_flag == 1: #prior SW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 2 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; MAXI, prior SW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 1 0 0 2 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
    elif mem_flag == 2: #prior LW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 2 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; MAXI, prior LW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 0 0 0 2 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 1 0 0 0 2 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")
    else: #normal
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 2 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+" ; MAXI\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 0 0 0 0 0 2 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 "+IMM_15_12+" "+IMM_11_8+" "+IMM_7_4+" "+IMM_3_0+"\n")        

##---------------------------------------------------------------------------------------------------------------------------------------------------
def SFL(input, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$","")
    input = input.replace("#", "")
    word = input.split()
    a = int(reg[int(word[1])], 16)
    b = (int(word[2], 16))
    mask = 2 ** 16 - 1

    if word[0] != "0":
        reg[int(word[0])] = hex((a << b)& mask)#Prevents shift left from increasing in bit size

    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
        #print str(reg[int(word[0])])
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")

    bin_b = h2b(word[2])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
    
    #Vecfile Logic
    IMM_3_0 = hex(int(bin_b[12:],2))[2:]

    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    #Output to Vector File
    if mem_flag == 1: #prior SW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 1 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+" ; SFL, prior SW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 1 1 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+"\n")
    elif mem_flag == 2: #prior LW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 1 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+" ; SFL, prior LW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 0 1 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+"\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 1 0 1 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+"\n")        
    else: #Normal
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 1 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+" ; SFL\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 0 0 0 1 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+"\n")    
##---------------------------------------------------------------------------------------------------------------------------------------------------
def SFR(input, reg, vecfile, clk, mem_flag, dictfile):
    #print input
    input = input.replace("$","")
    input = input.replace("#", "")
    word = input.split()
    a = int(reg[int(word[1])], 16)
    b = (int(word[2], 16))
    mask = 2 ** 16 - 1

    if word[0] != "0":
        reg[int(word[0])] = hex((a >> b)& mask)
    #print reg

    if str(reg[int(word[0])])[:2] == "0x":
        dictfile.write(str(reg[int(word[0])])[2:] + "\n")
    else:
        dictfile.write(str(reg[int(word[0])]) + "\n")
    #Michael, is this even necessary??
    bin_b = h2b(word[2])
    while len(bin_b) < 16:
        bin_b = '0' + bin_b
    
    #Vecfile Logic
    IMM_3_0 = hex(int(bin_b[12:],2))[2:]

    b_string = d2b(int(word[1]))
    while len(b_string) < 3:
        b_string = '0' + b_string
    ib_string = flip_bits(b_string)
    rd_addr_bar = hex(int(ib_string,2))[2:]

    #Output to Vector File
    if mem_flag == 1: #prior SW
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+" ; SFR, prior SW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 1 0 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+"\n")
    elif mem_flag == 2:
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+" ; SFR, prior LW\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 0 0 0 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+"\n")
        clk_bar = clk_bar + 0.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 1 1 0 0 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+"\n")        
    else:
        add_clk(clk)
        vecfile.write(str(clk[0])+"\t1 1 0 1 0 0 1 0 0 0 0 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+" ; SFR\n") 
        clk_bar = clk[0] + 1.25
        vecfile.write(str(clk_bar)+"\t1 0 1 1 0 0 1 0 0 0 0 0 1 " +word[1]+" "+rd_addr_bar+" 0 7 "+word[0]+" 0 0 0 0 0 "+IMM_3_0+"\n")
    
##---------------------------------------------------------------------------------------------------------------------------------------------------
    
def dir_dep_seven(outfile, buf, mem_buf, mul_buf):
    print "Direct MUL Dependency of 7\n"
    outfile.write("NOP\nNOP\nNOP\nNOP\nNOP\nNOP\nNOP\n")
    buf.get(3)
    buf.put("XXX")
    mem_buf.get(3)
    mem_buf.push_back("X",3)
    mul_buf.get(7)
    mul_buf.push_back("X",7)

def dir_dep_six(outfile, buf, mem_buf, mul_buf):
    print "Direct MUL Dependency of 6\n"
    outfile.write("NOP\nNOP\nNOP\nNOP\nNOP\nNOP\n")
    buf.get(3)
    buf.put("XXX")
    mem_buf.get(3)
    mem_buf.push_back("X",3)
    mul_buf.get(6)
    mul_buf.push_back("X",6)

def dir_dep_five(outfile, buf, mem_buf, mul_buf):
    print "Direct MUL Dependency of 5\n"
    outfile.write("NOP\nNOP\nNOP\nNOP\nNOP\n")
    buf.get(3)
    buf.put("XXX")
    mem_buf.get(3)
    mem_buf.push_back("X",3)
    mul_buf.get(5)
    mul_buf.push_back("X",5)

def dir_dep_four(outfile, buf, mem_buf, mul_buf):
    print "Direct MUL Dependency of 4\n"
    outfile.write("NOP\nNOP\nNOP\nNOP\n")
    buf.get(3)
    buf.put("XXX")
    mem_buf.get(3)
    mem_buf.push_back("X",3)
    mul_buf.get(4)
    mul_buf.push_back("X",4)

def dir_dep_three(outfile, buf, mem_buf, mul_buf):
    print "Direct Dependency of 3\n"
    outfile.write("NOP\nNOP\nNOP\n") #write 3 NOPs
    buf.get(3) #clean buffer to accomodate for NOPs
    buf.put("XXX")
    mem_buf.get(3)
    mem_buf.push_back("X",3)
    mul_buf.get(3)
    mul_buf.push_back("X",3)

def dir_dep_two(outfile, buf, mem_buf, mul_buf):
    print "Direct Dependency of 2\n"
    outfile.write("NOP\nNOP\n")
    buf.get(2)
    buf.put("XX")
    mem_buf.get(2)
    mem_buf.push_back("X",2)
    mul_buf.get(2)
    mul_buf.push_back("X",2)

def dir_dep_one(outfile, buf, mem_buf, mul_buf):
    print "Direct Dependency of 1\n"
    outfile.write("NOP\n") #write 1 NOP
    buf.get(1)
    buf.put("X")
    mem_buf.get(1)
    mem_buf.push_back("X",1)
    mul_buf.get(1)
    mul_buf.push_back("X",1)

def mem_dep_three(outfile, mem_buf):
    print "Memory Dependency of 3\n"
    outfile.write("NOP\nNOP\nNOP\n") #write 3 NOPs
    mem_buf.remove()
    mem_buf.remove()
    mem_buf.remove()
    mem_buf.push_back("X",3)

def mem_dep_two(outfile, mem_buf):
    print "Memory Dependency of 2\n"
    outfile.write("NOP\nNOP\n") #write 2 NOPs
    mem_buf.remove()
    mem_buf.remove()
    mem_buf.push_back("X",2)

def mem_dep_one(outfile, mem_buf):
    print "Memory Dependency of 1\n"
    outfile.write("NOP\n") #write 1 NOP
    mem_buf.remove()
    mem_buf.push_back("X", 1)

#This class and the "put" "peek" and "get" function are taken from:
#http://stackoverflow.com/questions/9219093/python-string-fifo
class Buffer(deque):
    def put(self, iterable):
        for i in iterable:
            self.append(i)

    def push_back(self, value, how_many):
        for i in range(0,how_many):
            self.append(value)

    def view(self, how_many):
        temp = []
        for i in range(0,how_many):
            temp.append(self[i])
        return temp
        #return join([self[i] for i in range(how_many)])

    def peek(self, how_many):
        return ''.join([self[i] for i in xrange(how_many)])

    def get(self, how_many):
        return ''.join([self.popleft() for _ in xrange(how_many)])

    def size(self):
        return len(self)

    def remove(self):
        self.popleft()
       
    
def main():
    infile = open('cmd_test.txt', 'r+')
    op_code = ["AND", "ANDI", "XOR","XORI","ADD","ADDI","MAX","MAXI","SFL","SFR"]
    registers = ['0','0','0','0','0','0','0','0']
    load_flag = True
    word_dict = {}#{'00': '#0000'}  #create a word dictionary
    buf = Buffer() #Initializes a buffer (FIFO) to "simulate" the reg pipeline
    mem_buf = Buffer() #Initializes a buffer (FIFO) to "simulate" the mem hazards
    mul_buf = Buffer() #Initializes a buffer (FIFO) to "simulate" mul pipeline
    buf.put("XXX") #Set FIFO to all NOPs
    mem_buf.push_back('X', 3) #Set FIFO to all NOPs
    mul_buf.push_back('X', 7)
    line_num = 1
    num_lines = 0
    modifiedFile = open('new_cmd.txt', 'w') #writes adjusted commands due to inserting NOOPS to this file
    newfile = open('cmd2.txt','w')

    for line in infile:
        word = line.split()
        if len(word) > 0:
            num_lines += 1
            newfile.write(line)
            
    #print num_lines
    infile.close()
    newfile.close()

    infile = open('cmd2.txt','r')
    all_lines = infile.readlines()
    #print all_lines
    infile.close()

    infile = open('cmd2.txt','r')
    
    for _line in infile:
        _word = _line.split()
        if len(_word) > 0:  #if the line we read is not just a blank space
            op_buf = list(str(buf.peek(buf.size())))  #converts buffer to a list for reg hazards
                
##---------------------------------------------------------------------------------------------------------------------
            #curr op has a register or memory dependency in pipeline:
            if _word[0] in op_code:
                load_flag = False
                if _word[2].replace("$","") in mul_buf or _word[3].replace("$","") in mul_buf:
                    print _word[0] + " " + _word[1] + " " + _word[2] + " " + _word[3] #outputs instructions that need to be stalled
                    print mul_buf
                    if _word[2].replace("$","") == mul_buf[6] or _word[3].replace("$","") == mul_buf[6]:
                        dir_dep_seven(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[5] or _word[3].replace("$","") == mul_buf[5]:
                        dir_dep_six(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[4] or _word[3].replace("$","") == mul_buf[4]:
                        dir_dep_five(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[3] or _word[3].replace("$","") == mul_buf[3]:
                        dir_dep_four(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[2] or _word[3].replace("$","") == mul_buf[2]:
                        dir_dep_three(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[1] or _word[3].replace("$","") == mul_buf[1]:
                        dir_dep_two(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[0] or _word[3].replace("$","") == mul_buf[0]:
                        dir_dep_one(modifiedFile, buf, mem_buf, mul_buf)
                        
                elif _word[2].replace("$","") in op_buf or _word[3].replace("$","") in op_buf: 
                    print _word[0] + " " + _word[1] + " " + _word[2] + " " + _word[3] #outputs instructions that need to be stalled
                    if _word[2].replace("$","") == op_buf[2] or _word[3].replace("$","") == op_buf[2]: #curr op has a depedency in EX
                        dir_dep_three(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == op_buf[1] or _word[3].replace("$","") == op_buf[1]: #curr op has a dependency in MEM
                        dir_dep_two(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == op_buf[0] or _word[3].replace("$","") == op_buf[0]: #curr op has a dependency in WB
                        dir_dep_one(modifiedFile, buf, mem_buf, mul_buf)
                        
                if buf.size() == 3:
                    buf.remove()    #Removes the op in WB stage
                if _word[0] in op_code:
                    buf.put(_word[1].replace("$","")) 
                else:
                    buf.put("X")
                    
                if mem_buf.size() == 3:
                    mem_buf.remove()
                mem_buf.push_back("X",1)
                
                if mul_buf.size() == 7:
                    mul_buf.remove()
                mul_buf.put("X")  
## -----------------------------------------------------------------------------------------------------------------------------------
            elif _word[0] == "NOP":
                load_flag = False
                if buf.size() == 3:
                    buf.remove()
                buf.put("X")
                if mem_buf.size() == 3:
                    mem_buf.remove()
                mem_buf.push_back("X",1)
                if mul_buf.size() == 7:
                    mul_buf.remove()
                mul_buf.put("X")
## -----------------------------------------------------------------------------------------------------------------------------------
            elif _word[0] == "MUL" or _word[0] == "MULI":
                load_flag = False
                if _word[2].replace("$","") in mul_buf or _word[3].replace("$","") in mul_buf:
                    print _word[0] + " " + _word[1] + " " + _word[2] + _word[3]
                    print mul_buf
                    if _word[2].replace("$","") == mul_buf[6] or _word[3].replace("$","") == mul_buf[6]:
                        dir_dep_seven(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[5] or _word[3].replace("$","") == mul_buf[5]:
                        dir_dep_six(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[4] or _word[3].replace("$","") == mul_buf[4]:
                        dir_dep_five(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[3] or _word[3].replace("$","") == mul_buf[3]:
                        dir_dep_four(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[2] or _word[3].replace("$","") == mul_buf[2]:
                        dir_dep_three(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[1] or _word[3].replace("$","") == mul_buf[1]:
                        dir_dep_two(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[0] or _word[3].replace("$","") == mul_buf[0]:
                        dir_dep_one(modifiedFile, buf, mem_buf, mul_buf)
                        
                elif _word[2].replace("$","") in op_buf or _word[3].replace("$","") in op_buf: 
                    print _word[0] + " " + _word[1] + " " + _word[2] + " " + _word[3] #outputs instructions that need to be stalled
                    if _word[2].replace("$","") in op_buf or _word[3].replace("$","") in op_buf:
                        print op_buf
                    if _word[2].replace("$","") == op_buf[2] or _word[3].replace("$","") == op_buf[2]: #curr op has a depedency in EX
                        dir_dep_three(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == op_buf[1] or _word[3].replace("$","") == op_buf[1]: #curr op has a dependency in MEM
                        dir_dep_two(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == op_buf[0] or _word[3].replace("$","") == op_buf[0]: #curr op has a dependency in WB
                        dir_dep_one(modifiedFile, buf, mem_buf, mul_buf)
                        
                if buf.size() == 3:
                    buf.remove()    #Removes the op in WB stage
                buf.put("X")
                    
                if mem_buf.size() == 3:
                    mem_buf.remove()
                mem_buf.push_back("X",1)
                
                if mul_buf.size() == 7:
                    mul_buf.remove()
                if _word[0] == "MUL" or _word[0] == "MULI":
                    mul_buf.put(_word[1].replace("$",""))
                else:
                    mul_buf.put("X")            
## -----------------------------------------------------------------------------------------------------------------------------------
            elif _word[0] == "STORE": #We only care about register dependencies. We will never have memory dependencies here
                load_flag = False
                if "H" in _word[1]:
                    temp = _word[1].replace("H","")
                    if temp[0] == '0':
                        hex_val = int(temp[1],16)
                    else:
                        hex_val = int(temp,16)
                elif "B" in _word[1] and len(_word[1]) > 3:
                    temp = _word[1].replace("B","")
                    idx = temp.find('1')
                    if idx > 0:
                        hex_val = int(temp[idx:],2)
                    else:
                        hex_val = 0
                        
                if _word[2].replace("$","") in mul_buf:
                    print _word[0] + " " + _word[1] + " " + _word[2]
                    print mul_buf
                    if _word[2].replace("$","") == mul_buf[6]:
                        dir_dep_seven(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[5]:
                        dir_dep_six(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[4]:
                       dir_dep_five(modifiedFile, buf, mem_buf, mul_buf) 
                    elif _word[2].replace("$","") == mul_buf[3]:
                        dir_dep_four(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[2]:
                        dir_dep_three(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[1]:
                        dir_dep_two(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == mul_buf[0]:
                        dir_dep_one(modifiedFile, buf, mem_buf, mul_buf)
                        
                elif _word[2].replace("$","") in op_buf: 
                    print _word[0] + " " + _word[1] + " " + _word[2] #outputs instructions that need to be stalled
                    print op_buf
                    if _word[2].replace("$","") == op_buf[2]: #curr op has a depedency in EX
                        dir_dep_three(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[2].replace("$","") == op_buf[1]: #curr op has a dependency in MEM
                        dir_dep_two(modifiedFile, buf, mem_buf, mul_buf)                      
                    elif _word[2].replace("$","") == op_buf[0]: #curr op has a dependency in WB
                        dir_dep_one(modifiedFile, buf, mem_buf, mul_buf)
                        
                if buf.size() == 3:
                    buf.remove()    #Removes the op in WB stage
                if _word[0] == "STORE":
                    buf.put(_word[2].replace("$",""))
                else:
                    buf.put("X")

                if mul_buf.size() == 7:
                    mul_buf.remove()
                mul_buf.put("X")
                    
                if mem_buf.size() == 3:
                    mem_buf.remove()
                if _word[0] == "STORE":
                    if "H" in _word[1]:
                        mem_buf.push_back(hex(hex_val),1)
                    elif "B" in _word[1] and len(_word[1]) > 3:    
                        mem_buf.push_back(bin(hex_val),1)
                else:
                    mem_buf.push_back("X",1)

##------------------------------------------------------------------------------------------------------------------------------------
            #Loads are trickier because we only care about if STORE has affected the dependencies. So we will always put an "X"
            #into the memory buffer, because we can have consecutive Loads without issue.
            elif _word[0] == "LOAD": #We care about both register and mem dependencies
                if "H" in _word[2]:
                    temp = _word[2].replace("H","")
                    if temp[0] == '0':
                        hex_val = int(temp[1],16)
                    else:
                        hex_val = int(temp,16)
                elif 'B' in _word[2] and len(_word[2]) > 3:
                    temp = _word[2].replace("B","")
                    idx = temp.find('1')
                    if idx > 0:
                        hex_val = int(temp[idx:],2)
                    else:
                        hex_val = 0

                if _word[1].replace("$","") in mul_buf:
                    print _word[0] + " " + _word[1] + " " + _word[2]
                    print mul_buf
                    if _word[1].replace("$","") == mul_buf[6]:
                        dir_dep_seven(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[1].replace("$","") == mul_buf[5]:
                        dir_dep_six(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[1].replace("$","") == mul_buf[4]:
                        dir_dep_five(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[1].replace("$","") == mul_buf[3]:
                        dir_dep_four(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[1].replace("$","") == mul_buf[2]:
                        dir_dep_three(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[1].replace("$","") == mul_buf[1]:
                        dir_dep_two(modifiedFile, buf, mem_buf, mul_buf)
                    elif _word[1].replace("$","") == mul_buf[0]:
                        dir_dep_one(modifiedFile, buf, mem_buf, mul_buf)
                        
                elif _word[1].replace("$","") in op_buf or hex(hex_val) in mem_buf: 
                    print _word[0] + " " + _word[1] + " " + _word[2] #outputs instructions that need to be stalled
                    if _word[1] in op_buf:
                        print op_buf
                    if hex(hex_val) in mem_buf:
                        print "['" + mem_buf.view(3)[2] + "', '" + mem_buf.view(3)[1] + "', '" + mem_buf.view(3)[0] + "']"
                    if _word[1].replace("$","") == op_buf[2] or hex(hex_val) == mem_buf.view(3)[2]: #curr op has a depedency in EX
                        if _word[1].replace("$","") == op_buf[2]:
                            print "Direct Dependency of 3\n"
                            modifiedFile.write("NOP\nNOP\nNOP\n") #write 3 NOPs
                            buf.get(3) #clean buffer to accomodate for NOPs
                            buf.put("XXX")
                        elif hex(hex_val) == mem_buf.view(3)[2]:
                            mem_dep_three(modifiedFile, mem_buf)                 
                    elif _word[1].replace("$","") == op_buf[1] or hex(hex_val) == mem_buf.view(3)[1]: #curr op has a dependency in MEM
                        if _word[1].replace("$","") == op_buf[1]:
                            print "Direct Dependency of 2\n"
                            modifiedFile.write("NOP\nNOP\n") #write 2 NOPs
                            buf.get(2)
                            buf.put("XX")
                        elif hex(hex_val) == mem_buf.view(3)[1]:
                            mem_dep_two(modifiedFile, mem_buf)
                    elif _word[1].replace("$","") == op_buf[0] or hex(hex_val) == mem_buf.view(3)[0]: #curr op has a dependency in WB
                        if _word[1].replace("$","") == op_buf[0]:
                            print "Direct Dependency of 1\n"
                            modifiedFile.write("NOP\n") #write 1 NOP
                            buf.get(1)
                            buf.put("X")
                        elif hex(hex_val) == mem_buf.view(3)[0]:
                            mem_dep_one(modifiedFile, mem_buf)

                    
                if buf.size() == 3:
                    buf.remove()    #Removes the op in WB stage
                load_flag = True
                for i in range(1,4):
                    if (line_num + i) <= num_lines:
                        _temp = all_lines[line_num + i-1].split() #takes in the following lines to check if they have LOAD or not
                        if _temp[0] != "LOAD":

                            load_flag = False
                if _word[0] == "LOAD" and not load_flag:
                    buf.put(_word[1].replace("$","")) 
                else:
                    buf.put("X")
                
                if mul_buf.size() == 7:
                    mul_buf.remove()
                mul_buf.put("X")
                    
                if mem_buf.size() == 3:
                    mem_buf.remove()
                if _word[0] == "LOAD":
                    mem_buf.push_back("X",1)
##---------------------------------------------------------------------------------------------------------------------------------         
            elif _word[0] == "STOREI": #If STOREI
                if len(_word) > 3: #If STOREI has burst Deals with WAW and WAR hazards
                    if "H" in _word[2]:
                        temp = _word[2].replace("H","")
                        if temp[0] == '0':
                            hex_val = int(temp[1],16)
                        else:
                            hex_val = int(temp,16)
                    elif "B" in _word[2] and len(_word[2]) > 3:
                        temp = _word[2].replace("B","")
                        idx = temp.find('1')
                        if idx > 0:
                            hex_val = int(temp[idx:],2)
                        else:
                            hex_val = 0                    
                    for i in range(0,int(_word[1])): #loop through burst memory accesses
                        if hex(hex_val+i*(0x1)) == mem_buf.view(3)[2] or hex(hex_val+i*(0x1))== mem_buf.view(3)[1] or hex(hex_val+i*(0x1)) == mem_buf.view(3)[0]:
                            print _word[0] + " " + _word[1] + " " + _word[2] + " " + _word[3]
                            print "['" + mem_buf.view(3)[2] + "', '" + mem_buf.view(3)[1] + "', '" + mem_buf.view(3)[0] + "']"
                        if hex(hex_val+i*(0x1)) == mem_buf.view(3)[2]:
                            mem_dep_three(modifiedFile, mem_buf)
                        elif hex(hex_val+i*(0x1))== mem_buf.view(3)[1]:
                            mem_dep_two(modifiedFile, mem_buf)
                        elif hex(hex_val+i*(0x1)) == mem_buf.view(3)[0]:
                            mem_dep_one(modifiedFile, mem_buf)
                            
                        if mem_buf.size() == 3:
                            mem_buf.remove()
                        if _word[0] == "STOREI":
                            if "H" in _word[2]:
                                mem_buf.push_back(hex(hex_val),1)
                            elif "B" in _word[2] and len(_word[2]) > 3:    
                                mem_buf.push_back(bin(hex_val),1)                           
                        else:
                            mem_buf.push_back("X",1)

                
                elif _word[1] == "1" and len(_word) == 4: #if STOREI has no burst but formatting (STOREI 1 xxH #xxxx)
                    if "H" in _word[2]:
                        temp = _word[2].replace("H","")
                        if temp[0] == '0':
                            hex_val = int(temp[1],16)
                        else:
                            hex_val = int(temp,16)
                    elif "B" in _word[2] and len(_word[1]) > 3:
                        temp = _word[2].replace("B","")
                        idx = temp.find('1')
                        if idx > 0:
                            hex_val = int(temp[idx:],2)
                        else:
                            hex_val = 0                        
                    if hex(hex_val) in mem_buf.view(3):
                        print _word[0] + " " + _word[1] + " " + _word[2] + _word[3]
                        if hex(hex_val) == mem_buf.view(3)[2]:  #curr op has a mem dependency in EX
                            mem_dep_three(modifiedFile, mem_buf)
                        elif hex(hex_val) == mem_buf.view(3)[1]:
                            mem_dep_two(modifiedFile, mem_buf)
                        elif hex(hex_val) == mem_buf.view(3)[0]:
                            mem_dep_one(modifiedFile, mem_buf)
                            
                    if mem_buf.size() == 3:
                        mem_buf.remove()
                    if _word[0] == "STOREI":
                        if "H" in _word[1]:
                            mem_buf.push_back(hex(hex_val),1)
                        elif "B" in _word[1] and len(_word[1]) > 3:    
                            mem_buf.push_back(bin(hex_val),1)   
                    else:
                        mem_buf.push_back("X",1)

                    
                else: #if STOREI has formatting (STOREI xxH #xxxx)
                    if "H" in _word[1]:
                        temp = _word[1].replace("H","")
                        if temp[0] == '0':
                            hex_val = int(temp[1],16)
                        else:
                            hex_val = int(temp,16)
                    elif "B" in _word[1] and len(_word[1]) > 3:
                        temp = _word[1].replace("B","")
                        idx = temp.find('1')
                        if idx > 0:
                            hex_val = int(temp[idx:],2)
                        else:
                            hex_val = 0                       
                    if hex(hex_val) in mem_buf.view(3):
                        print _word[0] + " " + _word[1] + " " + _word[2]
                        print "['" + mem_buf.view(3)[2] + "', '" + mem_buf.view(3)[1] + "', '" + mem_buf.view(3)[0] + "']\n"
                        if hex(hex_val) == mem_buf.view(3)[2]:  #curr op has a mem dependency in EX
                            mem_dep_three(modifiedFile, mem_buf)
                        elif hex(hex_val) == mem_buf.view(3)[1]:
                            mem_dep_two(modifiedFile, mem_buf)
                        elif hex(hex_val) == mem_buf.view(3)[0]:
                            mem_dep_one(modifiedFile, mem_buf)
                            
                    if mem_buf.size() == 3:
                        mem_buf.remove()
                    if _word[0] == "STOREI":
                        if "H" in _word[1]:
                            mem_buf.push_back(hex(hex_val),1)
                        elif "B" in _word[1] and len(_word[1]) > 3:    
                            mem_buf.push_back(bin(hex_val),1)       
                    else:
                        mem_buf.push_back("X",1)
                        
                if buf.size() == 3:
                    buf.remove()
                buf.push_back("X",1)

                if mul_buf.size() == 7:
                    mul_buf.remove()
                mul_buf.push_back("X",1)
                
            modifiedFile.write(_line)
            line_num += 1
    modifiedFile.write("\n")
    modifiedFile.write("NOP\n")
    modifiedFile.write("NOP\n")
    modifiedFile.write("NOP\n")
    modifiedFile.write("NOP\n")  
    print "-------------------------------------------"
	 
    #this loop performs the operations
    infile.close()
    modifiedFile.close()

    infile = open('new_cmd.txt','r')
    vecfile = open ('cpu.vec','w')

    dictfile = open('golden_results.txt', 'w')
    for i in range (0,5):
        dictfile.write("0\n")
        
    vecfile.write("output_wf 1\n")
    vecfile.write("radix 1 1 1 1 1 1 1 1 1 1 1 2 4 3 3 3 3 3 2 4 4 4 4 4\n")
    vecfile.write("io i i i i i i i i i i i i i i i i i i i i i i i i\n")
    vecfile.write("vname RESET_BAR CLK CLK_BAR ALU_SRC ALU_SRC_BAR MEM_TO_REG REG_WR MEM_PCHG MEM_RD MEM_WR LEFT ALU_OP<[5:4]> ALU_OP<[3:0]> RD_ADDR1<[2:0]> RD_ADDR_BAR1<[2:0]> RD_ADDR2<[2:0]> RD_ADDR_BAR2<[2:0]> WR_ADDR<[2:0]> MEM_ADDR<[5:4]> MEM_ADDR<[3:0]> IMM<[15:12]> IMM<[11:8]> IMM<[7:4]> IMM<[3:0]>\n")
    vecfile.write("tunit ns\n")
    vecfile.write("trise 10ps\n")
    vecfile.write("tfall 10ps\n")
    vecfile.write("vih 1.8\n")
    vecfile.write("vil 0.0\n")
    vecfile.write("vol 0\n\n")
    clk = [0]

    # Reset and Precharge
    vecfile.write("; RESET and PRECHARGE Sequence\n")
    vecfile.write(str(clk[0]) + "\t0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
    vecfile.write(str(1.25) + "\t0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
    add_clk(clk)
    vecfile.write(str(clk[0]) + "\t0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
    temp_clk = clk[0] + 1.25
    vecfile.write(str(temp_clk) + "\t0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")    
    vecfile.write("; Tabular Data \n")

    #Initialize Word Dictionary to all 0's
    for i in range(0,64):
        hex_key = hex(i)[2:]
        if len(hex_key) == 1:
            hex_key = '0' + hex_key
        hex_key = hex_key.upper()
        word_dict[hex_key+'H'] = '0'

    mem_flag = 0
    flags = [0,0,0]
    lw_sw = [0,0,0] #if it's 1: SW, if it's 2: LW
    burst_set = [0,1,2,4]
    mul_val = ""
    mul_count = [0]
    mul_flag = 0 #mul_flag is off
    write_flag = 0
    NOP_flag = 0
    dict_write = 1
    instr = ["STOREI", "STORE", "LOAD", "AND", "ANDI", "XOR", "XORI", "NOP", "ADD", "ADDI", "MUL", "MULI", "MAX", "MAXI", "SFL", "SFR"]
    num_lines = 0
    #count num of lines
    for line in infile:
        word = line.split()
        if len(word) > 0:
            num_lines += 1            
    #print num_lines
    
    infile.close()
    infile = open('new_cmd.txt','r')
    line_num = 0
    #Main Vec File Logic
    for line in infile:
        line_num += 1
        if line_num > (num_lines - 4): #if line_number is greater than the last 4 NOPs
            NOP_flag = 1
        #print line_num
        line = line.upper()
        for word in line.split():
            if mul_flag == 1 and word in instr: #if mul_flag is ON
                add_mult(mul_count)
                
            if mul_count[0] == 4:
                write_flag = 1
                mul_flag = 0
                clear_mult(mul_count)
        
            #if word in instr:
                #print word + " MUL_COUNT: " + str(mul_count[0]) + "\n"

            if write_flag == 1:
                dictfile.write(mul_val[2:] + "\n")
                write_flag = 0
                dict_write = 0
            
            if word == "STOREI":
                if int(line.split(' ',1)[1][0]) not in burst_set:
                    print "\nError000: Command " + line +" has invalid burst length.\n"
                else:
                    word = line.split(' ',1)[1].split()
                    if len(word) > 3: #If it's a burst command
                        bin_i = h2b(word[1].replace('H',' '))
                        while len(bin_i) < 6:
                            bin_i = '0' + bin_i
                        if ((word[0] == '2' and bin_i[5:] != "0") or (word[0] == '4' and bin_i[4:] != "00")):
                            print "\nError001: Command " + line + " is not aligned properly.\n"
                        else:
                    	    temp = STOREI(line.split(' ',1)[1], word_dict, vecfile, clk, mem_flag, dictfile,dict_write,mul_count,mul_val, mul_flag)
                    else:
                        temp = STOREI(line.split(' ',1)[1], word_dict, vecfile, clk, mem_flag, dictfile, dict_write,mul_count,mul_val, mul_flag)
                mul_flag = temp[0]
                mul_count = temp[1]
                #print mul_flag
                #print mul_count
                if flags == [0,0,0]:    #000
                    flags = [1,0,0]
                    lw_sw[0] = 1
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,1,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in STOREI"
                    lw_sw[1] = 1
                elif flags == [2,1,0]:  #210
                    flags = [0,2,1]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in STOREI"
                    lw_sw[2] = 1
                elif flags == [0,2,1]:   #021
                    flags = [1,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in STOREI"
                    lw_sw[0] = 1
                elif flags == [1,0,2]:   #102
                    flags = [2,1,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in STOREI"
                    lw_sw[1] = 1
                elif flags == [2,0,0]:  #200
                    flags = [0,1,0]
                    lw_sw[1] = 1
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,1]
                    lw_sw[2] = 1
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [1,0,0]
                    lw_sw[0] = 1
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,1]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in STOREI"
                    lw_sw[2] = 1
                elif flags == [0,0,1]:  #001
                    flags = [1,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in STOREI"
                    lw_sw[0] = 1              
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                dict_write = 1 #enable dict again
                
            elif word == "STORE":
                STORE(line.split(' ',1)[1], word_dict, registers, vecfile, clk, mem_flag, dictfile, dict_write)
                if flags == [0,0,0]:    #000
                    flags = [1,0,0]
                    lw_sw[0] = 1
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,1,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in STORE"
                    lw_sw[1] = 1
                elif flags == [2,1,0]:  #210
                    flags = [0,2,1]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in STORE"
                    lw_sw[2] = 1
                elif flags == [0,2,1]:   #021
                    flags = [1,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in STORE"
                    lw_sw[0] = 1
                elif flags == [1,0,2]:   #102
                    flags = [2,1,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in STORE"
                    lw_sw[1] = 1
                elif flags == [2,0,0]:  #200
                    flags = [0,1,0]
                    lw_sw[1] = 1
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,1]
                    lw_sw[2] = 1
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [1,0,0]
                    lw_sw[0] = 1
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,1]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in STORE"
                    lw_sw[2] = 1
                elif flags == [0,0,1]:  #001
                    flags = [1,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in STORE"
                    lw_sw[0] = 1              
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                dict_write = 1

                
            elif word == "LOAD":
                LOAD(line.split(' ',1)[1], word_dict, registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [1,0,0]
                    lw_sw[0] = 2
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,1,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in LOAD"
                    lw_sw[1] = 2
                elif flags == [2,1,0]:  #210
                    flags = [0,2,1]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in LOAD"
                    lw_sw[2] = 2
                elif flags == [0,2,1]:   #021
                    flags = [1,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in LOAD"
                    lw_sw[0] = 2
                elif flags == [1,0,2]:  #102
                    flags = [2,1,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in LOAD"
                    lw_sw[1] = 2
                elif flags == [2,0,0]:  #200
                    flags = [0,1,0]
                    lw_sw[1] = 2
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,1]
                    lw_sw[2] = 2
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [1,0,0]
                    lw_sw[0] = 2
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,1]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in LOAD"
                    lw_sw[2] = 2
                elif flags == [0,0,1]:  #001
                    flags = [1,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in LOAD"
                    lw_sw[0] = 2              
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)

            elif word == "AND":
                AND(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in AND"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in AND"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in AND"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in AND"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in AND"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in AND"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "ANDI":
                ANDI(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in ANDi"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in ANDI"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:  #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in ANDI"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:  #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in ANDI"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in ANDI"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in ANDI"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "XOR":
                XOR(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in XOR"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in XOR"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in XOR"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in XOR"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in XOR"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in XOR"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "XORI":
                XORI(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)       
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in XORI"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in XORI"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in XORI"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in XORI"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in XORI"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in XORI"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "NOP":
                NOP(vecfile, clk, mem_flag, dictfile, dict_write, NOP_flag)      
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in nop"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in nop"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in nop"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in nop"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in nop"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in nop"
                    lw_sw[0] = 0             
                dict_write = 1
                
            elif word == "ADD":
                ADD(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADD"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADD"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADD"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADD"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADD"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADD"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "ADDI":
                ADDI(line.split(' ',1)[1],registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADDI"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADDI"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADDI"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADDI"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADDI"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in ADDI"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "MUL":
                mul_val = MUL(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                mul_flag = 1 #set mul_flag on
                
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in MUL"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in MUL"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in MUL"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in MUL"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in MUL"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in MUL"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "MULI":
                mul_val = MULI(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                mul_flag = 1
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in MULI"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in MULI"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in MULI"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in MULI"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in MULI"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in MULI"
                    lw_sw[0] = 0             
               # print "updated flags: " + str(flags)
               # print "lw/sw: " + str(lw_sw)
                
            elif word == "MAX":
                MAX(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAX"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAX"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAX"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAX"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAX"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAX"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "MAXI":
                MAXI(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAXI"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAXI"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAXI"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAXI"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAXI"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in MAXI"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
                
            elif word == "SFL":
                SFL(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFL"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFL"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFL"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFL"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFL"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFL"
                    lw_sw[0] = 0             
               # print "updated flags: " + str(flags)
               # print "lw/sw: " + str(lw_sw)
                
            elif word == "SFR":
                SFR(line.split(' ',1)[1], registers, vecfile, clk, mem_flag, dictfile)
                if flags == [0,0,0]:    #000
                    flags = [0,0,0]
                    lw_sw = [0,0,0]
                    mem_flag = 0
                elif flags == [1,0,0]:  #100
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFR"
                    lw_sw[1] = 0
                elif flags == [2,1,0]:  #210
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFR"
                    lw_sw[2] = 0
                elif flags == [0,2,1]:   #021
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFR"
                    lw_sw[0] = 0
                elif flags == [1,0,2]:   #102
                    flags = [2,0,0]
                    if lw_sw[0] == 1:
                        mem_flag = 1
                    elif lw_sw[0] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFR"
                    lw_sw[1] = 0
                elif flags == [2,0,0]:  #200
                    flags = [0,0,0]
                    lw_sw[1] = 0
                    mem_flag = 0
                elif flags == [0,2,0]:  #020
                    flags = [0,0,0]
                    lw_sw[2] = 0
                    mem_flag = 0
                elif flags == [0,0,2]:  #002
                    flags = [0,0,0]
                    lw_sw[0] = 0
                    mem_flag = 0
                elif flags == [0,1,0]:  #010
                    flags = [0,2,0]
                    if lw_sw[1] == 1:
                        mem_flag = 1
                    elif lw_sw[1] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFR"
                    lw_sw[2] = 0
                elif flags == [0,0,1]:  #001
                    flags = [0,0,2]
                    if lw_sw[2] == 1:
                        mem_flag = 1
                    elif lw_sw[2] == 2:
                        mem_flag = 2
                    else:
                        print "error in SFR"
                    lw_sw[0] = 0             
                #print "updated flags: " + str(flags)
                #print "lw/sw: " + str(lw_sw)
            dict_write = 1
                
#    dictfile = open('golden_results.txt', 'w')
#    dictfile.write( "Memory Location | Value Stored\n" )
    #print("\n--------------------------------\n" )
    print "Values stored in Memory.\n"
    for val in sorted(word_dict):
       print val + "\t|\t"  + word_dict[val]
    print "\nVerilogA Golden Results printed to: golden_results.txt\n"
        
main()
    
