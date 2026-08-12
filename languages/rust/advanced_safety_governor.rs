// Advanced exhibit: typed side-effect safety governor with capability tokens.
// Owns boundary: payload size, depth, allowlist, rate window, capability proof.
// Fail-closed. Deterministic decision + receipt digest. No placeholders.

use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

#[derive(Clone, Debug, PartialEq)]
enum SideEffect {
    Read,
    Write,
    Network,
    Exec,
}

#[derive(Clone, Debug)]
struct Request {
    effect: SideEffect,
    path_or_cmd: String,
    payload_bytes: usize,
    depth: u32,
    capability: Option<String>,
}

#[derive(Clone, Debug, PartialEq)]
enum Decision {
    Allow,
    Deny(&'static str),
}

struct Governor {
    max_payload: usize,
    max_depth: u32,
    allow_exec: Vec<&'static str>,
    capabilities: HashMap<String, u32>,
    window_counts: HashMap<String, u32>,
    window_limit: u32,
}

impl Governor {
    fn new() -> Self {
        let mut capabilities = HashMap::new();
        capabilities.insert("cap-write-tmp".into(), 2);
        capabilities.insert("cap-net".into(), 1);
        Self {
            max_payload: 4096,
            max_depth: 8,
            allow_exec: vec!["search", "summarize", "echo"],
            capabilities,
            window_counts: HashMap::new(),
            window_limit: 5,
        }
    }

    fn rate_key(effect: &SideEffect) -> &'static str {
        match effect {
            SideEffect::Read => "read",
            SideEffect::Write => "write",
            SideEffect::Network => "net",
            SideEffect::Exec => "exec",
        }
    }

    fn decide(&mut self, req: &Request) -> Decision {
        if req.payload_bytes > self.max_payload {
            return Decision::Deny("payload_too_large");
        }
        if req.depth > self.max_depth {
            return Decision::Deny("depth_exceeded");
        }
        let rk = Self::rate_key(&req.effect).to_string();
        let count = self.window_counts.entry(rk).or_insert(0);
        *count += 1;
        if *count > self.window_limit {
            return Decision::Deny("rate_limited");
        }
        match req.effect {
            SideEffect::Read => {
                if req.path_or_cmd.contains("..") {
                    Decision::Deny("path_traversal")
                } else {
                    Decision::Allow
                }
            }
            SideEffect::Write => {
                if !req.path_or_cmd.starts_with("/tmp/") {
                    return Decision::Deny("write_outside_tmp");
                }
                match &req.capability {
                    Some(tok) if tok == "cap-write-tmp" => {
                        if let Some(left) = self.capabilities.get_mut(tok) {
                            if *left == 0 {
                                return Decision::Deny("capability_exhausted");
                            }
                            *left -= 1;
                            Decision::Allow
                        } else {
                            Decision::Deny("unknown_capability")
                        }
                    }
                    _ => Decision::Deny("missing_write_capability"),
                }
            }
            SideEffect::Network => match &req.capability {
                Some(tok) if tok == "cap-net" => {
                    if let Some(left) = self.capabilities.get_mut(tok) {
                        if *left == 0 {
                            return Decision::Deny("capability_exhausted");
                        }
                        *left -= 1;
                        Decision::Allow
                    } else {
                        Decision::Deny("unknown_capability")
                    }
                }
                _ => Decision::Deny("missing_net_capability"),
            },
            SideEffect::Exec => {
                if self.allow_exec.iter().any(|c| *c == req.path_or_cmd) {
                    Decision::Allow
                } else {
                    Decision::Deny("exec_not_allowlisted")
                }
            }
        }
    }
}

fn digest(decisions: &[Decision]) -> u64 {
    let mut h = DefaultHasher::new();
    for d in decisions {
        format!("{:?}", d).hash(&mut h);
    }
    h.finish()
}

fn main() {
    let mut g = Governor::new();
    let suite = vec![
        Request {
            effect: SideEffect::Read,
            path_or_cmd: "/data/doc.txt".into(),
            payload_bytes: 100,
            depth: 1,
            capability: None,
        },
        Request {
            effect: SideEffect::Write,
            path_or_cmd: "/tmp/out.txt".into(),
            payload_bytes: 200,
            depth: 1,
            capability: Some("cap-write-tmp".into()),
        },
        Request {
            effect: SideEffect::Write,
            path_or_cmd: "/etc/passwd".into(),
            payload_bytes: 10,
            depth: 1,
            capability: Some("cap-write-tmp".into()),
        },
        Request {
            effect: SideEffect::Exec,
            path_or_cmd: "rm".into(),
            payload_bytes: 0,
            depth: 1,
            capability: None,
        },
        Request {
            effect: SideEffect::Network,
            path_or_cmd: "api.example".into(),
            payload_bytes: 50,
            depth: 2,
            capability: Some("cap-net".into()),
        },
    ];
    let mut decisions = Vec::new();
    for r in &suite {
        decisions.push(g.decide(r));
    }
    assert_eq!(decisions[0], Decision::Allow);
    assert_eq!(decisions[1], Decision::Allow);
    assert!(matches!(decisions[2], Decision::Deny(_)));
    assert!(matches!(decisions[3], Decision::Deny(_)));
    assert_eq!(decisions[4], Decision::Allow);
    let d = digest(&decisions);
    println!("advanced_safety_governor: ok digest={:x}", d);
}
