---
license: cc-by-nc-4.0
task_categories:
- visual-question-answering
language:
- en
---

# DrawEduMath (Mirror)

This is a mirror of the original DrawEduMath dataset hosted at [Hugging Face](https://huggingface.co/datasets/Heffernan-WPI-Lab/DrawEduMath). This mirror is maintained by Kyle Lo (kylel_at_allenai_dot_org). We may make updates to this mirror that are not reflected on the original.
  * *Mirror created*: August 20, 2025
  * *Last updated*: August 20, 2025


## About the Dataset

DrawEduMath is a dataset containing images of students' handwritten responses to math problems, paired with detailed descriptions written by 
teachers and QA pairs of the models. The images are of handwritten math answers from U.S.-based students, to 188 math problems across Grades 2
through high school. 

The dataset is comprised of 1) 2,030 images of students' handwritten responses, 2) 2,030 free-form descriptions written by teachers, and 
3) 11,661 question-answer (QA) pairs written by teachers and 44,362 synthetically generated QA pairs created by 2 LLMs: GPT-4o and Claude, 
which transformed extracted facets from the teachers' descriptions into QA pairs.


Quick links:
- 📃 [NAACL 2025 Paper](https://aclanthology.org/2025.naacl-long.352/) (🏆 Outstanding paper award)
- 📃 [NeurIPS'24 Math-AI Workshop Paper](https://openreview.net/attachment?id=0vQYvcinij&name=pdf)

# Data Source
The images in the DrawEduMath dataset are from [ASSISTments](https://new.assistments.org/), where students upload their handwritten math work and receive feedback from teachers. 
To ensure student privacy, our team went through multiple rounds of the Personal Identifiable Information(PII) removal process. 
For the first round, undergraduate research assistants at WPI reviewed the individual images to extract only relevant pieces of information. 
This process involved undergraduate research assistants cropping the image to remove any irrelevant background. Further, the presence of any 
remaining PII such as the names of students was masked using black rectangular boxes.  PII-redacted images from this process were then passed 
through a second round of filtering. Teachers who wrote the free-form descriptions about these images also flagged images that were too blurry 
or included PII. All such images were removed from the dataset.

# Download

In Python:

```python
from datasets import load_dataset

ds = load_dataset("allenai/DrawEduMath", data_files="Data/DrawEduMath_QA.csv", split='train')

Dataset({
    features: ['Problem ID', 'Image Name', 'Image URL', 'Image SHA256', 'Image Caption', 'Facets By GPT4o', 'Facets By Claude', 'QA Teacher', 'QA GPT4o', 'QA Claude'],
    num_rows: 2030
})
```

# Data Format

Our main dataset file is `DrawEduMath_QA.csv`. This file contains math problem IDs (`Problem ID`) and filenames of each student response to each problem (`Image Name`). Teacher-written captions and QA pairs are included under `Image Caption` and `QA Teacher`, respectively. In our paper, we used Claude and GPT-4o to decompose teacher-written questions into facets (`Facets By Claude` and `Facets By GPT4o`), which we synthetically restructured into QA pairs (`QA Claude` and `QA GPT4o`).

You may use the following to load the csv cells that contain lists of QA pair dictionaries (e.g. the columns `QA Teacher`, `QA Claude`, `QA GPT4o`): 

```
import json

def load_qa_json(qa_pairs):
    try:
        qa = json.loads(qa_pairs)
        qa = ast.literal_eval(qa)

        return qa
    except:
        qa = json.loads(qa_pairs)
        return qa

# here, "row" is one line of the csv file, as produced by a csv DictReader or pandas iterrows
for row in ds:
    qa = load_qa_json(row['QA Claude'].strip())
    for qa_dict in qa:
        question = qa_dict['question']
        answer = qa_dict['answer']
```

Each image can be downloaded from URLs indicated in the `Image URL` column. 

## License
This dataset is licensed under CC-BY-NC-4.0. It is intended for research and educational purposes following ASSISTments's [Responsible Use Guidelines](https://sites.google.com/view/e-trials/resources/guidelines-for-drawedumath).

## Citation 

```
@inproceedings{baral-etal-2025-drawedumath,
    title = "{D}raw{E}du{M}ath: Evaluating Vision Language Models with Expert-Annotated Students' Hand-Drawn Math Images",
    author = "Baral, Sami  and Lucy, Li  and Knight, Ryan  and Ng, Alice  and Soldaini, Luca  and Heffernan, Neil  and Lo, Kyle",
    booktitle = "NAACL",
    month = apr,
    year = "2025",
    url = "https://aclanthology.org/2025.naacl-long.352/",
    doi = "10.18653/v1/2025.naacl-long.352",
}
```