Technical Roadmap for Optimized Cutting Table Software
======================================================

This roadmap breaks down the development of the Optimized Cutting Table Software into modules and features. Each section details the required components (views, URLs, templates, models, algorithms) and a step-by-step implementation plan. The focus is on building a Django web application that allows users to optimize cutting patterns using Linear Programming (LP), Genetic Algorithms (GA), or a hybrid approach, with real-time visualization and user account management.

1\. Views (`views.py`)
----------------------

Each Django app (module) in the project needs specific view classes or functions to handle page rendering and business logic. Below we identify the key views for each module and their purposes:

-   **Core Module Views**: Handles general pages and project listings.

    -   `HomeView` (TemplateView): Renders the landing page (`home.html`) with an introduction and navigation links. This is the public homepage for the site.
    -   `AboutView`, `ContactView`, `TeamView` (TemplateView): Static informational pages showing project information, contact form or details, and team members. These will use templates like `about.html`, `contact.html`, `team.html`.
    -   `ProjectListView` (ListView or TemplateView): Displays a list of the user's projects (optimization runs) in a dashboard-style view. Users can see all their past optimization projects, each with status, material used, etc. From here they can navigate to view details, visualize results, or export data. This view may also include a section for "curated projects" -- e.g. sample or featured projects provided by the team for demo purposes.
-   **Optimizer Module Views**: Manages optimization input and processing.

    -   `NewProjectView` (FormView or TemplateView): Presents a form for users to input a new cutting project. The form would allow entering material dimensions (stock length/width), piece dimensions and quantities to cut, selecting material type (e.g. wood, metal), and choosing cutting preferences such as tool type (laser or blade) and optimization method (LP, GA, or Hybrid). On submission, this view will either process the optimization immediately or initiate a background task. It uses a template like `new_project.html` with fields for all required inputs.
    -   `OptimizeResultView` (DetailView/TemplateView): Shows the results of an optimization run for a specific project. When an optimization is complete, this view will display the optimized cutting pattern (via a canvas or SVG), summary metrics (e.g. material used vs wasted), and provide options to download/export the results. It will use a template such as `project_detail.html` (or `project_dashboard.html`). If the optimization is still running (in case of longer processes handled asynchronously), this view can show a "processing" status or estimated wait time.
    -   (Optional) `ConfigurationView` (ListView/FormView): Allows users to manage saved cutting configurations (favorite tool settings). Users can create new configurations or edit/delete existing ones (for example, define a "Laser cutter 0.1mm kerf" configuration). This may also be integrated into the user profile settings instead of a standalone view.
-   **Dashboard Module Views**: Handles visualization of project metrics and comparison of results. (The **Dashboard** app in this project is intended for data visualization and advanced metrics display.)

    -   `ProjectDashboardView` (TemplateView): Provides a rich dashboard for a single project's outcome. It includes an interactive visualization of the cutting layout (e.g. an SVG showing how pieces are arranged on the material) and graphs of efficiency. The view will prepare data for the template to plot, such as percentage of material utilized vs wasted, number of sheets used, etc. This could be the same as the OptimizeResultView or a separate view that the OptimizeResultView redirects to once results are ready. In implementation, these might be combined for simplicity.
    -   `ComparisonView` (TemplateView, optional): If the software supports comparing different optimization methods or different project results, this view would show side-by-side metrics (for example, comparing GA vs LP outcomes on the same input). It could render comparative graphs (like bar charts of waste for each method). This is an advanced feature and can be planned after basic functionality.
-   **Accounts Module Views**: Manages user authentication, profiles, and notifications. (Many of these are already implemented in the provided code.)

    -   `LoginView` (FormView): Handles user login using Django's AuthenticationForm. On success, logs the user in, records the login event (creating a SessionLog and ActivityLog entry), and redirects to the user dashboard (`accounts/authenticate/v1/dashboard/`). It also triggers a session login notification email to the user (using the mixin to send an email about a new login).
    -   `RegisterView` (FormView): Handles new user registration with a custom RegistrationForm. On successful form submission, it creates a new User and UserProfile, generates an email verification token, and sends a welcome/verification email to the user. It then prompts the user to check their email.
    -   `EmailVerificationView` (View): Activated when the user clicks the email link. It checks the token in the URL, and if valid, marks the UserProfile as verified. It then redirects to login with a success or error message.
    -   `LogoutView` (RedirectView): Logs the user out, updates the SessionLog with logout time, and records an ActivityLog for the logout event.
    -   `ProfileUpdateView` (FormView): Allows the user to update profile info, specifically their email in this implementation. It uses ProfileUpdateForm to change the email and ensures no duplicate emails. On success, it sends a confirmation email about the update (using `profile_update_email.html`) and logs an 'update' activity. We will extend this view or add a similar view to manage other profile details, such as changing password or managing saved configurations. For example, we might include controls here for adding or removing favorite blade configurations (if not handled in a separate Optimizer config view).
    -   `DashboardView` (TemplateView): Currently, this view is meant to show the user's personal dashboard (accessible at `accounts/authenticate/v1/dashboard/`). It gathers the user's SessionLogs, ActivityLogs, Notifications, and EmailLogs and passes them to the `dashboard.html` template for display. This page will show the user's recent login activity, any unread notifications (such as "Your project XYZ optimization is complete"), and possibly quick links to their projects. We may modify this to also include a summary of project metrics (e.g. total projects run, average savings) or at least link to the main project dashboard section of the site.

**Purpose of these Views**: Together, the views above cover all user interactions: navigating informational pages, logging in/out, registering, verifying email, updating profile, creating optimization projects, viewing results, and visualizing data. They ensure separation of concerns by module while providing a seamless user experience (e.g. user goes from core homepage, logs in via accounts, then uses optimizer and views dashboards).

2\. URLs (`urls.py` Routing Configuration)
------------------------------------------

Proper URL routing will tie the above views into navigable paths. We will set up URL patterns for each app and include them in the project's main `urls.py`:

-   **Main Project URLs (`O_C_T_S/urls.py`)**:\
    Include the URL configurations of each app with appropriate prefixes. For example:

    python

    Copy

    `urlpatterns = [
        path('admin/', admin.site.urls),
        path('accounts/', include('accounts.urls')),   # Auth and profile related URLs
        path('optimizer/', include('optimizer.urls')), # Optimization input and result URLs
        path('dashboard/', include('dashboard.urls')), # Visualization dashboard URLs
        path('', include('core.urls')),                # Core pages (home, about, etc.)
    ]`

    This setup means: any URL starting with `accounts/` will be handled by the Accounts app, `optimizer/` by the Optimizer app, `dashboard/` by the Dashboard app, and the root (`/`) by the Core app.

-   **Core URLs (`core/urls.py`)**:\
    Map the core static and general pages. For example:

    python

    Copy

    `urlpatterns = [
        path('', HomeView.as_view(), name='home'),           # Landing page at "/"
        path('about/', AboutView.as_view(), name='about'),
        path('contact/', ContactView.as_view(), name='contact'),
        path('team/', TeamView.as_view(), name='team'),
        path('projects/', ProjectListView.as_view(), name='project_list'),
        path('projects/curated/', CuratedProjectsView.as_view(), name='curated_projects'),
    ]`

    The `projects/` page will show the user's projects (requires login), and `projects/curated/` can show example projects for anyone to view. We'll use Django's login required decorators or `LoginRequiredMixin` for views that need authentication (like ProjectListView). The core URLs cover general navigation and listing pages.

