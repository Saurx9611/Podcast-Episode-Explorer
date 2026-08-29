/**
 * Centralized Motion System for Podcast Explorer
 * Inspired by Linear, Raycast, and Motion design principles.
 */

export const transitions = {
  // Spring configurations for natural physics
  springSubtle: {
    type: "spring",
    stiffness: 400,
    damping: 30,
    mass: 0.8,
  },
  springBouncy: {
    type: "spring",
    stiffness: 500,
    damping: 25,
    mass: 0.6,
  },
  springGentle: {
    type: "spring",
    stiffness: 280,
    damping: 28,
  },
  // Smooth cubic-bezier easings
  easeOutQuart: [0.25, 1, 0.5, 1],
  easeInOutQuart: [0.76, 0, 0.24, 1],
  easeOutExpo: [0.16, 1, 0.3, 1],
} as const;

export const durations = {
  instant: 0.1,
  fast: 0.18,
  normal: 0.28,
  deliberate: 0.45,
  slow: 0.65,
} as const;

export const variants = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: durations.normal, ease: transitions.easeOutQuart } },
    exit: { opacity: 0, transition: { duration: durations.fast, ease: transitions.easeOutQuart } },
  },
  fadeInUp: {
    initial: { opacity: 0, y: 12 },
    animate: { opacity: 1, y: 0, transition: { duration: durations.normal, ease: transitions.easeOutQuart } },
    exit: { opacity: 0, y: -8, transition: { duration: durations.fast, ease: transitions.easeOutQuart } },
  },
  fadeInScale: {
    initial: { opacity: 0, scale: 0.96 },
    animate: { opacity: 1, scale: 1, transition: { duration: durations.normal, ease: transitions.easeOutExpo } },
    exit: { opacity: 0, scale: 0.97, transition: { duration: durations.fast, ease: transitions.easeOutQuart } },
  },
  staggerContainer: {
    initial: {},
    animate: {
      transition: {
        staggerChildren: 0.04,
        delayChildren: 0.02,
      },
    },
  },
  staggerItem: {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0, transition: { duration: durations.normal, ease: transitions.easeOutQuart } },
  },
  modalBackdrop: {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: durations.fast } },
    exit: { opacity: 0, transition: { duration: durations.fast } },
  },
  modalContent: {
    initial: { opacity: 0, scale: 0.95, y: 16 },
    animate: { opacity: 1, scale: 1, y: 0, transition: { duration: durations.normal, ease: transitions.easeOutExpo } },
    exit: { opacity: 0, scale: 0.97, y: 10, transition: { duration: durations.fast, ease: transitions.easeOutQuart } },
  },
  cardHover: {
    rest: { y: 0, transition: { duration: durations.fast, ease: transitions.easeOutQuart } },
    hover: { y: -2, transition: { duration: durations.fast, ease: transitions.easeOutQuart } },
  },
} as const;
