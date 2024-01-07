# 🌱 SWIFT - Sustainable Workflow for Idea Filtering and Testing 🌱

Welcome to SWIFT, your AI-powered partner in sustainable innovation! SWIFT is a cutting-edge tool designed to streamline the evaluation of innovative ideas, focusing on long-term sustainability.

## ✨ Key Features ✨

- 🔍 Specific Criteria Framework: SWIFT employs an AI model fine-tuned for sustainability, automatically identifying and filtering out vague or irrelevant ideas.
- 🌐 Real-Time Web Integration: Stay up-to-date with the latest trends and data in sustainability through SWIFT's web browsing feature, enriching your evaluations.
- 📊 Customizable Strictness: Tailor the tool's filtering criteria to your specific needs, from broad exploration to in-depth analysis.

## 🚀 How to Get Started 🚀

1. Clone this repository to your local machine.
2. Follow the setup instructions in our documentation to get SWIFT up and running.
3. Start using SWIFT to evaluate ideas and drive sustainable innovation!

## 🌏 Join us on our mission to create a "swifter" future for long-term sustainability. Together, we can make a lasting impact on our planet! 🌏

Instructions:

```
pip install -r requirements.txt

To run web browsing agent:

cd web-agent
python main.py

To run streamlit app:

streamlit run streamlit_app.py
```

## Technologies Used: 👨‍💻

- Serper: Employed to fetch relevant webpages for data retrieval.
- Beautiful Soup: Employed for web scraping tasks to extract data from websites.
- Langchain: Utilized for document vector embedding and retrieval to enhance data analysis.
- OpenAI: Utilized for generating responses using language models and processing data obtained from web scraping with Serper, as well as document embedding from Langchain.
- Pandas: Empowered data handling, including the upload of Excel files and the creation and manipulation of dataframes.
- Streamlit: Used to create a deployable frontend UI for the application, all within Python.
