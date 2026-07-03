import requests
import smtplib
from email.message import EmailMessage
import threading
import time
import difflib
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import csv
import os
import webbrowser


def is_safe_url(url):
    if not isinstance(url, str):
        return False
    url = url.strip().lower()
    return url.startswith("http://") or url.startswith("https://")

window = tk.Tk()
selected_id = None
database.create_database()
window.title("Job Application Management System")

window.geometry("1000x700")

# Header frame with title and job search button
header_frame = tk.Frame(window)
header_frame.pack(pady=20, fill="x", padx=20)

title_label = tk.Label(header_frame, text="Job Application Tracker", font=("Arial", 16))
title_label.pack(side=tk.LEFT)

# Jobs button to open job search
job_button = tk.Button(header_frame, text="Jobs", command=lambda: open_job_search_window())
job_button.pack(side=tk.RIGHT)
# SMTP settings button
smtp_button = tk.Button(header_frame, text="SMTP", command=lambda: open_smtp_settings_window())
smtp_button.pack(side=tk.RIGHT, padx=(6,0))
# Subscribe button
subscribe_button = tk.Button(header_frame, text="Subscribe", command=lambda: open_subscription_window())
subscribe_button.pack(side=tk.RIGHT, padx=(6,0))
# My subscriptions button
subscriptions_button = tk.Button(header_frame, text="My Subscriptions", command=lambda: open_subscriptions_window())
subscriptions_button.pack(side=tk.RIGHT, padx=(6,0))

form_status_label = tk.Label(window, text="", font=("Arial", 10, "italic"), fg="blue")
form_status_label.pack(pady=(0, 10))

# Search section
search_container = tk.Frame(window)
search_container.pack(pady=5, fill="x", anchor="w")

search_input_frame = tk.Frame(search_container)
search_input_frame.pack(pady=(0, 5), anchor="w")

search_label = tk.Label(
    search_input_frame,
    text="Search:"
)

search_label.grid(row=0, column=0, padx=(0, 5))

search_entry = tk.Entry(
    search_input_frame,
    width=30
)

search_entry.grid(row=0, column=1, padx=(0, 10))
search_input_frame.columnconfigure(0, weight=0)
search_input_frame.columnconfigure(1, weight=1)

company_label = tk.Label(
    window,
    text="Company:"
)

company_label.pack()

company_entry = tk.Entry(
    window,
    width=40
)

company_entry.pack(pady=5)

position_label = tk.Label(
    window,
    text="Position:"
)

position_label.pack()

# Position combobox with common roles plus 'Other'
positions_list = [
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Mobile Developer",
    "Data Scientist",
    "Data Analyst",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Site Reliability Engineer",
    "QA Engineer",
    "QA Tester",
    "Product Manager",
    "Project Manager",
    "UX Designer",
    "UI Designer",
    "Systems Administrator",
    "Security Engineer",
    "Business Analyst",
    "Technical Writer",
    "Researcher",
    "Sales",
    "Marketing",
    "Customer Support",
    "HR",
    "Finance",
    "Manager",
    "Director",
    "Intern",
    "Contractor",
    "Consultant",
    "Other",
]

position_combobox = ttk.Combobox(window, values=positions_list, width=37, state="readonly")
position_combobox.pack(pady=5)

# Entry to capture custom position when 'Other' is selected
position_other_entry = tk.Entry(window, width=40)
position_other_entry.pack(pady=2)
position_other_entry.config(state="disabled")


def on_position_select(event=None):
    if position_combobox.get() == "Other":
        position_other_entry.config(state="normal")
        position_other_entry.focus_set()
    else:
        position_other_entry.delete(0, tk.END)
        position_other_entry.config(state="disabled")

position_combobox.bind("<<ComboboxSelected>>", on_position_select)

status_label = tk.Label(window, text="Status:")
status_label.pack()

status_combobox = ttk.Combobox(
    window,
    values=["Applied", "Interview", "Offer", "Rejected", "Active"],
    width=37,
    state="readonly"
)
status_combobox.pack(pady=5)

basis_label = tk.Label(
    window,
    text="Basis:"
)

basis_label.pack()

basis_combobox = ttk.Combobox(
    window,
    values=["Full Time/Onsite", "Part Time/Remote", "Full Time/Remote", "Part Time/Onsite", "Internship", "Contract", "Freelance", "Other"],
    width=37,
    state="readonly"
)

