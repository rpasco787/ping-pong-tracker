#!/bin/bash

# Quick migration helper script

case "$1" in
  "init")
    echo "Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
    ;;
  "migrate")
    if [ -z "$2" ]; then
      echo "Usage: ./migrate.sh migrate 'message'"
      exit 1
    fi
    echo "Creating new migration: $2"
    alembic revision --autogenerate -m "$2"
    ;;
  "up")
    echo "Applying all pending migrations..."
    alembic upgrade head
    ;;
  "down")
    echo "Rolling back last migration..."
    alembic downgrade -1
    ;;
  "status")
    echo "Current migration status:"
    alembic current
    echo ""
    echo "Migration history:"
    alembic history
    ;;
  "reset")
    echo "⚠️  WARNING: This will destroy all data!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
      echo "Rolling back all migrations..."
      alembic downgrade base
    else
      echo "Cancelled."
    fi
    ;;
  *)
    echo "Ping Pong Tracker - Migration Helper"
    echo ""
    echo "Usage:"
    echo "  ./migrate.sh init           Create initial migration"
    echo "  ./migrate.sh migrate 'msg'  Create new migration"
    echo "  ./migrate.sh up             Apply all pending migrations"
    echo "  ./migrate.sh down           Rollback last migration"
    echo "  ./migrate.sh status         Show migration status"
    echo "  ./migrate.sh reset          Reset database (DESTRUCTIVE!)"
    echo ""
    echo "Examples:"
    echo "  ./migrate.sh init"
    echo "  ./migrate.sh migrate 'Add ranking field'"
    echo "  ./migrate.sh up"
    ;;
esac

