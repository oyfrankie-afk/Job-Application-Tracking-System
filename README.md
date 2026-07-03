# Job Application Tracking System (JATS) – Version 2.0

## Overview

The **Job Application Tracking System (JATS)** is a desktop application developed in **Python** using **Tkinter** and **SQLite**. It was designed to help job seekers organize their job search by tracking applications, discovering new opportunities online, and receiving automated email notifications when matching vacancies become available.

Version 2 transforms the project from a simple application tracker into a more complete job search and application management system by integrating live job search APIs, email automation, and subscription management.


## Features

### Application Management

* Add, edit and delete job applications
* Track application status
* Store applications in a SQLite database
* Automatically record application dates
* Search and manage saved applications

### Dashboard & Reports

* Application statistics dashboard
* Export application records to CSV
* Organized reporting for job search progress

### Live Job Search

* Search jobs directly from within the application
* Multi-source job search using online Job APIs
* Search by keywords and job titles
* View job information including:

  * Position
  * Company
  * Location
  * Application Link

### Email Integration

* SMTP configuration window
* Gmail App Password authentication
* Manual email sender
* Automatic email notifications

### Subscription Management

* Subscribe to job alerts
* View subscriptions
* Edit subscriptions
* Pause subscriptions
* Delete subscriptions
* Refresh subscription list
* Background monitoring for new jobs
* Automatic email alerts when matching vacancies are found


## Technologies Used

* Python
* Tkinter
* SQLite
* Requests
* REST APIs
* JSON
* SMTP
* EmailMessage
* Threading
* CSV
* Git
* GitHub


## Project Structure

```text
Job Application Tracking System
│
├── gui_tracker.py
├── database.py
├── tracker.py
├── requirements.txt
├── README.md
├── LICENSE
├── Data/
├── Reports/
└── tests/


## Installation

1. Clone the repository

2. Navigate into the project folder

3. Install dependencies

bash
pip install -r requirements.txt


4. Launch the application

 bash
python gui_tracker.py



## Future Improvements

Although Version 2 introduces major functionality, future versions may include:

* Duplicate email prevention
* Save online jobs directly into the tracker
* Salary and experience filters
* Support for additional Job APIs
* Resume management
* Cover letter generator
* AI-powered CV tailoring
* Interview preparation assistant
* Analytics dashboard
* Executable installer (.exe)
* Cloud synchronization
* User authentication and profiles


## Version History

### Version 1.0

* Desktop Job Application Tracker
* SQLite database
* CRUD operations
* CSV Export
* Statistics dashboard

### Version 2.0

* Multi-source Job Search
* REST API integration
* JSON data processing
* SMTP Email Configuration
* Manual Email Sender
* Automated Email Notifications
* Subscription Management
* Background Job Monitoring
* Improved User Interface


## Author

Developed by **Franklyn C. Izediunor** as a portfolio project demonstrating desktop application development, API integration, database management, automation, and software engineering using Python.
