# Online Ecommerce Mart API1

## Project Overview

This project involves developing an API for an online mart using an event-driven microservices architecture. It leverages various technologies like FastAPI, Docker, Docker Compose, PostgreSQL, Kafka, and Kong. The system is designed to handle high volumes of transactions and data efficiently.

## Objectives

- Develop a scalable API for an online mart using microservices.
- Implement an event-driven architecture to manage asynchronous communication between services.
- Use FastAPI for API development and Docker for containerization.
- Ensure seamless development and deployment with Docker Compose.
- Manage API requests with Kong API Gateway.
- Persist data using PostgreSQL.

## Technologies

- **FastAPI**: A high-performance web framework for building APIs with Python.
- **Docker**: For containerizing microservices, ensuring consistency across environments.
- **Docker Compose**: For orchestrating multi-container Docker applications.
- **PostgreSQL**: A powerful, open-source relational database system.
- **Kafka**: A distributed event streaming platform for building real-time data pipelines.
- **Kong**: An open-source API Gateway for managing and routing API requests.

## Microservices

- **User Service**: Manages user authentication, registration, and profiles.
- **Product Service**: Manages product catalog, including CRUD operations for products.
- **Order Service**: Handles order creation, updating, and tracking.
- **Inventory Service**: Manages stock levels and inventory updates.
- **Notification Service**: Sends notifications (email, SMS) to users about order statuses and other updates.
- **Payment Service**: Processes payments and manages transaction records.

## Setup and Running

1. **Clone the Repository**

   ```bash
   git clone github.com/HamzaNasiem/ecommerce-mart-api
   ```

2. **Setup Docker Containers**

   Run the following command to start the Docker containers:

   ```bash
   docker compose --profile database up -d
   ```

3. **Environment Variables**

   This project does not use a `.env` file. Make sure to set any necessary environment variables directly in your Docker configuration or local setup.

4. **Testing and Development**

   For development, ensure all services are running and interact with the API as needed. Update or add configurations as required.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to adjust any specifics or add more details as needed!

## Contact

For any questions, contact (ziaee.pk@gmail.com).
