/**
 * Shim for window.spark.user() — Spark-specific API.
 * Replace with actual user context in production.
 */
export async function getSparkUser() {
  return {
    id: 1,
    login: 'You',
    avatarUrl: '',
  }
}
