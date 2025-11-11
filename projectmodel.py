import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pjt=pd.read_csv(r"C:\Frontend_model(minor project)\minor project\final_project_dataset.csv")
print(pjt.head())

print("\nDataFrame Info:")
pjt.info()

# Fill missing values in 'Certifications Obtained' with a placeholder string.
pjt['Certifications Obtained'].fillna('No Certification', inplace=True)

#missing values cheaking
print("Missing values per column:")
print(pjt.isnull().sum())

#duplicate rows
print(f"Number of duplicate rows: {pjt.duplicated().sum()}")    
    
from sklearn.preprocessing import LabelEncoder

#here i am doing the separation from the target coloumn 
X = pjt.drop(columns=['Recommended Career Path'])
y = pjt['Recommended Career Path']

#lable encoding the target variable(y) 
le = LabelEncoder()
y_encoded = le.fit_transform(y)

#the encoding part 
# Columns with single text values (e.g., 'B.Tech')
single_value_categorical = [
   'Current Education Level', 
    'Stream / Specialization', 
    'Certifications Obtained',
    'Personality Type', 
    'Salary Expectation (Annual, in INR)', 
    'Preferred Work Environment',
    'Learning Style',
    'Open to Relocating',
    'Willingness to Pursue Higher Studies'
]
multi_value_categorical = [
   'Technical / Hard Skills', 
    'Soft Skills'
]
numerical_cols = ['Latest Grade / CGPA']




# A. One-Hot Encode the single-value columns
X_single_encoded = pd.get_dummies(X[single_value_categorical])

# B. Use str.get_dummies for the multi-value columns
# This correctly splits the strings by the comma and creates a column for each item.
X_multi_encoded_list = []
for col in multi_value_categorical:
    dummies = X[col].str.get_dummies(sep=', ')  
    dummies = dummies.add_prefix(f"{col}_")
    X_multi_encoded_list.append(dummies)


# C. Combine all the processed columns into one final feature DataFrame
# We combine the numerical columns, the encoded single-value columns, and all the encoded multi-value columns.
X_processed = pd.concat([X[numerical_cols], X_single_encoded] + X_multi_encoded_list, axis=1)

#data visualization step 
#bar chart to show how many students fall into each carrier catagory 
'''print("Displaying Plot 1: Distribution of Recommended Career Paths...")
plt.figure(figsize=(12, 8))
sns.countplot(y='Recommended Career Path', data=pjt, order=pjt['Recommended Career Path'].value_counts().index, palette='viridis')
plt.title('Distribution of Recommended Career Paths', fontsize=16)
plt.xlabel('Number of Students', fontsize=12)
plt.ylabel('Career Path', fontsize=12)
plt.tight_layout()
plt.show()'''

#box plot to see if there any relation between the students grades and the carrier that they are choosing 
'''print("Displaying Plot 2: CGPA Distribution by Career...")
plt.figure(figsize=(14, 8))
sns.boxplot(x='Recommended Career Path', y='Latest Grade / CGPA', data=pjt, palette='coolwarm')
plt.title('CGPA Distribution by Recommended Career Path', fontsize=16)
plt.xlabel('Recommended Career Path', fontsize=12)
plt.ylabel('Latest Grade / CGPA', fontsize=12)
plt.xticks(rotation=90) # Rotate labels to prevent overlap
plt.tight_layout()
plt.show()'''

#another grouped bar chart to show personalty types across diffrent carrir paths 
'''print("Displaying Plot 3: Personality Types Across Careers...")
plt.figure(figsize=(12, 10))
sns.countplot(y='Recommended Career Path', hue='Personality Type', data=pjt, order=pjt['Recommended Career Path'].value_counts().index, palette='plasma')
plt.title('Personality Type Distribution Across Careers', fontsize=16)
plt.xlabel('Number of Students', fontsize=12)
plt.ylabel('Recommended Career Path', fontsize=12)
plt.legend(title='Personality Type')
plt.tight_layout()
plt.show()'''

#heat map bet carrir and education level
print("\nDisplaying Plot 4: Heatmap of Career vs. Education Level...")

contingency_table = pd.crosstab(pjt['Recommended Career Path'], pjt['Current Education Level'])

# Step 2: Create the heatmap from the crosstab
plt.figure(figsize=(12, 10))
sns.heatmap(contingency_table, annot=True, fmt='d', cmap='YlGnBu')

plt.title('Heatmap of Education Level vs. Recommended Career', fontsize=16)
plt.ylabel('Recommended Career Path', fontsize=12)
plt.xlabel('Current Education Level', fontsize=12)
plt.tight_layout()
plt.show()


#traning and testing 
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(X_processed, y_encoded, test_size=0.2, random_state=42)

print("\nTraining a Random Forest model on the final, high-quality dataset...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print("Model training complete!")

# Evaluate the Model
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Model Accuracy with Final Dataset: {accuracy * 100:.2f}%")

from sklearn.metrics import confusion_matrix

print("\nDisplaying Confusion Matrix to visualize model performance...")

cm = confusion_matrix(y_test, predictions)

# Create a heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=le.classes_, yticklabels=le.classes_)

plt.title('Confusion Matrix', fontsize=16)
plt.ylabel('Actual Career Path', fontsize=12)
plt.xlabel('Predicted Career Path', fontsize=12)
plt.show()