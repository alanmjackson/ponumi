"""Functions for converting Ponumi poems to OSC"""

from ponumi import poem_list_to_notes
from ponumi import flatten
from ponumi import syllable_list

_osc_scaling = len(syllable_list) * 1.0



def syllables_to_kyma_osc(syllables):
    """
    Converts a list of syllables into a list of values suitable for sending to kyma / pacarana
    over OSC.
    """
    notelist = poem_list_to_notes(syllables)
    return notelist_to_kyma_osc(notelist)


def poem_to_kyma_osc(poem):
    """
    Converts a poem into a list of values suitable for sending to kyma / pacarana
    over OSC.
    """
    return syllables_to_kyma_osc(poem.syllables)


def notelist_to_kyma_osc(notelist):
    """
    Creates a list of values suitable for sending to kyma / pacarana
    over OSC. All values are scaled by _osc_scaling, usually so the 
    result is between 0 and 1.
    """
    osc = []

    notelist = flatten(notelist)
    for note in notelist:
        osc.append(note / _osc_scaling)

    return osc
