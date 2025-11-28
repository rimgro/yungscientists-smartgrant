## Use BuildKit cache mounts for faster installs and add a dev target for live reloads.
# syntax=docker/dockerfile:1.5

FROM node:20-alpine AS base
WORKDIR /app

# Build-time API base URL for static bundle (browser must reach this host)
ARG PUBLIC_API_BASE_URL=http://localhost:8000
ENV PUBLIC_API_BASE_URL=${PUBLIC_API_BASE_URL}

COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM base AS dev
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "--port", "4173"]

FROM base AS build
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
