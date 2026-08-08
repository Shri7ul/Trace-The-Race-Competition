
# 📘 02_eda.ipynb

## Purpose

এই notebook-এর উদ্দেশ্য হলো **dataset-কে গভীরভাবে বুঝা**, যাতে feature engineering ও model building-এর আগে data-এর behavior সম্পর্কে পরিষ্কার ধারণা পাওয়া যায়।

এখানে কোনো model train করা হয়নি এবং নতুন feature final dataset-এ যোগ করা হয়নি। বরং data analysis করে কোন ধরনের feature useful হতে পারে সেটা identify করা হয়েছে।

---

# কেন এই notebook করেছি?

Model train করার আগে dataset সম্পর্কে কিছু গুরুত্বপূর্ণ প্রশ্নের উত্তর জানা দরকার ছিল:

* Target balanced নাকি imbalanced?
* Learning objective-এর distribution কেমন?
* Transcript বড় নাকি ছোট?
* Student ও Tutor interaction কেমন?
* Question বেশি হলে কি correctness বাড়ে?
* Unclear transcript prediction-এ প্রভাব ফেলে কিনা?
* Conversation length গুরুত্বপূর্ণ কিনা?

এই প্রশ্নগুলোর উত্তর বের করার জন্য EDA করা হয়েছে।

---

# এই notebook-এ কী কী analyze করেছি?

### 1. Dataset Health Check

প্রথমে dataset verify করা হয়েছে:

* Total rows
* Total columns
* Missing values
* Duplicate response
* Duplicate session
* Dataset consistency

উদ্দেশ্য ছিল training শুরু করার আগে dataset clean কিনা নিশ্চিত হওয়া।

---

### 2. Target Analysis

`is_correct` label-এর distribution দেখা হয়েছে।

এতে বোঝা গেছে:

* কত শতাংশ correct
* কত শতাংশ incorrect
* Dataset balanced নাকি skewed

এটা পরে evaluation strategy বুঝতে সাহায্য করেছে।

---

### 3. Learning Objective Analysis

Learning objective নিয়ে analysis করা হয়েছে।

দেখা হয়েছে:

* মোট unique objective
* কোন objective সবচেয়ে বেশি এসেছে
* কোন objective খুব rare
* কোন objective সহজ
* কোন objective কঠিন

এতে বোঝা গেছে objective information prediction-এর জন্য খুব গুরুত্বপূর্ণ হতে পারে।

---

### 4. Transcript Analysis

Conversation-এর size analyze করা হয়েছে।

যেমন:

* Transcript length
* Student text length
* Tutor text length
* Background text length

উদ্দেশ্য ছিল conversation size prediction-এর সাথে সম্পর্কিত কিনা দেখা।

---

### 5. Conversation Structure

Conversation flow analyze করা হয়েছে।

যেমন:

* Student turns
* Tutor turns
* Total turns
* Tutor/Student ratio
* Turn fraction

এতে interaction pattern সম্পর্কে ধারণা পাওয়া গেছে।

---

### 6. Question Analysis

Transcript-এ question mark এবং questioning behavior analyze করা হয়েছে।

কারণ tutoring session-এ প্রশ্ন করার ধরন learning outcome-এর সাথে সম্পর্কিত হতে পারে।

---

### 7. Unclear Speech Analysis

Transcript-এ `[unclear]` বা unclear text কতবার এসেছে সেটা analyze করা হয়েছে।

উদ্দেশ্য ছিল audio/transcript quality prediction-এ impact করে কিনা দেখা।

---

### 8. Tutor Behavior Analysis

Tutor-এর positive ও instructional শব্দ analyze করা হয়েছে।

যেমন:

* Good
* Great
* Excellent
* Explain
* Think
* Remember

এতে encouragement ও instruction সম্পর্কিত feature তৈরির idea পাওয়া গেছে।

---

# এই notebook থেকে কী শিখেছি?

এই EDA থেকেই feature engineering-এর অনেক idea এসেছে।

যেমন:

* Objective frequency
* Transcript length
* Student/Tutor ratio
* Turn ratio
* Question count
* Unclear count
* Encouragement score
* Instruction score

পরে `03_feature_engineering.ipynb`-এ এগুলো feature হিসেবে implement করা হয়েছে।

---

# Pipeline-এ Position

```text
01_master_dataset_creation
        │
        ▼
02_eda
        │
        ▼
Data Understanding
        │
        ▼
Feature Ideas
        │
        ▼
03_feature_engineering
```

---

# Output

এই notebook কোনো নতুন training dataset তৈরি করেনি।

এর output ছিল:

* Dataset সম্পর্কে insight
* Visualization
* Feature engineering-এর roadmap
* কোন information predictive হতে পারে তার ধারণা

---

# এক লাইনের Summary

> **EDA notebook-এর মাধ্যমে dataset, learning objectives, transcript structure এবং tutoring behavior বিশ্লেষণ করে feature engineering-এর জন্য গুরুত্বপূর্ণ insight সংগ্রহ করা হয়েছে।**

---

