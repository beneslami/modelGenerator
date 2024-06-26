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
        if packet.split("\t")[0] == "request injected":
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


def generate_spatial_burst_level1(request_packet):
    """
        - source chip is chosen randomly based on memoyless distribution
        - destination is chosen depended on the source
        - packet is chosen depended on the destination
        - memory latency is chosen randomly
    """
    source = {}
    destination = {}
    request_packet_type = {}
    reply_packet_type = {}
    request_window = {}
    request_trace = {}
    reply_window = {}
    reply_trace = {}
    for packet in request_packet:
        if packet.split("\t")[0] == "request injected":
            src = int(packet.split("\t")[1].split(": ")[1])
            dst = int(packet.split("\t")[2].split(": ")[1])
            sze = int(packet.split("\t")[7].split(": ")[1])
            cyc = int(packet.split("\t")[5].split(": ")[1])
            if cyc not in request_trace.keys():
                request_trace[cyc] = 1
            else:
                request_trace[cyc] += 1
            if src not in source.keys():
                source[src] = 1
            else:
                source[src] += 1
            if src not in destination.keys():
                destination.setdefault(src, {})[dst] = 1
            else:
                if dst not in destination[src].keys():
                    destination[src][dst] = 1
                else:
                    destination[src][dst] += 1
            if src not in request_packet_type.keys():
                request_packet_type.setdefault(src, {}).setdefault(dst, {})[sze] = 1
            else:
                if dst not in request_packet_type[src].keys():
                    request_packet_type[src].setdefault(dst, {})[sze] = 1
                else:
                    if sze not in request_packet_type[src][dst].keys():
                        request_packet_type[src][dst][sze] = 1
                    else:
                        request_packet_type[src][dst][sze] += 1
        elif packet.split("\t")[0] == "reply injected":
            src = int(packet.split("\t")[1].split(": ")[1])
            dst = int(packet.split("\t")[2].split(": ")[1])
            cyc = int(packet.split("\t")[5].split(": ")[1])
            sze = int(packet.split("\t")[7].split(": ")[1])
            if cyc not in reply_trace.keys():
                reply_trace[cyc] = 1
            else:
                reply_trace[cyc] += 1
            if dst not in reply_packet_type.keys():
                reply_packet_type.setdefault(dst, {}).setdefault(src, {})[sze] = 1
            else:
                if src not in reply_packet_type[dst].keys():
                    reply_packet_type[dst].setdefault(src, {})[sze] = 1
                else:
                    if sze not in reply_packet_type[dst][src].keys():
                        reply_packet_type[dst][src][sze] = 1
                    else:
                        reply_packet_type[dst][src][sze] += 1
    for k, v in request_trace.items():
        if v not in request_window.keys():
            request_window[v] = 1
        else:
            request_window[v] += 1
    for k, v in reply_trace.items():
        if v not in reply_window.keys():
            reply_window[v] = 1
        else:
            reply_window[v] += 1
    source = dict(sorted(source.items(), key=lambda x: x[0]))
    destination = dict(sorted(destination.items(), key=lambda x: x[0]))
    for src in destination.keys():
        destination[src] = dict(sorted(destination[src].items(), key=lambda x: x[0]))
    request_packet_type = dict(sorted(request_packet_type.items(), key=lambda x: x[0]))
    for src in request_packet_type.keys():
        request_packet_type[src] = dict(sorted(request_packet_type[src].items(), key=lambda x: x[0]))
        for dst in request_packet_type[src].keys():
            request_packet_type[src][dst] = dict(sorted(request_packet_type[src][dst].items(), key=lambda x: x[0]))
    reply_packet_type = dict(sorted(reply_packet_type.items(), key=lambda x: x[0]))
    for src in reply_packet_type.keys():
        reply_packet_type[src] = dict(sorted(reply_packet_type[src].items(), key=lambda x: x[0]))
        for dst in reply_packet_type[src].keys():
            reply_packet_type[src][dst] = dict(sorted(reply_packet_type[src][dst].items(), key=lambda x: x[0]))
    request_window = dict(sorted(request_window.items(), key=lambda x: x[0]))
    reply_window = dict(sorted(reply_window.items(), key=lambda x: x[0]))
    return source, destination, request_packet_type, reply_packet_type, request_window, reply_window


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
        if packet.split("\t")[0] == "request injected":
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
        if packet.split("\t")[0] == "request injected":
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
    burst_volume_chain = dict(sorted(burst_volume_chain.items(), key=lambda x: x[0]))
    for dur in burst_volume_chain.keys():
        burst_volume_chain[dur] = dict(sorted(burst_volume_chain[dur].items(), key=lambda x: x[0]))
    return cycle, iat, burst_duration_chain, burst_volume_chain