basis_combobox.pack(pady=5)


def load_applications():
    rows = database.get_all_applications()

    for row in tree.get_children():
        tree.delete(row)

    for application in rows:
        status = application[3]
        tags = ()
        if status == "Interview":
            tags = ("interview",)
        elif status == "Offer":
            tags = ("offer",)
        elif status == "Rejected":
            tags = ("rejected",)
        tree.insert("", tk.END, values=(application[0], application[1], application[2], application[3], application[4], application[5]), tags=tags)


def get_summary():
    return database.get_application_summary()


def open_statistics_window():
    summary = get_summary()

    stats_window = tk.Toplevel(window)
    stats_window.title("Application Statistics")
    stats_window.geometry("360x220")
    stats_window.resizable(False, False)
    stats_window.transient(window)
    stats_window.grab_set()

    header_label = tk.Label(stats_window, text="Application Statistics", font=("Arial", 14, "bold"))
    header_label.pack(pady=(12, 8))

    stats_frame = tk.Frame(stats_window)
    stats_frame.pack(padx=20, pady=5, fill="x")

    tk.Label(stats_frame, text=f"Total Applications: {summary['total']}", font=("Arial", 11, "bold")).pack(anchor="w", pady=2)
    tk.Label(stats_frame, text=f"Applied: {summary['Applied']}", font=("Arial", 10)).pack(anchor="w", pady=2)
    tk.Label(stats_frame, text=f"Interview: {summary['Interview']}", font=("Arial", 10)).pack(anchor="w", pady=2)
    tk.Label(stats_frame, text=f"Offer: {summary['Offer']}", font=("Arial", 10)).pack(anchor="w", pady=2)
    tk.Label(stats_frame, text=f"Rejected: {summary['Rejected']}", font=("Arial", 10)).pack(anchor="w", pady=2)
    tk.Label(stats_frame, text=f"Active: {summary['Active']}", font=("Arial", 10)).pack(anchor="w", pady=2)

    close_button = tk.Button(stats_window, text="Close", width=12, command=stats_window.destroy)
    close_button.pack(pady=(12, 10))


def export_to_csv():
    rows = database.get_all_applications()

    if not rows:
        messagebox.showwarning("No Data", "No applications to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile="applications.csv"
    )

    if not file_path:
        return

    try:
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Company", "Position", "Status", "Basis", "Date Added"])
            writer.writerows(rows)

        messagebox.showinfo("Export Successful", f"Applications exported to:\n{file_path}")
        os.startfile(file_path)
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")


def validate_application_inputs(company, position, status, basis):
    if not company.strip():
        messagebox.showwarning("Invalid Input", "Company name is required.")
        return False

    if not position.strip():
        messagebox.showwarning("Invalid Input", "Position is required.")
        return False

    if not status.strip():
        messagebox.showwarning("Invalid Input", "Status is required.")
        return False

    if not basis.strip():
        messagebox.showwarning("Invalid Input", "Basis is required.")
        return False

    return True


def add_application():
    global selected_id

    if selected_id is not None:
        messagebox.showinfo(
            "Edit In Progress",
            "You are editing an existing application. Click Update Application to save changes or Clear to start a new entry."
        )
        return

    company = company_entry.get().strip()
    position = position_combobox.get().strip()
    if position == "Other":
        position = position_other_entry.get().strip()
    status = status_combobox.get().strip()
    basis = basis_combobox.get().strip()

    if not validate_application_inputs(company, position, status, basis):
        return

    database.add_to_database(company, position, status, basis)

    messagebox.showinfo("Success", "Application saved successfully.")

    clear_fields()
    load_applications()


def update_application():
    global selected_id

    if selected_id is None:
        messagebox.showwarning(
            "No Selection",
            "Please select an application and click Edit before updating."
        )
        return

    company = company_entry.get().strip()
    position = position_combobox.get().strip()
    if position == "Other":
        position = position_other_entry.get().strip()
    status = status_combobox.get().strip()
    basis = basis_combobox.get().strip()

    if not validate_application_inputs(company, position, status, basis):
        return

    database.update_application(selected_id, company, position, status, basis)

    messagebox.showinfo("Success", "Application updated successfully.")

    selected_id = None
    clear_fields()
    load_applications()


