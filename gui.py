from generate import *
from delete import truncate_and_reset_all_data
from config import CONNECTION_URL, ROOM_TYPES

from dbtypes import Campus, Building, Room, Worker, Request, RequestStatus, Base

import sqlalchemy, datetime
from sqlalchemy.orm import sessionmaker

import tkinter as tk
from tkinter import ttk, messagebox

from custom_sql import custom_sql

engine = sqlalchemy.create_engine(CONNECTION_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class Maintenance(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maintenance Management System")
        self.geometry("1200x700")
        self.session = Session()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=1, fill='both')
        
        self.sql = custom_sql(self.session, engine)
        
        self.worker_view_tab()
        self.add_location_tab()
        self.user_view_tab()
            
    def user_view_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="User View")

        # Account Creation Section
        self.create_frame = ttk.LabelFrame(frame, text="Create Account")
        self.create_frame.pack(pady=10, fill='x', padx=10)

        ttk.Label(self.create_frame, text="Email:").grid(row=0, column=0, sticky='e')
        self.user_email_var = tk.StringVar()
        ttk.Entry(self.create_frame, textvariable=self.user_email_var).grid(row=0, column=1)

        ttk.Label(self.create_frame, text="First Name:").grid(row=1, column=0, sticky='e')
        self.first_name_var = tk.StringVar()
        ttk.Entry(self.create_frame, textvariable=self.first_name_var).grid(row=1, column=1)

        ttk.Label(self.create_frame, text="Last Name:").grid(row=2, column=0, sticky='e')
        self.last_name_var = tk.StringVar()
        ttk.Entry(self.create_frame, textvariable=self.last_name_var).grid(row=2, column=1)

        ttk.Button(self.create_frame, text="Create Account", command=self.create_user).grid(row=3, column=0, columnspan=2, pady=5)

        # Login Section
        login_frame = ttk.LabelFrame(frame, text="Log In")
        login_frame.pack(pady=10, fill='x', padx=10)

        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky='e')
        self.login_email_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.login_email_var).grid(row=0, column=1)

        ttk.Button(login_frame, text="Log In", command=self.login_user).grid(row=1, column=0, columnspan=2, pady=5)
        self.logout_button = ttk.Button(login_frame, text="Log Out", command=self.logout_user)
        self.logout_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.logout_button.grid_remove()  # Hide initially
        
        # After Login
        self.user_action_frame = ttk.LabelFrame(frame, text="Submit Request")
        self.user_action_frame.pack(pady=20, fill='x', padx=10)
        self.user_action_frame.pack_forget()  # Hide initially
        

        # Room
        ttk.Label(self.user_action_frame, text="Select Room:").grid(row=0, column=0, sticky='e')
        self.request_room_var = tk.StringVar()
        self.room_dropdown = ttk.Combobox(self.user_action_frame, textvariable=self.request_room_var, width=40)
        self.room_dropdown.grid(row=0, column=1)
        self.refresh_room_dropdown()  # Populate dropdown with rooms

        ttk.Label(self.user_action_frame, text="Description:").grid(row=1, column=0, sticky='e', pady=5)
        self.request_description_var = tk.StringVar()
        ttk.Entry(self.user_action_frame, textvariable=self.request_description_var, width=40).grid(row=1, column=1, pady=5)

        ttk.Button(self.user_action_frame, text="Submit Request", command=self.submit_request).grid(row=2, column=0, columnspan=2, pady=10)

        # User Requests View
        self.user_requests_frame = ttk.LabelFrame(frame, text="Your Requests")
        self.user_requests_frame.pack(pady=20, fill='x', padx=10)
        self.user_requests_frame.pack_forget()  # Hide initially
        
        self.user_request_tree = ttk.Treeview(self.user_requests_frame, columns=('ID', 'Room', 'Description', 'Status', 'Req Time', 'Complete Time'), show='headings')
        for col in self.user_request_tree["columns"]:
            self.user_request_tree.heading(col, text=col)
        self.user_request_tree.pack(fill='x')
        
    def worker_view_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Worker View")

        # Workers
        worker_label = ttk.Label(frame, text="Workers")
        worker_label.pack()
        self.worker_tree = ttk.Treeview(frame, columns=('Email', 'First Name', 'Last Name', 'Specialization'), show='headings')
        for col in self.worker_tree["columns"]:
            self.worker_tree.heading(col, text=col)
        self.worker_tree.pack(fill='x')
        self.refresh_worker_table()

        # Requests
        ttk.Label(frame, text="Requests").pack()
        self.request_tree = ttk.Treeview(frame, columns=('ID', 'User', 'Room', 'Description', 'Assignee','Status', 'Req Time', 'Complete Time'), show='headings')
        for col in self.request_tree["columns"]:
            self.request_tree.heading(col, text=col)
        self.request_tree.pack(fill='x')
        self.refresh_request_table()

        # Worker Assignments
        ttk.Label(frame, text="Assign Worker to Request").pack()
        assign_frame = ttk.Frame(frame)
        assign_frame.pack(pady=5)

        ttk.Button(assign_frame, text="Assign", command=self.assign_worker).pack(side='left', padx=2)

        # Completion Time
        ttk.Button(frame, text="Set Selected Request To Complete", command=self.set_completion_time).pack(pady=10)
    
    def add_location_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Add Locations")

        # Campus
        ttk.Label(frame, text="Add Campus").grid(row=0, column=0, columnspan=2, pady=(10, 0))

        ttk.Label(frame, text="Campus Name:").grid(row=1, column=0, sticky='e')
        self.campus_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.campus_name_var).grid(row=1, column=1)

        ttk.Label(frame, text="Campus Address:").grid(row=2, column=0, sticky='e')
        self.campus_address_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.campus_address_var).grid(row=2, column=1)

        ttk.Button(frame, text="Add Campus", command=self.add_campus).grid(row=3, column=0, columnspan=2, pady=5)

        # Building 
        ttk.Label(frame, text="Add Building").grid(row=4, column=0, columnspan=2, pady=(20, 0))

        ttk.Label(frame, text="Building Name:").grid(row=5, column=0, sticky='e')
        self.building_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.building_name_var).grid(row=5, column=1)

        ttk.Label(frame, text="Building Address:").grid(row=6, column=0, sticky='e')
        self.building_address_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.building_address_var).grid(row=6, column=1)

        ttk.Label(frame, text="Campus:").grid(row=7, column=0, sticky='e')
        self.building_campus_var = tk.StringVar()
        self.campus_dropdown = ttk.Combobox(frame, textvariable=self.building_campus_var)
        self.campus_dropdown.grid(row=7, column=1)
        self.refresh_campus_dropdown()

        ttk.Button(frame, text="Add Building", command=self.add_building).grid(row=8, column=0, columnspan=2, pady=5)

        # Room  
        ttk.Label(frame, text="Add Room").grid(row=9, column=0, columnspan=2, pady=(20, 0))

        ttk.Label(frame, text="Room Name:").grid(row=10, column=0, sticky='e')
        self.room_name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.room_name_var).grid(row=10, column=1)

        ttk.Label(frame, text="Room Type:").grid(row=11, column=0, sticky='e')
        self.room_type_var = tk.StringVar()
        self.room_type_dropdown = ttk.Combobox(frame, textvariable=self.room_type_var, values=ROOM_TYPES, state='readonly')
        self.room_type_dropdown.grid(row=11, column=1)

        ttk.Label(frame, text="Building:").grid(row=12, column=0, sticky='e')
        self.room_building_var = tk.StringVar()
        self.building_dropdown = ttk.Combobox(frame, textvariable=self.room_building_var)
        self.building_dropdown.grid(row=12, column=1)
        self.refresh_building_dropdown()

        ttk.Button(frame, text="Add Room", command=self.add_room).grid(row=13, column=0, columnspan=2, pady=5)

    def create_user(self):
        email = self.user_email_var.get().strip()
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()

        if not email or not first_name or not last_name:
            messagebox.showerror("Error", "Email, First Name, and Last Name are required.")
            return

        if self.sql.query_where(User, f"email={email}")[0] or self.sql.query_where(Worker, f"email={email}")[0]:
            messagebox.showerror("Error", "User with this email already exists.")
            return

        new_user = User(email=email, firstname=first_name, lastname=last_name)
        self.sql.create_entry(User)

    def refresh_user_requests_table(self):
        self.user_request_tree.delete(*self.user_request_tree.get_children())  # Clear existing rows
        email = getattr(self, "current_user_email", None)
        if email:
            user_requests = self.sql.query_where(Request, f"user_email={email}")
            for r in user_requests:
                status_str = self.sql.query_where(RequestStatus, f"id={r.status_id}")[0].name
                self.user_request_tree.insert('', 'end', values=(r.id, f"{r.room.building.campus.name} - {r.room.building.name} - {r.room.name}", r.description, status_str, r.reqtime, r.comptime))

    def login_user(self):
        email = self.login_email_var.get().strip()
        if self.sql.query_where(User, f"email={email}")[0] is not None:
            self.current_user_email = email
            self.user_action_frame.pack()
            self.user_requests_frame.pack()
            self.refresh_user_requests_table()
            self.refresh_request_table()
            self.logout_button.grid()
        else:
            messagebox.showerror("Error", "Email not associated with a user.")

    def logout_user(self):
        self.current_user_email = None
        self.user_action_frame.pack_forget()
        self.logout_button.grid_remove()
        self.user_requests_frame.pack_forget()

    def refresh_room_dropdown(self):
        self.room_dropdown['values'] = [
            f"{r.building.campus.name} - {r.building.name} - {r.name}"
            for r in self.sql.query_all(Room)
        ]


    def submit_request(self):
        email = getattr(self, "current_user_email", None)
        if not email:
            messagebox.showerror("Error", "No user logged in.")
            return

        user = self.sql.query_where(User, f"email={email}")[0]
        if not user:
            messagebox.showerror("Error", f"User with email '{email}' does not exist.")
            return

        room_text = self.request_room_var.get().strip()
        description = self.request_description_var.get().strip()

        if not room_text or " - " not in room_text:
            messagebox.showerror("Error", "Please complete all fields.")
            return

        campus_name, building_name, room_name = map(str.strip, room_text.split(" - ", 2))
        room = None
        for r in self.sql.query_all(Room):
            if r.name == room_name and r.building.name == building_name and r.campus.name == campus_name:
                room = r
                break

        if room:
            new_req = Request(
                user_email=email,
                description=description,
                worker_email=None,
                status_id=1,
                reqtime=datetime.datetime.now(),
                comptime=None
            )
            self.sql.create_entry(room)
            self.refresh_request_table()
            self.refresh_user_requests_table()

        else:
            messagebox.showerror("Error", "Room not found.")

    def refresh_worker_table(self):
        self.worker_tree.delete(*self.worker_tree.get_children())
        for w in self.sql.query_all(Worker):
            job_type = self.sql.query_where(JobType, f"id={w.job_type_id}")[0].name
            # print(job_type)
            self.worker_tree.insert('', 'end', values=(w.email, w.firstname, w.lastname, job_type))

    def refresh_request_table(self):
        self.request_tree.delete(*self.request_tree.get_children())
        for r in self.sql.query_all(Request):
            status_str = self.sql.query_where(RequestStatus, f"id={r.status_id}")[0].name
            self.request_tree.insert('', 'end', values=(r.id, r.user_email, f"{r.room.building.campus.name} - {r.room.building.name} - {r.room.name}", r.description, r.worker_email, status_str, r.reqtime, r.comptime))

    def assign_worker(self):
        selected_request = self.request_tree.selection()
        selected_worker = self.worker_tree.selection()

        if not selected_request or not selected_worker:
            messagebox.showerror("Error", "Please select both a request and a worker.")
            return

        req_id = self.request_tree.item(selected_request[0])['values'][0]
        worker_email = self.worker_tree.item(selected_worker[0])['values'][0]

        req = self.sql.query_where(Request, f"id={req_id}")[0]
        if req:
            req.worker_email = worker_email
            self.sql.update_entry(req)
            self.refresh_request_table()
        else:
            messagebox.showerror("Error", "Request not found.")

    def set_completion_time(self):
        selected = self.request_tree.selection()
        for item in selected:
            req_id = self.request_tree.item(item)['values'][0]
            req = self.sql.query_where(Request, f"id={req_id}")[0]
            if req:
                req.comptime = datetime.datetime.now()
                req.status_id = self.sql.query_where(RequestStatus, f"name=Complete")[0].id

        self.refresh_request_table()
        self.refresh_user_requests_table()

    def refresh_campus_dropdown(self):
        self.campus_dropdown['values'] = [c.name for c in self.sql.query_all(Campus)]

    def refresh_building_dropdown(self):
        self.building_dropdown['values'] = [
            f"{b.campus.name} - {b.name}" for b in self.session.query_all(Building)
        ]


    def add_campus(self):
        name = self.campus_name_var.get().strip()
        address = self.campus_address_var.get().strip()
        if name:
            if not self.sql.query_where(Campus, f"name={name}")[0]:
                self.sql.create_entry(Campus(name=name, address=address))
                self.refresh_campus_dropdown()
                self.campus_name_var.set("")
                self.campus_address_var.set("")
            else:
                messagebox.showwarning("Error", "Campus already exists.")

    def add_building(self):
        name = self.building_name_var.get().strip()
        campus_name = self.building_campus_var.get().strip()
        address = self.building_address_var.get().strip()
        campus = self.sql.query_where(Campus, f"name={campus_name}")[0]
        if name and campus:
            if not self.sql.query_where(Building, f"name={name}")[0]:
                self.sql.create_entry(Building(name=name, address=address, campus_id=campus.id))
                self.refresh_building_dropdown()
                self.building_name_var.set("")
                self.building_address_var.set("")
                self.building_campus_var.set("")
            else:
                messagebox.showwarning("Error", "Building already exists.")

    def add_room(self):
        name = self.room_name_var.get().strip()
        rtype = self.room_type_var.get().strip()
        building_text = self.room_building_var.get().strip()
        if " - " not in building_text:
            messagebox.showerror("Error", "Invalid building selection.")
            return
        campus_name, building_name = building_text.split(" - ", 1)
        building = None
        for b in self.sql.query_all(Building):
            if b.name == building_name and b.campus.name == campus_name:
                building = b
                break
        if name and rtype and building:
            room_type_id = self.sql.query_where(RoomType, f"name={rtype}")[0].id
            if not self.sql.query_where(Room, f"name={name} AND building_id={building.id}")[0]:
                self.sql.create_entry(Room(name=name, type_id=room_type_id, building_id=building.id))
                self.refresh_room_dropdown()
                self.room_name_var.set("")
                self.room_type_var.set("")
                self.room_building_var.set("")
            else:
                messagebox.showwarning("Error", "Room already exists.")
                
class Delete(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clean/Repopulate Data")
        self.geometry("300x150")
        self.session = Session()

        generate_button = tk.Button(self, text="Generate", command=self.generate, bg="lightgreen")
        generate_button.pack(pady=10)

        delete_button = tk.Button(self, text="Delete All", command=self.delete_all, bg="red")
        delete_button.pack(pady=10)

    def generate(self):
        if messagebox.askyesno("Confirm Generation", "Are you sure you want to generate data?"):
            generate_data(self.session)

    def delete_all(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete everything?"):
            truncate_and_reset_all_data(self.session)

def main():
    delete = Delete()
    delete.mainloop()
    delete.session.close()
    
    maintenance = Maintenance()
    maintenance.mainloop()
    maintenance.session.close() 
    
if __name__ == "__main__":
    main()
