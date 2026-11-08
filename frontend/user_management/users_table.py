"""
User Table Component
Displays list of users in a scrollable table with search functionality
"""

import tkinter as tk
from tkinter import ttk
from ..utils.styles import Colors, Fonts


class UsersTable:
    """Table widget to display users."""
    
    def __init__(self, parent, tab_instance):
        """
        Initialize users table.
        
        Args:
            parent: Parent frame
            tab_instance: Reference to UserManagementTab instance
        """
        self.parent = parent
        self.tab = tab_instance
        self.tree = None
        self.scrollbar_y = None
        self.scrollbar_x = None
        self.search_var = None
        self.search_entry = None
    
    def create(self):
        """Create the users table UI."""
        search_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        search_frame.pack(fill=tk.X, padx=8, pady=(5, 5))
        
        search_label = tk.Label(
            search_frame,
            text="🔍 Search:",
            font=("Arial", 11, "bold"),
            fg=Colors.WHITE,
            bg=Colors.PRIMARY_BG
        )
        search_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_users())
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            width=25,
            bg=Colors.WHITE,
            fg=Colors.BLACK
        )
        self.search_entry.pack(side=tk.LEFT, padx=3)
        
        clear_btn = tk.Button(
            search_frame,
            text="❌",
            font=("Arial", 10),
            bg=Colors.DANGER,
            fg=Colors.WHITE,
            cursor="hand2",
            width=3,
            command=self.clear_search
        )
        clear_btn.pack(side=tk.LEFT, padx=3)
        
        table_frame = tk.Frame(self.parent, bg=Colors.PRIMARY_BG)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 5))
        
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(
            "Users.Treeview",
            background=Colors.SECONDARY_BG,
            foreground=Colors.WHITE,
            fieldbackground=Colors.SECONDARY_BG,
            borderwidth=0,
            font=("Arial", 10),
            rowheight=22
        )
        style.configure(
            "Users.Treeview.Heading",
            background=Colors.BUTTON_BG,
            foreground=Colors.WHITE,
            borderwidth=1,
            font=("Arial", 11, "bold"),
            relief="raised"
        )
        style.map(
            "Users.Treeview",
            background=[("selected", Colors.PRIMARY_BLUE)],
            foreground=[("selected", Colors.WHITE)]
        )
        
        columns = ("employee_id", "email", "role", "status", "created")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Users.Treeview",
            selectmode="browse"
        )
        
        self.tree.heading("employee_id", text="👤 Employee ID", anchor=tk.W)
        self.tree.heading("email", text="📧 Email Address", anchor=tk.W)
        self.tree.heading("role", text="🔑 Role", anchor=tk.W)
        self.tree.heading("status", text="🔘 Status", anchor=tk.CENTER)
        self.tree.heading("created", text="📅 Created", anchor=tk.W)
        
        self.tree.column("employee_id", width=120, minwidth=80)
        self.tree.column("email", width=200, minwidth=150)
        self.tree.column("role", width=120, minwidth=80)
        self.tree.column("status", width=80, minwidth=60, anchor=tk.CENTER)
        self.tree.column("created", width=100, minwidth=80)
        
        self.scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self.tree.bind("<Double-1>", lambda e: self.tab.read_user())
    
    def load_users(self, users=None):
        """
        Load users into the table.
        
        Args:
            users: List of user dictionaries (if None, fetch from database)
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if users is None:
            from .user_database import UserDatabase
            db = UserDatabase()
            if db.connect():
                users = db.get_all_users()
                db.disconnect()
            else:
                users = []
        
        for user in users:
            created = user.get('created_at', '')
            if created and len(created) > 10:
                created = created[:10]
            
            self.tree.insert(
                "",
                tk.END,
                values=(
                    user.get('employee_id', ''),
                    user.get('email', ''),
                    user.get('role', ''),
                    user.get('status', ''),
                    created
                ),
                tags=(user.get('id'),)
            )
    
    def search_users(self):
        """Search users based on search term."""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            self.load_users()
            return
        
        from .user_database import UserDatabase
        db = UserDatabase()
        if db.connect():
            users = db.search_users(search_term)
            db.disconnect()
            self.load_users(users)
    
    def clear_search(self):
        """Clear search field and reload all users."""
        self.search_var.set("")
        self.load_users()
    
    def get_selected_user(self):
        """
        Get the currently selected user.
        
        Returns:
            dict: User data or None
        """
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        values = item['values']
        tags = item['tags']
        
        if not tags:
            return None
        
        user_id = tags[0]
        
        from .user_database import UserDatabase
        db = UserDatabase()
        if db.connect():
            user = db.get_user_by_id(user_id)
            db.disconnect()
            return user
        
        return None
    
    def on_select(self, event):
        """Handle user selection event."""
        selected_user = self.get_selected_user()
        if selected_user:
            self.tab.populate_user_details(selected_user)
