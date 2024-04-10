import os
import markov
import matplotlib.pyplot as plt
import utils
import numpy as np


def compare_iat(iat, bench_path):
    cmp_cdf = {}
    plt.figure(figsize=(10, 8))
    hurst = {"real": 0, "synthetic": 0}
    for tp in iat.keys():
        hurst[tp] = utils.compute_hurst(iat[tp])
        _, cdf = utils.generate_pdf_cdf(iat[tp])
        plt.plot(cdf.keys(), cdf.values(), marker="o", label=tp + "- hurst: " + str("{:.3f}".format(hurst[tp])))
        cmp_cdf[tp] = cdf
        markov.measure_markov_property_wrapper(iat[tp], tp, bench_path)
    plt.legend()
    plt.title("Inter Arrival Time")
    plt.ylabel("CDF")
    plt.xlabel("cycle")
    plt.tight_layout()
    plt.savefig(bench_path + "iat_CDF.jpg")
    plt.close()
    syn_hurst = utils.compute_hurst(cmp_cdf["synthetic"])
    ful_hurst = utils.compute_hurst(cmp_cdf["real"])
    return utils.measure_hellinger(cmp_cdf["synthetic"], cmp_cdf["real"]), utils.measure_MAE(cmp_cdf["synthetic"], cmp_cdf["real"]), (np.abs(syn_hurst - ful_hurst))


def compare_intensity(intensity, bench_path):
    cmp_cdf = {}
    plt.figure(figsize=(10, 8))
    for tp in intensity.keys():
        _, cdf = utils.generate_pdf_cdf(intensity[tp])
        plt.plot(cdf.keys(), cdf.values(), marker="o", label=tp)
        cmp_cdf[tp] = cdf
    plt.legend()
    plt.title("burst Intensity")
    plt.ylabel("CDF")
    plt.xlabel("Intensity (volume / duration)")
    plt.tight_layout()
    plt.savefig(bench_path + "burst_intensity_CDF.jpg")
    plt.close()
    syn_hurst = utils.compute_hurst(cmp_cdf["synthetic"])
    ful_hurst = utils.compute_hurst(cmp_cdf["real"])
    return utils.measure_hellinger(cmp_cdf["synthetic"], cmp_cdf["real"]), utils.measure_MAE(cmp_cdf["synthetic"], cmp_cdf["real"]), np.abs(syn_hurst - ful_hurst)


def compare_autocorrelation(iat, bench_path, string):
    vals = utils.generate_autocorrelation(iat)
    plt.figure(figsize=(10, 8))
    for k, v in vals.items():
        plt.plot(v.keys(), v.values(), label=k)
    plt.legend()
    plt.title("ACF")
    plt.xlabel("lag")
    plt.ylabel("correlation coefficient")
    plt.tight_layout()
    plt.savefig(bench_path + string + "_ACF.jpg")
    plt.close()
    return utils.measure_cosine_similarity(vals["synthetic"], vals["real"]), utils.measure_euclidean(vals["synthetic"], vals["real"])


def burst_comparison(fullsystem_path, synthetic_path, save_path):
    iat = {"real": [], "synthetic": []}
    intensity = {"real": [], "synthetic": []}
    temporal = {"real": [], "synthetic": []}

    for file_n in ["iat", "intensity", "temporal"]:
        syn_content = []
        real_content = []
        for f in os.listdir(synthetic_path):
            if file_n in f and f.split(".")[1] == "txt":
                with open(synthetic_path + f, "r") as list_file:
                    syn_content = list_file.readlines()
        for f in os.listdir(fullsystem_path):
            if file_n in f and f.split(".")[1] == "txt":
                with open(fullsystem_path + f, "r") as list_file:
                    real_content = list_file.readlines()
        if file_n == "iat":
            for line in syn_content:
                iat["synthetic"].append(int(line.split("\n")[0]))
            for line in real_content:
                iat["real"].append(int(line.split("\n")[0]))
        elif file_n == "intensity":
            for line in syn_content:
                intensity["synthetic"].append(float(line.split("\n")[0]))
            for line in real_content:
                intensity["real"].append(float(line.split("\n")[0]))
        elif file_n == "temporal":
            for line in syn_content:
                temporal["synthetic"].append(float(line.split("\n")[0]))
            for line in real_content:
                temporal["real"].append(float(line.split("\n")[0]))
    hell_iat, mae_iat, hurst_iat = compare_iat(iat, save_path)
    hell_int, mae_int, hurst_int = compare_intensity(intensity, save_path)

    c_tmp, euc_tmp = compare_autocorrelation(temporal, save_path, "temporal")
    c_iat, euc_iat = compare_autocorrelation(iat, save_path, "iat")
    c_int, euc_int = compare_autocorrelation(intensity, save_path, "intensity")

    return hell_iat, mae_iat, hurst_iat, hell_int, mae_int, hurst_int