def delete_application():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select an application to delete.")
        return

    values = tree.item(selected_item[0], "values")
    application_id = values[0]
    company = values[1]

    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the application for {company}?")
    if confirm:
        database.delete_application(application_id)
        load_applications()
        messagebox.showinfo("Deleted", "Application deleted successfully.")
    else:
        messagebox.showinfo("Cancelled", "Deletion cancelled.")

    clear_fields()

button_frame = tk.Frame(window)
button_frame.pack(pady=15)

add_button = tk.Button(
    button_frame,
    text="Add Application",
    width=16,
    command=add_application
)

update_button = tk.Button(
    button_frame,
    text="Update Application",
    width=16,
    command=update_application,
    state="disabled"
)


delete_button = tk.Button(
    button_frame,
    text="Delete Application",
    width=16,
    command=delete_application
)

def search_applications(event=None):
    search_term = search_entry.get().strip()

    if not search_term:
        load_applications()
        return

    rows = database.search_applications(search_term)

    for item in tree.get_children():
        tree.delete(item)

    for row in rows:
        status = row[3]
        tags = ()
        if status == "Interview":
            tags = ("interview",)
        elif status == "Offer":
            tags = ("offer",)
        elif status == "Rejected":
            tags = ("rejected",)
        tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], row[4], row[5]), tags=tags)

search_entry.bind("<KeyRelease>", search_applications)

view_stats_button = tk.Button(
    button_frame,
    text="View Statistics",
    width=14,
    command=open_statistics_window
)

view_stats_button.pack(side=tk.LEFT, padx=5)

export_button = tk.Button(
    button_frame,
    text="Export CSV",
    width=12,
    command=export_to_csv
)

export_button.pack(side=tk.LEFT, padx=5)

show_all_button = tk.Button(
    button_frame,
    text="Show All",
    width=12,
    command=load_applications
)

show_all_button.pack(side=tk.LEFT, padx=5)

def edit_application():

    global selected_id

    selected_item = tree.selection()

    if not selected_item:

        messagebox.showwarning(
            "No Selection",
            "Please select an application to edit."
        )

        return

    values = tree.item(
        selected_item[0],
        "values"
    )

    selected_id = values[0]

    company = values[1]
    position = values[2]
    status = values[3]
    basis = values[4]

    company_entry.delete(0, tk.END)
    company_entry.insert(0, company)

    position_combobox.set(position)

    status_combobox.set(status)

    basis_combobox.set(basis)

    form_status_label.config(text=f"Editing application ID {selected_id}")
    add_button.config(state="disabled")
    update_button.config(state="normal")

edit_button = tk.Button(
    button_frame,
    text="Edit Application",
    width=16,
    command=edit_application
)
edit_button.pack(side=tk.LEFT, padx=5)

def search_arbeitnow():

    jobs = []

    try:

        resp = requests.get(
            "https://www.arbeitnow.com/api/job-board-api",
            timeout=12
        )

        resp.raise_for_status()

        data = resp.json()

        jobs = data.get("data", [])

    except Exception as e:

        print("ArbeitNow Error:", e)

    return jobs

def search_remotive():

    jobs = []

    try:

        resp = requests.get(
            "https://remotive.com/api/remote-jobs",
            timeout=12
        )

        resp.raise_for_status()

        data = resp.json()

        jobs = data.get("jobs", [])

    except Exception as e:

        print("Remotive Error:", e)

    return jobs

### Jobs API integration
def search_jobs_api(query="", limit=200):

    all_jobs = []
    all_jobs.extend(search_arbeitnow())
    all_jobs.extend(search_remotive())

    qlow = query.strip().lower()
    results = []

    def matches_query(job, q):
        title = job.get("title", "") or ""
        company = job.get("company_name", "") or job.get("company", "") or ""
        location = job.get("location", "") or job.get("candidate_required_location", "") or ""
        description = job.get("description", "") or job.get("job_description", "") or ""

        hay = " ".join([title, company, location, description]).lower()

        if not q:
            return True

        tokens = [t for t in q.split() if t]

        if any(t in hay for t in tokens):
            return True

        try:
            return bool(difflib.get_close_matches(q, [title.lower()], cutoff=0.6))
        except Exception:
            return False

    for j in all_jobs:

        if matches_query(j, qlow):

            results.append({
                "title": j.get("title", ""),
                "company": j.get("company_name", "") or j.get("company", ""),
                "location": j.get("location", "") or j.get("candidate_required_location", ""),
                "url": j.get("url", ""),
                "date": j.get("created_at", "") or j.get("publication_date", "")
            })

            if len(results) >= limit:
                break

    return results

