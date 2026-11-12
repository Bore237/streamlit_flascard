# Flashcard Learning App
![Python](https://img.shields.io/badge/Python-3.10%25-blue?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405e?style=flat&logo=sqlite&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![uv](https://img.shields.io/badge/uv-De5efe?style=flat&logo=astral&logoColor=white)

**[Live Demo](https://appflascard-awpdcldtvmdvziitp2pch5.streamlit.app/)**

A simple and interactive flashcard learning application built with Python, Streamlit, and SQLite. It allows users to create and manage flashcard decks, study questions and answers, and track their learning progress through performance statistics.

## Features
* Create and manage flashcard decks.
* Add questions and answers to flashcards.
* Interactive study mode with answer reveal.
* Track correct and incorrect answers.
* Monitor learning progress and accuracy.
* Store data persistently using SQLite.

## Technologies
- **Language:** Python
- **Frontend:** Streamlit
- **Database:** SQLite
- **Graphics** Plotly
- **Package Manager:** uv

## Getting Started

```bash
uv sync
uv pip install -e .     
PATHPYTHON=src streamlit run src/app/Flashcards.py
```


A lightweight project demonstrating database integration, Python development, and interactive web application design.