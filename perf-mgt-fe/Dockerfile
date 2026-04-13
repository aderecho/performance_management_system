# -------------------------
# Build stage
# -------------------------
FROM node:20-alpine AS build

WORKDIR /app

# Copy the entire Quasar project FIRST
COPY . .

# Install dependencies (Quasar now sees the project)
RUN npm install

# Build SPA
RUN npm run build

# -------------------------
# Runtime stage
# -------------------------
FROM nginx:alpine

COPY --from=build /app/dist/spa /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]