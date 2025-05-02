from generate import *
from delete import truncate_and_reset_all_data
from config import CONNECTION_URL, ROOM_TYPES

from dbtypes import Campus, Building, Room, Worker, Request, Base

import sqlalchemy, datetime
from sqlalchemy.orm import sessionmaker

import tkinter as tk
from tkinter import ttk, messagebox

engine = sqlalchemy.create_engine(CONNECTION_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class Maintenance(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Maintenance Management System")
        self.geometry("1000x700")
        self.session = Session()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=1, fill='both')
        
        self.worker_view_tab()
        self.add_location_tab()
        self.user_view_tab()
            
    def user_view_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="User View")

        # Login
        ttk.Label(frame, text="User Email:").pack(pady=(10, 0))
        self.user_email_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.user_email_var).pack()

        ttk.Button(frame, text="Log In", command=self.login_user).pack(pady=5)
        ttk.Button(frame, text="Create Account", command=self.create_user).pack()

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
        self.request_tree = ttk.Treeview(frame, columns=('ID', 'User', 'Room', 'Worker', 'Status', 'Req Time', 'Complete Time'), show='headings')
        for col in self.request_tree["columns"]:
            self.request_tree.heading(col, text=col)
        self.request_tree.pack(fill='x')
        self.refresh_request_table()

        # Worker Assignments
        ttk.Label(frame, text="Assign Worker to Request").pack()
        assign_frame = ttk.Frame(frame)
        assign_frame.pack(pady=5)

        self.worker_email_var = tk.StringVar()
        self.worker_dropdown = ttk.Combobox(assign_frame, textvariable=self.worker_email_var)
        self.worker_dropdown.pack(side='left', padx=2)
        self.refresh_worker_dropdown()

        ttk.Button(assign_frame, text="Assign", command=self.assign_worker).pack(side='left', padx=2)

        # Completion Time
        ttk.Button(frame, text="Set Completion Time for Selected Requests", command=self.set_completion_time).pack(pady=10)

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
        if email:
            if not self.session.query(User).filter_by(email=email).first() and not self.session.query(Worker).filter_by(email=email).first():
                new_user = User(email=email)
                self.session.add(new_user)
                self.session.commit()
                messagebox.showinfo("Account Created", f"Account for {email} created.")
            else:
                messagebox.showwarning("Exists", "User already exists.")
        else:
            messagebox.showerror("Error", "Email cannot be empty.")


    def login_user(self):
        email = self.user_email_var.get().strip()
        if email:
            self.current_user_email = email 
            print(f"Logged in as: {self.current_user_email}")
            self.user_action_frame.pack()
            messagebox.showinfo("Login", f"Logged in as {email}")
        else:
            messagebox.showerror("Error", "Email cannot be empty.")


    def refresh_room_dropdown(self):
        self.room_dropdown['values'] = [
            f"{r.building.campus.name} - {r.building.name} - {r.name}"
            for r in self.session.query(Room).join(Building).join(Campus).all()
        ]


    def submit_request(self):
        email = getattr(self, "current_user_email", None)
        if not email:
            messagebox.showerror("Error", "No user logged in.")
            return

        user = self.session.query(User).filter_by(email=email).first()
        if not user:
            messagebox.showerror("Error", f"User with email '{email}' does not exist.")
            return

        room_text = self.request_room_var.get().strip()
        description = self.request_description_var.get().strip()

        if not room_text or " - " not in room_text:
            messagebox.showerror("Error", "Please complete all fields.")
            return

        campus_name, building_name, room_name = map(str.strip, room_text.split(" - ", 2))
        room = self.session.query(Room).join(Building).join(Campus).filter(
            Room.name == room_name,
            Building.name == building_name,
            Campus.name == campus_name
        ).first()

        if room:
            new_req = Request(
                user_email=email,
                room_id=room.id,
                description=description,
                worker_email=None,
                status="Incomplete",
                reqtime=datetime.datetime.now(),
                comptime=None
            )
            self.session.add(new_req)
            self.session.commit()
            self.refresh_request_table()
        else:
            messagebox.showerror("Error", "Room not found.")

    def refresh_worker_table(self):
        self.worker_tree.delete(*self.worker_tree.get_children())
        for w in self.session.query(Worker).all():
            self.worker_tree.insert('', 'end', values=(w.email, w.firstname, w.lastname, w.specialization))

    def refresh_request_table(self):
        self.request_tree.delete(*self.request_tree.get_children())
        for r in self.session.query(Request).all():
            self.request_tree.insert('', 'end', values=(r.id, r.user_email, r.room_id, r.worker_email, r.status, r.reqtime, r.comptime))

    def refresh_worker_dropdown(self):
        self.worker_dropdown['values'] = [w.email for w in self.session.query(Worker).all()]

    def assign_worker(self):
        try:
            req_id = int(self.req_id_var.get())
            worker_email = self.worker_email_var.get()
            req = self.session.query(Request).filter_by(id=req_id).first()
            if req:
                req.worker_email = worker_email
                self.session.commit()
                self.refresh_request_table()
            else:
                messagebox.showerror("Error", "Request not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def set_completion_time(self):
        selected = self.request_tree.selection()
        for item in selected:
            req_id = self.request_tree.item(item)['values'][0]
            req = self.session.query(Request).filter_by(id=req_id).first()
            if req:
                req.comptime = datetime.datetime.now()
                req.status = "Complete"
        self.session.commit()
        self.refresh_request_table()

    def refresh_campus_dropdown(self):
        self.campus_dropdown['values'] = [c.name for c in self.session.query(Campus).all()]

    def refresh_building_dropdown(self):
        self.building_dropdown['values'] = [
            f"{b.campus.name} - {b.name}" for b in self.session.query(Building).join(Campus).all()
        ]


    def add_campus(self):
        name = self.campus_name_var.get().strip()
        address = self.campus_address_var.get().strip()
        if name:
            if not self.session.query(Campus).filter_by(name=name).first():
                self.session.add(Campus(name=name, address=address))
                self.session.commit()
                self.refresh_campus_dropdown()
                self.campus_name_var.set("")
                self.campus_address_var.set("")
            else:
                messagebox.showwarning("Warning", "Campus already exists.")

    def add_building(self):
        name = self.building_name_var.get().strip()
        campus_name = self.building_campus_var.get().strip()
        address = self.building_address_var.get().strip()
        campus = self.session.query(Campus).filter_by(name=campus_name).first()
        if name and campus:
            if not self.session.query(Building).filter_by(name=name).first():
                self.session.add(Building(name=name, address=address, campus_id=campus.id))
                self.session.commit()
                self.refresh_building_dropdown()
                self.building_name_var.set("")
                self.building_address_var.set("")
                self.building_campus_var.set("")
            else:
                messagebox.showwarning("Warning", "Building already exists.")

    def add_room(self):
        name = self.room_name_var.get().strip()
        rtype = self.room_type_var.get().strip()
        building_text = self.room_building_var.get().strip()
        if " - " not in building_text:
            messagebox.showerror("Error", "Invalid building selection.")
            return
        campus_name, building_name = building_text.split(" - ", 1)
        building = self.session.query(Building).join(Campus).filter(
            Building.name == building_name,
            Campus.name == campus_name
        ).first()
        if name and rtype and building:
            if not self.session.query(Room).filter_by(name=name, building_id=building.id).first():
                self.session.add(Room(name=name, type=rtype, building_id=building.id))
                self.session.commit()
                self.refresh_room_dropdown()
                self.room_name_var.set("")
                self.room_type_var.set("")
                self.room_building_var.set("")
            else:
                messagebox.showwarning("Warning", "Room already exists.")
                
class Delete(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Repopulate Data")
        self.geometry("300x150")
        self.session = Session()

        generate_button = tk.Button(self, text="Generate", command=self.generate, bg="lightgreen")
        generate_button.pack(pady=10)

        delete_button = tk.Button(self, text="Delete All", command=self.delete_all, bg="red")
        delete_button.pack(pady=10)

    def generate(self):
        if messagebox.askyesno("Confirm Generation", "Are you sure you want to generate data?"):
            generate_buildings_and_rooms(self.session)

    def delete_all(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete everything?"):
            truncate_and_reset_all_data(self.session)
            
if __name__ == "__main__":
    maintenance = Maintenance()
    maintenance.mainloop()
    maintenance.session.close()

    delete = Delete()
    delete.mainloop()
    delete.session.close()