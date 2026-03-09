/**
 * Shared Framer Motion animation variants for consistent, subtle UI transitions.
 * Max duration: 300ms. Keep transforms small.
 */

/** Fade in from below — ideal for chat messages and content cards. */
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
  transition: { duration: 0.3, ease: "easeOut" },
};

/** Staggered container — wrap a list; children animate sequentially. */
export const staggerContainer = {
  animate: { transition: { staggerChildren: 0.05 } },
};

/** Scale on hover — subtle lift for interactive cards. */
export const hoverScale = {
  whileHover: { scale: 1.02, transition: { duration: 0.2 } },
  whileTap: { scale: 0.98 },
};

/** Slide in from the left — sidebar list items. */
export const slideInLeft = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  transition: { duration: 0.25 },
};

/** Simple cross-fade for view transitions (chat <-> dashboard). */
export const viewTransition = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.2 },
};
