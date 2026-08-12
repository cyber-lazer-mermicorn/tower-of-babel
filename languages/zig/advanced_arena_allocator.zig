// Advanced exhibit: mission-scoped arena allocator discipline.
// Owns systems boundary: arena lifetime, hard sample ceiling, deterministic reset.

const std = @import("std");

pub const Arena = struct {
    buffer: []u8,
    offset: usize,
    alloc_count: usize,
    max_allocs: usize,

    pub fn init(buffer: []u8, max_allocs: usize) Arena {
        return .{
            .buffer = buffer,
            .offset = 0,
            .alloc_count = 0,
            .max_allocs = max_allocs,
        };
    }

    pub fn alloc(self: *Arena, n: usize) ![]u8 {
        if (self.alloc_count >= self.max_allocs) return error.BudgetExhausted;
        if (self.offset + n > self.buffer.len) return error.OutOfMemory;
        const start = self.offset;
        self.offset += n;
        self.alloc_count += 1;
        return self.buffer[start .. start + n];
    }

    pub fn reset(self: *Arena) void {
        self.offset = 0;
        self.alloc_count = 0;
    }

    pub fn used(self: *const Arena) usize {
        return self.offset;
    }
};

pub fn main() !void {
    var buf: [256]u8 = undefined;
    var arena = Arena.init(&buf, 3);

    _ = try arena.alloc(16);
    _ = try arena.alloc(32);
    _ = try arena.alloc(8);

    if (arena.alloc(1)) |_| {
        return error.ExpectedBudgetFail;
    } else |err| {
        if (err != error.BudgetExhausted) return err;
    }

    arena.reset();
    if (arena.used() != 0 or arena.alloc_count != 0) return error.ResetFailed;

    const slice = try arena.alloc(4);
    slice[0] = 'T';
    slice[1] = 'o';
    slice[2] = 'w';
    slice[3] = 'r';

    std.debug.print("advanced_arena_allocator: ok used={d}\n", .{arena.used()});
}
