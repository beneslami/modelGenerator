def capture_simulation_time(fullsystem_path, synthetic_path):
    real = 0.0
    syn = 0.0
    with open(fullsystem_path, "r") as file:
        content = file.readlines()

    for item in content:
        if item.split(",")[0] == "simulation time":
            real = float(item.split(",")[1].split("\n")[0])
            break

    with open(synthetic_path, "r") as file:
        content = file.readlines()
    for item in content:
        if "Total run time " in item:
            syn = float(item.split("e ")[1].split(" s")[0])

    return real, syn