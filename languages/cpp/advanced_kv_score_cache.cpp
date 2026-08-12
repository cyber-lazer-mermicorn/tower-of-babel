// Advanced exhibit: bounded KV score cache with utility eviction + TTL.
// Owns systems boundary: fixed capacity, utility scoring, TTL expiry,
// fingerprint receipt. Fail-closed on capacity/key/ttl rules.

#include <thread>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
#include <chrono>

struct Entry {
    std::string key;
    double score;
    uint64_t fingerprint;
    int64_t expires_at_ms;
};

class ScoreCache {
public:
    explicit ScoreCache(std::size_t capacity) : capacity_(capacity) {
        if (capacity_ == 0) throw std::invalid_argument("capacity must be > 0");
    }

    static int64_t now_ms() {
        using namespace std::chrono;
        return duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
    }

    bool upsert(const std::string& key, double score, int64_t ttl_ms = 60000) {
        if (key.empty() || score < 0.0 || ttl_ms <= 0) return false;
        expire_due();
        auto it = index_.find(key);
        int64_t exp = now_ms() + ttl_ms;
        if (it != index_.end()) {
            entries_[it->second].score = score;
            entries_[it->second].fingerprint = fingerprint(key, score);
            entries_[it->second].expires_at_ms = exp;
            return true;
        }
        if (entries_.size() >= capacity_) evict_lowest();
        if (entries_.size() >= capacity_) return false;
        Entry e{key, score, fingerprint(key, score), exp};
        index_[key] = entries_.size();
        entries_.push_back(std::move(e));
        return true;
    }

    bool get(const std::string& key, double& out) {
        expire_due();
        auto it = index_.find(key);
        if (it == index_.end()) return false;
        out = entries_[it->second].score;
        return true;
    }

    std::size_t size() const { return entries_.size(); }

    uint64_t receipt_digest() const {
        uint64_t h = 0xcbf29ce484222325ULL;
        for (const auto& e : entries_) {
            for (unsigned char c : e.key) {
                h ^= c;
                h *= 0x100000001b3ULL;
            }
            uint64_t bits = 0;
            std::memcpy(&bits, &e.score, sizeof(bits));
            h ^= bits;
            h *= 0x100000001b3ULL;
            h ^= e.fingerprint;
            h *= 0x100000001b3ULL;
            h ^= static_cast<uint64_t>(e.expires_at_ms);
            h *= 0x100000001b3ULL;
        }
        return h;
    }

private:
    void expire_due() {
        int64_t now = now_ms();
        for (std::size_t i = 0; i < entries_.size();) {
            if (entries_[i].expires_at_ms <= now) {
                index_.erase(entries_[i].key);
                if (i + 1 != entries_.size()) {
                    entries_[i] = std::move(entries_.back());
                    index_[entries_[i].key] = i;
                }
                entries_.pop_back();
            } else {
                ++i;
            }
        }
    }

    void evict_lowest() {
        if (entries_.empty()) return;
        auto min_it = std::min_element(
            entries_.begin(), entries_.end(),
            [](const Entry& a, const Entry& b) { return a.score < b.score; });
        std::size_t idx = static_cast<std::size_t>(min_it - entries_.begin());
        index_.erase(min_it->key);
        if (idx + 1 != entries_.size()) {
            entries_[idx] = std::move(entries_.back());
            index_[entries_[idx].key] = idx;
        }
        entries_.pop_back();
    }

    static uint64_t fingerprint(const std::string& key, double score) {
        uint64_t h = 0x84222325ULL;
        for (unsigned char c : key) h = (h ^ c) * 0x1b3ULL;
        uint64_t bits = 0;
        std::memcpy(&bits, &score, sizeof(bits));
        return h ^ bits;
    }

    std::size_t capacity_;
    std::vector<Entry> entries_;
    std::unordered_map<std::string, std::size_t> index_;
};

int main() {
    ScoreCache cache(2);
    if (!cache.upsert("a", 0.9, 60000)) return 1;
    if (!cache.upsert("b", 0.5, 60000)) return 1;
    if (!cache.upsert("c", 0.8, 60000)) return 1;
    double v = 0;
    if (cache.get("b", v)) return 1;
    if (!cache.get("a", v) || v != 0.9) return 1;
    if (!cache.get("c", v) || v != 0.8) return 1;
    if (cache.size() != 2) return 1;
    if (cache.upsert("", 1.0)) return 1;
    if (!cache.upsert("ttl", 1.0, 1)) return 1;
    std::this_thread::sleep_for(std::chrono::milliseconds(5));
    if (cache.get("ttl", v)) return 1;
    std::cout << "advanced_kv_score_cache: ok digest="
              << std::hex << cache.receipt_digest() << "\n";
    return 0;
}
