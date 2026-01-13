# Horuseye: Distributed Cybersecurity Scanning Platform

Horuseye is a scalable, event-driven cybersecurity scanning system designed to decouple monolithic scanning tools into independent, containerized microservices. Orchestrated by Google Kubernetes Engine (GKE), it replaces single-VM bottlenecks with a dynamic architecture that scales on demand.

## 🏗 System Architecture

Horuseye utilizes a microservices architecture where the control plane is separated from the execution plane.

### Core Components

* **Frontend (User Interface):** Built with **Next.js**, handling user interactions and communicating exclusively with the API Gateway.


* **API Gateway (Control Plane):** A robust service (recommended **FastAPI**) running in GKE. It acts as the single entry point, managing authentication, authorization, input validation, and rate limiting.


* **Workflow Engine:** **Argo Workflows** manages the sequence of scanning tasks, creating dedicated namespaces and pods for every scan to ensure isolation.


* **Asynchronous Messaging:** **Google Pub/Sub** decouples services, allowing tools to communicate via events rather than direct dependencies.


* **Data & Storage:**
* **Cloud SQL (PostgreSQL):** Stores user data and scan configurations.


* **Google Cloud Storage (GCS):** Stores all tool outputs (logs, XML, evidence) and final reports.




* **AI Analysis:** **Vertex AI (Gemini API)** processes raw tool logs to generate structured insights and summaries, avoiding local resource bottlenecks.



## 🚀 Workflow: Life of a Scan

1. **Initiation:** A user submits a scan request via the Next.js UI, which sends the request to the API Gateway.


2. **Validation & Trigger:** The Gateway authenticates the user via JWT, validates inputs (e.g., target domain), stores metadata in Cloud SQL, and submits a workflow template to Argo.


3. **Orchestration:** Argo creates a unique namespace (e.g., `scan-abc123`) for network isolation.


4. **Execution Phase:**
* **Reconnaissance:** The Recon Service pod launches, runs tools (e.g., Nmap), uploads logs to GCS, and publishes a completion message to Pub/Sub.


* **Vulnerability Scanning:** Subscribed to the Recon topic, the Vulnerability Service spins up automatically, processes data, and uploads its own results.




5. **Reporting:** Upon completion of all steps, the Report Generation Service fetches all logs from GCS, sends them to the Gemini API for analysis, and generates a PDF/Markdown report.


6. **Cleanup:** Argo automatically deletes the temporary namespace and pods to free up resources.



## 🛡 Security Implementation

Horuseye implements security best practices to protect the infrastructure and the integrity of the scans:

* **Workload Identity:** Kubernetes Service Accounts (KSA) are linked to Google Service Accounts (GSA), allowing pods to authenticate with GCP services (like Secret Manager) without hardcoded keys.


* **Secrets Management:** Sensitive data (e.g., API keys, database credentials) are stored in **Google Secret Manager** and injected into pods only at runtime.


* **Input Sanitization:** The API Gateway validates all inputs using Pydantic schemas to prevent command injection before data ever reaches the worker pods.


* **Least Privilege:** Each worker pod is assigned a specific service account with the minimum permissions required (e.g., only read/write access to its specific GCS folder).



## 📈 Scalability & Performance

* **Horizontal Pod Autoscaling (HPA):** GKE automatically scales the API Gateway replicas based on traffic load.


* **Cluster Autoscaling:** Node pools expand or contract based on the number of concurrent pentest scans.


* **Cost Efficiency:**
* **Spot VMs:** Utilized for fault-tolerant workflow steps to reduce compute costs.


* **GKE Autopilot:** Manages underlying nodes, charging only for per-pod resource usage.


* **Serverless AI:** Offloading LLM tasks to Vertex AI prevents the need for expensive, always-on GPU instances.





## 🛠 Tech Stack

| Component | Technology | Role |
| --- | --- | --- |
| **Frontend** | Next.js | User Interface |
| **API Gateway** | FastAPI / Flask | Control Plane & Security |
| **Database** | Cloud SQL (PostgreSQL) | Structured Data Storage |
| **Object Storage** | Google Cloud Storage | Log & Artifact Storage |
| **Orchestration** | Argo Workflows | K8s Native Workflow Engine |
| **Messaging** | Google Pub/Sub | Event Bus |
| **Scanner Tools** | Docker | Container Runtime for Tools |
| **AI Engine** | Vertex AI (Gemini) | Report Generation |
| **Secrets** | Google Secret Manager | Credential Management |
