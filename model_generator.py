from utils import *
from network_centric import *
import json

MODEL_LEVEL = "level1"

if __name__ == "__main__":
    path = "/home/ben/Desktop/test/ring/NVLink4/4chiplet/data/synthetic/"
    trace_name = "trace0.txt"
    request_packet = capture_requests(path, trace_name)
    data = generate_network_centric_model(request_packet, MODEL_LEVEL)

    save_file = open(path + "burst_model_" + MODEL_LEVEL + ".json", "w")
    json.dump(data, save_file, indent=4)
    save_file.close()