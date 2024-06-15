from network_centric import *
import json
import sys
sys.path.append("..")
import benchlist
import utils
import shutil
import os


MODEL_LEVEL = "level1"
CHIPLET = "4chiplet"


def model_gen(suite, bench):
    for kernel in benchlist.kernels_list[suite][bench]:
        file_name = benchlist.model_gen_path + suite + "/" + bench + "/ideal/" + CHIPLET + "/kernels/" + str(kernel) + ".txt"
        file_path = benchlist.model_gen_path + suite + "/" + bench + "/ideal/" + CHIPLET + "/"
        request_packet = utils.capture_requests(file_name)
        data = generate_network_centric_model(request_packet, MODEL_LEVEL)

        save_file = open(file_path + "traffic_model_" + str(kernel) + "_" + MODEL_LEVEL + ".json", "w")
        json.dump(data, save_file, indent=4)
        save_file.close()
        os.makedirs(benchlist.model_eval_path + suite + "/" + bench + "/ideal/" + CHIPLET + "/" + MODEL_LEVEL, exist_ok=True)
        shutil.move(file_path + "traffic_model_" + str(kernel) + "_" + MODEL_LEVEL + ".json",
           benchlist.model_eval_path + suite + "/" + bench + "/ideal/" + CHIPLET + "/" + MODEL_LEVEL
           + "/traffic_model_" + str(kernel) + "_" + MODEL_LEVEL + ".json")


if __name__ == "__main__":
    suite = sys.argv[1]
    bench = sys.argv[2]
    model_gen(suite, bench)
