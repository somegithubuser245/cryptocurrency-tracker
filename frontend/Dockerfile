FROM node:20-alpine

WORKDIR /frontend

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci --only=production=false

# Copy application code
COPY . .

EXPOSE 5173

# Use development server with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]