# Job Application Tracker

A Python application that helps users track job applications using an SQLite database.

## Features

- Add applications
- Edit applications
- Delete applications
- Search applications by company
- Update application status
- View application statistics
- Export applications to CSV reports
- Email subscription alerts for job matches
- Desktop GUI with Tkinter

## Technologies Used

- Python
- SQLite
- Tkinter
- requests
- CSV

## How to Run

1. Clone the repository:

```bash
git clone <repository-url>
```

2. Navigate to the project folder:

```bash
cd "Job Application Tracker"
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the GUI application:

```bash
python gui_tracker.py
```

5. Or run the command-line tracker:

```bash
python tracker.py
```

## Project Structure

```
Job Application Tracker/
├── Data/
│   └── applications.db
├── Reports/
│   └── job_report.csv
├── gui_tracker.py
├── database.py
├── tracker.py
├── tests/
│   └── test_subscriptions.py
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Notes

- The SQLite database file is stored in `Data/applications.db`.
- Exported reports are stored in `Reports/job_report.csv`.
- The GUI version uses `gui_tracker.py`, while `tracker.py` provides a simple CLI interface.

## Future Improvements

- Excel export
- Follow-up reminders
- Application filtering by date
- Enhanced notification workflows
