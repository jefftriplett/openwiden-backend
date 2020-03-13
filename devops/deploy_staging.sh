#!/bin/sh

ssh "$DEPLOY_USER"@"$DEPLOY_IP" << 'EOF'
  cd openwiden-backend-staging || git clone https://github.com/OpenWiden/openwiden-backend openwiden-backend-staging && cd openwiden-backend-staging
  git checkout develop
  git pull
  make COMPOSE_FILES=STAGING_COMPOSE_FILES pull
  make COMPOSE_FILES=STAGING_COMPOSE_FILES up
EOF
