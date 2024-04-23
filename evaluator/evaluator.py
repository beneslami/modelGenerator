import os
import sys
sys.path.append("..")
import utils
import benchlist
import numpy as np
import temporal_analysis
import latency_analysis
import throughput_analysis


if __name__ == "__main__":
    LEVEL = "level1"
    ######################################-burst analysis-#######################################
    for nv in ["NVLink4", "NVLink3", "NVLink2", "NVLink1"]:
        burst_comparison_out = [",,,IAT,IAT,IAT,Burst_int,Burst_int,Burst_int",
                                ",,kernel,hellinger,MAE,hurst,hellinger,MAE,hurst"]
        for suite in benchlist.kernels_list.keys():
            for bench, k_list in benchlist.kernels_list[suite].items():
                for kernel in k_list:
                    fullsystem_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/" + str(kernel) + "/"
                    synthetic_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/" + str(kernel) + "/"
                    output_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/" + str(kernel) + "/"
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    hell_iat, mae_iat, hurst_iat, hell_int, mae_int, hurst_int = temporal_analysis.burst_comparison(fullsystem_path, synthetic_path, output_path)
                    burst_string = suite + "," + bench + "," + str(kernel) + "," + str(hell_int) + "," + str(mae_int) + "," + str(hurst_iat) + "," + str(hell_int) + "," + str(mae_int) + "," + str(hurst_int)
                    burst_comparison_out.append(burst_string)
        with open(benchlist.path + "burst_analysis_" + nv + ".csv", "w") as file:
            for string in burst_comparison_out:
                file.write(string)

    #######################################-packet latency difference (hellinger)-######################################
    packet_latency_hellinger = [",,,Hellinger distance for packet latency distribution,Hellinger distance for packet "
                                "latency distribution,Hellinger distance for packet latency distribution,Hellinger "
                                "distance for packet latency distribution", ",,kernel,NVLink4,NVLink3,NVLink2,NVLink1"]
    for suite in benchlist.kernels_list.keys():
        for bench, k_list in benchlist.kernels_list[suite].items():
            for kernel in k_list:
                packet_latency_string = suite + "," + bench + "," + str(kernel) + ","
                for nv in ["NVLink4", "NVLink3", "NVLink2", "NVLink1"]:
                    fullsystem_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/" + str(
                        kernel) + "/"
                    synthetic_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/" + str(
                        kernel) + "/"
                    output_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/" + str(
                        kernel) + "/"
                    request_packet = utils.capture_requests(synthetic_path, "trace_0.txt")  # TODO: double check later
                    synthetic_packet_latency_freq = latency_analysis.capture_packet_latency(request_packet)
                    packet_latency_hellinger = latency_analysis.compare_packet_latency(fullsystem_path, synthetic_packet_latency_freq, output_path)
                    packet_latency_string += str(packet_latency_hellinger)
                packet_latency_hellinger.append(packet_latency_string)
    with open(benchlist.path + "packet_latency_hellinger.csv", "w") as file:
        for string in packet_latency_hellinger:
            file.write(string)

    ########################################-relative/absolute average latency/throughput-######################################
    absolute_throughput_err = [",,,NVLink1,NVLink2,NVLink3,NVLink4"]
    absolute_packet_latency_err = [",,,NVLink1,NVLink2,NVLink3,NVLink4"]
    absolute_network_latency_err = [",,,NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_throughput = [",,,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_packet_latency = [",,,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_network_latency = [",,,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4"]
    absolute_ipc = [",,,NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_ipc = [",,,NVLink1,NVLink2,NVLink3,NVLink4"]
    for suite in benchlist.kernels_list.keys():
        for bench, k_list in benchlist.kernels_list[suite].items():
            for kernel in k_list:
                abs_thr_string = suite + "," + bench + "," + str(kernel) + ","
                abs_plat_string = suite + "," + bench + "," + str(kernel) + ","
                abs_nlat_string = suite + "," + bench + "," + str(kernel) + ","
                rel_thr_string = suite + "," + bench + "," + str(kernel) + ","
                rel_plat_string = suite + "," + bench + "," + str(kernel) + ","
                rel_nlat_string = suite + "," + bench + "," + str(kernel) + ","
                syn_rel_thr_string = ""
                syn_rel_plat_string = ""
                syn_rel_nlat_string = ""
                thr_real = ["full system,"]
                thr_synt = ["synthetic,"]
                plat_real = ["full system,"]
                plat_synt = ["synthetic,"]
                nlat_real = ["full system,"]
                nlat_synt = ["synthetic,"]
                plat_temp = 0
                nlat_temp = 0
                thro_temp = 0
                syn_plat_temp = 0
                syn_nlat_temp = 0
                syn_thro_temp = 0
                for nv in ["NVLink1", "NVLink2", "NVLink3", "NVLink4"]:
                    fullsystem_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/" + str(kernel) + "/accelsim.csv"
                    synthetic_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/" + str(kernel) + "/booksim.txt"
                    output_path = benchlist.path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/" + str(kernel) + "/"
                    real_thr, synthetic_thr = throughput_analysis.collect_throughput(fullsystem_path, synthetic_path)
                    thr_real[0] += str(real_thr) + ","
                    thr_synt[0] += str(synthetic_thr) + ","
                    real_plat, synthetic_plat = latency_analysis.collect_packet_latency(fullsystem_path, synthetic_path)
                    plat_real[0] += str(real_plat) + ","
                    plat_synt[0] += str(synthetic_plat) + ","
                    real_nlat, synthetic_nlat = latency_analysis.collect_network_latency(fullsystem_path, synthetic_path)
                    abs_thr_string += str(np.abs(real_thr - synthetic_thr)) + ","
                    abs_plat_string += str(np.abs(real_plat - synthetic_plat)) + ","
                    abs_nlat_string += str(np.abs(real_nlat - synthetic_nlat)) + ","
                    if nv == "NVLink1":
                        plat_temp = real_plat
                        nlat_temp = real_nlat
                        thro_temp = real_thr
                        syn_plat_temp = synthetic_plat
                        syn_nlat_temp = synthetic_nlat
                        syn_thro_temp = synthetic_thr
                        rel_thr_string += str(1) + ","
                        rel_plat_string += str(1) + ","
                        rel_nlat_string += str(1) + ","
                        syn_rel_thr_string += str(1) + ","
                        syn_rel_plat_string += str(1) + ","
                        syn_rel_nlat_string += str(1) + ","
                    else:
                        rel_thr_string += str(real_thr/thro_temp) + ","
                        rel_plat_string += str(real_plat/plat_temp) + ","
                        rel_nlat_string += str(real_nlat/nlat_temp) + ","
                        syn_rel_thr_string += str(synthetic_thr/syn_thro_temp) + ","
                        syn_rel_plat_string += str(synthetic_plat/syn_plat_temp) + ","
                        syn_rel_nlat_string += str(synthetic_nlat/syn_nlat_temp) + ","

                rel_thr_string += syn_rel_thr_string
                rel_plat_string += syn_rel_plat_string
                rel_nlat_string += syn_rel_nlat_string
                absolute_throughput_err.append(abs_thr_string)
                absolute_packet_latency_err.append(abs_plat_string)
                absolute_network_latency_err.append(abs_nlat_string)
                relative_throughput.append(rel_thr_string)
                relative_packet_latency.append(rel_plat_string)
                relative_network_latency.append(rel_nlat_string)
                with open(output_path + "absolute_throughput_" + str(kernel) + ".csv", "w") as file:
                    file.write("AVG throughput,NVLink1,NVLink2,NVLink3,NVLink4")
                    file.write(thr_real[0])
                    file.write(thr_synt[0])
                    file.write(abs_thr_string)
                with open(output_path + "absolute_packet_latency_" + str(kernel) + ".csv", "w") as file:
                    file.write("AVG throughput,NVLink1,NVLink2,NVLink3,NVLink4")
                    file.write(plat_real[0])
                    file.write(plat_synt[0])
                    file.write(abs_plat_string)
                with open(output_path + "absolute_network_latency_" + str(kernel) + ".csv", "w") as file:
                    file.write("AVG throughput,NVLink1,NVLink2,NVLink3,NVLink4")
                    file.write(nlat_real[0])
                    file.write(nlat_synt[0])
                    file.write(abs_nlat_string)

    with open(benchlist.path + "absolute_throughput_error.csv", "w") as file:
        for item in absolute_throughput_err:
            file.write(item)
    with open(benchlist.path + "absolute_packet_latency_error.csv", "w") as file:
        for item in absolute_packet_latency_err:
            file.write(item)
    with open(benchlist.path + "absolute_network_latency_error.csv", "w") as file:
        for item in absolute_network_latency_err:
            file.write(item)
    with open(benchlist.path + "relative_throughput.csv", "w") as file:
        for item in relative_throughput:
            file.write(item)
    with open(benchlist.path + "relative_packet_latency", "w") as file:
        for item in relative_packet_latency:
            file.write(item)
    with open(benchlist.path + "relative_network_latency", "w") as file:
        for item in relative_network_latency:
            file.write(item)