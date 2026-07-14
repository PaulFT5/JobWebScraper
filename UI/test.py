import customtkinter as ctk
import random

# Initialize the main application window
ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"


class JobMatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window size and title
        self.title("AI Job Matcher")
        self.geometry("900x600")

        # Configure the grid (1 row, 2 columns)
        # Column 0 is the sidebar (weight 0 = fixed width)
        # Column 1 is the main area (weight 1 = expands to fill space)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        self.populate_mock_jobs()

    def setup_sidebar(self):
        """Creates the left panel with user inputs."""
        # Create Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)  # Pushes bottom content down

        # Title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Candidate Profile",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 1. Upload CV Button
        self.upload_btn = ctk.CTkButton(self.sidebar_frame, text="📄 Upload CV", command=self.upload_cv_mock)
        self.upload_btn.grid(row=1, column=0, padx=20, pady=10)

        # 2. Domain Selection
        self.domain_label = ctk.CTkLabel(self.sidebar_frame, text="Select Domain:")
        self.domain_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")

        self.domain_menu = ctk.CTkOptionMenu(self.sidebar_frame,
                                             values=["Software Engineering", "Data Science", "Marketing", "Finance",
                                                     "Design"])
        self.domain_menu.grid(row=3, column=0, padx=20, pady=(0, 10))

        # 3. Location Input
        self.location_label = ctk.CTkLabel(self.sidebar_frame, text="Location:")
        self.location_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")

        self.location_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="e.g. Remote, New York...")
        self.location_entry.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="nw")

    def setup_main_area(self):
        """Creates the right panel with the score and job list."""
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # --- TOP RIGHT: Compatibility Score Area ---
        self.score_frame = ctk.CTkFrame(self.main_frame, height=80, fg_color="#2b2b2b")
        self.score_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.score_frame.grid_propagate(False)  # Keep fixed height

        self.score_title = ctk.CTkLabel(self.score_frame, text="Compatibility Score:", font=ctk.CTkFont(size=16))
        self.score_title.place(relx=0.05, rely=0.5, anchor="w")

        self.score_display = ctk.CTkLabel(self.score_frame, text="Select a job...",
                                          font=ctk.CTkFont(size=24, weight="bold"), text_color="gray")
        self.score_display.place(relx=0.95, rely=0.5, anchor="e")

        # --- BOTTOM RIGHT: Scrollable Job List ---
        self.job_list_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Available Positions")
        self.job_list_frame.grid(row=1, column=0, sticky="nsew")
        self.job_list_frame.grid_columnconfigure(0, weight=1)

    def create_job_card(self, company_name, role, location, row_index):
        """Creates a clickable card for a job."""
        # Create a frame to act as the "Box/Card"
        card = ctk.CTkFrame(self.job_list_frame, fg_color="#333333", corner_radius=10)
        card.grid(row=row_index, column=0, sticky="ew", padx=10, pady=10)
        card.grid_columnconfigure(1, weight=1)

        # Mock Logo (using a colored square label instead of an actual image file for simplicity here)
        logo = ctk.CTkLabel(card, text=company_name[0], width=50, height=50, fg_color="#1f538d", corner_radius=10,
                            font=ctk.CTkFont(size=20, weight="bold"))
        logo.grid(row=0, column=0, rowspan=2, padx=15, pady=15)

        # Job Details
        role_label = ctk.CTkLabel(card, text=role, font=ctk.CTkFont(size=16, weight="bold"))
        role_label.grid(row=0, column=1, sticky="sw", padx=10, pady=(15, 0))

        company_label = ctk.CTkLabel(card, text=f"{company_name} • {location}", text_color="gray")
        company_label.grid(row=1, column=1, sticky="nw", padx=10, pady=(0, 15))

        # BIND THE CLICK EVENT
        # We bind the click (<Button-1>) to the card and all its children so clicking anywhere on the box works.
        def on_click(event, c_name=company_name, r_name=role):
            self.calculate_score(c_name, r_name)

        card.bind("<Button-1>", on_click)
        logo.bind("<Button-1>", on_click)
        role_label.bind("<Button-1>", on_click)
        company_label.bind("<Button-1>", on_click)

    def calculate_score(self, company, role):
        """Simulates calculating a score when a card is clicked."""
        # Generate a random score for the demo
        score = random.randint(45, 99)

        # Change color based on score
        color = "#2ECC71" if score >= 80 else "#F1C40F" if score >= 60 else "#E74C3C"

        self.score_display.configure(
            text=f"{score}% Match",
            text_color=color
        )
        self.score_title.configure(text=f"Score for {company}:")

    def upload_cv_mock(self):
        """Mock function for file upload."""
        # In a real app, you would use filedialog.askopenfilename() here
        self.upload_btn.configure(text="✅ CV Uploaded", fg_color="green")

    def populate_mock_jobs(self):
        """Fills the scrollable frame with dummy data."""
        jobs = [
            ("TechNova", "Senior Python Developer", "Remote"),
            ("DataFlow Corp", "Data Scientist", "New York, NY"),
            ("CloudSync", "Backend Engineer", "San Francisco, CA"),
            ("FinEdge", "Quantitative Analyst", "Chicago, IL"),
            ("HealthAI", "Machine Learning Engineer", "Remote"),
            ("DesignHub", "UI/UX Designer", "Austin, TX"),
            ("CyberShield", "Security Analyst", "Washington, DC"),
        ]

        for i, (company, role, location) in enumerate(jobs):
            self.create_job_card(company, role, location, i)


if __name__ == "__main__":
    app = JobMatcherApp()
    app.mainloop()