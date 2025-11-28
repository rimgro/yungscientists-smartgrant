FROM node:20-alpine AS build
WORKDIR /app

# Build-time API base URL for static bundle (browser must reach this host)
ARG PUBLIC_API_BASE_URL=http://localhost:8000
ENV PUBLIC_API_BASE_URL=${PUBLIC_API_BASE_URL}

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
