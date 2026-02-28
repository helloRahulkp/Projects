# Neural Collaborative Filtering (NCF) From Scratch 🧠💻

[![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen)]()

## Table of Contents

1. [Project Overview](#project-overview)
2. [Motivation](#motivation)
3. [Features](#features)
4. [Project Structure](#project-structure)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Datasets](#datasets)
8. [Models & Approach](#models--approach)
9. [Results](#results)
10. [Future Work](#future-work)
11. [License](#license)

---

## Project Overview

This project implements a **Neural Collaborative Filtering (NCF)** system from scratch using **NumPy** and **PyTorch** to recommend items to users based on historical interactions. The project emphasizes:

- Understanding NCF from first principles
- Building models without relying solely on libraries
- Integration of data preprocessing, model training, evaluation, and deployment
- Modular architecture suitable for production and research

The backend API allows serving recommendations via **FastAPI**, enabling scalable integration with other platforms.

---

## Motivation

Recommender systems are integral to modern digital platforms (e-commerce, streaming, social media).  
Most existing solutions rely on pre-built libraries; this project:

- Teaches **deep learning fundamentals from scratch**
- Bridges **academic research and real-world applications**
- Demonstrates **end-to-end system design** from raw data to deployed API

---

## Features

- **Data Preprocessing**: Handling raw user-item interaction datasets
- **NCF Model**: Implemented both **MLP-based** and **generalized matrix factorization**
- **Training From Scratch**: Using only NumPy for initial experiments
- **Advanced Models**: Transition to PyTorch for scalable training
- **Evaluation**: Hit Ratio (HR), NDCG, MSE, MAE
- **RAG/GenAI Integration**: Generate recommendations with contextual explanations (optional extension)
- **API Deployment**: Serve predictions with FastAPI
- **Dockerized Environment**: Reproducible setup for development and deployment

---

## Project Structure

```text
NCF-Recommender-From-Scratch/
│
├── data/               # Raw and processed datasets
├── notebooks/          # EDA & experimentation notebooks
├── src/                # Source code: models, training, utils, API
├── experiments/        # Saved model checkpoints and logs
├── reports/            # Figures, thesis drafts, presentations
├── docker/             # Docker setup
├── scripts/            # Quick run scripts
├── tests/              # Unit tests
├── requirements.txt    # Python dependencies
└── README.md
```
