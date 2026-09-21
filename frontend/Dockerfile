# Image de developpement du frontend Next.js (hot reload).
FROM node:22-alpine

ENV NEXT_TELEMETRY_DISABLED=1

WORKDIR /app

# Certificats racine d'entreprise (proxy d'inspection TLS). Dossier
# eventuellement vide : voir certs/README.md. On evite `apk` ici, qui echouerait
# lui-meme sur le proxy avant que les certificats soient installes.
COPY --from=certs . /tmp/corp-certs/
RUN mkdir -p /usr/local/share/ca-certificates \
    && { cat /tmp/corp-certs/*.crt > /usr/local/share/ca-certificates/corporate-ca.crt 2>/dev/null || true; } \
    && touch /usr/local/share/ca-certificates/corporate-ca.crt \
    && cat /usr/local/share/ca-certificates/corporate-ca.crt >> /etc/ssl/certs/ca-certificates.crt \
    && rm -rf /tmp/corp-certs

ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/corporate-ca.crt

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
