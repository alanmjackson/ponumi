import time
import OSC

BPM = 60

client = OSC.OSCClient()
client.connect( ('192.168.0.8', 8000) )

vcs_addresses = ["/vcs/Amp/1", "/vcs/Freq/1"]
vcs_messages = [(0.6,), (0.0,), (0.1,), (0.2,), (0.5,)]

simple_float_data_addresses = ["/amplitude", "/frequency"]
simple_float_data_messages = [(1.0,), (0.0,), (0.1,), (0.2,), (0.333,), (0.5,)]

simple_integer_data_addresses = ["/notenumber"]
simple_integer_data_messages = [(60,), (63,), (65,), (58,)]

integer_list_addresses = ["/notelist"]
#integer_list_messages = [ ([60, 72, 58, 70],) ]
integer_list_messages = [ ([0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12],),  
                          ([0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21],), 
                          ([0.20, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.31],),
                          ([0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.40, 0.41],),
                          ([30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41],)  
                          ]

poems      = [
              [ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,
               13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
               25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 
               37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
              [48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 
               36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 
               24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 
               12, 11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1],
              [ 2,  4, 42, 29, 32, 30, 41, 14, 24,  6, 10, 47, 
               40, 34,  9, 22, 23, 27, 33,  8, 35, 12, 17,  7, 
               16, 19,  5, 20, 21, 36, 48, 11,  1, 26, 28, 25, 
               39, 37, 46, 13, 38, 45, 18, 15, 44, 31,  3, 43]
             ]


#convert a list of poem note numbers into a kyma OSC format
def poem_to_OSC_list(int_list):
    float_list = []
    for item in int_list:
        #it seems I don't have to put numbers in a range 0 - 1, I just need to make them floats.
        float_list.append(item / 1.0) 

    return (float_list,)


def send_osc_messages(addresses, messages):
    for address in addresses:
        for message in messages:
    
            msg = OSC.OSCMessage()
            msg.setAddress(address)

            if isinstance(message[0], list):
                data_list = message[0]
            else:
                data_list = [message[0]]

            for data in data_list:
                if len(message) > 1: # use the data type hint if present
                    msg.append(data, message[1])
                else:
                    msg.append(data)

            client.send(msg)
            print address
            print message
            time.sleep(60.0 / BPM) # wait here some secs


try :
    
    while 1: # endless loop
        
        #print "\nTesting VCS control"
        #send_osc_messages(vcs_addresses, vcs_messages)

        #print "\nTesting simple float data"
        #send_osc_messages(simple_float_data_addresses, simple_float_data_messages)        

        #print "\nTesting simple integer data"
        #send_osc_messages(simple_integer_data_addresses, simple_integer_data_messages)

        #print "\nTesting integer list"
        #send_osc_messages(integer_list_addresses, integer_list_messages)        

        print "\nTesting sending a whole poem"
        poem_messages = []
        for poem in poems:
            poem_messages.append(poem_to_OSC_list(poem))
        
        send_osc_messages(["/notelist"], poem_messages)


except KeyboardInterrupt:
    print "Closing OSCClient"
    client.close()
    print "Done"
        


msg = OSC.OSCMessage() 
msg.setAddress("/doofus")
msg.append(0.1, "f")
client.send(msg) 
print msg
print "address: ", client.address()

