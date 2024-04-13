import os
import benchlist


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


def collect_output_numbers(suite, bench, kernel_id, file_path, save_path):
    string = ""
    for item in os.listdir(file_path):
        if (suite in item) and (bench in item) and ("1vc") in item and ("4ch") in item:
            with open(file_path + item, "r") as file:
                content = file.readlines()
            flag1 = 0
            flag2 = 0
            flag3 = 0
            flag4 = 0
            flag5 = 0
            for line in content:
                if "-kernel id" in line.split(" = ")[0] and kernel_id == int(line.split(" = ")[1]):
                    flag1 = 1
                if flag1 == 1:
                    if "Number of Local Requests" in line:
                        string += ("local_request," + str(line.split(": ")[2]))
                    elif "Number of Remote Requests" in line:
                        string += ("remote_request," + line.split(": ")[2])
                    elif "gpu_sim_cycle" in line.split(" = ")[0]:
                        string += ("gpu_cycle," + (line.split(" = ")[1]))
                    elif "gpu_sim_insn" in line.split(" = ")[0]:
                        string += ("instruction," + (line.split(" = ")[1]))
                    elif "gpu_ipc" in line.split(" = ")[0]:
                        string += ("ipc," + (line.split(" = ")[1]))
                    elif "gpu_tot_issued_cta" in line.split(" = ")[0]:
                        string += ("CTA," + (line.split(" = ")[1]))
                    elif "gpu_occupancy" in line.split(" = ")[0]:
                        string += ("GPU_occupancy," + line.split(" = ")[1])
                    elif "gpu_throughput" in line.split(" = ")[0]:
                        string += ("throughput," + (line.split(" = ")[1]))
                    elif "partiton_level_parallism" in line.split(" = ")[0] and "total" not in line.split(" = ")[0] and "util" not in line.split(" = ")[0]:
                        string += ("partition_lvel_parallelism," + (line.split(" = ")[1]))
                    elif "partiton_level_parallism_util" in line.split(" = ")[0] and "total" not in line.split(" = ")[0]:
                        string += ("partition_lvel_parallelism_util," + (line.split(" = ")[1]))
                    elif "L1D_total_cache_accesses" in line.split(" = ")[0]:
                        string += ("L1D_total_access," + (line.split(" = ")[1]))
                    elif "L1D_total_cache_misses" in line.split(" = ")[0]:
                        string += ("L1D_total_miss," + (line.split(" = ")[1]))
                    elif "L1D_total_cache_miss_rate" in line.split(" = ")[0]:
                        string += ("L1D_miss_rate," + (line.split(" = ")[1]))
                    elif "gpgpu_n_mem_read_global" in line.split(" = ")[0]:
                        string += ("total_mem_read," + (line.split(" = ")[1]))
                    elif "gpgpu_n_mem_write_global" in line.split(" = ")[0]:
                        string += ("total_mem_write," + (line.split(" = ")[1]))
                    elif "gpgpu_n_load_insn" in line.split(" = ")[0]:
                        string += ("total_load_inst," + (line.split(" = ")[1]))
                    elif "gpgpu_n_store_insn" in line.split(" = ")[0]:
                        string += ("total_store_inst," + (line.split(" = ")[1]))
                    elif "gpgpu_n_shmem_insn" in line.split(" = ")[0]:
                        string += ("total_shmem_inst," + (line.split(" = ")[1]))
                        #pass
                    #elif "traffic_breakdown_coretomem[GLOBAL_ACC_W]" in line.split(" = ")[0]:
                        #per_ker_out.append()  # 5250600 {40:131265,}
                        #pass
                    #elif "traffic_breakdown_memtocore[GLOBAL_ACC_R]" in line.split(" = ")[0]:
                        #per_ker_out.append()  # 474760 {40:11869,}
                        #pass
                    #elif "traffic_breakdown_memtocore[GLOBAL_ACC_W]" in line.split(" = ")[0]:
                        #per_ker_out.append()  # 1050120 {8:131265,}
                        #pass
                    elif "maxmflatency" in line.split(" = ")[0]:
                        string += ("maxflatency," + (line.split(" = ")[1]))
                    elif "max_icnt2mem_latency" in line.split(" = ")[0]:
                        string += ("max_icnt2mem_latency," + (line.split(" = ")[1]))
                    elif "maxmrqlatency" in line.split(" = ")[0]:
                        string += ("maxmrqlatency," + (line.split(" = ")[1]))
                    elif "max_icnt2sh_latency" in line.split(" = ")[0]:
                        string += ("max_icnt2sh_latency," + (line.split(" = ")[1]))
                    elif "averagemflatency" in line.split(" = ")[0]:
                        string += ("averageflatency," + (line.split(" = ")[1]))
                    elif "avg_icnt2mem_latency" in line.split(" = ")[0]:
                        string += ("avg_icnt2mem_latency," + (line.split(" = ")[1]))
                    elif "avg_mrq_latency" in line.split(" = ")[0]:
                        string += ("avg_mrq_latency," + (line.split(" = ")[1]))
                    elif "avg_icnt2sh_latency" in line.split(" = ")[0]:
                        string += ("avg_icnt2sh_latency," + (line.split(" = ")[1]))
                    elif "L2_total_cache_accesses" in line.split(" = ")[0]:
                        string += ("L2_total_access," + (line.split(" = ")[1]))
                    elif "L2_total_cache_misses" in line.split(" = ")[0]:
                        string += ("L2_total_miss," + (line.split(" = ")[1]))
                    elif "L2_total_cache_miss_rate" in line.split(" = ")[0]:
                        string += ("L2_miss_rate," + (line.split(" = ")[1]))
                    elif "chLet-DETAILS" in line:
                        flag2 = 1
                    elif "Packet latency average" in line.split(" = ")[0] and flag2 == 1:
                        string += ("average packet latency," + str(line.split(" = ")[1]))
                        flag3 = 1
                    elif "\tminimum = " in line and flag3 == 1:
                        string += ("min packet latency," + str(line.split(" = ")[1]))
                    elif "\tmaximum = " in line and flag3 == 1:
                        string += ("max packet latency," + str(line.split(" = ")[1]))
                        flag3 = 0
                    elif "Network latency average" in line.split(" = ")[0] and flag2 == 1:
                        string += ("average network latency," + str(line.split(" = ")[1]))
                        flag4 = 1
                    elif "\tminimum = " in line and flag4 == 1:
                        string += ("min network latency," + str(line.split(" = ")[1]))
                    elif "\tmaximum = " in line and flag4 == 1:
                        string += ("max network latency," + str(line.split(" = ")[1]))
                        flag4 = 0
                    elif "Injected packet rate average" in line.split(" = ")[0] and flag2 == 1:
                        string += ("average injection rate," + str(line.split(" = ")[1]))
                        flag5 = 1
                    elif "\tminimum = " in line and flag5 == 1:
                        string += ("min injection rate," + str(line.split(" = ")[1].split(" ")[0]) + "," + str(line.split(" = ")[1].split(" ")[-1][:-2]) + "\n")
                    elif "\tmaximum = " in line and flag5 == 1:
                        string += ("max injection rate," + str(line.split(" = ")[1].split(" ")[0]) + "," + str(line.split(" = ")[1].split(" ")[-1][:-2]))
                        flag5 = 0
                        flag4 = 0
                        flag1 = 0
                        flag2 = 0
                        break
            with open(save_path + "/accelsim.csv", "w") as file:
                file.write(string)
            break


if __name__ == "__main__":
    for suite in benchlist.kernels_list.keys():
        for bench in benchlist.kernels_list[suite].keys():
            for nv in ["NVLink4", "NVLink3", "NVLink2", "NVLikn1"]:
                file_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/"
                if os.path.exists(file_path):
                    for name in os.listdir(file_path + "kernels/"):
                        if (not os.path.isdir(name)) and int(name.split(".")[0].split("_")[-1]) in benchlist.kernels_list[suite][bench]:
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
                                    file.write(str(num))
                            with open(save_path + "/burst_intensity_sequence.txt") as file:
                                for num in burst:
                                    file.write(str(num))
                            with open(save_path + "/temporal_sequence.txt") as file:
                                for num in combo:
                                    file.write(str(num))
                            latency = packet_latency_dist(request)
                            with open(save_path + "/packet_latency_dist.csv") as file:
                                for k, v in latency.items():
                                    file.write(str(k) + "," + str(v))
                    for i in benchlist.kernels_list[suite][bench]:
                        collect_output_numbers(suite, bench, i, file_path, file_path + "data/" + str(i) + "/")