# FastAPI and Next.js Project

This project integrates a FastAPI backend with a Next.js frontend, providing a robust platform for geospatial data management and user interaction through a Progressive Web App (PWA).

## Backend Overview

The backend is built using FastAPI and includes several microservices that handle different aspects of geospatial data:

- **FastGeospatial**: Endpoints for managing geospatial data.
- **FastImporter**: Endpoints for importing data into the system.
- **FateGeoFeature**: Endpoints for managing geo-feature queries.
- **FastGeoTable**: Endpoints for handling table-related operations.
- **FastGeoSuitability**: Endpoints for assessing geospatial suitability.

### Directory Structure

- `app/main.py`: Entry point for the FastAPI application.
- `app/api/v1/`: Contains all API endpoint definitions.
- `app/core/`: Contains configuration and database management files.
- `app/models/`: Intended for database models.
- `app/schemas/`: Intended for Pydantic schemas for data validation.
- `app/utils/`: Contains utility functions.

### Requirements

To install the necessary dependencies for the backend, run:

```
pip install -r requirements.txt
```

## Frontend Overview

The frontend is developed using Next.js and serves as the user interface for interacting with the backend services. It is designed as a Progressive Web App (PWA) for enhanced user experience.

### Directory Structure

- `public/manifest.json`: Metadata for the PWA.
- `src/pages/`: Contains the main pages of the application.
- `src/components/`: Contains reusable components.
- `src/styles/`: Contains global styles.
- `src/utils/`: Contains utility functions for API calls.

### Running the Frontend

To start the frontend application, navigate to the `frontend` directory and run:

```
npm install
npm run dev
```

## Setup Instructions

1. Clone the repository.
2. Navigate to the `backend` directory and install the requirements.
3. Start the FastAPI application using a command like `uvicorn app.main:app --reload`.
4. Navigate to the `frontend` directory and install the npm packages.
5. Start the Next.js application.

## Usage

Once both the backend and frontend are running, you can access the application through your web browser. The frontend will provide a user-friendly interface to interact with the backend services.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.