def open_job_search_window():
    """Open a small job search window and display vacancies."""
    win = tk.Toplevel(window)
    win.title("Job Search")
    win.geometry("640x320")
    win.transient(window)
    win.grab_set()

    all_jobs = search_jobs_api("")

    # extract unique job titles for dropdown
    titles = []
    seen = set()
    for j in all_jobs:
        t = j.get("title", "").strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            titles.append(t)
        if len(titles) >= 200:
            break

    if not titles:
        titles = [
            "Software Engineer", "Frontend Developer", "Backend Developer",
            "Full Stack Developer", "Data Scientist", "DevOps Engineer", "Product Manager",
            "Designer", "QA Engineer"
        ]

    top_frame = tk.Frame(win)
    top_frame.pack(fill="x", padx=8, pady=6)

    tk.Label(top_frame, text="Choose job title:").pack(side=tk.LEFT)

    combo_values = titles[:50]
    combo_values.append("Other")
    title_combo = ttk.Combobox(top_frame, values=combo_values, width=40)
    title_combo.set("")
    title_combo.pack(side=tk.LEFT, padx=6)

    other_entry = tk.Entry(top_frame, width=30)
    other_entry.pack(side=tk.LEFT, padx=6)
    other_entry.config(state="disabled")

    def toggle_other(event=None):
        val = title_combo.get().strip()
        if val.lower() == "other":
            other_entry.config(state="normal")
            other_entry.focus_set()
        else:
            other_entry.delete(0, tk.END)
            other_entry.config(state="disabled")

    title_combo.bind("<<ComboboxSelected>>", toggle_other)
    title_combo.bind("<KeyRelease>", toggle_other)

    cols = ("Title", "Company", "Location", "Date", "URL")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=10)
    for c in cols[:-1]:
        tree.heading(c, text=c)
        tree.column(c, width=140)
    tree.heading("URL", text="URL")
    tree.column("URL", width=0, stretch=False)

    vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscroll=vsb.set)
    tree.pack(side=tk.LEFT, fill="both", expand=True, padx=(8,0), pady=8)
    vsb.pack(side=tk.LEFT, fill="y", pady=8)

    def populate_results(results):
        for i in tree.get_children():
            tree.delete(i)
        for r in results:
            tree.insert("", tk.END, values=(r.get("title", ""), r.get("company", ""), r.get("location", ""), r.get("date", ""), r.get("url", "")))

    def do_search(event=None):
        q = title_combo.get().strip()
        if q.lower() == "other":
            q = other_entry.get().strip()
        if not q:
            messagebox.showwarning("No Query", "Please choose or enter a query.")
            return

        results = search_jobs_api(q, limit=200)
        populate_results(results)
        if not results:
            messagebox.showinfo("No Results", "No jobs found for that query. Try a broader term or check your internet connection.")

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", padx=8, pady=(0,8))
    search_btn = tk.Button(btn_frame, text="Search", command=do_search)
    search_btn.pack(side=tk.LEFT)

    def show_all():
        title_combo.set("")
        other_entry.delete(0, tk.END)
        other_entry.config(state="disabled")
        populate_results(all_jobs)

    show_all_btn = tk.Button(btn_frame, text="Show All", command=show_all)
    show_all_btn.pack(side=tk.LEFT, padx=6)

    # Email subscription controls
    email_label = tk.Label(btn_frame, text="Notify email:")
    email_label.pack(side=tk.LEFT, padx=(12,4))
    email_entry = tk.Entry(btn_frame, width=28)
    email_entry.pack(side=tk.LEFT, padx=4)

    def subscribe_current_query():
        q = title_combo.get().strip()
        if q.lower() == "other":
            q = other_entry.get().strip()
        email = email_entry.get().strip()
        if not q:
            messagebox.showwarning("No Query", "Please choose or enter a query to subscribe.")
            return
        if not email or "@" not in email:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return
        try:
            database.add_subscription(email, q)
            messagebox.showinfo("Subscribed", f"Subscribed {email} for '{q}' job alerts.")
        except Exception as e:
            messagebox.showerror("Subscribe Error", str(e))

    subscribe_btn = tk.Button(btn_frame, text="Subscribe", command=subscribe_current_query)
    subscribe_btn.pack(side=tk.LEFT, padx=6)

    title_combo.bind('<Return>', do_search)
    other_entry.bind('<Return>', do_search)

    def on_open(event=None):
        sel = tree.selection()
        if not sel:
            return
        url = tree.item(sel[0], "values")[4]
        if url and is_safe_url(url):
            webbrowser.open(url)
        elif url:
            messagebox.showwarning("Invalid URL", "The selected job link is not safe to open.")

    tree.bind("<Double-1>", on_open)

    def import_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a job to import.")
            return
        vals = tree.item(sel[0], "values")
        title, company, location, date, url = vals
        basis = location if location else "Remote"
        try:
            database.add_to_database(company, title, "Active", basis)
            messagebox.showinfo("Imported", f"Imported job '{title}' at {company}")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    import_btn = tk.Button(btn_frame, text="Import to Tracker", command=import_selected)
    import_btn.pack(side=tk.LEFT, padx=6)
    open_btn = tk.Button(btn_frame, text="Open Link", command=on_open)
    open_btn.pack(side=tk.LEFT)

    populate_results(all_jobs)
    return win

