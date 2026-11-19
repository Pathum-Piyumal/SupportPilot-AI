FROM node:22.21.0-alpine
WORKDIR /workspace
COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN npm ci
COPY --chown=node:node apps/web ./apps/web
RUN chown -R node:node /workspace/node_modules /workspace/apps
USER node
EXPOSE 5173
CMD ["npm", "run", "dev"]
