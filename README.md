Timetable Project AI

An interactive application designed to help users explore and learn about tourist destinations through games, quizzes, and personalized recommendations. Built with Streamlit, the project integrates data preprocessing, automated question generation, and a hybrid recommendation engine.
🚀 Features
🧠 What am I thinking?

Guess the destination by answering questions about its attributes.
The system narrows down possibilities using automatically generated decision-tree–optimized questions.

📚 Quiz Module

Test your knowledge about a specific destination with dynamically generated questions.

✨ Personalized Recommendations

Receive destination suggestions based on your preferences using:

Cosine similarity for numerical attributes

Categorical similarity for non-numerical attributes

Highlighting key differences between suggested and input destinations

❓ Question Generation

Questions are automatically generated based on the unique values of processed attributes.
A Decision Tree classifier determines the optimal ordering to maximize information gain during the "What am I thinking?" game.
