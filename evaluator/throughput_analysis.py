

def collect_throughput(fullsystem_path, synthetic_path, nv):
    real = 0.0
    syn = 0.0
    period = 0
    if nv == "NVLink4":
        period = 0.177
    elif nv == "NVLink3":
        period = 0.266
    elif nv == "NVLink2":
        period = 0.533
    elif nv == "NVLink1":
        period = 1
    with open(fullsystem_path, "r") as file:
        content = file.readlines()

    for item in content:
        if item.split(",")[0] == "average injection rate":
            real = float(item.split(",")[1].split("\n")[0])*40 / period
            break
    flag = 0
    with open(synthetic_path, "r") as file:
        content = file.readlines()
    for item in content:
        if "====== Traffic class 0 ======" in item:
            flag = 1
        if flag == 1 and item.split(" = ")[0] == "Injected flit rate average":
            syn = float(item.split(" = ")[1].split(" (")[0])*40 / period

    return real, syn
