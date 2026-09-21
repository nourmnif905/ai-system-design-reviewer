FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 4200

# --host 0.0.0.0 : indispensable dans Docker, sinon le serveur n'écoute
# que sur localhost DANS le conteneur, inaccessible depuis l'extérieur.
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--poll", "2000"]
