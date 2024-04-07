import numpy
import statsmodels.api as sm
from hurst import compute_Hc


def capture_requests(path, file_name):
    with open(path + file_name, "r") as file:
        raw_content = file.readlines()
    request_packet = []
    for line in raw_content:
        if line.split("\t")[0] == "request injected" or line.split("\t")[0] == "request received" or line.split("\t")[0] == "reply injected":
            request_packet.append(line)
    return request_packet


def equate_dictionaries(p, q):
    for k, v in p.items():
        if k not in q.keys():
            q[k] = v
    for k, v in q.items():
        if k not in p.keys():
            p[k] = v
    p = dict(sorted(p.items(), key=lambda x: x[0]))
    q = dict(sorted(q.items(), key=lambda x: x[0]))
    return p, q


def measure_hellinger(p, q):
    new_p, new_q = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += (numpy.sqrt(new_p[i]) - numpy.sqrt(new_q[i]))**2
    hellinger = (1/numpy.sqrt(2))*(numpy.sqrt(partial_sum))
    return hellinger


def measure_euclidean(p, q):
    new_p, new_q = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += (new_p[i] - new_q[i])**2
    EUC = numpy.sqrt(partial_sum)
    return EUC


def measure_manhattan(p, q):
    new_p, new_q = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += numpy.abs(new_p[i] - new_q[i])
    man = partial_sum
    return man


def measure_cosine_similarity(p, q):
    new_p, new_q = equate_dictionaries(p, q)
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
    new_p, new_q = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += numpy.abs(new_p[i] - new_q[i])
    MAE = partial_sum / len(new_p)
    return MAE


def measure_MSE(p, q):
    new_p, new_q = equate_dictionaries(p, q)
    partial_sum = 0
    for i in new_p.keys():
        partial_sum += (new_p[i] - new_q[i])**2
    MSE = (1/len(new_p))*(partial_sum)
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
    return pdf_data, cdf_data


def generate_autocorrelation(data):
    minimum = len(data["real"]) if len(data["real"]) < len(data["synthetic"]) else len(data["synthetic"])
    val = {}
    val["real"] = sm.tsa.acf(data["real"][:minimum], nlags=minimum)
    val["synthetic"] = sm.tsa.acf(data["synthetic"][:minimum], nlags=minimum)
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
        H, c, _ = compute_Hc(data, kind='random_walk', simplified=True)
    except ValueError:
        H = -1
    return H