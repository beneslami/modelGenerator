import os


def extract_traffic(file_name):
    file = open(file_name, "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    file.close()
    request_packet = []
    for line in raw_content:
        if "request injected" in line.split("\t")[0]:
            request_packet.append(line)
    del (raw_content)
    return request_packet


def generate_temporal_burst(request_packet):
    trace = {}
    iat = []
    burst = []
    combo = []
    for packet in request_packet:
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


if __name__ == "__main__":
    path = ""
    kernels_list = {"SDK": {"conjugate-gradient": [2, 3]},
                    "pannotia": {"color-max": [1],
                                 "color-maxmin": [2, 3, 4, 5, 7, 8, 9, 10],
                                 "pagerank-spmv": [2, 3, 5, 7, 9],
                                 "sssp": [3, 6, 9]},
                    "rodinia": {"cfd": [3]},
                    "polybench": {"syr2k": [1]}
    }
    for suite in ["SDK", "pannotia", "parboil", "rodinia", "polybench"]:
        for bench in ["conjugate-gradient", "pagerank-spmv", "sssp", "color-max", "color-maxmin", "cfd", "syr2k", "spmv", "mri-gridding"]:
            file_path = path + suite + "/" + bench + "/ring/NVLink4/4chiplet/"
            if os.path.exists(file_path):
                for name in os.listdir(file_path + "kernels/"):
                    if int(name.split(".")[0].split("_")[-1]) in kernels_list[suite][bench]:
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