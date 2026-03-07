import { afterEach, describe, expect, it, vi } from "vitest";

import { listConversations } from "./client";

describe("api client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("returns parsed data on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue({
          ok: true,
          data: {
            conversations: [
              { id: "c1", title: "A", project_path: "/tmp", active: 0, updated_at: "t" },
            ],
          },
        }),
      }),
    );

    const result = await listConversations();
    expect(result).toHaveLength(1);
    expect(result[0]?.id).toBe("c1");
  });

  it("uses API error message when non-2xx response has JSON body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: vi.fn().mockResolvedValue({ ok: false, error: "Conversation not found" }),
      }),
    );

    await expect(listConversations()).rejects.toThrow("Conversation not found");
  });

  it("falls back to status-based message when non-JSON error body is returned", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: vi.fn().mockRejectedValue(new SyntaxError("Unexpected token < in JSON")),
      }),
    );

    await expect(listConversations()).rejects.toThrow("Request failed: 500");
  });

  it("throws envelope error when ok=false in JSON body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue({ ok: false, error: "Domain failure" }),
      }),
    );

    await expect(listConversations()).rejects.toThrow("Domain failure");
  });

  it("propagates network failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Network down")));
    await expect(listConversations()).rejects.toThrow("Network down");
  });
});
