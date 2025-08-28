# Development Dockerfile for React frontend with hot reload
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the application code
COPY . .

# Expose the development server port
EXPOSE 3000

# Set environment for development
ENV NODE_ENV=development

# Start the development server with hot reload
CMD ["npm", "start"]
