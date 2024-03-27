

def generate_temporal_burst_level1(request_packet):
    """
    This is the first level of temporal burstiness statistics capturing.
    - inter arrival time is modeled with memoryless distribution
    - burst duration is modeled with memoryless distribution
    - burst volume is modeled with memoryless distribution with the fact that it is conditional to the
      occurrence of burst duration
    """
    trace = {}
    iat = {}
    burst = {}
    cycle = {"cycle": 0}
    for packet in request_packet:
        if int(packet.split("\t")[5].split(": ")[1]) not in trace.keys():
            trace[int(packet.split("\t")[5].split(": ")[1])] = int(packet.split("\t")[7].split(": ")[1])
        else:
            trace[int(packet.split("\t")[5].split(": ")[1])] += int(packet.split("\t")[7].split(": ")[1])
        cycle["cycle"] = int(packet.split("\t")[5].split(": ")[1])
    prev_off = int(list(trace.keys())[0])
    prev_on = int(list(trace.keys())[0])
    volume = 0
    for cycle, byte in trace.items():
        if cycle - prev_off > 1:
            if prev_on == prev_off:
                burst_duration = 1
            else:
                burst_duration = prev_off - prev_on
            if (cycle - prev_off - 1) not in iat.keys():
                iat[cycle - prev_off - 1] = 1
            else:
                iat[cycle - prev_off - 1] += 1
            if burst_duration not in burst.keys():
                burst.setdefault(burst_duration, {}).setdefault(volume, {})
                burst[burst_duration][volume] = 1
            else:
                if volume not in burst[burst_duration].keys():
                    burst[burst_duration][volume] = 1
                else:
                    burst[burst_duration][volume] += 1
            volume = byte
            prev_on = cycle
            prev_off = cycle
        else:
            prev_off = cycle
            volume += byte
    iat = dict(sorted(iat.items(), key=lambda x: x[0]))
    burst = dict(sorted(burst.items(), key=lambda x: x[0]))
    for dur in burst.keys():
        burst[dur] = dict(sorted(burst[dur].items(), key=lambda x: x[0]))
    return cycle, iat, burst


def generate_temporal_burst_level2(request_packet):
    """
    This is the second level of temporal burstiness statistics capturing.
    - inter arrival time is modeled with 1 step of memory using markov chain
    - burst duration is modeled with memoryless distribution
    - burst volume is modeled with memoryless distribution with the fact that it is conditional to the
      occurrence of burst duration
    """
    trace = {}
    iat = {}
    burst = {}
    cycle = {}
    for packet in request_packet:
        if int(packet.split("\t")[5].split(": ")[1]) not in trace.keys():
            trace[int(packet.split("\t")[5].split(": ")[1])] = int(packet.split("\t")[7].split(": ")[1])
        else:
            trace[int(packet.split("\t")[5].split(": ")[1])] += int(packet.split("\t")[7].split(": ")[1])
        cycle["cycle"] = int(packet.split("\t")[5].split(": ")[1])
    prev_off = int(list(trace.keys())[0])
    prev_on = int(list(trace.keys())[0])
    prev_iat = 0
    volume = 0
    for cycle, byte in trace.items():
        if cycle - prev_off > 1:
            if prev_on == prev_off:
                burst_duration = 1
            else:
                burst_duration = prev_off - prev_on
            if prev_iat == 0:
                prev_iat = cycle - prev_off - 1
                iat.setdefault(prev_iat, {})
            else:
                if prev_iat not in iat.keys():
                    iat.setdefault(prev_iat, {})
                if (cycle - prev_off - 1) not in iat[prev_iat].keys():
                    iat[prev_iat][cycle - prev_off - 1] = 1
                else:
                    iat[prev_iat][cycle - prev_off - 1] += 1
                prev_iat = cycle - prev_off - 1
            if burst_duration not in burst.keys():
                burst.setdefault(burst_duration, {}).setdefault(volume, {})
                burst[burst_duration][volume] = 1
            else:
                if volume not in burst[burst_duration].keys():
                    burst[burst_duration][volume] = 1
                else:
                    burst[burst_duration][volume] += 1
            volume = byte
            prev_on = cycle
            prev_off = cycle
        else:
            prev_off = cycle
            volume += byte
    iat = dict(sorted(iat.items(), key=lambda x: x[0]))
    for s in iat.keys():
        iat[s] = dict(sorted(iat[s].items(), key=lambda x: x[0]))
    burst = dict(sorted(burst.items(), key=lambda x: x[0]))
    for dur in burst.keys():
        burst[dur] = dict(sorted(burst[dur].items(), key=lambda x: x[0]))
    return cycle, iat, burst


