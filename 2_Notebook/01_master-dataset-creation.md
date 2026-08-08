# 01_master_dataset_creation.ipynb

## Purpose

এটা পুরো project-এর **foundation notebook**।

এই notebook-এর কাজ হচ্ছে competition-এর সব raw dataset এক জায়গায় এনে **একটা clean master dataset** তৈরি করা, যাতে পরের সব notebook একই data নিয়ে কাজ করতে পারে।

---

## কেন এটা করেছি?

Competition-এর data আলাদা আলাদা file-এ ছিল।

যেমন:

* Features
* Labels
* Transcript
* Session information

এভাবে ছড়িয়ে থাকলে প্রতিবার training বা feature engineering-এর আগে merge করতে হতো।

তাই আমরা শুরুতেই সব merge করে একটা **master dataset** বানিয়েছি।

---

## এই notebook-এ কী করেছি?

### Step 1

সব raw file load করেছি।

---

### Step 2

প্রতিটা tutoring session-এর transcript পড়েছি।

---

### Step 3

Transcript থেকে আলাদা করেছি:

* Full transcript
* Student text
* Tutor text
* Background text

কারণ পরে এগুলো থেকে আলাদা feature বের করব।

---

### Step 4

Features + Labels + Transcript

সব merge করেছি।

এখন প্রতিটা row-এর মধ্যে prediction করার জন্য দরকারি সব information আছে।

---

### Step 5

Dataset validate করেছি।

Check করেছি:

* Missing data আছে কিনা
* Duplicate response আছে কিনা
* Merge ঠিক হয়েছে কিনা

---

### Step 6

সবশেষে master dataset parquet format-এ save করেছি।

এই dataset-টাই পরের সব notebook use করবে।

---

# Input

Raw Competition Files

↓

# Output

Master Dataset

↓

সব পরের notebook-এর input

---

# Pipeline-এ Position

```text
Raw Dataset
      │
      ▼
01_master_dataset_creation
      │
      ▼
Master Dataset
      │
      ▼
02_EDA
      │
      ▼
03_feature_engineering
      │
      ▼
Training
      │
      ▼
Optuna
      │
      ▼
Final Model
```

---

# এই notebook-এর benefit

* বারবার merge করতে হয় না।
* পুরো project একই dataset use করে।
* Feature engineering অনেক সহজ হয়ে যায়।
* Training notebook clean থাকে।
* Data leakage বা merge mistake-এর chance কমে যায়।

---

# এক লাইনে Summary

> **Raw competition data-কে merge করে একটি clean, response-level master dataset তৈরি করেছি, যেটা পুরো ML pipeline-এর base dataset হিসেবে পরের সব notebook ব্যবহার করবে।**

---

