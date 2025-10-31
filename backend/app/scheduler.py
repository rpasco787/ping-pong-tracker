"""
Background scheduler for periodic tasks.

This module sets up APScheduler to run automated tasks:
- Weekly leaderboard reset every Sunday at midnight
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .weekly_reset import perform_weekly_reset


# Create scheduler instance
scheduler = BackgroundScheduler()


def start_scheduler():
    """
    Start the background scheduler with configured jobs.
    
    Scheduled jobs:
    - Weekly reset: Every Sunday at 00:00:00 (midnight)
    """
    # Schedule weekly reset for Sunday at midnight
    scheduler.add_job(
        perform_weekly_reset,
        trigger=CronTrigger(day_of_week='sun', hour=0, minute=0, second=0),
        id='weekly_reset',
        name='Weekly Leaderboard Reset',
        replace_existing=True,
        misfire_grace_time=3600  # Allow up to 1 hour late execution if server was down
    )
    
    # Start the scheduler
    scheduler.start()
    print("Scheduler started. Weekly reset scheduled for Sundays at midnight.")
    
    # Print next run time
    job = scheduler.get_job('weekly_reset')
    if job:
        print(f"Next weekly reset scheduled for: {job.next_run_time}")


def shutdown_scheduler():
    """
    Shutdown the scheduler gracefully.
    Called when the application is shutting down.
    """
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler shut down successfully.")


def get_scheduler_status() -> dict:
    """
    Get current scheduler status and job information.
    
    Returns:
        dict: Scheduler status including running state and scheduled jobs
    """
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger)
        })
    
    return {
        'running': scheduler.running,
        'jobs': jobs
    }

