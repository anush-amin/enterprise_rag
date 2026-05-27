# Enterprise RAG Implementation Guide on GCP

This document outlines the standard operating procedure for setting up and deploying an Enterprise Retrieval-Augmented Generation (RAG) pipeline on Google Cloud Platform (GCP).

## 1. Project Initialization & Environment Setup
Before any development begins, the infrastructure foundation must be established.

* **Create Project:** Open the [GCP Console](https://console.cloud.google.com/) and create a new project. 
    * *Action:* Record the **Project Name** and **Project ID**.
* **Local CLI Configuration (VS Code):**
    * Open the terminal in VS Code.
    * Authenticate: `gcloud auth login`
    * Link to project: `gcloud config set project [YOUR_PROJECT_ID]`
* **Enable Core Services:** Ensure the following APIs are enabled via the console or CLI:
    * Compute Engine (`compute.googleapis.com`)
    * Artifact Registry (`artifactregistry.googleapis.com`)
    * Cloud Run (`run.googleapis.com`)
    * Document AI (`documentai.googleapis.com`)
    * Vertex AI / Discovery Engine (`discoveryengine.googleapis.com`)

## 2. Identity and Access Management (IAM)
Proper permissions are required for the application to interact with storage and AI services.

* **Roles to Assign:**
    * `Storage Admin`: For GCS bucket management.
    * `Document AI API User`: To run OCR processes.
    * `Artifact Registry Repository Administrator`: For CI/CD and image pushing.
    * `Cloud Run Developer`: For managing the compute environment.

## 3. Data Ingestion & Processing (Retrieval Layer)
Setting up the pipeline to handle unstructured data (PDFs).

* **Cloud Storage (GCS):** Create a bucket to store the source documents.
* **Document AI:**
    * Configure a processor for OCR.
    * This component handles the conversion of PDF data into structured text/JSON for embedding.
* **Discovery Engine (Vertex AI Search):**
    * *Note:* Scheduled for future use. This will serve as the managed search/retrieval engine.

## 4. Application Containerization & Deployment
Transitioning the RAG application logic from local development to production.

* **Artifact Registry:**
    * Create a Docker repository.
    * Configure local Docker authentication: `gcloud auth configure-docker [REGION]-docker.pkg.dev`
* **Containerization:**
    * Build your RAG application image.
    * Push the image to the created Artifact Registry repository.
* **Cloud Run:**
    * Deploy the service by selecting the image from the Artifact Registry.
    * Assign the necessary service account to the Cloud Run instance to ensure it can reach GCS and Document AI.

---
**Team Note:** Use either the Google Cloud Console UI for manual configuration or the `gcloud` CLI for automated setups as per your workflow preference.

https://github.com/d-hackmt/enterprise_rag-with-GCP
