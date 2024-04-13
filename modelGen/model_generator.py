import utils
from network_centric import *
import json
import sys
sys.path.append("..")
import benchlist

MODEL_LEVEL = "level1"
CHIPLET = "4chiplet"

if __name__ == "__main__":
    for suite in benchlist.kernels_list.keys():
        for bench, kernels_list in benchlist.kernels_list[suite].items():
            for kernel in kernels_list:
                file_name = benchlist.path + suite + "/" + bench + "/ideal/" + CHIPLET + "/kernels/" + str(kernel) + ".txt"
                file_path = benchlist.path + suite + "/" + bench + "/ideal/" + CHIPLET + "/"
                request_packet = utils.capture_requests(bench.path, file_name)
                data = generate_network_centric_model(request_packet, MODEL_LEVEL)

                save_file = open(file_path + "traffic_model_" + MODEL_LEVEL + ".json", "w")
                json.dump(data, save_file, indent=4)
                save_file.close()