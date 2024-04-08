import os
import markov
import matplotlib.pyplot as plt
import utils


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

    return utils.measure_hellinger(cmp_cdf["synthetic"], cmp_cdf["real"]), utils.measure_MAE(cmp_cdf["synthetic"], cmp_cdf["real"])


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
    return utils.measure_hellinger(cmp_cdf["synthetic"], cmp_cdf["real"]), utils.measure_MAE(cmp_cdf["synthetic"], cmp_cdf["real"])


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

    for suite in kernels_list.keys():
        for bench, k_list in kernels_list[suite].items():
            for nv in ["NVLink4", "NVLink3", "NVLink2", "NVLink1"]:
                for kernel in k_list:
                    fullsystem_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/"
                    synthetic_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/"
                    output_path = path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/"
                    iat = {"real": [], "synthetic": []}
                    intensity = {"real": [], "synthetic": []}
                    temporal = {"real": [], "synthetic": []}

                    if not os.path.exists(synthetic_path):
                        os.makedirs(synthetic_path)
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)

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
                    hell_iat, mae_iat = compare_iat(iat, output_path)
                    hell_int, mae_int = compare_intensity(intensity, output_path)

                    c_tmp, euc_tmp = compare_autocorrelation(temporal, bench_path, "temporal")
                    c_iat, euc_iat = compare_autocorrelation(iat, bench_path, "iat")
                    c_int, euc_int = compare_autocorrelation(intensity, bench_path, "intensity")

    with open(path + LEVEL + ".csv", "w") as file:
        for item in output:
            file.write(item)
