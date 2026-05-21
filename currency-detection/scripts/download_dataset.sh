#!/bin/bash

# --- Color Codes ---
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
BLUE='\033[0;34m'

DATASET_NAME="jagtaranacademy/indian-currency-dataset"
RAW_DIR="dataset/raw"

echo -e "${BLUE}🔍 Checking Kaggle API credentials...${NC}"

if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo -e "${RED}❌ Error: Kaggle API token not found at ~/.kaggle/kaggle.json${NC}"
    echo -e "Please download your token from Kaggle Settings and place it in the ~/.kaggle folder."
    exit 1
fi

echo -e "${GREEN}✅ Credentials found.${NC}"

# Ensure raw directory exists
mkdir -p "$RAW_DIR"

echo -e "${BLUE}📥 Downloading dataset: $DATASET_NAME...${NC}"

# Download dataset using Kaggle CLI
kaggle datasets download -d "$DATASET_NAME" -p "$RAW_DIR" --unzip

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dataset downloaded and extracted successfully to $RAW_DIR${NC}"
    
    # Optional: Remove any leftover zip files if they exist
    rm -f "$RAW_DIR"/*.zip
    
    echo -e "${BLUE}📊 Dataset Structure:${NC}"
    ls -R "$RAW_DIR" | head -n 20
else
    echo -e "${RED}❌ Failed to download dataset. Please check your internet connection or Kaggle quota.${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Preparation complete. You can now run the preprocessing scripts.${NC}"