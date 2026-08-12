// Easy exhibit: simple counter. Teaches ownership basics only.

fn main() {
    let mut count = 0u32;
    count += 1;
    assert_eq!(count, 1);
    println!("easy_counter: ok");
}
