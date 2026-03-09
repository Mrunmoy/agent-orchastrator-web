import { describe, expect, it } from "vitest";
import { fadeInUp, staggerContainer, hoverScale, slideInLeft, viewTransition } from "../animations";

describe("animation variants", () => {
  describe("fadeInUp", () => {
    it("has initial, animate, exit, and transition keys", () => {
      expect(fadeInUp).toHaveProperty("initial");
      expect(fadeInUp).toHaveProperty("animate");
      expect(fadeInUp).toHaveProperty("exit");
      expect(fadeInUp).toHaveProperty("transition");
    });

    it("has opacity and y transforms in initial state", () => {
      expect(fadeInUp.initial).toEqual(expect.objectContaining({ opacity: 0, y: 20 }));
    });

    it("animates to full opacity and y=0", () => {
      expect(fadeInUp.animate).toEqual(expect.objectContaining({ opacity: 1, y: 0 }));
    });

    it("has a duration of at most 300ms", () => {
      expect(fadeInUp.transition.duration).toBeLessThanOrEqual(0.3);
    });
  });

  describe("staggerContainer", () => {
    it("has animate key with staggerChildren", () => {
      expect(staggerContainer).toHaveProperty("animate");
      expect(staggerContainer.animate.transition).toHaveProperty("staggerChildren");
    });

    it("staggers children by 50ms", () => {
      expect(staggerContainer.animate.transition.staggerChildren).toBe(0.05);
    });
  });

  describe("hoverScale", () => {
    it("has whileHover and whileTap keys", () => {
      expect(hoverScale).toHaveProperty("whileHover");
      expect(hoverScale).toHaveProperty("whileTap");
    });

    it("scales up on hover", () => {
      expect(hoverScale.whileHover.scale).toBeGreaterThan(1);
    });

    it("scales down on tap", () => {
      expect(hoverScale.whileTap.scale).toBeLessThan(1);
    });
  });

  describe("slideInLeft", () => {
    it("has initial, animate, and transition keys", () => {
      expect(slideInLeft).toHaveProperty("initial");
      expect(slideInLeft).toHaveProperty("animate");
      expect(slideInLeft).toHaveProperty("transition");
    });

    it("has x transform in initial state", () => {
      expect(slideInLeft.initial).toEqual(expect.objectContaining({ x: -20 }));
    });

    it("animates to x=0", () => {
      expect(slideInLeft.animate).toEqual(expect.objectContaining({ x: 0 }));
    });
  });

  describe("viewTransition", () => {
    it("has initial, animate, exit, and transition keys", () => {
      expect(viewTransition).toHaveProperty("initial");
      expect(viewTransition).toHaveProperty("animate");
      expect(viewTransition).toHaveProperty("exit");
      expect(viewTransition).toHaveProperty("transition");
    });

    it("fades from 0 to 1", () => {
      expect(viewTransition.initial).toEqual(expect.objectContaining({ opacity: 0 }));
      expect(viewTransition.animate).toEqual(expect.objectContaining({ opacity: 1 }));
    });
  });
});
