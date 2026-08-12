// Advanced exhibit: typed side-effect safety governor.
// Fail-closed path, payload/depth/approval policy, receipt.
// No placeholders.

use std::collections::HashSet;

#[derive(Debug, Clone)]
pub struct Action {
    pub path: String,
    pub payload_bytes: usize,
    pub depth: u32,
    pub requires_approval: bool,
    pub approved: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Decision {
    Allow,
    Block { reason: String },
}

#[derive(Debug)]
pub struct GovernorConfig {
    pub max_payload_bytes: usize,
    pub max_depth: u32,
    pub allowed_prefixes: HashSet<String>,
}

#[derive(Debug)]
pub struct SafetyReceipt {
    pub decision: Decision,
    pub path: String,
    pub digest: String,
}

pub struct SafetyGovernor {
    config: GovernorConfig,
}

impl SafetyGovernor {
    pub fn new(config: GovernorConfig) -> Self {
        Self { config }
    }

    pub fn evaluate(&self, action: &Action) -> SafetyReceipt {
        let decision = self.decide(action);
        let digest = format!(
            "{:?}|{}|{}",
            decision, action.path, action.payload_bytes
        );
        // Simple stable digest for exhibit purposes
        let digest = format!("{:x}", simple_hash(&digest));
        SafetyReceipt {
            decision,
            path: action.path.clone(),
            digest,
        }
    }

    fn decide(&self, action: &Action) -> Decision {
        if action.payload_bytes > self.config.max_payload_bytes {
            return Decision::Block {
                reason: format!(
                    "payload {} exceeds max {}",
                    action.payload_bytes, self.config.max_payload_bytes
                ),
            };
        }
        if action.depth > self.config.max_depth {
            return Decision::Block {
                reason: format!("depth {} exceeds max {}", action.depth, self.config.max_depth),
            };
        }
        let allowed = self
            .config
            .allowed_prefixes
            .iter()
            .any(|p| action.path.starts_with(p));
        if !allowed {
            return Decision::Block {
                reason: format!("path not in allowed prefixes: {}", action.path),
            };
        }
        if action.requires_approval && !action.approved {
            return Decision::Block {
                reason: "action requires approval".into(),
            };
        }
        Decision::Allow
    }
}

fn simple_hash(s: &str) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for b in s.bytes() {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

fn main() {
    let mut prefixes = HashSet::new();
    prefixes.insert("/tools/".into());
    prefixes.insert("/read/".into());

    let gov = SafetyGovernor::new(GovernorConfig {
        max_payload_bytes: 4096,
        max_depth: 8,
        allowed_prefixes: prefixes,
    });

    let ok = gov.evaluate(&Action {
        path: "/tools/search".into(),
        payload_bytes: 128,
        depth: 1,
        requires_approval: false,
        approved: false,
    });
    assert_eq!(ok.decision, Decision::Allow);

    let blocked = gov.evaluate(&Action {
        path: "/admin/delete".into(),
        payload_bytes: 10,
        depth: 1,
        requires_approval: false,
        approved: false,
    });
    assert!(matches!(blocked.decision, Decision::Block { .. }));

    let mut_blocked = gov.evaluate(&Action {
        path: "/tools/write".into(),
        payload_bytes: 100,
        depth: 1,
        requires_approval: true,
        approved: false,
    });
    assert!(matches!(mut_blocked.decision, Decision::Block { .. }));

    println!("advanced_safety_governor: ok digest={}", ok.digest);
}
