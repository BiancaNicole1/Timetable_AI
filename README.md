A university timetable generator built using Constraint Satisfaction Problem (CSP) modeling, AC-3 arc consistency, and Backtracking search, with support for natural-language (NLP) constraints.
The system automatically assigns courses, teachers, rooms, and time slots while respecting availability rules and user-defined restrictions.
.

🚀 Features
🧠 CSP-Based Timetable Generation

Each course is modeled as a variable

Domains include all valid combinations of (day, hour, room)

Constraints limit scheduling based on teacher availability, room occupancy, group conflicts, and maximum hours per day

📉 AC-3 Arc Consistency

Automatically reduces domains before search, significantly improving performance.

🔍 Backtracking Search

Finds a complete and conflict-free timetable by recursively assigning valid slots.

💬 Natural Language Constraints (NLP)

Users can write rules such as:

“Professor X cannot teach after 12”

“Room A101 is unavailable on Tuesday”

“Do not schedule courses on Thursday after 14:00”

“Teachers should have max 4 hours per day”

The system interprets them using regex-based parsing and updates the CSV data accordingly.

📄 Automatic Output

Generates a human-readable timetable grouped by:

Day

Hour

Room