def clear_fields():
    global selected_id

    selected_id = None
    company_entry.delete(0, tk.END)
    position_combobox.set("")
    position_other_entry.delete(0, tk.END)
    position_other_entry.config(state="disabled")
    status_combobox.set("")
    basis_combobox.set("")
    form_status_label.config(text="")
    add_button.config(state="normal")
    update_button.config(state="disabled")
    company_entry.focus_set()

clear_button = tk.Button(
    button_frame,
    text="Clear",
    width=16,
    command=clear_fields
)

add_button.pack(side=tk.LEFT, padx=5)
update_button.pack(side=tk.LEFT, padx=5)
edit_button.pack(side=tk.LEFT, padx=5)
delete_button.pack(side=tk.LEFT, padx=5)
clear_button.pack(side=tk.LEFT, padx=5)

# Create sorting variable
sort_column = "Company"
sort_reverse = False

def on_heading_click(col):
    global sort_column, sort_reverse
    if sort_column == col:
        sort_reverse = not sort_reverse
    else:
        sort_column = col
        sort_reverse = False
    sort_applications()

def sort_applications():
    # Get all items with their tags
    items = [(tree.item(item, "values"), tree.item(item, "tags")) for item in tree.get_children()]
    
    # Column index mapping
    col_index = {"ID": 0, "Company": 1, "Position": 2, "Status": 3, "Basis": 4, "Date Added": 5}
    
    # Sort by the selected column
    try:
        items.sort(key=lambda x: x[0][col_index[sort_column]], reverse=sort_reverse)
    except:
        items.sort(key=lambda x: str(x[0][col_index[sort_column]]), reverse=sort_reverse)
    
    # Refresh tree with sorted items
    for item in tree.get_children():
        tree.delete(item)
    
    for values, tags in items:
        tree.insert("", tk.END, values=values, tags=tags)

tree = ttk.Treeview(
    window,
    columns=(
        "ID",
        "Company",
        "Position",
        "Status",
        "Basis",
        "Date Added"
    ),
    show="headings"
)
tree.heading("ID", text="ID", command=lambda: on_heading_click("ID"))

tree.column("ID", width=50)

tree.heading("Company", text="Company", command=lambda: on_heading_click("Company"))

tree.heading("Position", text="Position", command=lambda: on_heading_click("Position"))

tree.heading("Status", text="Status", command=lambda: on_heading_click("Status"))

tree.heading("Basis", text="Basis", command=lambda: on_heading_click("Basis"))

tree.heading("Date Added", text="Date Added", command=lambda: on_heading_click("Date Added"))

tree.column("Company", width=150)

tree.column("Position", width=150)

tree.column("Status", width=100)

tree.column("Basis", width=150)

tree.column("Date Added", width=150)

# Configure tag colors
tree.tag_configure("interview", background="#FFFF99")
tree.tag_configure("offer", background="#99FF99")
tree.tag_configure("rejected", background="#FF9999")

tree.pack(
    pady=20,
    fill="both",
    expand=True
)


