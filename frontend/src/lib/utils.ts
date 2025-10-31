/**
 * Get the start of the current week (Sunday at midnight)
 */
export function getCurrentWeekStart(): Date {
  const today = new Date();
  const daysSinceSunday = (today.getDay() + 7) % 7; // 0 for Sunday, 1 for Monday, etc.
  const weekStart = new Date(today);
  weekStart.setDate(today.getDate() - daysSinceSunday);
  weekStart.setHours(0, 0, 0, 0);
  return weekStart;
}

/**
 * Format the week start date for display
 */
export function formatWeekStart(): string {
  const weekStart = getCurrentWeekStart();
  const options: Intl.DateTimeFormatOptions = { 
    month: "short", 
    day: "numeric", 
    year: "numeric" 
  };
  return weekStart.toLocaleDateString("en-US", options);
}

/**
 * Format a date range for display
 */
export function formatDateRange(weekStart: string, weekEnd: string): string {
  const start = new Date(weekStart);
  const end = new Date(weekEnd);
  
  const options: Intl.DateTimeFormatOptions = { month: "short", day: "numeric", year: "numeric" };
  const startStr = start.toLocaleDateString("en-US", options);
  const endStr = end.toLocaleDateString("en-US", options);
  
  return `${startStr} - ${endStr}`;
}

/**
 * Calculate win rate as a percentage string
 */
export function calculateWinRate(wins: number, losses: number): string {
  const totalGames = wins + losses;
  return totalGames > 0 ? ((wins / totalGames) * 100).toFixed(1) : "0.0";
}

