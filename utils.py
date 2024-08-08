import os
import numpy
import statsmodels.api as sm
from hurst import compute_Hc


def capture_requests(file_name):
    with open(file_name, "r") as file:
        raw_content = file.readlines()
    request_packet = []
    for line in raw_content:
        if line.split("\t")[0] == "request injected" or line.split("\t")[0] == "request received" or line.split("\t")[0] == "reply injected" or line.split("\t")[0] == "reply received":
            request_packet.append(line)
    return request_packet


def extend_distribution(dist, keys):
    """Extend a distribution to include all keys, setting missing keys to 0."""
    extended_dist = {key: dist.get(key, 0) for key in keys}
    return extended_dist


def equate_dictionaries(p, q):
    common_keys = set(p.keys()).intersection(q.keys())
    # Extend both distributions
    p = extend_distribution(p, common_keys)
    q = extend_distribution(q, common_keys)
    return p, q, common_keys


def measure_hellinger(p, q):
    new_p, new_q, common_keys = equate_dictionaries(p, q)
    partial_sum = sum((numpy.sqrt(new_p[key]) - numpy.sqrt(new_q[key]))**2 for key in common_keys)
    hellinger = (1/numpy.sqrt(2))*(numpy.sqrt(partial_sum))
    return hellinger


def measure_euclidean(p, q):
    new_p, new_q, _ = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += (new_p[i] - new_q[i])**2
    EUC = numpy.sqrt(partial_sum)
    return EUC


def measure_manhattan(p, q):
    new_p, new_q, _ = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += numpy.abs(new_p[i] - new_q[i])
    man = partial_sum
    return man


def measure_cosine_similarity(p, q):
    new_p, new_q, _ = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += new_p[i]*new_q[i]
    euc_p = 0
    euc_q = 0
    for i in new_p.values():
        euc_p += i**2
    for i in new_q.values():
        euc_q += i**2
    cos = partial_sum / (numpy.sqrt(euc_p)*numpy.sqrt(euc_q))
    return cos


def measure_MAE(p, q):
    new_p, new_q, common_keys = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += numpy.abs(new_p[i] - new_q[i])
    MAE = partial_sum / len(common_keys)
    return MAE


def measure_MSE(p, q):
    new_p, new_q, common_keys = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += (new_p[i] - new_q[i])**2
    MSE = (1/len(common_keys))*(partial_sum)
    return MSE


def generate_pdf_cdf(item):
    freq_data = {}
    for num in item:
        if num not in freq_data.keys():
            freq_data[num] = 1
        else:
            freq_data[num] += 1
    freq_data = dict(sorted(freq_data.items(), key=lambda x: x[0]))
    pdf_data = {}
    for k, v in freq_data.items():
        pdf_data[k] = v / sum(freq_data.values())
    prev = 0
    cdf_data = {}
    for k, v in pdf_data.items():
        prev += v
        cdf_data[k] = prev
    pdf_data = dict(sorted(pdf_data.items(), key=lambda x: x[0]))
    cdf_data = dict(sorted(cdf_data.items(), key=lambda x: x[0]))
    return pdf_data, cdf_data


def generate_autocorrelation(data):
    minimum = len(data["real"]) if len(data["real"]) < len(data["synthetic"]) else len(data["synthetic"])
    val = {}
    try:
        val["real"] = sm.tsa.acf(data["real"][:minimum], nlags=minimum)
    except FloatingPointError:
        val["real"] = [-1]
    try:
        val["synthetic"] = sm.tsa.acf(data["synthetic"][:minimum], nlags=minimum)
    except FloatingPointError:
        val["real"] = [-1]
    result = {"real": {}, "synthetic": {}}
    i = 1
    for tp in val.keys():
        for item in val[tp]:
            result[tp][i] = item
            i += 1
        i = 1
    return result


def compute_hurst(data):
    try:
        H, c, _ = compute_Hc(data, kind='price', simplified=True)
    except ValueError:
        H = -1
    except FloatingPointError:
        H = -1
    return H


def select_trace(file_path):
    max = 0
    selection = ""
    for item in os.listdir(file_path):
        if "trace" in item:
            if os.stat(file_path + item).st_size > max:
                max = os.stat(file_path + item).st_size
                selection = item
    return selection
