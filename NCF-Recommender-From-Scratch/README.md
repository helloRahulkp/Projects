Neural Collaborative Filtering (NCF) Movie Recommender

This project implements a state-of-the-art movie recommendation engine based on the Neural Collaborative Filtering (NCF) framework. By moving beyond the linear limitations of traditional Matrix Factorization (MF), this system utilizes deep neural networks to learn the complex interaction function between users and items.

🚀 Overview
The system is built to provide personalized movie recommendations using implicit feedback (interaction data) from the MovieLens 1M dataset. It is designed as a production-ready web service using Flask and Docker, following Object-Oriented Programming (OOP) patterns for machine learning.
Key Features

NeuMF (Neural Matrix Factorization): A fused model architecture that combines the linearity of GMF (Generalized Matrix Factorization) and the non-linearity of a Multi-Layer Perceptron (MLP).

Implicit Feedback Engine: Transforms explicit ratings into binary signals (1 for interaction, 0 for no interaction) to model user interest.
Deep Latent Modeling: Uses Embedding Layers to project users and movies into a shared dense latent space.

Advanced Optimization: Implements Log Loss (Binary Cross-Entropy) with Negative Sampling to effectively learn from sparse data.

---

🏗 Architecture
The NCF framework utilizes a multi-layer architecture:

Input Layer: Accepts binarized sparse vectors via one-hot encoding of User and Movie IDs.

Embedding Layer: Projects sparse inputs into dense latent vectors.
Neural CF Layers:

GMF Path: Performs an element-wise product to capture linear patterns.

MLP Path: Concatenates vectors and passes them through multiple hidden layers
with ReLU activation to capture non-linearities.

NeuMF Layer: Concatenates the outputs of GMF and MLP to leverage both model strengths.

Output Layer: A Sigmoid activation function that predicts a score between 0 and 1 representing the likelihood of user interest.

---

📊 Dataset
The system uses the MovieLens 1M dataset.

Statistics: 1,000,209 interactions across 6,040 users and 3,706 movies.

Processing: Since the system focuses on implicit signals, all ratings are binarized.

Storage: Following project requirements, the system processes raw .dat or .csv files directly without a database.

---

🛠 Tech Stack
Deep Learning: Keras/TensorFlow (For Comparing Scratch with Library Model).

Web API: Flask.

ML Ops & OOP: Pydantic for data validation and schema definition.

Containerization: Docker.

Data Science: NumPy, Pandas, Scipy.

---

💻 Project Structure (OOP Design)

The project is organized into modular classes to satisfy ML OOPs requirements:

DataLoader: Handles MovieLens file parsing and negative sampling.

NCFModel: Base class for neural architectures.

NeuMFTrainer: Manages stochastic gradient descent (SGD) and Adam optimization.

RecommenderAPI: Flask application serving predictions.

---

🚦 Getting Started

Prerequisites
Docker installed on your machine.
Installation & Deployment
Clone the repository:
Build the Docker Image:
Run the Container:

---

📈 Evaluation Metrics
The model performance is evaluated using the Leave-one-out protocol:

Hit Ratio (HR@10): Measures if the held-out movie is in the Top-10 recommended list.

NDCG@10: Accounts for the position of the recommended movie in the list.
Performance

NeuMF consistently outperforms traditional models like BPR and eALS, showing significant improvements by fusing linear and non-linear pathways.