def capture_packet_latency(request_packet):
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


def compare_packet_latency(fullsystem_path, synthetic_packet_latency_freq, output_path):
    real_packet_latency_freq = {}
    with open(fullsystem_path + "packet_latency_dist.csv", "r") as file:
        content = file.readlines()
    for item in content:
        real_packet_latency_freq[int(item.split(",")[0])] = int(item.split(",")[1])
    _, real_cdf = utils.generate_pdf_cdf(real_packet_latency_freq)
    _, synt_cdf = utils.generate_pdf_cdf(synthetic_packet_latency_freq)
    plt.plot(real_cdf.keys(), real_cdf.values(), label="AccelSim")
    plt.plot(synt_cdf.keys(), synt_cdf.values(), label="AccelSim")
    plt.legend()
    plt.title("packet latency CDF")
    plt.tight_layout()
    plt.savefig(output_path + "packet_latency_CDF.jpg")
    plt.close()
    hell = utils.measure_hellinger(real_cdf, synt_cdf)
    return hell


def capture_network_latency(fullsystem_path, synthetic_packet_latency_freq, output_path):
    pass


if __name__ == "__main__":
    LEVEL = "level1"
    path = "/home/ben/Desktop/benchmarks/"
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
    ######################################-burst analysis-#######################################
    for nv in ["NVLink4", "NVLink3", "NVLink2", "NVLink1"]:
        burst_comparison_out = [",,,IAT,IAT,IAT,Burst_int,Burst_int,Burst_int",
                                ",,kernel,hellinger,MAE,hurst,hellinger,MAE,hurst"]
        for suite in kernels_list.keys():
            for bench, k_list in kernels_list[suite].items():
                for kernel in k_list:
                    fullsystem_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/" + str(kernel) + "/"
                    synthetic_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/" + str(kernel) + "/"
                    output_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/" + str(kernel) + "/"
                    if not os.path.exists(synthetic_path):
                        os.makedirs(synthetic_path)
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    hell_iat, mae_iat, hurst_iat, hell_int, mae_int, hurst_int = burst_comparison(fullsystem_path, synthetic_path, output_path)
                    burst_string = suite + "," + bench + "," + str(kernel) + "," + str(hell_int) + "," + str(mae_int) + "," + str(hurst_iat) + "," + str(hell_int) + "," + str(mae_int) + "," + str(hurst_int)
                    burst_comparison_out.append(burst_string)
        with open(path + "burst_analysis_" + nv + ".scv", "w") as file:
            for string in burst_comparison_out:
                file.write(string)

    #######################################-packet latency difference (hellinger)-######################################
    packet_latency_hellinger = [",,,Hellinger distance for packet latency distribution,Hellinger distance for packet "
                                "latency distribution,Hellinger distance for packet latency distribution,Hellinger "
                                "distance for packet latency distribution", ",,kernel,NVLink4,NVLink3,NVLink2,NVLink1"]
    for suite in kernels_list.keys():
        for bench, k_list in kernels_list[suite].items():
            for kernel in k_list:
                packet_latency_string = suite + "," + bench + "," + str(kernel) + ","
                for nv in ["NVLink4", "NVLink3", "NVLink2", "NVLink1"]:
                    fullsystem_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/" + str(
                        kernel) + "/"
                    synthetic_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/" + str(
                        kernel) + "/"
                    output_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/" + str(
                        kernel) + "/"
                    if not os.path.exists(synthetic_path):
                        os.makedirs(synthetic_path)
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    request_packet = utils.capture_requests(synthetic_path, "trace_0.txt")  # TODO: double check later
                    synthetic_packet_latency_freq = capture_packet_latency(request_packet)
                    packet_latency_hellinger = compare_packet_latency(fullsystem_path, synthetic_packet_latency_freq,
                                                                      output_path)
                    packet_latency_string += str(packet_latency_hellinger)
                    if nv != "NVLink1":
                        packet_latency_string += ","
                packet_latency_hellinger.append(packet_latency_string)
    with open(path + "packet_latency_hellinger.scv", "w") as file:
        for string in packet_latency_hellinger:
            file.write(string)

    ########################################-relative/absolute average latency/throughput-######################################
    absolute_throughput = ["avg throughput,NVLink1,NVLink2,NVLink3,NVLink4"]
    absolute_latency = ["avg latency,NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_throughput = ["throughput,NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_latency = ["throughput,NVLink1,NVLink2,NVLink3,NVLink4"]


