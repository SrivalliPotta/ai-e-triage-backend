def start_triage(patient):
    # GREEN
    if patient.can_walk:
        return "GREEN"

    # BLACK or RED
    if not patient.breathing:
        if patient.airway_opened:
            return "RED"
        return "BLACK"

    # RED
    if patient.resp_rate > 30:
        return "RED"

    # RED
    if not patient.radial_pulse:
        return "RED"

    # RED
    if patient.cap_refill > 2:
        return "RED"

    # RED
    if not patient.follows_commands:
        return "RED"

    # YELLOW
    return "YELLOW"
