FROM oven/bun:1.2 AS build

WORKDIR /app
COPY package.json bun.lock ./
COPY frontend/package.json frontend/package.json
RUN bun install --frozen-lockfile

COPY frontend frontend
ARG VITE_API_URL=http://127.0.0.1:8000/api/v1
ENV VITE_API_URL=$VITE_API_URL
WORKDIR /app/frontend
RUN bun run build

FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
EXPOSE 80