def generate_memory_latency(request_packet):
    trace = {}
    latency = {}
    for packet in request_packet:
        if int(packet.split("\t")[3].split(": ")[1]) not in trace.keys():
            trace.setdefault(int(packet.split("\t")[3].split(": ")[1]), []).append(packet)
        else:
            trace[int(packet.split("\t")[3].split(": ")[1])].append(packet)
    for id, packet in trace.items():
        start = 0
        for step in packet:
            if step.split("\t")[0] == "request received":
                start = int(step.split("\t")[5].split(": ")[1])
            elif step.split("\t")[0] == "reply injected":
                end = int(step.split("\t")[5].split(": ")[1])
                chip = int(step.split("\t")[6].split(": ")[1])
                if chip not in latency.keys():
                    latency.setdefault(chip, {})[end - start] = 1
                else:
                    if end - start not in latency[chip].keys():
                        latency[chip][end - start] = 1
                    else:
                        latency[chip][end - start] += 1
    latency = dict(sorted(latency.items(), key=lambda x: x[0]))
    for src in latency.keys():
        latency[src] = dict(sorted(latency[src].items(), key=lambda x: x[0]))
    return latency


def generate_network_centric_model(request_packet, level):
    data = {}
    iat = {}
    burst = {}
    cycle = {}
    burst_volume = {}
    burst_duration = {}
    source = {}
    destination = {}
    request_packet_type = {}
    reply_packet_type = {}
    request_window = {}
    latency = {}
    reply_window = {}
    if level == "level1":
        cycle, iat, burst = generate_temporal_burst_level1(request_packet)
        source, destination, request_packet_type, reply_packet_type, request_window, reply_window = generate_spatial_burst_level1(request_packet)
        latency = generate_memory_latency(request_packet)
    elif level == "level2":
        cycle, iat, burst = generate_temporal_burst_level2(request_packet)
    elif level == "level3":
        cycle, iat, burst_duration, burst_volume = generate_temporal_burst_level3(request_packet)

    if level == "level1":
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
        data.setdefault("spatial", {}).setdefault("request_window", {})
        data["spatial"]["request_window"] = request_window
        #data.setdefault("spatial", {}).setdefault("source", {})
        data["spatial"]["source"] = source
        data["spatial"].setdefault("chip", {})
        per_core = {}
        for src in destination.keys():
            if src not in per_core.keys():
                per_core.setdefault(src, {})
        for src in source.keys():
            if src not in per_core.keys():
                per_core.setdefault(src, {})
        for src in destination.keys():
            per_core[src]["destination"] = destination[src]
        for src in request_packet_type.keys():
            per_core[src]["request_packet"] = request_packet_type[src]
        for src in reply_packet_type.keys():
            if src not in per_core.keys():
                per_core.setdefault(src, {})
            per_core[src]["reply_packet"] = reply_packet_type[src]
        for src in latency.keys():
            per_core[src]["latency"] = latency[src]
        data["spatial"]["chip"] = per_core
        data["spatial"].setdefault("reply_window", {})
        data["spatial"]["reply_window"] = reply_window
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
