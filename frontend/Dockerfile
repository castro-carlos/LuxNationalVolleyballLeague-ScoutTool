# ==========================================
# Stage 1: Build the React Application (Vite)
# ==========================================
FROM node:22-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy app files and build static bundle
COPY . .
RUN npm run build

# ==========================================
# Stage 2: Serve Static Assets with Nginx
# ==========================================
FROM nginx:alpine

# Copy built static assets from Stage 1 (Vite outputs to /app/dist)
COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]