# Dockerfile for Dexter Frontend
# Simple nginx static file server

FROM nginx:alpine

# Copy static files
COPY public /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 8080
EXPOSE 8080

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
