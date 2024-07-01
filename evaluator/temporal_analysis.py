import matplotlib.pyplot as plt
import sys
sys.path.append("..")
import utils
from modelGen import markov
import os
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
    syn_hurst = utils.compute_hurst(iat["synthetic"])
    ful_hurst = utils.compute_hurst(iat["real"])
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
    syn_hurst = utils.compute_hurst(intensity["synthetic"])
    ful_hurst = utils.compute_hurst(intensity["real"])
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


def capture_burst(synthetic_path):
    selected_trace = utils.select_trace(synthetic_path)
    with open(synthetic_path + selected_trace, "r") as file:
        content = file.readlines()
    trace = {}
    iat = []
    burst = []
    combo = []
    for packet in content:
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
            burst.append(volume / burst_duration)
            combo.append(volume / burst_duration)
            combo.append(cycle - prev_off - 1)
            volume = byte
            prev_on = cycle
            prev_off = cycle
        else:
            prev_off = cycle
            volume += byte
    with open(synthetic_path + "iat_sequence.txt", "w") as file:
        for num in iat:
            file.write(str(num) + "\n")
    with open(synthetic_path + "burst_intensity_sequence.txt", "w") as file:
        for num in burst:
            file.write(str(num) + "\n")
    with open(synthetic_path + "temporal_sequence.txt", "w") as file:
        for num in combo:
            file.write(str(num) + "\n")


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
                with open(fullsystem_path + f, "r") as list_file2:
                    real_content = list_file2.readlines()
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