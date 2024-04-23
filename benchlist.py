

path = "/home/ben/Desktop/benchmarks/"
kernels_list_original = {
    "SDK": {"conjugate-gradient": [2, 3],
            "matrixmul": [1]
            },
    "cutlass": {"splitk-gemm": [2]
                },
    "deepbench": {"gemm": [3, 5, 6],
                  "rnn": [4, 8, 10]
                  },
    "pannotia": {"color-max": [1],
                 "color-maxmin": [2, 3, 4, 5, 7, 8, 9, 10],
                 "pagerank-spmv": [2, 3, 5, 7, 9],
                 "sssp": [3, 6, 9],
                 "fw": [1],
                 "pagerank": [2, 4]
                 },
    "parboil": {"mri-gridding": [1],
                "spmv": [1],
                "cutcp": [1]
                },
    "polybnech": {"syrk": [1],
                  "syr2k": [1],
                  "2mm": [1],
                  "gemm": [1]
                  },
    "rodinia": {"b+tree": [1],
                "bt": [1, 2],
                "cfd": [3],
                "gaussian": [2, 4, 6],
                "hybridsort": [4, 5, 6, 7, 8, 9, 10],
                "lud": [3, 6, 9]
                },
    "shoc": {"FFT": [3]
             },
    "UVM": {"lr": [1, 3, 6, 8, 11, 13]
            },
    "tango": {"AlexNet": [1],
              "ResNet": [1],
              "SqueezeNet": [1]
              }
}

"""kernels_list = {
    "pannotia": {"color-max": [1],
                 "color-maxmin": [2, 3, 4, 5, 7, 8, 9, 10],
                 "pagerank-spmv": [2, 3, 5, 7, 9],
                 "sssp": [3, 6, 9],
                 "fw": [1],
                 "pagerank": [2, 4]
                 },
    "parboil": {"mri-gridding": [1],
                "spmv": [1],
                },
    "rodinia": {
                "cfd": [3],
                "gaussian": [2, 4, 6],
                },
}"""

kernels_list = {
    "pannotia": {
                 "color-maxmin": [10]
                 },
}