def check_subscriptions_once():
    """Check all saved subscriptions and send a mail only when new matching jobs appear."""
    subs = database.get_subscriptions()
    for sub in subs:
        sub_id, email, query, location, last_notified, _, paused = sub
        if paused:
            continue

        try:
            results = search_jobs_api(query, limit=50)
        except Exception:
            results = []

        def matches_location(job):
            requested_location = (location or "").strip().lower()
            if not requested_location:
                return True
            location_fields = [
                job.get("location", "") or "",
                job.get("candidate_required_location", "") or "",
            ]
            hay = " ".join(location_fields).lower()
            return requested_location in hay

        matching_jobs = [job for job in results if matches_location(job)]
        if not matching_jobs:
            continue

        seen_urls = database.get_subscription_sent_urls(sub_id)
        new_jobs = []
        new_urls = []
        for job in matching_jobs:
            url = (job.get("url") or "").strip()
            if not url:
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)
            new_urls.append(url)
            new_jobs.append(job)

        if not new_jobs:
            continue

        body_lines = [f"New job alerts for '{query}':", ""]
        for r in new_jobs[:10]:
            body_lines.append(f"{r.get('title','')} - {r.get('company','')}")
            if r.get('location'):
                body_lines.append(f"Location: {r.get('location')}")
            if r.get('url'):
                body_lines.append(r.get('url'))
            body_lines.append("")
        body = "\n".join(body_lines)

        msg = EmailMessage()
        msg['Subject'] = f"New jobs for {query}"
        msg['To'] = email
        msg.set_content(body)

        smtp_cfg = database.get_smtp_settings()
        sent = False
        if smtp_cfg and smtp_cfg.get('server'):
            try:
                server = smtp_cfg.get('server')
                port = int(smtp_cfg.get('port') or 25)
                username = smtp_cfg.get('username')
                password = smtp_cfg.get('password')
                use_tls = bool(smtp_cfg.get('use_tls'))
                from_email = smtp_cfg.get('from_email') or username or 'no-reply@example.com'

                msg['From'] = from_email
                with smtplib.SMTP(server, port, timeout=20) as s:
                    if use_tls:
                        try:
                            s.starttls()
                        except Exception:
                            pass
                    if username:
                        s.login(username, password)
                    s.send_message(msg)
                print(f"Sent subscription email to {email} for '{query}' via {server}:{port}")
                sent = True
            except Exception as e:
                print(f"Failed to send subscription email to {email} via configured SMTP: {e}")

        if not sent:
            try:
                msg['From'] = msg.get('From', 'no-reply@example.com')
                with smtplib.SMTP('localhost') as s:
                    s.send_message(msg)
                print(f"Sent subscription email to {email} for '{query}' via localhost")
                sent = True
            except Exception as e:
                print(f"Failed to send subscription email to {email} via localhost: {e}")

        if sent:
            database.update_subscription_last_notified(
                sub_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                new_urls[0] if new_urls else None
            )
            database.save_subscription_sent_urls(sub_id, new_urls)


def subscription_worker(interval_seconds=3600):
    while True:
        try:
            check_subscriptions_once()
        except Exception as e:
            print(f"Subscription worker error: {e}")
        time.sleep(interval_seconds)

# Start background subscription worker (daemon thread)
try:
    threading.Thread(target=subscription_worker, args=(3600,), daemon=True).start()
except Exception:
    pass


def send_email_via_smtp(to_email, subject, body):
    cfg = database.get_smtp_settings() or {}
    if not cfg.get('username') or not cfg.get('password'):
        raise RuntimeError("Please configure SMTP settings first.")

    server = (cfg.get('server') or 'smtp.gmail.com').strip() or 'smtp.gmail.com'
    port = int(cfg.get('port') or 587)
    username = cfg.get('username')
    password = cfg.get('password')
    use_tls = bool(cfg.get('use_tls', True))
    from_email = cfg.get('from_email') or username or 'no-reply@example.com'

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['To'] = to_email
    msg['From'] = from_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(server, port, timeout=20) as smtp:
            if use_tls:
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        return True, "Email sent successfully."
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Use a valid Gmail app password."
    except Exception as exc:
        return False, f"Failed to send email: {exc}"


