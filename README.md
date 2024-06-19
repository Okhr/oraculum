# Oraculum

## Description

This project is an application aimed at readers to help them easily keep track of their reading, whether it's a single book or a multi-volume saga. The user can upload an electronic book in ePub format, and the tool extracts various information about the book, such as:

- List of characters with their descriptions.
- List of locations with their descriptions.
- Occurrence of characters and locations throughout the chapters.
- Interaction graph between characters.
- Chatbot for asking questions about the book(s).
- Image generation for locations and characters.

## Usage 

The application is not yet deployed but I'm working hard for a minimal alpha version to be available very soon.

## Roadmap

- [x] ePub parsing / TOC and content extraction
- [x] Named Entity Recognition : local models and Google NLP API
- [x] Text chunking and embedding
- [x] Refined tagging with LLM model
- [x] FastAPI backend authentication boilerplate
- [ ] React frontend
- [ ] RAG chatbot
- [ ] Monitoring