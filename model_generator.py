from utils import *
from network_centric import *
import json

MODEL_LEVEL = "level2"

if __name__ == "__main__":
    path = "/home/ben/Desktop/accelsim-chiplet_ideal_noc/test/bfs_64k/kernels/"
    trace_name = "4_ideal.txt"
    request_packet = capture_requests(path, trace_name)
    data = generate_network_centric_model(request_packet, MODEL_LEVEL)

    save_file = open(path + "burst_model.json", "w")
    json.dump(data, save_file, indent=4)
    save_file.close()