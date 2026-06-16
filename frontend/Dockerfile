FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM node:22-alpine

WORKDIR /app

COPY server.mjs .
COPY --from=builder /app/dist ./dist

EXPOSE 80

CMD ["node", "server.mjs"]
