FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the code and build the app
COPY . .
RUN npm run build

# Production Nginx stage
FROM nginx:1.23-alpine

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Remove default nginx static files
#RUN rm -rf /usr/share/nginx/html/*

# Copy static files from builder stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