-   **Optimizer URLs (`optimizer/urls.py`)**:\
    Define routes for creating a new project and viewing results. For example:

    python

    Copy

    `urlpatterns = [
        path('new/', NewProjectView.as_view(), name='new_project'),
        path('<int:project_id>/', OptimizeResultView.as_view(), name='project_detail'),
        path('<int:project_id>/export/', ExportResultView.as_view(), name='project_export'),
        # (Optional) paths for config management if in optimizer, e.g.:
        path('configs/', ConfigurationView.as_view(), name='config_list'),
        path('configs/new/', ConfigCreateView.as_view(), name='config_create'),
    ]`

    Here, `/optimizer/new/` presents the form for a new optimization job. After submission, it might redirect to the project detail page (perhaps `/optimizer/123/` for project ID 123) to show status or results. The `<int:project_id>/export/` URL can trigger a file download of the optimized cutting plan (for example, a CSV of coordinates or PDF report). We also include optional URLs for managing saved configurations if implemented under the optimizer app.

-   **Dashboard URLs (`dashboard/urls.py`)**:\
    Provide endpoints for visualization and comparisons. For example:

    python

    Copy

    `urlpatterns = [
        path('project/<int:project_id>/', ProjectDashboardView.as_view(), name='project_dashboard'),
        path('compare/<int:proj1_id>-vs-<int:proj2_id>/', ComparisonView.as_view(), name='compare_dashboard'),
    ]`

    The `project_dashboard` URL can be similar to the optimizer's project detail, but possibly under a different namespace for clarity. It will show the detailed dashboard (canvas + graphs) for the given project. The compare URL (if used) would take two project IDs and display comparative metrics. If we decide not to implement a separate compare view initially, we can omit it.

-   **Accounts URLs (`accounts/urls.py`)**:\
    (Already largely defined in the provided code.) These handle authentication flows. From the snippet, the accounts URLs are:

    python

    Copy

    `urlpatterns = [
        path('authenticate/v1/login/', LoginView.as_view(), name='login'),
        path('authenticate/v1/register/', RegisterView.as_view(), name='register'),
        path('authenticate/v1/logout/', LogoutView.as_view(), name='logout'),
        path('authenticate/v1/verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify_email'),
        path('authenticate/v1/dashboard/', DashboardView.as_view(), name='dashboard'),
        path('authenticate/v1/profile-update/', ProfileUpdateView.as_view(), name='profile_update'),
    ]`

    These URLs are all prefixed by `accounts/` in the main include, so the actual paths are `/accounts/authenticate/v1/login/` etc. We might simplify these paths for usability (for example, using `/accounts/login/` instead of the `authenticate/v1` prefix), but we will keep them as is if consistent with an API versioning scheme. The `dashboard` here is the user's account dashboard (recent activity, notifications). We may add new URLs in this app if needed, such as for managing user's saved blade configurations (e.g., `accounts/settings/configurations/` for adding/removing favorite blades). Alternatively, those could be handled in the Optimizer app as noted.

In summary, the routing will ensure that:

-   Visiting the site root shows the homepage,
-   `/about/`, `/contact/`, `/team/` show informational pages,
-   `/accounts/register` and `/accounts/login` handle user auth,
-   `/accounts/dashboard` shows user-specific info,
-   `/projects/` (or similar) lists projects,
-   `/optimizer/new` and `/optimizer/<id>` handle the core feature of optimization input and output, and
-   `/dashboard/project/<id>` displays the interactive results.

