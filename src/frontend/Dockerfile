FROM node:18-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ARG NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
RUN NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=$NEXT_PUBLIC_GOOGLE_MAPS_API_KEY npm run build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app /app

ENV NODE_ENV=production
# Expose the port where the website will run in
EXPOSE 3000
CMD ["npm", "run", "start"]
