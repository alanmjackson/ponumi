"""Functions for converting Ponumi poems to OSC"""

from ponumi import poem_list_to_notes
from ponumi import flatten
from ponumi import syllable_list

_osc_scaling = len(syllable_list) * 1.0



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
