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
    if not os.path.exists(benchlist.model_eval_path + "OUTPUTS/" + LEVEL):
        os.makedirs(benchlist.model_eval_path + "OUTPUTS/" + LEVEL)
    ######################################-burst analysis-#######################################
    for nv in benchlist.NVLinks:
        burst_comparison_out = [",,,IAT,IAT,IAT,Burst_int,Burst_int,Burst_int", "suite,benchmark,kernel,hellinger,MAE,hurst,hellinger,MAE,hurst"]
        for suite in benchlist.kernels_list.keys():
            for bench, k_list in benchlist.kernels_list[suite].items():
                for kernel in k_list:
                    fullsystem_path = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/" + str(kernel) + "/"
                    synthetic_path = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/" + str(kernel) + "/"
                    output_path = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/" + str(kernel) + "/"
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    temporal_analysis.capture_burst(synthetic_path)
                    hell_iat, mae_iat, hurst_iat, hell_int, mae_int, hurst_int = temporal_analysis.burst_comparison(fullsystem_path, synthetic_path, output_path)
                    burst_string = suite + "," + bench + "," + str(kernel) + "," + str(hell_int) + "," + str(mae_int) + "," + str(hurst_iat) + "," + str(hell_int) + "," + str(mae_int) + "," + str(hurst_int)
                    burst_comparison_out.append(burst_string)
        with open(benchlist.model_eval_path + "OUTPUTS/" + LEVEL + "/burst_analysis_" + nv + ".csv", "w") as file:
            for string in burst_comparison_out:
                file.write(string + "\n")
    print("burst analysis finished")
    #######################################-packet latency difference (hellinger)-######################################
    packet_latency_hellinger = [",,,Hellinger distance for packet latency distribution,Hellinger distance for packet "
                                "latency distribution,Hellinger distance for packet latency distribution,Hellinger "
                                "distance for packet latency distribution", "suite,benchmark,kernel,NVLink1,NVLink2,NVLink3,NVLink4"]
    for suite in benchlist.kernels_list.keys():
        for bench, k_list in benchlist.kernels_list[suite].items():
            for kernel in k_list:
                packet_latency_string = suite + "," + bench + "," + str(kernel) + ","
                for nv in benchlist.NVLinks:
                    fullsystem_path = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/" + str(kernel) + "/"
                    synthetic_path  = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/" + str(kernel) + "/"
                    output_path     = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/" + str(kernel) + "/"
                    selected_trace = utils.select_trace(synthetic_path)
                    request_packet = utils.capture_requests(synthetic_path + selected_trace)
                    synthetic_packet_latency_freq = latency_analysis.capture_packet_latency(request_packet)
                    packet_lat_hellinger          = latency_analysis.compare_packet_latency(fullsystem_path, synthetic_packet_latency_freq, output_path)
                    packet_latency_string += str(packet_lat_hellinger) + ","
                packet_latency_hellinger.append(packet_latency_string)
    with open(benchlist.model_eval_path + "OUTPUTS/" + LEVEL + "/packet_latency_hellinger.csv", "w") as file:
        for string in packet_latency_hellinger:
            file.write(string + "\n")
    print("packet latency analysis finished")
    ########################################-relative/absolute average latency/throughput-######################################
    absolute_throughput_err = ["suite,benchmark,kernel,NVLink1,NVLink2,NVLink3,NVLink4"]
    absolute_packet_latency_err = ["suite,benchmark,kernel,NVLink1,NVLink2,NVLink3,NVLink4"]
    absolute_network_latency_err = ["suite,benchmark,kernel,NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_throughput = ["suite,benchmark,kernel,FullSystem,FullSystem,FullSystem,FullSystem,Synthetic,Synthetic,Synthetic,Synthetic", ",,,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_packet_latency = ["suite,benchmark,kernel,FullSystem,FullSystem,FullSystem,FullSystem,Synthetic,Synthetic,Synthetic,Synthetic", ",,,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_network_latency = ["suite,benchmark,kernel,FullSystem,FullSystem,FullSystem,FullSystem,Synthetic,Synthetic,Synthetic,Synthetic", ",,,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4"]
    absolute_ipc = ["suite,benchmark,kernel,NVLink1,NVLink2,NVLink3,NVLink4"]
    relative_ipc = ["suite,benchmark,kernel,NVLink1,NVLink2,NVLink3,NVLink4"]
    for suite in benchlist.kernels_list.keys():
        for bench, k_list in benchlist.kernels_list[suite].items():
            absolute_throughput = []
            absolute_packet_latency = []
            absolute_network_latency = []
            for kernel in k_list:
                abs_thr_string = str(kernel) + ","
                abs_thr_string_syn = ""
                abs_plat_string =str(kernel) + ","
                abs_plat_string_syn = ""
                abs_nlat_string = str(kernel) + ","
                abs_nlat_string_syn = ""
                err_thr_string = suite + "," + bench + "," + str(kernel) + ","
                err_plat_string = suite + "," + bench + "," + str(kernel) + ","
                err_nlat_string = suite + "," + bench + "," + str(kernel) + ","
                rel_thr_string = suite + "," + bench + "," + str(kernel) + ","
                rel_plat_string = suite + "," + bench + "," + str(kernel) + ","
                rel_nlat_string = suite + "," + bench + "," + str(kernel) + ","
                syn_rel_thr_string = ""
                syn_rel_plat_string = ""
                syn_rel_nlat_string = ""
                plat_temp = 0
                nlat_temp = 0
                thro_temp = 0
                syn_plat_temp = 0
                syn_nlat_temp = 0
                syn_thro_temp = 0
                for nv in benchlist.NVLinks:
                    fullsystem_path = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/fullsystem/" + str(kernel) + "/accelsim.csv"
                    synthetic_path = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/data/synthetic/" + LEVEL + "/" + str(kernel) + "/bookSim_output.txt"
                    output_path = benchlist.model_eval_path + suite + "/" + bench + "/ring/" + nv + "/4chiplet/output/" + LEVEL + "/" + str(kernel) + "/"
                    real_thr, synthetic_thr = throughput_analysis.collect_throughput(fullsystem_path, synthetic_path)
                    abs_thr_string += str(real_thr) + ","
                    abs_thr_string_syn += str(synthetic_thr) + ","
                    real_plat, synthetic_plat = latency_analysis.collect_packet_latency(fullsystem_path, synthetic_path)
                    abs_plat_string += str(real_plat) + ","
                    abs_plat_string_syn += str(synthetic_plat) + ","
                    real_nlat, synthetic_nlat = latency_analysis.collect_network_latency(fullsystem_path, synthetic_path)
                    abs_nlat_string += str(real_nlat) + ","
                    abs_nlat_string_syn += str(synthetic_nlat) + ","
                    err_thr_string += str(np.abs(float(real_thr) - float(synthetic_thr))) + ","
                    err_plat_string += str(np.abs(float(real_plat) - float(synthetic_plat))) + ","
                    err_nlat_string += str(np.abs(float(real_nlat) - float(synthetic_nlat))) + ","
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
                        rel_thr_string += str(float(real_thr)/float(thro_temp)) + ","
                        rel_plat_string += str(float(real_plat)/float(plat_temp)) + ","
                        rel_nlat_string += str(float(real_nlat)/float(nlat_temp)) + ","
                        syn_rel_thr_string += str(float(synthetic_thr)/float(syn_thro_temp)) + ","
                        syn_rel_plat_string += str(float(synthetic_plat)/float(syn_plat_temp)) + ","
                        syn_rel_nlat_string += str(float(synthetic_nlat)/float(syn_nlat_temp)) + ","
                abs_thr_string += abs_thr_string_syn
                abs_plat_string += abs_plat_string_syn
                abs_nlat_string += abs_nlat_string_syn
                absolute_throughput.append(abs_thr_string)
                absolute_packet_latency.append(abs_plat_string)
                absolute_network_latency.append(abs_nlat_string)
                rel_thr_string += syn_rel_thr_string
                rel_plat_string += syn_rel_plat_string
                rel_nlat_string += syn_rel_nlat_string
                absolute_throughput_err.append(err_thr_string)
                absolute_packet_latency_err.append(err_plat_string)
                absolute_network_latency_err.append(err_nlat_string)
                relative_throughput.append(rel_thr_string)
                relative_packet_latency.append(rel_plat_string)
                relative_network_latency.append(rel_nlat_string)
            with open(benchlist.model_eval_path + suite + "/" + bench + "/ring/" + "absolute_throughput_" + ".csv", "w") as file:
                file.write("kernel,FullSystem,FullSystem,FullSystem,FullSystem,Synthetic,Synthetic,Synthetic,Synthetic\n,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4\n")
                for item in absolute_throughput:
                    file.write(item + "\n")
            with open(benchlist.model_eval_path + suite + "/" + bench + "/ring/" + "absolute_packet_latency_" + ".csv", "w") as file:
                file.write("kernel,FullSystem,FullSystem,FullSystem,FullSystem,Synthetic,Synthetic,Synthetic,Synthetic\n,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4\n")
                for item in absolute_packet_latency:
                    file.write(item + "\n")
            with open(benchlist.model_eval_path + suite + "/" + bench + "/ring/" + "absolute_network_latency_" + ".csv", "w") as file:
                file.write("kernel,FullSystem,FullSystem,FullSystem,FullSystem,Synthetic,Synthetic,Synthetic,Synthetic\n,NVLink1,NVLink2,NVLink3,NVLink4, NVLink1,NVLink2,NVLink3,NVLink4\n")
                for item in absolute_network_latency:
                    file.write(item + "\n")
    with open(benchlist.model_eval_path + "OUTPUTS/" + LEVEL + "/absolute_throughput_error.csv", "w") as file:
        for item in absolute_throughput_err:
            file.write(item + "\n")
    with open(benchlist.model_eval_path + "OUTPUTS/" + LEVEL + "/absolute_packet_latency_error.csv", "w") as file:
        for item in absolute_packet_latency_err:
            file.write(item + "\n")
    with open(benchlist.model_eval_path + "OUTPUTS/" + LEVEL + "/absolute_network_latency_error.csv", "w") as file:
        for item in absolute_network_latency_err:
            file.write(item + "\n")
    with open(benchlist.model_eval_path + "OUTPUTS/" + LEVEL + "/relative_throughput.csv", "w") as file:
        for item in relative_throughput:
            file.write(item + "\n")
    with open(benchlist.model_eval_path + "OUTPUTS/" + LEVEL + "/relative_packet_latency.csv", "w") as file:
        for item in relative_packet_latency:
            file.write(item + "\n")
    with open(benchlist.model_eval_path + "OUTPUTS/" + LEVEL + "/relative_network_latency.csv", "w") as file:
        for item in relative_network_latency:
            file.write(item + "\n")
    print("throughput/latency analysis finished")