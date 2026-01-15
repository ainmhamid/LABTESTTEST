import streamlit as st
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import requests
import pandas as pd

# Page config
st.set_page_config(
    page_title="Real-time Image Classification (PyTorch)",
    layout="centered",
)

st.title("Real-time Webcam Image Classification")
st.write("Using **PyTorch ResNet-18 (pretrained on ImageNet)**")

# Load ImageNet labels
@st.cache_data
def load_imagenet_labels():
    url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
    r = requests.get(url)
    return r.text.strip().split("\n")

# Load model
@st.cache_resource
def load_model():
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.eval()
    return model

labels = load_imagenet_labels()
model = load_model()

# Preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

# Webcam input
st.subheader("Capture from Webcam")
img_data = st.camera_input("Take a photo")

if img_data is not None:
    image = Image.open(img_data).convert("RGB")
    st.image(image, caption="Captured Image", use_container_width=True)

    input_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        output = model(input_tensor)
        probs = F.softmax(output[0], dim=0)

    top5_prob, top5_catid = torch.topk(probs, 5)

    st.subheader("Top-5 Predictions")
    df = pd.DataFrame({
        "Label": [labels[idx] for idx in top5_catid],
        "Probability": [float(p) for p in top5_prob],
    })

    st.dataframe(df, use_container_width=True)
else:
    st.warning("Please take a photo using the webcam.")
