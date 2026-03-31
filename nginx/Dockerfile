# Nginx web server for serving static frontend files
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend files to nginx
COPY frontend /usr/share/nginx/html/
COPY index.html /usr/share/nginx/html/

# Expose port 80 for HTTP traffic
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