def open_subscription_window():
    win = tk.Toplevel(window)
    win.title("Subscribe")
    win.geometry("520x260")
    win.transient(window)
    win.grab_set()

    frm = tk.Frame(win)
    frm.pack(padx=14, pady=12, fill="both", expand=True)

    tk.Label(frm, text="Email:").grid(row=0, column=0, sticky="w", pady=(0, 6))
    email_entry = tk.Entry(frm, width=48)
    email_entry.grid(row=0, column=1, sticky="ew", pady=(0, 6))

    tk.Label(frm, text="Job Title:").grid(row=1, column=0, sticky="w", pady=(0, 6))
    title_entry = tk.Entry(frm, width=48)
    title_entry.grid(row=1, column=1, sticky="ew", pady=(0, 6))

    tk.Label(frm, text="Location (optional):").grid(row=2, column=0, sticky="w", pady=(0, 6))
    location_entry = tk.Entry(frm, width=48)
    location_entry.grid(row=2, column=1, sticky="ew", pady=(0, 6))

    tk.Label(
        frm,
        text="Subscriptions are checked every hour and emails are sent when new jobs match.",
        fg="gray40",
        justify="left"
    ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 0))

    frm.columnconfigure(1, weight=1)

    def save_subscription():
        email = email_entry.get().strip()
        title = title_entry.get().strip()
        location = location_entry.get().strip()

        if not email or "@" not in email:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return
        if not title:
            messagebox.showwarning("Missing Job Title", "Please enter a job title to subscribe to.")
            return

        try:
            created = database.add_subscription(email, title, location or None)
            if created:
                messagebox.showinfo("Subscribed", "Your subscription was saved. New matching jobs will be emailed automatically.")
                win.destroy()
            else:
                messagebox.showinfo("Already Subscribed", "That subscription already exists.")
        except Exception as exc:
            messagebox.showerror("Subscribe Error", str(exc))

    btn_frame = tk.Frame(frm)
    btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="e")
    tk.Button(btn_frame, text="Save Subscription", width=16, command=save_subscription).pack(side=tk.LEFT, padx=(0, 6))
    tk.Button(btn_frame, text="Cancel", width=12, command=win.destroy).pack(side=tk.LEFT)


def open_subscriptions_window():
    win = tk.Toplevel(window)
    win.title("My Subscriptions")
    win.geometry("820x400")
    win.transient(window)
    win.grab_set()

    frm = tk.Frame(win)
    frm.pack(fill="both", expand=True, padx=12, pady=12)

    columns = ("ID", "Email", "Job Title", "Location", "Last Notified", "Paused")
    tree = ttk.Treeview(frm, columns=columns, show="headings", height=12)
    for col in columns:
        width = 100
        if col == "Job Title":
            width = 220
        elif col == "Location":
            width = 150
        elif col == "Last Notified":
            width = 140
        tree.heading(col, text=col)
        tree.column(col, width=width)
    tree.pack(fill="both", expand=True)

    def refresh_subscriptions():
        for item in tree.get_children():
            tree.delete(item)
        for sub in database.get_subscriptions():
            sub_id, email, query, location, last_notified, _, paused = sub
            tree.insert(
                "",
                tk.END,
                values=(sub_id, email, query, location or "-", last_notified or "Never", "Yes" if paused else "No")
            )

    refresh_subscriptions()

    btn_frame = tk.Frame(frm)
    btn_frame.pack(fill="x", pady=(8, 0))

    def delete_selected():
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a subscription to delete.")
            return
        sub_id = tree.item(selection[0], "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", "Delete this subscription?")
        if confirm:
            database.delete_subscription(sub_id)
            refresh_subscriptions()

    def edit_selected():
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a subscription to edit.")
            return
        sub_id, email, query, location, _, paused = tree.item(selection[0], "values")
        sub_id = int(sub_id)

        edit_win = tk.Toplevel(win)
        edit_win.title("Edit Subscription")
        edit_win.geometry("420x220")
        edit_win.transient(win)
        edit_win.grab_set()

        edit_frm = tk.Frame(edit_win)
        edit_frm.pack(padx=12, pady=12, fill="x")

        tk.Label(edit_frm, text="Email:").grid(row=0, column=0, sticky="w")
        email_entry = tk.Entry(edit_frm, width=40)
        email_entry.grid(row=0, column=1, pady=4)
        email_entry.insert(0, email)

        tk.Label(edit_frm, text="Query:").grid(row=1, column=0, sticky="w")
        query_entry = tk.Entry(edit_frm, width=40)
        query_entry.grid(row=1, column=1, pady=4)
        query_entry.insert(0, query)

        tk.Label(edit_frm, text="Location:").grid(row=2, column=0, sticky="w")
        location_entry = tk.Entry(edit_frm, width=40)
        location_entry.grid(row=2, column=1, pady=4)
        location_entry.insert(0, location if location != "-" else "")

        def save_edit():
            new_email = email_entry.get().strip()
            new_query = query_entry.get().strip()
            new_location = location_entry.get().strip() or None
            if not new_email or "@" not in new_email:
                messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
                return
            if not new_query:
                messagebox.showwarning("Invalid Query", "Please enter a search query.")
                return
            database.update_subscription(sub_id, new_email, new_query, new_location)
            refresh_subscriptions()
            edit_win.destroy()

        save_btn = tk.Button(edit_frm, text="Save", width=12, command=save_edit)
        save_btn.grid(row=3, column=0, columnspan=2, pady=(12, 0))

    def toggle_pause_selected():
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a subscription to pause or resume.")
            return
        sub_id, _, _, _, _, paused = tree.item(selection[0], "values")
        sub_id = int(sub_id)
        paused_flag = 0 if paused == "Yes" else 1
        database.set_subscription_paused(sub_id, paused_flag)
        refresh_subscriptions()

    tk.Button(btn_frame, text="Edit Selected", command=edit_selected).pack(side=tk.LEFT)
    tk.Button(btn_frame, text="Pause/Resume", command=toggle_pause_selected).pack(side=tk.LEFT, padx=(6, 0))
    tk.Button(btn_frame, text="Delete Selected", command=delete_selected).pack(side=tk.LEFT, padx=(6, 0))
    tk.Button(btn_frame, text="Refresh", command=refresh_subscriptions).pack(side=tk.LEFT, padx=(6, 0))