def generate_temporal_burst_level3(request_packet):
    """
        This is the third level of temporal burstiness statistics capturing.
        -
        -
        -
    """
    trace = {}
    iat = {}
    burst_volume_chain = {}
    burst_duration_chain = {}
    cycle = {}
    for packet in request_packet:
        if int(packet.split("\t")[5].split(": ")[1]) not in trace.keys():
            trace[int(packet.split("\t")[5].split(": ")[1])] = int(packet.split("\t")[7].split(": ")[1])
        else:
            trace[int(packet.split("\t")[5].split(": ")[1])] += int(packet.split("\t")[7].split(": ")[1])
        cycle["cycle"] = int(packet.split("\t")[5].split(": ")[1])
    prev_off = int(list(trace.keys())[0])
    prev_on = int(list(trace.keys())[0])
    prev_iat = 0
    prev_burst_duration = 0
    volume = 0
    for cycle, byte in trace.items():
        if cycle - prev_off > 1:
            if prev_on == prev_off:
                burst_duration = 1
            else:
                burst_duration = prev_off - prev_on
            if prev_iat == 0:
                prev_iat = cycle - prev_off - 1
                iat.setdefault(prev_iat, {})
            else:
                if prev_iat not in iat.keys():
                    iat.setdefault(prev_iat, {})
                if (cycle - prev_off - 1) not in iat[prev_iat].keys():
                    iat[prev_iat][cycle - prev_off - 1] = 1
                else:
                    iat[prev_iat][cycle - prev_off - 1] += 1
                prev_iat = cycle - prev_off - 1
            #burst duration begin
            if prev_burst_duration == 0:
                prev_burst_duration = burst_duration
            if prev_burst_duration not in burst_duration_chain.keys():
                burst_duration_chain.setdefault(prev_burst_duration, {})
                burst_duration_chain[prev_burst_duration][burst_duration] = 1
            else:
                if burst_duration not in burst_duration_chain[prev_burst_duration].keys():
                    burst_duration_chain[prev_burst_duration][burst_duration] = 1
                else:
                    burst_duration_chain[prev_burst_duration][burst_duration] += 1
            prev_burst_duration = burst_duration
            # burst duration end
            #burst volume begin
            if burst_duration not in burst_volume_chain.keys():
                burst_volume_chain.setdefault(burst_duration, {}).setdefault(volume, {})
                burst_volume_chain[burst_duration][volume] = 1
            else:
                if volume not in burst_volume_chain[burst_duration].keys():
                    burst_volume_chain[burst_duration][volume] = 1
                else:
                    burst_volume_chain[burst_duration][volume] += 1
            # burst volume end

            volume = byte
            prev_on = cycle
            prev_off = cycle
        else:
            prev_off = cycle
            volume += byte
    iat = dict(sorted(iat.items(), key=lambda x: x[0]))
    for s in iat.keys():
        iat[s] = dict(sorted(iat[s].items(), key=lambda x: x[0]))
    burst_duration_chain = dict(sorted(burst_duration_chain.items(), key=lambda x: x[0]))
    for prev in burst_duration_chain.keys():
        burst_duration_chain[prev] = dict(sorted(burst_duration_chain[prev].items(), key=lambda x: x[0]))
    for dur in burst_volume_chain.keys():
        burst_volume_chain[dur] = dict(sorted(burst_volume_chain[dur].items(), key=lambda x: x[0]))
    return cycle, iat, burst_duration_chain, burst_volume_chain


def spatial_locality(request_packet):
    pass


def generate_network_centric_model(request_packet, level):
    data = {}
    iat = {}
    burst = {}
    cycle = {}
    burst_volume = {}
    burst_duration = {}
    if level == "level1":
        cycle, iat, burst = generate_temporal_burst_level1(request_packet)
    elif level == "level2":
        cycle, iat, burst = generate_temporal_burst_level2(request_packet)
    elif level == "level3":
        cycle, iat, burst_duration, burst_volume = generate_temporal_burst_level3(request_packet)

    if level == "level1" or level == "level2":
        data.setdefault("cycle", {})
        data["cycle"] = cycle
        data.setdefault("temporal", {}).setdefault("iat", {})
        data["temporal"]["iat"] = iat
        duration = {}
        for dur, volume in burst.items():
            duration[dur] = sum(volume.values())
        data["temporal"]["duration"] = duration
        data["temporal"].setdefault("volume", {})
        for dur, volume in burst.items():
            data["temporal"]["volume"][dur] = volume
    elif level == "level3":
        data.setdefault("cycle", {})
        data["cycle"] = cycle
        data.setdefault("temporal", {}).setdefault("iat", {})
        data["temporal"]["iat"] = iat
        data["temporal"].setdefault("duration", {})
        for prev in burst_duration.keys():
            data["temporal"]["duration"][prev] = burst_duration[prev]
        data["temporal"].setdefault("volume", {})
        for dur, volume in burst_volume.items():
            data["temporal"]["volume"][dur] = volume

    return data