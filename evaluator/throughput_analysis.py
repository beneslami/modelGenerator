

def collect_throughput(fullsystem_path, synthetic_path, nv):
    real = 0.0
    syn = 0.0
    with open(fullsystem_path, "r") as file:
        content = file.readlines()

    for item in content:
        if item.split(",")[0] == "average injection rate":
            real = str(float(item.split(",")[1].split("\n")[0])*40 / 0.88)
            break
    flag = 0
    with open(synthetic_path, "r") as file:
        content = file.readlines()
    for item in content:
        if "====== Traffic class 0 ======" in item:
            flag = 1
        if flag == 1 and item.split(" = ")[0] == "Injected flit rate average":
            syn = str(float(item.split(" = ")[1].split(" (")[0])*40 / 0.88)

    return real, syn
