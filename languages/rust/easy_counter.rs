// Easy exhibit: simple counter with assert. Hardened ownership demo.
fn main() {
    let mut count: u32 = 0;
    count = count.saturating_add(1);
    assert_eq!(count, 1);
    println!("easy_counter: ok");
}
