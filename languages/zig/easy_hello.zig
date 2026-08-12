// Easy exhibit: explicit print. Teaches Zig entry basics.
const std = @import("std");

pub fn main() void {
    std.debug.print("easy_hello: ok\n", .{});
}
