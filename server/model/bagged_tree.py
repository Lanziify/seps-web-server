import os
import joblib

current_dir = os.path.dirname(__file__)

cadmlm_model = os.path.join(current_dir, "cadmlm-bt.pkl")

model = joblib.load(cadmlm_model)