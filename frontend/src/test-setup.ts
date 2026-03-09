import "@testing-library/jest-dom/vitest";

// jsdom does not implement scrollIntoView
Element.prototype.scrollIntoView = () => {};

// Disable framer-motion animations in tests so AnimatePresence transitions
// resolve immediately and don't block test assertions.
import { vi } from "vitest";

vi.mock("framer-motion", async () => {
  const actual = await vi.importActual<typeof import("framer-motion")>("framer-motion");
  return {
    ...actual,
    AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
    motion: new Proxy(actual.motion, {
      get(target, prop) {
        // Return a forwardRef component that renders the plain HTML element
        // with all non-motion props passed through.
        if (typeof prop === "string" && /^[a-z]/.test(prop)) {
          const Component = (target as unknown as Record<string, unknown>)[prop];
          return Component;
        }
        return (target as unknown as Record<string, unknown>)[prop as string];
      },
    }),
  };
});
