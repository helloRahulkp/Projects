import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

df = pd.read_csv("/Users/rahulkpkurup/Learning/Git-Portfolio/Projects/Phishing-Detection/data/processed/url_dataset.csv")

X = df.drop("label",axis=1)
y = df["label"]

X_train,X_test,y_train,y_test = train_test_split(
    X,y,test_size=0.2,random_state=42
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    random_state=42
)

model.fit(X_train,y_train)

accuracy = model.score(X_test,y_test)

print("Accuracy:",accuracy)

pickle.dump(model,open("phishing_model.pkl","wb"))