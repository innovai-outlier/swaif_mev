FROM node:20-alpine AS build
WORKDIR /app
COPY services/web/package*.json ./
RUN npm install
COPY services/web ./
RUN npm run build

FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
COPY --from=build /app ./
EXPOSE 3000
CMD ["npm", "run", "start"]
