/**
 * Advanced exhibit: governed MCP/JSON-RPC gateway.
 * Owns boundary: method allowlist, JSON schema shape, rate limit,
 * idempotency keys, mutation approval, hashed receipts.
 */

import { createHash } from "crypto";

type Json = null | boolean | number | string | Json[] | { [k: string]: Json };

interface RpcRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: Json;
  idempotency_key?: string;
}

interface RpcResponse {
  jsonrpc: "2.0";
  id: string | number | null;
  result?: Json;
  error?: { code: number; message: string };
}

interface Receipt {
  ok: boolean;
  allowed: number;
  denied: number;
  duplicates: number;
  digest: string;
}

const ALLOWED = new Set(["tools/list", "tools/call", "ping"]);
const MUTATING = new Set(["tools/call"]);

class RateLimiter {
  private timestamps: number[] = [];
  constructor(private limit: number, private windowMs: number) {}
  allow(): boolean {
    const now = Date.now();
    this.timestamps = this.timestamps.filter((t) => now - t < this.windowMs);
    if (this.timestamps.length >= this.limit) return false;
    this.timestamps.push(now);
    return true;
  }
}

class McpGateway {
  private rate = new RateLimiter(10, 1000);
  private seenIds = new Set<string>();
  private idempotency = new Map<string, RpcResponse>();
  private allowed = 0;
  private denied = 0;
  private duplicates = 0;
  private approvedMutations = new Set<string>();

  approveMutation(id: string): void {
    this.approvedMutations.add(id);
  }

  private validateShape(req: RpcRequest): string | null {
    if (req.jsonrpc !== "2.0") return "bad jsonrpc";
    if (req.id === undefined || req.id === null) return "missing id";
    if (typeof req.method !== "string" || !req.method) return "bad method";
    return null;
  }

  handle(raw: RpcRequest): RpcResponse {
    const shapeErr = this.validateShape(raw);
    if (shapeErr) {
      this.denied++;
      return { jsonrpc: "2.0", id: raw.id ?? null, error: { code: -32600, message: shapeErr } };
    }
    if (raw.idempotency_key && this.idempotency.has(raw.idempotency_key)) {
      this.duplicates++;
      return this.idempotency.get(raw.idempotency_key)!;
    }
    if (!this.rate.allow()) {
      this.denied++;
      return { jsonrpc: "2.0", id: raw.id, error: { code: -32000, message: "rate_limited" } };
    }
    if (!ALLOWED.has(raw.method)) {
      this.denied++;
      return { jsonrpc: "2.0", id: raw.id, error: { code: -32601, message: "method_not_found" } };
    }
    if (MUTATING.has(raw.method) && !this.approvedMutations.has(String(raw.id))) {
      this.denied++;
      return { jsonrpc: "2.0", id: raw.id, error: { code: -32001, message: "mutation_not_approved" } };
    }
    const idKey = String(raw.id);
    if (this.seenIds.has(idKey)) {
      this.duplicates++;
      return { jsonrpc: "2.0", id: raw.id, error: { code: -32002, message: "duplicate_id" } };
    }
    this.seenIds.add(idKey);
    this.allowed++;
    let result: Json = { ok: true };
    if (raw.method === "ping") result = { pong: true };
    if (raw.method === "tools/list") result = { tools: ["search", "summarize"] };
    if (raw.method === "tools/call") result = { called: true, params: raw.params ?? null };
    const resp: RpcResponse = { jsonrpc: "2.0", id: raw.id, result };
    if (raw.idempotency_key) this.idempotency.set(raw.idempotency_key, resp);
    return resp;
  }

  receipt(): Receipt {
    const payload = `${this.allowed}|${this.denied}|${this.duplicates}`;
    const digest = createHash("sha256").update(payload).digest("hex").slice(0, 16);
    return {
      ok: this.denied === 0 || this.allowed > 0,
      allowed: this.allowed,
      denied: this.denied,
      duplicates: this.duplicates,
      digest,
    };
  }
}

function main(): void {
  const gw = new McpGateway();
  gw.approveMutation("2");
  const r1 = gw.handle({ jsonrpc: "2.0", id: 1, method: "ping" });
  const r2 = gw.handle({
    jsonrpc: "2.0",
    id: 2,
    method: "tools/call",
    params: { name: "search" },
    idempotency_key: "ik-1",
  });
  const r2b = gw.handle({
    jsonrpc: "2.0",
    id: 3,
    method: "tools/call",
    params: { name: "search" },
    idempotency_key: "ik-1",
  });
  const r3 = gw.handle({ jsonrpc: "2.0", id: 4, method: "explode" });
  if (!r1.result || !r2.result || !r2b.result) throw new Error("expected results");
  if (!r3.error) throw new Error("expected deny");
  const rec = gw.receipt();
  console.log(
    `advanced_mcp_gateway: ok digest=${rec.digest} allowed=${rec.allowed} denied=${rec.denied} duplicates=${rec.duplicates}`
  );
}

main();
