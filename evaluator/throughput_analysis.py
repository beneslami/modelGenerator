

def collect_throughput(fullsystem_path, synthetic_path):
    real = 0.0
    syn = 0.0
    with open(fullsystem_path, "r") as file:
        content = file.readlines()
    for item in content:
        if item.split(",")[0] == "throughput":
            real = item.split(",")[1].split("\n")[0]
            break
    with open(synthetic_path, "r") as file:
        content = file.readlines()
    for item in content:
        if item.split(" = ")[0] == "total average throughput":
            syn = item.split(" = ")[1].split("\n")[0]
    return real, syn
