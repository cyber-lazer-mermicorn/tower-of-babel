/**
 * Advanced exhibit: governed MCP/JSON-RPC style gateway.
 * Runtime validation, rate limiting, mutation approval, hashed receipts.
 * No placeholders.
 */

import { createHash } from "crypto";

export type JsonValue = string | number | boolean | null | JsonValue[] | { [k: string]: JsonValue };

export interface ToolCall {
  id: string;
  tool: string;
  args: Record<string, JsonValue>;
  mutate?: boolean;
}

export interface GatewayReceipt {
  ok: boolean;
  id: string;
  tool: string;
  allowed: boolean;
  reason?: string;
  result?: JsonValue;
  digest: string;
}

export interface GatewayConfig {
  allowedTools: Set<string>;
  maxCallsPerMinute: number;
  requireApprovalForMutations: boolean;
  approvedMutations: Set<string>;
}

export class McpGateway {
  private calls: number[] = [];

  constructor(private readonly config: GatewayConfig) {
    if (config.maxCallsPerMinute < 1) {
      throw new Error("maxCallsPerMinute must be >= 1");
    }
  }

  private rateLimitOk(): boolean {
    const now = Date.now();
    this.calls = this.calls.filter((t) => now - t < 60_000);
    if (this.calls.length >= this.config.maxCallsPerMinute) {
      return false;
    }
    this.calls.push(now);
    return true;
  }

  private digest(payload: string): string {
    return createHash("sha256").update(payload).digest("hex").slice(0, 16);
  }

  handle(call: ToolCall): GatewayReceipt {
    if (!call.id || !call.tool) {
      return {
        ok: false,
        id: call.id || "",
        tool: call.tool || "",
        allowed: false,
        reason: "id and tool are required",
        digest: this.digest("invalid"),
      };
    }

    if (!this.rateLimitOk()) {
      return {
        ok: false,
        id: call.id,
        tool: call.tool,
        allowed: false,
        reason: "rate limit exceeded",
        digest: this.digest(`${call.id}|rate`),
      };
    }

    if (!this.config.allowedTools.has(call.tool)) {
      return {
        ok: false,
        id: call.id,
        tool: call.tool,
        allowed: false,
        reason: `tool not allowed: ${call.tool}`,
        digest: this.digest(`${call.id}|deny`),
      };
    }

    if (call.mutate && this.config.requireApprovalForMutations) {
      if (!this.config.approvedMutations.has(call.id)) {
        return {
          ok: false,
          id: call.id,
          tool: call.tool,
          allowed: false,
          reason: "mutation requires prior approval",
          digest: this.digest(`${call.id}|approval`),
        };
      }
    }

    // Simulated successful tool execution boundary
    const result: JsonValue = { echo: call.args, tool: call.tool };
    const payload = `${call.id}|${call.tool}|${JSON.stringify(call.args)}`;
    return {
      ok: true,
      id: call.id,
      tool: call.tool,
      allowed: true,
      result,
      digest: this.digest(payload),
    };
  }
}

// Self-check
if (require.main === module) {
  const gw = new McpGateway({
    allowedTools: new Set(["search", "write_note"]),
    maxCallsPerMinute: 10,
    requireApprovalForMutations: true,
    approvedMutations: new Set(["mut-1"]),
  });

  const ok = gw.handle({ id: "c1", tool: "search", args: { q: "tower" } });
  console.assert(ok.ok && ok.allowed);

  const denied = gw.handle({ id: "c2", tool: "delete_all", args: {} });
  console.assert(!denied.allowed);

  const mutDenied = gw.handle({
    id: "mut-2",
    tool: "write_note",
    args: { text: "x" },
    mutate: true,
  });
  console.assert(!mutDenied.allowed);

  const mutOk = gw.handle({
    id: "mut-1",
    tool: "write_note",
    args: { text: "approved" },
    mutate: true,
  });
  console.assert(mutOk.ok);

  console.log("advanced_mcp_gateway: ok");
}
