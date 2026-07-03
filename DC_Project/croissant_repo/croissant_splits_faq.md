# Croissant Mappings FAQ

This document tracks common questions and design decisions for mapping datasets to the Croissant format.

---

## Q1: Shall I split the data into test and train for this?

**Answer:**
That depends heavily on the nature of your data and what you intend for people to do with it!

Here is the most important thing to know about splits in Croissant: **Croissant does not dynamically split data for you (e.g., doing an 80/20 random split). It only *documents* splits that already exist in your underlying files.**

**When you SHOULD add a split:**
*   If your underlying data already has a column dictating the split (e.g., a `split` column with "train" and "test" values).
*   If you have specific files dedicated to splits (e.g., `train.csv` and `test.csv`).
*   If this is specifically designed to be a Machine Learning benchmark (like the UCI Adult Census dataset where you use demographic data to predict an income bracket), and you want everyone to evaluate their models on the exact same test subset.

**When you SHOULD NOT add a split:**
*   If this is just a general-purpose analytical dataset (which raw Census data usually is!).
*   If the user downloading it is expected to do their own data science, filtering, and splitting using pandas/scikit-learn depending on what specific question they are trying to answer.

> **Conclusion for the Argentina Census Dataset:**
> Given that this is the **Argentina Census**, the recommendation is to **leave it as a single unsplit dataset** unless your API is specifically serving a pre-defined ML benchmark task. It is perfectly standard (and encouraged) in Croissant to just serve the raw tabular data without splits if there is no official ML benchmark attached to it!

---

## Q2: [Your next question goes here]

**Answer:**
[Your next answer goes here]

---
