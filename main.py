import streamlit as st
import numpy as np
import pandas as pd
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import torchvision.transforms as transforms

st.title("Fremtind Bordtennis Ranking")

st.write("Her kan du se rankingen til Fremtind Bordtennis")

ranking = pd.read_csv("bordtennis.csv")

st.write(ranking, format="csv")