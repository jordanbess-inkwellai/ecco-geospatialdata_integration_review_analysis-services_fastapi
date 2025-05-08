# FastAPI & Next.js Project

This project integrates a FastAPI backend with a Next.js frontend, providing a robust platform for geospatial data management and visualization.

## Frontend Overview

The frontend is built using Next.js and is designed as a Progressive Web App (PWA). It allows users to interact with the FastAPI microservices and configure database connection settings.

### Project Structure

- **public/**: Contains static assets and the PWA manifest.
- **src/**: Contains the main application code.
  - **pages/**: Next.js pages for routing.
  - **components/**: Reusable React components.
  - **styles/**: Global CSS styles.
  - **utils/**: Utility functions for API calls.
- **package.json**: Lists dependencies and scripts for the frontend.
- **tsconfig.json**: TypeScript configuration file.

### Getting Started

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd fastapi-nextjs-project/frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Run the Development Server**
   ```bash
   npm run dev
   ```

4. **Access the Application**
   Open your browser and navigate to `http://localhost:3000`.

### Configuration

You can configure the database connection settings in the backend FastAPI application. Ensure that the backend is running to interact with the frontend.

### Features

- User-friendly interface for managing geospatial data.
- Integration with FastAPI microservices for data operations.
- PWA capabilities for offline access and improved performance.

### Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

### License

This project is licensed under the MIT License. See the LICENSE file for details.