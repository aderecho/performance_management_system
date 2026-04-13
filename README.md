<h1>Performance Management System</h1>

The Performance Management System is a web-based platform designed to support planning, monitoring, and evaluation of organizational initiatives. It enables institutions to track targets, measure accomplishments, and generate insights for data-driven decision-making.

<h2>Features</h2>
<ul>
  <li>Planning of programs, projects, and initiatives</li>
  <li>Hierarchical structure using Adjacency List Model</li>
  <li>Configurable Templates for standardization</li>
  <li>Monitoring of targets and accomplishments</li>
  <li>Evaluation using performance indicators</li>
  <li>Performance Management integration</li>
  <li>Role-based access control (RBAC)</li>
  <li>Reports and dashboards</li>
</ul>

<h2>Core Concepts</h2>
<h3>Adjacency List Structure</h3>

<p>The system uses an adjacency list model to represent hierarchical data such as:</p>
<ul>
  <li>Organizational structures</li>
  <li>Strategic plans</li>
  <li>Programs → Projects → Activities</li>
</ul>
<p>Each record references its parent, enabling flexible and scalable tree structures.</p>

<h2>Tech Stack</h2>
<b>Backend:</b> Django </br>
<b>Database:</b> PostgreSQL </br>
<b>API:</b> Django REST Framework </br>
<b>Frontend:</b> Quasar Framework (VueJS) </br>

<h2>Project Structure</h2>
<pre>
pme/
│── backend (API)
│  │── apps/
│    ├── authentication/                # Authentication
│    ├── core/                          # Shared models (Profile, Units, etc.)
│    └──  pme/                           # Templates, Documents, and hierarchical items
│  │── perf-mgt/
│  │── config/
│  │── manage.py
│  │── requirements.txt
│  └── Dockerfile
│── frontend
│  │── src/
│  │── public/
│  │── quasar.config.js/
│  └── Dockerfile
│── .env.dev
│── .env.prod
│── docker-compose.dev.yml
└── docker-compose.prod.yml

</pre>

<h2>Environment Variables</h2>
<pre>
DEBUG=True
SECRET_KEY=your_secret_key
DB_NAME=pme_db
DB_USER=your_user
DB_PASSWORD=your_password
ALLOWED_HOSTS=localhost
CSRF_TRUSTED_ORIGINS=http://localhost:9000
</pre>
