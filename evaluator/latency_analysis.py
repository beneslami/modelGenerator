import utils
import matplotlib.pyplot as plt


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
            if step.split("\t")[0] == "request injected":
                start = int(step.split("\t")[5].split(": ")[1])
            elif step.split("\t")[0] == "request received" and start != 0:
                if int(step.split("\t")[5].split(": ")[1]) - start not in latency.keys():
                    latency[int(step.split("\t")[5].split(": ")[1]) - start] = 1
                else:
                    latency[int(step.split("\t")[5].split(": ")[1]) - start] += 1
                start = 0
            if step.split("\t")[0] == "reply injected":
                start = int(step.split("\t")[5].split(": ")[1])
            elif step.split("\t")[0] == "reply received" and start != 0:
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


def collect_packet_latency(fullsystem_path, synthetic_path):
    real = 0.0
    syn = 0.0
    return real, syn


def collect_network_latency(fullsystem_path, synthetic_path):
    real = 0.0
    syn = 0.0
    return real, syn