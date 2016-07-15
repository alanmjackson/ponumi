"""Functions for converting Ponumi poems to OSC"""

import OSC

from ponumi import poem_list_to_notes
from ponumi import flatten

_osc_scaling = 1.0
_osc_destination = ['127.0.0.1', 8000]
_osc_address = '/notelist' 
_osc_go_address = '/go'

def send_via_osc(poem):
    osc = poem_to_kyma_osc(poem)

    try:
        client = OSC.OSCClient()
        client.connect((_osc_destination[0], _osc_destination[1]))

        #send poem array
        msg = OSC.OSCMessage(_osc_address)
        msg.append(osc)
        client.send(msg)


        #send the go gate signal
        msg = OSC.OSCMessage(_osc_go_address)
        msg.append(1.0)
        client.send(msg)

    finally:
        client.close()

    return osc


def poem_to_kyma_osc(poem):
    """
    Converts a poem into a list of values suitable for sending to kyma / pacarana
    over OSC.
    """
    notelist = poem_list_to_notes(poem.syllables)
    return notelist_to_kyma_osc(notelist)


def notelist_to_kyma_osc(notelist):
    """
    Creates a list of values suitable for sending to kyma / pacarana
    over OSC. All values need to be scaled between 0 and 1, which is done
    by dividing all note numbers by 1000. 
    """
    osc = []

    notelist = flatten(notelist)
    for note in notelist:
        osc.append(note / _osc_scaling)

    return osc