def open_smtp_settings_window():
    win = tk.Toplevel(window)
    win.title("SMTP Settings")
    win.geometry("480x260")
    win.transient(window)
    win.grab_set()

    cfg = database.get_smtp_settings() or {}

    frm = tk.Frame(win)
    frm.pack(padx=12, pady=8, fill="x")

    tk.Label(frm, text="SMTP Server:").grid(row=0, column=0, sticky="w")
    server_e = tk.Entry(frm, width=40)
    server_e.grid(row=0, column=1, pady=4)
    server_e.insert(0, cfg.get('server','smtp.gmail.com'))

    tk.Label(frm, text="Port:").grid(row=1, column=0, sticky="w")
    port_e = tk.Entry(frm, width=12)
    port_e.grid(row=1, column=1, sticky="w", pady=4)
    port_e.insert(0, str(cfg.get('port','587')))

    tk.Label(frm, text="Use TLS:").grid(row=2, column=0, sticky="w")
    use_tls_var = tk.IntVar(value=1 if cfg.get('use_tls', True) else 0)
    tk.Checkbutton(frm, variable=use_tls_var).grid(row=2, column=1, sticky="w", pady=4)

    tk.Label(frm, text="Username:").grid(row=3, column=0, sticky="w")
    user_e = tk.Entry(frm, width=40)
    user_e.grid(row=3, column=1, pady=4)
    user_e.insert(0, cfg.get('username',''))

    tk.Label(frm, text="Password:").grid(row=4, column=0, sticky="w")
    pass_e = tk.Entry(frm, width=40, show='*')
    pass_e.grid(row=4, column=1, pady=4)
    pass_e.insert(0, cfg.get('password',''))

    tk.Label(frm, text="From Email:").grid(row=5, column=0, sticky="w")
    from_e = tk.Entry(frm, width=40)
    from_e.grid(row=5, column=1, pady=4)
    from_e.insert(0, cfg.get('from_email',''))

    tk.Label(frm, text="Use a Gmail app password for security.", fg="gray40").grid(row=6, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def save_settings():
        server = server_e.get().strip()
        try:
            port = int(port_e.get().strip())
        except Exception:
            messagebox.showwarning("Invalid Port", "Port must be a number.")
            return
        username = user_e.get().strip()
        password = pass_e.get()
        use_tls = bool(use_tls_var.get())
        from_email = from_e.get().strip()
        try:
            database.set_smtp_settings(server, port, username, password, use_tls, from_email)
            messagebox.showinfo("Saved", "SMTP settings saved.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    save_btn = tk.Button(win, text="Save", command=save_settings)
    save_btn.pack(pady=8)


load_applications()

company_entry.bind(
    "<Return>",
    lambda event: position_combobox.focus_set()
)

position_combobox.bind(
    "<Return>",
    lambda event: position_other_entry.focus_set() if position_combobox.get() == "Other" else status_combobox.focus_set()
)

status_combobox.bind(
    "<Return>",
    lambda event: basis_combobox.focus_set()
)

company_entry.focus_set()

window.mainloop()