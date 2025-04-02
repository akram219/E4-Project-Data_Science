import pandas as pd
import numpy as np
import glob

files = glob.glob('Documents\ProjetE4_data_science\Data\Raw\conso_mix_RTE_*')
df = pd.read_csv