import os


def extract_traffic(file_name):
    file = open(file_name, "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    file.close()
    request_packet = []
    for line in raw_content:
        if "request injected" in line.split("\t")[0] or "request received" in line.split("\t")[0] or "reply injected" in line.split("\t")[0] or "reply received" in line.split("\t")[0]:
            request_packet.append(line)
    del (raw_content)
    return request_packet


def generate_temporal_burst(request_packet):
    trace = {}
    iat = []
    burst = []
    combo = []
    for packet in request_packet:
        if packet.split("\t")[0] == "request injected":
            if int(packet.split("\t")[5].split(": ")[1]) not in trace.keys():
                trace[int(packet.split("\t")[5].split(": ")[1])] = int(packet.split("\t")[7].split(": ")[1])
            else:
                trace[int(packet.split("\t")[5].split(": ")[1])] += int(packet.split("\t")[7].split(": ")[1])
    prev_off = int(list(trace.keys())[0])
    prev_on = int(list(trace.keys())[0])
    volume = 0
    for cycle, byte in trace.items():
        if cycle - prev_off > 1:
            if prev_on == prev_off:
                burst_duration = 1
            else:
                burst_duration = prev_off - prev_on
            iat.append(cycle - prev_off - 1)
            burst.append(volume/burst_duration)
            combo.append(volume / burst_duration)
            combo.append(cycle - prev_off - 1)
            volume = byte
            prev_on = cycle
            prev_off = cycle
        else:
            prev_off = cycle
            volume += byte
    return iat, burst, combo


def packet_latency_dist(request_packet):
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
            if packet.split("\t")[0] == "request injected":
               start = int(step.split("\t")[5].split(": ")[1])
            elif packet.split("\t")[0] == "request received" and start != 0:
                if int(step.split("\t")[5].split(": ")[1]) - start not in latency.keys():
                    latency[int(step.split("\t")[5].split(": ")[1]) - start] = 1
                else:
                    latency[int(step.split("\t")[5].split(": ")[1]) - start] += 1
                start = 0
            if packet.split("\t")[0] == "reply injected":
               start = int(step.split("\t")[5].split(": ")[1])
            elif packet.split("\t")[0] == "reply received" and start != 0:
                if int(step.split("\t")[5].split(": ")[1]) - start not in latency.keys():
                    latency[int(step.split("\t")[5].split(": ")[1]) - start] = 1
                else:
                    latency[int(step.split("\t")[5].split(": ")[1]) - start] += 1
                start = 0
    latency = dict(sorted(latency.items(), key=lambda x: x[0]))
    return latency


if __name__ == "__main__":
    path = ""
    kernels_list = {"SDK": {"conjugate-gradient": [2, 3],
                            "matrixmul": [1]},
                    "cutlass": {"splitk-gemm": [2]},
                    "deepbench": {"gemm": [3, 5, 6],
                                  "rnn": [4, 8, 10]},
                    "pannotia": {"color-max": [1],
                                 "color-maxmin": [2, 3, 4, 5, 7, 8, 9, 10],
                                 "pagerank-spmv": [2, 3, 5, 7, 9],
                                 "sssp": [3, 6, 9],
                                 "fw": [1],
                                 "pagerank": [2, 4]},
                    "parboil": {"mri-gridding": [1],
                                "spmv": [1],
                                "cutcp": [1]},
                    "polybnech": {"syrk": [1],
                                  "syr2k": [1],
                                  "2mm": [1],
                                  "gemm": [1]},
                    "rodinia": {"b+tree": [1, 2],
                                "bt": [1, 2],
                                "cfd": [3],
                                "gaussian": [2, 4, 6],
                                "hybridsort": [4, 5, 6, 7, 8, 9, 10],
                                "lud": [3, 6, 9]},
                    "shoc": {"FFT": [3]},
                    "UVM": {"lr": [1, 3, 6, 8, 11, 13]},
                    "tango": {"AlexNet": [1],
                            "ResNet": [1],
                            "SqueezeNet": [1]}
                    }
    for suite in kernels_list.keys():
        for bench in kernels_list[suite].keys():
            for nv in ["NVLink4", "NVLink3", "NVLink2", "NVLikn1"]:
                file_path = path + suite + "/" + bench + "/ring/NVLink4/4chiplet/"
                if os.path.exists(file_path):
                    for name in os.listdir(file_path + "kernels/"):
                        if (not os.path.isdir(name)) and int(name.split(".")[0].split("_")[-1]) in kernels_list[suite][bench]:
                            file_name = file_path + "kernels/" + name
                            request = extract_traffic(file_name)
                            iat, burst, combo = generate_temporal_burst(request)
                            if not os.path.exists(file_path + "data/"):
                                os.mkdir(file_path + "data/")
                            save_path = file_path + "data/" + str(name.split(".")[0].split("_")[-1])
                            if not os.path.exists(save_path):
                                os.mkdir(save_path)
                            with open(save_path + "/iat_sequence.txt") as file:
                                for num in iat:
                                    file.write(str(num) + "\n")
                            with open(save_path + "/burst_intensity_sequence.txt") as file:
                                for num in burst:
                                    file.write(str(num) + "\n")
                            with open(save_path + "/temporal_sequence.txt") as file:
                                for num in combo:
                                    file.write(str(num) + "\n")
                            latency = packet_latency_dist(request)
                            with open(save_path + "/packet_latency_dist.csv") as file:
                                for k, v in latency.items():
                                    file.write(str(k) + "," + str(v) + "\n")
                else:
                    print(suite + " " + bench + " not exist")