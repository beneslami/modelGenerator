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
    plt.savefig(bench_path + "synthetic/" + LEVEL + "/" + "iat_CDF.jpg")
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
    plt.savefig(bench_path + "synthetic/" + LEVEL + "/" + "burst_intensity_CDF.jpg")
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
    plt.savefig(bench_path + "synthetic/" + LEVEL + "/" + string + "_ACF.jpg")
    plt.close()
    return utils.measure_cosine_similarity(vals["synthetic"], vals["real"]), utils.measure_euclidean(vals["synthetic"], vals["real"])


if __name__ == "__main__":
    LEVEL = "level2"
    path = "/home/ben/Desktop/benchmarks/"
    kernels_list = {"SDK": {"conjugate-gradient": [2, 3]},
                    "pannotia": {"color-max": [1],
                                 "color-maxmin": [2, 3, 4, 5, 7, 8, 9, 10],
                                 "pagerank-spmv": [2, 3, 5, 7, 9],
                                 "sssp": [3, 6, 9]},
                    "polybench": {"syr2k": [1]},
                    "parboil": {"spmv": [1],
                               "mri-gridding": [1]},
                    "cutlass": {"splitk-gemm": [2],
                                "gemm": [1, 2, 3]},
                    "deepbench": {"rnn": [4, 8, 10],
                                  "gemm": [3, 6]}
                    }
    #kernels_list = {"SDK": {"conjugate-gradient": [3]}}
    output = []
    output.append(",,,IAT Error, IAT Error, IAT Error, IAT Error, Intensity Error, Intensity Error, Intensity Error, Intensity Error",)
    output.append(",,kernel, hellinger, MAE, Cosine, Euclidean, hellinger, MAE, Cosine, Euclidean")
    for suite in kernels_list.keys():
        for bench, k_list in kernels_list[suite].items():
            for kernel in k_list:
                bench_path = path + suite + "/" + bench + "/ring/NVLink4/4chiplet/data/" + str(kernel) + "/"
                synthetic_path = bench_path + "synthetic/" + LEVEL + "/"
                real_path = bench_path
                iat = {"real": [], "synthetic": []}
                intensity = {"real": [], "synthetic": []}
                temporal = {"real": [], "synthetic": []}

                for file_n in ["iat", "intensity", "temporal"]:
                    for f in os.listdir(synthetic_path):
                        if file_n in f and f.split(".")[1] == "txt":
                            with open(synthetic_path + f, "r") as list_file:
                                syn_content = list_file.readlines()
                    for f in os.listdir(real_path):
                        if file_n in f and f.split(".")[1] == "txt":
                            with open(real_path + f, "r") as list_file:
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
                c_tmp, euc_tmp = compare_autocorrelation(temporal, bench_path, "temporal")
                h_iat, mae_iat = compare_iat(iat, bench_path)
                c_iat, euc_iat = compare_autocorrelation(iat, bench_path, "iat")
                h_int, mae_int = compare_intensity(intensity, bench_path)
                c_int, euc_int = compare_autocorrelation(intensity, bench_path, "intensity")
                output.append(suite + "," + bench + "," + str(kernel) + "," + "{:.3f}".format(h_iat) + "," +
                            "{:.3f}".format(mae_iat) + "," + "{:.3f}".format(c_iat) + "," + "{:.3f}".format(euc_iat)
                            + "," + "{:.3f}".format(h_int) + "," + "{:.3f}".format(mae_int) + "," +
                            "{:.3f}".format(c_int) + "," + "{:.3f}".format(euc_int))
    with open(path + LEVEL + ".csv", "w") as file:
        for item in output:
            file.write(item + "\n")
