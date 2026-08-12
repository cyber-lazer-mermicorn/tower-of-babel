/** Easy exhibit: typed greeting. Teaches contracts only. */

export function greet(name: string): string {
  if (!name || name.trim().length === 0) {
    throw new Error("name must be non-empty");
  }
  return `Hello, ${name.trim()}`;
}

if (require.main === module) {
  console.assert(greet("Tower") === "Hello, Tower");
  console.log("easy_greet: ok");
}