All URLs will be named for reverse lookup (as seen above) to easily link between views in templates. Proper use of `login_required` and permissions will be enforced on views that need the user to be logged in (like creating a project or viewing one's projects).

3\. Templates
-------------

We need a set of HTML templates to render the pages defined by our views. The templates will extend a base layout and use consistent navigation. We will create any missing templates identified in the code and additional ones for new views:

-   **Base Layout**: `base.html` -- A global template that defines the overall HTML structure (header, footer, navigation bar, messages). It likely already exists in `templates/base.html`. We will ensure it includes links to core pages (Home, About, Contact), and if user is authenticated, links to their dashboard, projects list, and a logout button. If not authenticated, links to Login/Register. This base template will use Django template tags to include content (using `{% block content %}` for page-specific content) and to display flash messages (like success/error messages from the views). Styling (CSS) and scripts (JS for interactive charts, etc.) will be linked here as needed.

-   **Core Page Templates**:

    -   `home.html`: Exists (per provided files) and shows the landing page content. It might contain a welcome message and perhaps a brief description of the software's benefits (possibly drawn from the project's abstract). We will refine it to include calls-to-action (e.g., "Get Started" button leading to login or new project if logged in).
    -   `about.html`, `contact.html`, `team.html`: We will create these templates to provide static information. For example, **About** can describe the project motivation and features, **Team** can list team members and roles, and **Contact** can either show contact info or include a form (if we want a feedback form, we'd create a simple form view to email the team). These pages extend `base.html`.
    -   `projects_list.html`: A template to list user projects and curated projects. It will iterate over a context variable like `my_projects` to display each project (name, date, status, material used, etc.), with links or buttons to view details (`View Results`) and to export results. If a project's result is not ready yet, it might show a "Processing..." label. For curated projects (if any), we can list them in a separate section -- these could be simply hardcoded examples or loaded from the database (projects with a `is_curated` flag). Each curated project can have a "View" link that takes the user to a read-only dashboard of that project's results, even if they aren't the owner.
-   **Authentication Templates (Accounts)**:

    -   `login.html`: Template for the login page (provided). It should have a form that posts to the login URL, with fields for username and password. It extends `base.html` (or a minimal variant) and should display form errors (like "invalid credentials") if present.
    -   `register.html`: Template for user registration (provided). It includes fields for username, email, password, confirm password (as per RegistrationForm). After successful registration, we show a message (via messages framework) telling the user to check their email for verification.
    -   `profile_update.html`: **(Missing)** We need to create this template. It will contain a form to update the user's email (and we might extend it to update other profile info or preferences). It should pre-fill the current email and allow submission to change it. If we incorporate password change or other settings, those might be separate, but for now this handles email updates. On success, the view redirects to dashboard with a success message (and an email is sent).
    -   `dashboard.html` (Accounts dashboard): **(Missing)** This template will display the context provided by `DashboardView` in accounts. It should show: recent sessions (e.g. list of login times and IPs from SessionLog), recent activities (from ActivityLog -- login, logout, register, etc.), any notifications (from Notification model, such as verification success or project completion notices), and email logs if needed (though email logs could be for admin debugging; we might show the user which system emails have been sent to them). This page gives the user an overview of their account security and actions. It can be laid out in cards or tables for each category. It also serves as a landing after login -- from here the user can navigate to create a new project or view existing projects.
    -   Email templates: The project already includes some HTML email templates: `register_email.html` (for welcome/verification), `profile_update_email.html` (for email change notification), and `session_login_email.html` (for new login alerts). These templates are used by the `EmailNotificationMixin` in views to construct emails. We should ensure these templates have appropriate content and branding (they likely include placeholders for username, verification link, etc.). No additional email templates are needed unless we add one for project completion (we could, for example, email the user when a long-running optimization finishes -- in that case, a new template like `project_complete_email.html` would be created and used).
-   **Optimizer Templates**:

    -   `new_project.html`: A form page for creating a new optimization project. It will have input fields for all required parameters:

        -   A field (or set of fields) to input the stock material dimensions (length and width of the sheet, or perhaps length if roll, etc.).
        -   Fields to input piece dimensions. This could be a dynamic form where the user can add multiple pieces (each with width, height, and quantity). Implementing this might require some JavaScript or a formset. To simplify, we might start with a fixed number of rows or instruct the user to input pieces separated by commas and parse it, but a more user-friendly approach is preferred (possibly using formsets or a small JS to clone input rows).
        -   Dropdown or options for material type (e.g. choose from predefined types like Wood, Metal, Plastic). This could influence kerf or just for record.
        -   Dropdown or radio for cutting tool type (Laser vs Blade). If blade, possibly allow entering blade thickness (kerf) value; if laser, kerf might be near zero or a default value. We can adjust the form via JS if needed: e.g. if tool=blade, show an extra field for blade thickness; if laser, hide it.
        -   Dropdown for optimization method (LP, GA, Hybrid).
        -   Possibly a checkbox for "Allow piece rotation" (if relevant in cutting -- often we can rotate pieces 90° to fit better; we should allow user to specify if rotation is permitted or not, since some materials have grain direction constraints).
        -   A submit button to start the optimization.\
            This template extends `base.html` and should be designed to be as user-friendly as possible, perhaps with descriptions or placeholders for each field. We will also need to handle form validation errors (e.g. missing fields or non-positive dimensions).
    -   `project_detail.html` (or `optimizer_result.html`): This template displays the outcome for a single project. It will likely overlap with what we describe for the Dashboard module, since that's where graphs and visualization come in. Key elements on this page:

        -   **Cutting layout visualization**: We can include an `<svg>` or `<canvas>` element in the HTML. The view will pass data (positions and sizes of each cut piece) to the template or via an AJAX call to be rendered. One approach is to embed an SVG via template context: e.g., generate SVG rectangles for each piece and the stock, coloring them distinctly. Another approach is to include a script (maybe using a library or custom drawing code) that draws the layout on an HTML5 canvas. Since the PPT mentioned using **SVG & Plotly** for visualization, we might lean on Plotly for charts and possibly use Plotly's SVG capabilities or simply output an SVG ourselves for the layout. Either way, the template will have a designated area for this visual.
        -   **Metrics and stats**: The template will display key metrics such as total material area vs used area (and thereby the waste percentage), number of pieces cut, perhaps time taken for computation, etc. A simple table or list can show these.
        -   **Graphs**: We can embed a Plotly chart (like a pie chart of Used vs Wasted material, or a bar chart comparing waste % across different methods if multiple runs). Plotly can be included via CDN JS and then a small script to plot using data from context. For example, a pie chart with two values (Used, Wasted) to visually illustrate efficiency. If hybrid method combines LP and GA, maybe a line chart showing improvement over iterations could be shown if data is available (not mandatory). Comparative graph (if only one project's data) might just be the used vs waste. If we had multiple solutions to compare, this could be shown here or on a separate compare page.
        -   **Actions**: A button or link to "Export Results" (linking to the export URL). Also perhaps a "Back to Projects" link. If the project isn't verified as complete (in case of async), maybe a refresh or "check status" option (though if we handle synchronously in request, this won't be needed -- more on that in algorithms section).
    -   **Export format**: No dedicated template (the export is likely not an HTML page). But we plan to implement the export view to provide a downloadable file. This could be a CSV listing each piece's coordinates on the stock, or a PDF report. For simplicity, we might generate a CSV or JSON file of the results. If later a PDF is needed, we could use a library like ReportLab or xhtml2pdf to convert an HTML report to PDF. This is an optional enhancement -- initially, focusing on CSV export is fine.

-   **Dashboard Templates**:

    -   `project_dashboard.html`: Similar to `project_detail.html` described above. If we separate the Dashboard app's template, it will contain the visualization and charts as described. Essentially, we might not need two different templates for project results -- one can suffice. The distinction could be just in which view serves it. We should ensure consistency: possibly using one template file for both Optimizer's result view and Dashboard's view if they're not actually different pages. We can decide to keep them unified to avoid duplication.
    -   `compare_dashboard.html`: If implementing comparison of two projects or two methods, this template would show multiple sets of metrics and perhaps overlay charts. For example, two pie charts side by side, or one combined bar chart with bars for each scenario's waste. This is a nice-to-have template after core features are done.

Overall, the templates will use the base layout for consistent look and feel. We will incorporate Bootstrap (the example `index.html` and base template suggests Bootstrap is being used for styling) to make pages responsive and clean. Short, clear messages and labels will guide the user. We will also make sure to create the **missing templates** that the code references (such as `profile_update.html` for the ProfileUpdateView and `dashboard.html` for the account DashboardView) since those are not yet in the files. By structuring templates logically (perhaps grouping them in directories per app, e.g. `templates/core/home.html`, `templates/optimizer/new_project.html`, etc., or all in a common folder with distinct names), we ensure easy maintenance. Each template's structure will reflect the data provided by its view's context.

4\. Models (`models.py`)
------------------------

The database design will include several tables (Django models) across the apps to store user data, project data, and logs. We identify the necessary models and their relationships:

-   **Accounts Models** (already defined in `accounts/models.py`): These handle user profile and activity tracking.

    -   `UserProfile`: Extends the built-in Django `User` with additional fields. It has a OneToOneField to User (with `related_name='profile'`). Fields include `email_verified` (boolean), `verification_token` (for email confirmation), `verification_expires` (DateTime for token expiry), and timestamps. This model is used to manage email verification status and can be extended later for additional user info.
    -   `SessionLog`: Logs each user login session. It has ForeignKey to User (`related_name='session_logs'`) and fields for session key, IP address, login_time (auto now add) and logout_time. Every time a user logs in, a SessionLog is created; when they log out, that record is updated with the logout time. This helps in security auditing (the user can see where and when their account was accessed).
    -   `ActivityLog`: Records user activities with a type and description. ForeignKey to User (`related_name='activity_logs'`). Fields: `activity_type` (choices like 'login', 'logout', 'register', 'update', etc.), `description` (text detail), and timestamp. The views use this to log events (e.g. LoginView logs "User logged in" with type 'login'). We might add a new activity type for project creation or optimization run (e.g. 'optimize') so that when a user runs a new optimization, we log that action for completeness.
    -   `Notification`: Represents notifications to the user. ForeignKey to User (`related_name='notifications'`). Fields: message (text), is_read (bool), created_at. This can be used to notify the user of important events. We will use this model to create a notification when an optimization result is ready -- e.g., message: "Your project **Project ABC** has completed optimization." The user's dashboard can show it and possibly link to the project page.
    -   `EmailLog`: Stores a log of emails sent to the user. ForeignKey to User (`related_name='email_logs'`). It tracks the type of email (choices: 'welcome', 'verification', 'profile_update', 'session_login'), subject, body, recipients, timestamp, and success flag. Whenever the system sends an email (registration confirmation, etc.), an EmailLog entry is created. This is useful for auditing and debugging email delivery. We might add an email type 'project_complete' if we decide to send an email when an optimization job finishes.

    All these accounts models are connected to the User, establishing a one-to-many or one-to-one relationships as appropriate. The existence of these models means the system is already set up to track user actions and communications, which we will leverage for the optimizer module integration (for example, logging an activity when a project is created, or adding a notification on completion).

-   **Optimizer Models**: These will store data related to cutting optimization projects and configurations. We need to design models for the core domain objects:

    -   `Project`: Represents an optimization project/cutting job. Key fields might include:

        -   `user` (ForeignKey to User, with `related_name='projects'`), indicating the owner of the project.
        -   `title` or `name` (CharField): a user-friendly name for the project (or we can auto-generate one like "Project 1" if not provided).
        -   `material_type` (CharField or ChoiceField): type of material (e.g. Wood, Metal, etc.), as selected by user.
        -   `stock_width` and `stock_height` (FloatField or IntegerField): dimensions of the raw material sheet. Possibly also `stock_thickness` or other properties if needed (though thickness might not affect layout, only weight which is out of scope here).
        -   `tool_type` (CharField/ChoiceField): either "Laser" or "Blade" (or others in future).
        -   `kerf_width` (FloatField): the cutting beam/blade width to account for cut thickness (default could be 0 for laser, some mm for blade).
        -   `allow_rotation` (BooleanField): whether pieces can be rotated for fitting (default True, unless material grain disallows it).
        -   `algorithm` (CharField or ChoiceField): which optimization method was used or is requested (e.g. 'LP', 'GA', 'Hybrid').
        -   `status` (CharField or ChoiceField): e.g. 'pending', 'processing', 'completed'. This is useful if using background tasks -- the project could start as 'pending' or 'processing', and then marked 'completed' when results are ready. If we handle optimization synchronously, we might set it directly to 'completed' along with result data.
        -   `created_at` (DateTimeField auto_now_add) and possibly `completed_at` (DateTimeField) to track timings.
        -   **Result fields**: We need to store the outcome of the optimization. Several approaches here:
            -   We could have a separate model for results, but to keep it simple, adding fields to Project may suffice. For example: `utilization` (FloatField for percentage of material used), `waste` (FloatField or Integer for waste area or count of unused pieces), and perhaps a blob of solution data. We could use a JSONField (if using a database like PostgreSQL or Django's JSONField) to store the layout results (coordinates of pieces). Alternatively, a text field where we store some structured data (like CSV string or serialized Python object). A JSON structure might look like: `{"pieces": [{"w":10,"h":5,"x":0,"y":0}, ...], "sheet_used": 1}` etc. Storing this allows us to regenerate the visualization without rerunning the algorithm each time.
            -   If not using a JSONField, another approach is to create a `PiecePlacement` model for each piece position, but that could be a lot of rows if many pieces (less efficient to query). Given typical use (maybe tens of pieces, not thousands), it's feasible but an overkill for MVP. JSONField is convenient here.
        -   `is_curated` (BooleanField, default False): a flag to mark projects that are "curated" examples. Admins can set some projects as curated so they show up publicly. This way, the curated projects page can query `Project.objects.filter(is_curated=True)` to display them.
    -   `Piece` (or `RequiredPiece`): Represents the dimensions (and possibly quantity) of a piece to cut in a project. Fields: `project` (ForeignKey to Project, related_name='pieces'), `width`, `height` (FloatFields or IntegerFields, as per units we decide), and `quantity` (IntegerField, default 1). If quantity > 1, it means there are that many identical pieces required. We could either create multiple Piece entries or one entry with quantity -- using a quantity field is simpler for input, but when computing we might internally expand them. However, storing as one entry with quantity is fine.\
        Each piece does not have a position -- it's just the requirement. The positions of pieces will be determined by the algorithm and stored in the project's result data (as discussed above).\
        The relationship is one-to-many: a Project has many Pieces. This structure makes it easy to list what needs to be cut for a given project and could be reused if we allow editing a project's requirements.

    -   `OptimizerConfig` (or `CuttingConfig` / "favorite blades" model): Allows users to save custom configurations for cutting. This can store user preferences such as blade/laser settings and possibly algorithm settings. Fields might include: `user` (ForeignKey to User, related_name='configs'), `name` (CharField -- a nickname like "Default Wood Laser" or "Metal Saw Config"), `tool_type` (choice), `kerf_width`, and any other relevant parameters (maybe a default material type or default algorithm). We might also include a boolean `is_default` to mark one favorite configuration that auto-loads for new projects.\
        This model connects to the user with a many-to-one (one user, many configs). In the UI, the user can create multiple configurations -- e.g., one for laser cuts (kerf=0, uses Hybrid algorithm), another for saw (kerf=3mm, uses GA by default), etc. When starting a new project, they could choose one of their saved configs to auto-fill the form. We'll need to create forms and views to manage these if we include this feature. (If short on time, we might implement just a single default config stored in UserProfile or skip this; but since the requirements call it out, we plan for it.)

    Relationships recap: A `User` has many `Project` (via Project.user FK). A Project has many Piece requirements. A User can have many OptimizerConfig entries (favorite configs). Also, a Project may link to an OptimizerConfig if we want to record which config was used, but since we store the relevant values in the project itself (tool, kerf, etc.), linking back to config is optional (for instance, if a user applies a saved config, we could note `project.config_used = config`, a FK to OptimizerConfig). Initially, we can skip linking the config and just copy values into the Project.

-   **Dashboard Models**: The Dashboard app might not need its own new models, as it will draw upon Projects for data. We will mainly use the Project model's data to visualize results. If we wanted to track aggregated statistics (like overall material saved across all projects, or historical data for a user), we could add models or just compute on the fly. At this stage, no additional models are strictly required for the dashboard. We'll generate charts from existing data.

One consideration: If we use asynchronous processing (say using Celery for running the optimization algorithms in the background), we might have a model like `TaskStatus` or simply use the Project.status field to check if a project's result is ready. Since the requirement explicitly mentions notifying the user when results are ready, having the `status` field and Notification model in place is sufficient. The workflow would be: user submits new Project (Project created with status 'processing'), backend task runs and updates Project with results and status 'completed', then creates a Notification for the user ("Project X is complete"). The front-end (user dashboard or project list) can periodically refresh or use WebSocket to inform the user in real-time, but at minimum when they next load their dashboard page they'll see the notification. Implementing Celery/async is an advanced step; initially, we might run algorithms synchronously (small input sizes) and simply redirect to results immediately. The architecture, however, is prepared for async if needed (with status and notifications).

In summary, the models ensure we can store everything: user data (with verification and logs), project data (inputs and outputs of optimization), and user preferences. We will use migrations to create these tables and possibly a Django admin interface (the code has `admin.py` files which we can register these models in) to inspect or manage data. Setting up proper foreign keys and related names helps in querying (e.g., `user.projects.all()` to list a user's projects, or `project.pieces.all()` for requirements, etc.).

5\. Algorithmic Functions (Cutting Optimization)
------------------------------------------------

At the heart of the software are the algorithms that compute optimal cutting patterns to minimize waste. We will implement three methods: Linear Programming, Genetic Algorithm, and a Hybrid approach. These will likely reside in the Optimizer module, possibly in a separate Python file (e.g., `optimizer/solver.py` or within `views.py` if simple). Here's an outline of each:

-   **Linear Programming (LP) Approach**:\
    Using linear (or integer linear) programming to model the cutting problem. In essence, this is a form of the 2D bin packing or cutting stock problem. We need to decide how to place rectangular pieces within a larger rectangle (the stock) without overlap, minimizing wasted area. A pure linear programming formulation might involve variables for each potential placement of each piece -- which can become complex. A simpler linear model could allocate pieces to strips or use linear relaxation to get an optimal area usage. We might formulate it as an integer program:

    -   Decision variables could be defined for each piece and each possible placement (like on a grid). Alternatively, variables could represent whether a piece is cut or not (but since all pieces must be cut, those are constants) and perhaps how many stocks used.
    -   A known approach for cutting stock: use ILP to decide how to cut strips of certain widths from the stock, then assign pieces to those strips (if we restrict cuts to guillotine style). However, given this is a 2D layout, an ILP might involve binary grid (which can be huge).\
        Given the complexity, we might simplify by using LP for the one-dimensional version (if, say, all pieces height equal to stock height, then it reduces to a 1D cutting problem of widths). But generally, since the project emphasizes LP, we assume using an ILP solver to directly maximize total area of pieces on the sheet subject to non-overlap constraints. We can use a library like **PuLP** or **OR-Tools** for this. For example:
        -   Create binary variables `x_{i,j}` = 1 if piece *i* is placed in position *j* (where *j* indexes possible grid positions that align pieces without overlap). Constraints ensure each piece i is placed exactly once and positions don't overlap usage. The objective maximizes the sum of areas of placed pieces (or minimizes waste = stock area minus used area).
        -   If an ILP is too slow, we might use a heuristic even in the LP method (like first-fit or greedy placement) but since it's called LP, we'll attempt a mathematical approach.

    Implementation-wise, we will write a function `optimize_with_lp(project)` that takes the project (with its pieces and stock dimensions) and returns a solution (positions for each piece). This function might:

    -   Use PuLP: define an LP problem, add constraints (stock width/height as bounds, each piece placed within bounds, no overlapping constraints -- which are tricky, might linearize using big-M formulations), then solve using an LP solver.
    -   Once solved, parse the solution values to get piece coordinates.
    -   Calculate usage stats (sum of piece areas, etc.) and format the result (perhaps as the JSON of placements). If an external solver is not readily available, we might implement a simpler heuristic and still call it "LP method" for the scope of the project (for instance, sorting pieces by size and placing them row by row, which is not truly LP but ensures a fairly optimized use of space). However, since this is a capstone, we should attempt a legitimate optimization approach, so using a solver is ideal. We'll need to ensure the chosen solver is installed (perhaps include PuLP in the project's environment as indicated by the dev environment provided).
-   **Genetic Algorithm (GA) Approach**:\
    A GA will treat a layout as an individual in a population and evolve layouts to reduce waste. We need to design a genetic encoding for a layout. One possible encoding: an ordering of pieces and a rule for how to place them sequentially (e.g., the genome is a sequence of piece IDs which implies the order in which pieces are placed onto the sheet using a packing heuristic). Alternatively, the genome could directly encode coordinates, but that might be less natural for crossover. A simpler approach is:

    -   **Representation**: Represent a solution by an ordering of pieces (and maybe a rotation flag for each). The decoding (the "phenotype") is achieved by a deterministic algorithm that takes that ordering and places pieces one by one on the sheet (like a greedy algorithm: place each piece in the first available spot from top-left scanning rightwards and then down). This way, the GA's job is to find the best ordering (and rotations) that lead to the least waste layout.
    -   **Initial Population**: Generate a number of random orders of the pieces (shuffle the list of pieces for each individual). If rotation is considered, randomly decide rotation on individuals as well (could be part of genome encoding as a bit per piece indicating rotated or not). Ensure all individuals are valid (all pieces accounted for exactly once).
    -   **Fitness Function**: Define fitness based on waste or utilization. For instance, fitness = (Total area of pieces placed) / (Stock area) -- we want to maximize this. Or minimize waste area. We must compute the layout (using the greedy packing decoder) for each genome to know how much area is used or if some pieces didn't fit at all (if an order leads to pieces not fitting, that solution might be considered invalid or have a lower fitness). We should heavily penalize solutions that don't place all pieces (since requirement is to place all required pieces).
    -   **Genetic Operators**: Apply crossover and mutation to evolve the population:
        -   *Crossover*: Take two parent orderings and produce children by, for example, order crossover (OX) or partially matched crossover (PMX) since we are dealing with permutations. These ensure that the offspring are also valid permutations of pieces. For rotation bits, we could simply combine or inherit from parents randomly.
        -   *Mutation*: Randomly swap two pieces in the order (or a small segment reversal), and randomly flip the rotation bit of a piece. This introduces new layouts.
    -   **Evolution loop**: Iterate for a number of generations (which could be a parameter based on problem size). In each generation, calculate fitness for each individual, select the fittest (using tournament or roulette selection), produce new offspring, and repeat. Track the best solution found.
    -   The result will be the best ordering (and rotations) found, which we then decode into the final layout coordinates.\
        We will implement this likely in a function `optimize_with_ga(project)` which returns similar output structure (placements, utilization, etc.). We have to be mindful of performance -- GA can be slow if population or generations are large. For a moderate number of pieces (say 20-50), a GA with population of 50 and 100 generations might be okay. We should allow the algorithm to be configurable (maybe in code or via parameters in OptimizerConfig) for population size, etc., but defaults will do for now.\
        This GA approach provides a flexible, if not guaranteed optimal, solution. It's useful for more complex scenarios where an ILP might be too slow or complicated.
-   **Hybrid Approach**:\
    The hybrid method will combine LP and GA to leverage strengths of both. There are a couple of ways to do this:

    -   **Sequential Hybrid**: Use one method's result to seed the other. For example, use a quick LP-based arrangement to get an initial layout, then feed that into the GA as one of the initial population individuals (a good starting point). The GA can then refine the solution further. Or vice versa: run a GA for a while to get a decent solution, then use its result as a starting point in an ILP solver (maybe to linearize the final tweaks). Given the complexity, the former (LP then GA) might be more straightforward: LP gives an initial optimized distribution (maybe optimal in terms of count of pieces per row or something), and GA fine-tunes any arrangement details.
    -   **Combined Algorithm**: Alternatively, use LP for one dimension and GA for the other. For instance, LP could determine the optimal number of rows or cuts in one direction, and GA could arrange pieces within those constraints. This is more speculative, but could be an approach where LP handles cut lengths and GA handles ordering in those cuts.
    -   **Heuristic Hybrid**: Another hybrid strategy is to run both algorithms and choose the better result for each case, or present both solutions to the user. But likely they intend a single method that mixes techniques automatically.

    We will implement a function `optimize_with_hybrid(project)` that possibly does:

    1.  Solve a simplified linear program to get a baseline (e.g., maximize number of pieces that can fit by area or an initial packing ignoring some constraints).
    2.  Use that result to influence a GA -- for example, the LP might tell us an approximate distribution of pieces or the fraction of sheet used, and we create an initial individual for GA from a greedy fill (which could be similar to what LP implies).
    3.  Run a shorter GA evolution since we already have a good start, to adjust piece placements.
    4.  Return the improved solution. This hybrid will likely yield a result at least as good as the better of the two methods alone, and ideally faster than a full GA from scratch if LP pruned the search space. We will have to carefully design the interaction so they're compatible (perhaps focusing on using LP outcome as starting layout).\
        If time or complexity is an issue, an alternative interpretation of "Hybrid" is simply offering a third choice that under the hood either picks one of the methods based on problem size or does a simple combination. For example, for smaller piece counts, use LP (exact); for larger, use GA (heuristic), and call that strategy "Hybrid". But given this is a learning project, we attempt an actual combination as above.
-   **Integration of Algorithmic Functions**:\
    These functions (LP, GA, Hybrid) will not be direct views but will be invoked by the views (specifically when a new project is submitted). We might create a Python module like `optimizer/algorithms.py` containing these functions or even classes (e.g., a class `GeneticOptimizer` encapsulating the GA operations). For maintainability, separating algorithm logic from Django views is good practice. The NewProjectView on form submission can call the appropriate function based on the selected method:

    python

    Copy

    `if method == 'LP':
        result = optimize_with_lp(project)
    elif method == 'GA':
        result = optimize_with_ga(project)
    else:
        result = optimize_with_hybrid(project)`

    The `result` would contain the layout info and metrics, which we then save into the Project model (update the project instance's fields like utilization, etc., and mark status complete). If the processing is quick, we do this within the same request and then redirect to the result page. If it's potentially slow (GA could take several seconds or more), we might spawn a background job. To keep initial implementation straightforward, we assume the datasets are small enough to compute within a few seconds in the web request. If not, we will integrate a task queue (e.g., Celery) later.

-   **Accuracy and Verification**:\
    We will test these algorithms with known small cases:

    -   e.g., stock 100x100, pieces 50x50 and 50x50 (should exactly fill the sheet with zero waste).
    -   odd cases like pieces that cannot all fit (the algorithm should still place as many as possible or at least report waste accordingly -- though in our scenario, we assume all pieces must fit onto given stock; we might clarify if multiple stock sheets can be used. We could allow the concept of using multiple sheets if pieces don't fit in one, which would turn it into a bin packing problem of minimizing number of sheets. This adds complexity, so initial version may assume the stock is large enough or exactly one sheet is used. If multiple sheets needed, we could modify the LP to allow multiple of the given stock size and minimize count used. The GA could also evolve solutions that use an additional sheet if needed. For now, assume one sheet per project to keep scope limited).
    -   Compare results of LP vs GA on the same input to ensure hybrid at least matches the better.
    -   Ensuring no overlap in final layout (we'll create a function to validate that no two pieces overlap and all are within bounds).

In summary, the algorithmic component requires developing optimization logic for cutting patterns:

-   LP: likely an ILP model solved by a solver for an exact solution on smaller problems.
-   GA: a metaheuristic approach for more complex cases.
-   Hybrid: combining both to balance speed and optimality. We will modularize these so future improvements (like using more advanced algorithms or adding deep learning as mentioned in future directions) can be incorporated. The outcome from any method will be standardized (e.g. a list of piece placements) so that the rest of the system (views, templates) can handle it uniformly.

6\. Technical Roadmap (Day-by-Day Development Plan)
---------------------------------------------------

To ensure an organized development process, we break the implementation into a day-by-day checklist. This assumes a roughly two-week timeline (adjust as needed), focusing on one module or major feature at a time while keeping the project integrated:

**Day 1: Project Setup and Core Framework**

-   Set up the Django project and apps structure. Confirm that the apps **core**, **accounts**, **optimizer**, and **dashboard** are created and added to `INSTALLED_APPS` in settings. Run initial migrations for the default User model.
-   Implement the basic core views and URLs: create `HomeView` and templates for home, about, contact, team. Define `core/urls.py` with paths for these pages and include it in the main `urls.py`.
-   Create the base template (`base.html`) with a basic navigation bar and blocks for content. Include links to Home, About, Contact, etc., and placeholders for login/register (we will hook these up once accounts views are ready).
-   Test that the home page and static pages load correctly in the development server (with dummy placeholder text). This sets up the foundation and ensures routing and template inheritance are working.

**Day 2: User Accounts Module**

-   Implement authentication views in the accounts app. Use Django's built-in auth forms or the provided forms: set up `LoginView`, `LogoutView`, `RegisterView` according to the code (most of this is already written in `accounts/views.py`). Create or adjust the `accounts/urls.py` as needed (the provided code already has them).
-   Create the `login.html` and `register.html` templates (from the provided files) and style them to match the base layout. Ensure the registration form includes password confirmation and that the view's logic (password matching and saving user) works.
-   Set up email sending for verification: configure SMTP or console email backend for development. Implement the `EmailVerificationView` such that clicking the link in the email updates the UserProfile. Create a simple `register_email.html` template content if not done (provided in files).
-   Implement `ProfileUpdateView` to allow changing email. Create `profile_update.html` template with a form for new email. Make sure it validates unique email and on save, sends the profile update email.
-   Implement the `accounts/DashboardView` to display SessionLogs, ActivityLogs, Notifications, etc. Design and create the `dashboard.html` template to list this information in a user-friendly way (e.g., a table for recent logins, a list for notifications).
-   By end of Day 2, the basic user account functionality should be working: users can register, verify email, log in, log out, update their email, and see their account dashboard. Test these flows manually. Also ensure that activity logging (login/logout events) and email logging are happening by checking the database or admin site.

**Day 3: Accounts Module -- Advanced Profile Features**

-   (If not already done) Implement the Notification model usage: when a new user registers, perhaps create a welcome notification; when email is verified, maybe a notification; these are nice-to-have touches. Ensure unread notifications show up distinctly on the dashboard template.
-   Implement the "favorite blades/configurations" feature in accounts or optimizer module: Create the `OptimizerConfig` model (or similar) with fields for tool settings (as discussed in Models section). Run migrations to add this model.
-   Create views and forms for managing these configurations. For simplicity, you can integrate it into the profile update page or make a new page in accounts. For example, on the dashboard or profile page, list existing configs and provide a link to add a new one. Implement `ConfigCreateView` and template with fields: name, tool type, kerf, etc. Allow deletion of configs (could be a simple view or even done via the admin interface initially).
-   Test adding a new configuration and ensure it appears in the list. This feature will later tie into the new project form (Day 5) to allow quick selection of a saved config to pre-fill fields.
-   Finish any remaining pieces of accounts: e.g., integrate password change (Django's built-in view/template) if required, or ensure the email verification token expiration logic works (maybe write a small script to clean expired tokens or just rely on handling it in the view).
-   By end of Day 3, the user accounts system is fully featured, including the groundwork for saving custom optimizer preferences.

**Day 4: Optimizer Module -- Models and Project Creation**

-   Define the `Project` and `Piece` models in `optimizer/models.py` as per the design. Include fields for project details (user, dimensions, etc.) and possibly a placeholder for result (like a JSONField for layout). Make migrations and apply them to create the database tables. Also, register these models in `optimizer/admin.py` for easy inspection.
-   Implement the `NewProjectForm` (if using a Django Form or FormView) to handle input for a new project. This could be a `forms.ModelForm` for Project plus some extra fields or a custom form that writes to Project and Piece models. Because pieces are a sub-model, consider how to collect them: maybe use formsets for Piece or a custom field that parses multiple piece entries. If formset is complex, a simpler way: have the form accept a text field like "Pieces (widthxheight Qty)" where user enters something like "50x30 qty2; 20x10 qty5" -- then parse this in the view. For a more structured approach, we might include a few set of fields in the form for piece dims and allow JavaScript to duplicate. For now, implement at least one way to input multiple pieces.
-   Create the `NewProjectView` to handle GET (display form) and POST (validate form and create project). On valid submission:
    -   Create a Project instance (status = 'processing' or 'completed' depending on sync vs async decision).
    -   Create related Piece instances for each required piece.
    -   If we decide to process immediately (synchronously), call the chosen algorithm function right here and get results, update the Project, and redirect to result page. If we plan for background processing, just save the project with status 'pending' and return a response indicating it will be ready soon (and perhaps have a separate mechanism to trigger the algorithm in background).
    -   For initial implementation, proceed with synchronous processing for simplicity.
-   Set up `optimizer/urls.py` with at least the path for `new_project` pointing to this view. Add the optimizer include to main urls so that the form page can be accessed.
-   Create the `new_project.html` template to render the form. Ensure the form fields correspond to what the view expects. If not using a ModelForm for pieces, clearly instruct the user how to input their piece requirements. Also include a dropdown for selecting one of their saved configurations: for this, you might populate a list of OptimizerConfig objects from the user and allow selecting one to auto-fill the form via JS (for now, you can implement a simple onchange handler that sets tool type and kerf fields according to the selected config -- requiring a bit of JS on the template). If time doesn't permit, just have them manually fill the fields and note that favorite configs are a planned enhancement.
-   By end of Day 4, a logged-in user should be able to go to "New Project" page, fill in details, submit, and at least have a Project record created (even if the actual optimization algorithm is not yet implemented). Possibly, you can temporarily implement a dummy result (like just mark all pieces as placed at coordinate (0,0) stacked, or a trivial packing) so that the result page can be tested. The key is that data flows from form to database.

**Day 5: Algorithm Implementation -- Linear Programming**

-   Begin implementing the optimization algorithms, starting with the LP approach. In a file like `optimizer/algorithms.py`, set up the function `optimize_with_lp(project)`. Use the Project and related Pieces data to formulate the problem.
-   Install or ensure availability of an LP solver library (if using PuLP, ensure it's in the environment; the dev environment might already have `ortools` or `pulp`). Write the ILP model:
    -   Define variables (this might require discretizing the stock into a grid of small units if doing exact placement, or using a different formulation like knapSack approach for each row/column). Keep it as straightforward as possible: one idea is to linearize using big M constraints for each pair of pieces i, j: either i is to left of j or i is to right of j, etc. That yields many constraints for n pieces (on the order of n^2), which might be okay for n up to 20 or so. Implement these constraints: for each pair of pieces, enforce that they don't overlap by stating one of them is shifted beyond the other either horizontally or vertically. Because which way is also a decision, you actually need binary variables to choose orientation of non-overlap (this becomes a MILP). If this is too complex to implement fully today, simplify: assume pieces cannot be rotated (to reduce decision space), and perhaps even assume a certain ordering strategy (like sort by height and fill left to right).
    -   Another approach: treat it as a packing of piece widths into the stock width for each row (like cut by cut). This can be formulated as cutting stock (1D) and repeated for the other dimension. But given time, try the pairwise non-overlap method with binary variables if possible.
    -   Use PuLP's LpProblem with LpMaximize (maximize total area used or sum of piece areas * placement variable). Add constraint that each piece is placed exactly once (if using placement variables), and non-overlap constraints.
    -   Solve the LP and check the solver status. Retrieve solution values. Compute utilized area = sum(piece.area) if all placed, which ideally should equal total area if all pieces fit; if not all fit due to a too-small stock, LP would leave some variables 0 (but in our use-case, we expect user wouldn't request more area than stock has, or if they do, maybe we allow multiple stock usage -- optional).
    -   If solving fails or is too slow, fall back to a heuristic: you could implement a simple algorithm like sort pieces by area and place greedily (top-left fill strategy) as a placeholder, ensuring all pieces get a position.
-   Integrate this with the project: In `NewProjectView.form_valid`, after saving the Project and Pieces, call `optimize_with_lp(project)` if that method was chosen. Save the returned layout (for now maybe as JSON in a text field or set Project.utilization, etc.). Mark project status as completed.
-   Create or update the result template to visualize the LP output. For example, if `optimize_with_lp` returns a list of coordinates, embed an SVG in the template to draw rectangles. You can generate a small SVG snippet in Python: iterate over pieces and create `<rect>` elements with `x`, `y`, width, height. Pass that as part of context (or as an HTML-safe string to insert). Or pass the data and use a `<script>` in template to draw. Today, aim to display at least a textual result (like list of pieces and their coordinates, or highlight which pieces fit) if graphical is not ready.
-   Test with a simple scenario: stock 10x10, pieces 5x5 (two of them). The LP should place two pieces with no overlap (both fit exactly, utilization 100%). Verify the result page shows both pieces placed (maybe you'll just see output values or a simple drawing).
-   By end of Day 5, the LP-based optimization path should be functional for basic cases, and its output should be stored and viewable. This means one of the core optimization methods is done, which is a big milestone.

**Day 6: Algorithm Implementation -- Genetic Algorithm**

-   Implement the GA approach in `optimize_with_ga(project)`. This will be more code than LP. Steps to code:
    -   Write a helper to encode a solution (probably just the order list of piece indices and maybe a parallel list for rotations if applicable).
    -   Write the decoder (placement function) that given an order (and rotation flags) will place pieces on the sheet and compute used area. This is essentially a packing algorithm: for each piece in order, iterate over the sheet to find the first position it fits (you can maintain a list of "gaps" or use a simple heuristic like place in the lowest y position possible). A common strategy is the Guillotine packing or Skyline algorithm. Implement a basic version: keep track of filled areas row by row.
    -   Fitness evaluation: likely simply the total used area (or negative waste). Since all pieces must ideally be placed, we can define fitness = used_area. If pieces don't all fit, the used_area is less (not placing some means they're effectively wasted or cause waste).
    -   Create initial population: maybe 20 or 30 random permutations of pieces (Python's `random.shuffle` can help).
    -   GA main loop: for generation in range(N):
        -   Calculate fitness for each individual (decode and compute area).
        -   Select parents (use simple tournament selection or take top 2 for elitism).
        -   Produce offspring with crossover (implement order crossover or even simpler: take a cut of the sequence from parent A and fill the rest from parent B's order).
        -   Mutate some offspring (swap two pieces in order or random shuffle a small portion).
        -   Form the new population (could use elitism to carry over the best solution from previous gen).
    -   After N generations, take the best individual as the result. Decode it to get final placement coordinates.
    -   Make sure to incorporate piece rotation in the genome if we want rotation. Perhaps represent each piece ID as is, but separately carry a bit string or just decide rotation during placement for best fit (e.g., if a piece doesn't fit one way, try rotated if allowed). For initial implementation, maybe assume rotation is allowed and always try both orientations in placement, effectively the GA doesn't need to choose rotation -- it just chooses order, and placement algorithm will rotate pieces if they fit better (or we can simplify by treating pieces as non-rotatable to reduce complexity).
    -   Optimize for correctness first, then consider tuning parameters (population size, generations).
-   Once implemented, integrate GA into the view: if user selected GA, call `optimize_with_ga`. Save results similarly.
-   On the template side, reuse the same visualization logic to display the GA result layout (since format will be the same kind of list of positions).
-   Test with a scenario known to be a bit tricky for greedy algorithms to ensure GA actually improves it (for example, a case where a naive left-to-right fill leaves a gap that could have fit a smaller piece if order was different -- GA should find the better ordering).
-   By end of Day 6, the GA optimization option should be working. We will likely test and tweak it (maybe adjust generation count for reasonable speed). We should also ensure that if GA takes too long, we have a fallback or at least it's documented to be slow for large inputs.

**Day 7: Algorithm Implementation -- Hybrid Method**

-   Develop the hybrid optimization in `optimize_with_hybrid(project)`. Possible approach to implement today:
    -   Use the LP output as a starting point: Run a quick LP (maybe with relaxed constraints or simplifying assumptions) to get an initial solution. For instance, run LP without non-overlap constraints purely to maximize area usage -- it might just select all pieces (since all are needed) which doesn't give layout but could give a trivial result. Alternatively, use a simpler greedy pack (like sort by largest area and place sequentially) as an initial individual.
    -   Then initialize a GA population that includes this initial solution plus random others. Run a shorter GA (since presumably the initial is good). Perhaps incorporate some mutation that uses LP logic (like occasionally solve a subproblem optimally).
    -   Another idea: split pieces into groups, use LP to arrange groups, GA to arrange within group.
    -   Given time constraints, an effective hybrid might be: **Greedy + GA**. Use a greedy algorithm (or LP if it's easy) to get one good layout. Then perform a GA as in Day 6 but starting population includes that layout. This likely speeds up convergence.
    -   Implement accordingly: e.g., use the decoder from GA in a deterministic way for one individual (like sort pieces by height then width as a strategy) to get initial solution. Then run GA loop as before but fewer generations (since we assume near optimal already).
-   Integrate hybrid option in the view. Test it on various inputs, compare results with pure GA or LP if possible to verify it's at least not worse.
-   By end of Day 7, all three optimization modes (LP, GA, Hybrid) are implemented. The heavy lifting code is done. At this stage, the system can actually perform its primary function.

**Day 8: Visualization and Dashboard Module**

-   Focus on improving the visualization of results in the dashboard. Until now, we might have basic SVG drawing. Now refine the `project_detail.html` or `project_dashboard.html` template:
    -   Implement a clear SVG representation: maybe draw the outline of the stock material as a large rectangle with a distinct border. Draw each piece as a smaller rectangle with different colors. Possibly label each piece (like number them) or show dimensions on them. This can be done by embedding text in SVG or using a tooltip. Simpler: give each piece a number and have a legend listing piece number and its size.
    -   Ensure the SVG scales nicely (use viewBox in SVG to make it responsive). The template might set the SVG width to, say, 500px for display regardless of actual mm, and scale contents accordingly.
    -   Add a Plotly graph to the page: include Plotly JS (via CDN). For example, a pie chart of [used_area, unused_area] or a bar chart with one bar = utilization%. If we want to compare algorithms, and if we have data for multiple runs, we could plot that, but at least show something like "Material Utilization: X%" text and maybe a simple visual indicator (like a filled bar).
    -   If multiple sheets usage was possible, show number of sheets used. But currently assume one sheet.
    -   Testing the SVG and chart with real data from algorithms to ensure they render correctly. Adjust colors or layout for clarity (like if pieces are very small, maybe show zoom or just trust the overall view).
    -   Work on the Dashboard app's `ProjectDashboardView` if separate: it might actually just use the same template as project detail. We could decide to consolidate and not use a separate dashboard app view for project results, since the optimizer's detail is essentially the dashboard. However, for clean separation, we keep the **Dashboard app** to handle any analysis beyond just showing one project. Perhaps it can be responsible for the comparison feature:
        -   Implement `ComparisonView`: allow user to pick two of their projects to compare (this could be a form on the projects list page: select two project checkboxes and click compare). For now, create the view to accept two project IDs (ensuring they belong to the user or one is curated if we allow that). The view will gather their utilization and waste data and render a chart comparing them. For example, a bar chart: X-axis has two projects, Y-axis is utilization%, or two bars per project (used vs waste).
        -   Template for compare: Show basic info of each project (name, method used, etc.) and a Plotly chart or simple table comparing metrics.
        -   This is an optional enhancement; if time is short, skip detailed implementation but outline it for future.
-   By end of Day 8, the user experience for viewing results should be polished. When a project is complete, the user sees a nicely formatted page with a visual layout and key numbers, making the benefit of optimization clear (e.g., "Utilization: 90%, Waste: 10%"). This addresses the requirement of **project metrics visualization and comparative graphs**.

**Day 9: Project Listing, Export, and Curated Projects**

-   Now that projects can be created and visualized, ensure the projects listing page (`ProjectListView` and template) is showing correct data:
    -   Query the database for the current user's projects, order by date. For each project, display its name, date, and perhaps the utilization result if completed. If status is 'pending/processing', indicate that and maybe provide a refresh link. If 'completed', provide a link to view details (which goes to the project dashboard).
    -   Also, add an "Export" link or button next to each completed project. This should hit the `project_export` URL we set up. Implement `ExportResultView` to retrieve the project's data and return a downloadable file:
        -   Possibly create a CSV: columns like Piece #, Width, Height, X, Y, Rotated.
        -   Or create a PDF summary. CSV is simpler -- we can generate it on the fly using Python's `csv` module and return as HttpResponse with `Content-Disposition: attachment`.
        -   Test downloading and opening the file to ensure it contains the expected data.
    -   The project list page should also have a button "New Project" to go to the form, and maybe a note about curated projects.
    -   Implement the curated projects listing if required: If using `is_curated` flag, query `Project.objects.filter(is_curated=True)`. For each curated project (which might belong to an admin user), show its name and a link to view. We should allow non-owners to view curated project details. This may require the `OptimizeResultView` and `ProjectDashboardView` to not restrict to owner for those particular projects. We can implement logic like: if `project.is_curated == True`, allow any user (even anonymous maybe) to view it; otherwise, ensure request.user == project.user. This can be handled via a permission check in the view.
    -   Populate some curated projects: either by using the admin site to create a couple of Project entries with predefined pieces and marking curated, then running the optimization to fill results, or by hardcoding some example in the view if not using actual DB. Ideally, use actual data -- maybe as developers, we create a few nice examples (like one showing a neat packing, one showing waste).
    -   Add these curated examples to the database. Now the curated projects page will show them. This satisfies the "viewing curated projects" requirement, providing users (or potential customers) a peek at what the software can do without having to run one themselves.
-   By end of Day 9, the project management aspects are complete: users can see all their projects, know their status, launch new ones, view results, and download reports. Also, some example outputs are available for browsing.

**Day 10: Testing, Notifications, and Final Touches**

-   Conduct thorough testing of all user flows:
    -   Create a new user and go through email verification. Ensure emails are sent and logs appear.
    -   Log in, create a new project with a simple input, confirm that after submission the result appears and is correct. Try each optimization method to see that they all work (for the same input, perhaps compare outputs manually for sanity).
    -   Test error handling: e.g., what if the user inputs a piece larger than the stock -- does the algorithm handle it (maybe it will just show unused piece or 0 utilization; consider adding validation in form to prevent impossible cases or at least warn)?
    -   Try the export functionality to ensure files download properly.
    -   Verify that notifications are generated when appropriate (if we implemented a notification for project completion in the algorithm, check the user's account dashboard for that message).
    -   Test the favorite config feature: create a config and then start a new project using it -- ensure the values populate correctly if we wired that up.
    -   Cross-browser/interface check: open the site in another browser or an incognito window to see that curated projects are accessible without login (if we allowed that).
    -   Use the Django admin to inspect the data models for any inconsistencies.
-   Implement any missing notification triggers: for example, after a project is optimized (especially if done asynchronously, but even if sync, we can simulate it), create a Notification entry for the user like `Notification.objects.create(user=..., message="Project '%s' is ready." % project.name)`. This way, when the user goes to their dashboard or project list, they see a notice. If we wanted, we could also send an email using the `EmailNotificationMixin` for project completion (this would require adding an email template, but we can skip email for completion to avoid complexity, notifications on-site are enough).
-   Refine UI/UX: adjust any layout issues in templates (e.g., maybe improve the navigation bar to show user's name when logged in, add a logout link, etc.). Ensure that protected pages redirect to login if accessed by anonymous users (Django's `LoginRequiredMixin` on views helps this).
-   Documentation & Cleanup: Update the README.md with instructions on how to use the software, how to run the optimization (if any CLI or background tasks needed), and the technologies used. Include notes about any assumptions or limitations (e.g., "currently supports one stock sheet at a time; multi-sheet coming in future", or "pieces are assumed rectangular and can be rotated 90° by default").
-   If deployment is a goal, prepare a production settings file or WSGI config. Possibly create a Dockerfile if needed (the PPT mentions Docker/AWS -- if time permits, containerize the app and ensure it runs). This could be an extended task beyond day-by-day scope, but mention it as the next step.
-   By end of Day 10, the project should be feature-complete and relatively bug-free. All major requirements have been implemented and verified.

**Beyond Day 10 (Future Enhancements):**

-   Although not part of the immediate roadmap, note future steps such as integrating a task queue for running algorithms asynchronously (so the web UI remains responsive for big jobs), adding more advanced algorithms (or improving the existing ones for efficiency and optimality), refining the UI (perhaps with drag-and-drop pieces in the future for manual adjustment), and deployment steps (setting up on AWS with Docker for example).
-   We might also consider additional features like multi-user collaboration or a public gallery of optimized layouts if this were a longer-term project.

