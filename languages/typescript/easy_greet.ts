/** Easy exhibit: typed greeting. Teaches contracts only. */

export function greet(name: string): string {
  if (!name || name.trim().length === 0) {
    throw new Error("name must be non-empty");
  }
  return `Hello, ${name.trim()}`;
}

// Self-check (works under ts-node / tsx / compiled CJS)
function runSelfCheck(): void {
  const result = greet("Tower");
  if (result !== "Hello, Tower") {
    throw new Error(`unexpected greet result: ${result}`);
  }
  console.log("easy_greet: ok");
}

const isMain =
  typeof require !== "undefined" &&
  typeof module !== "undefined" &&
  require.main === module;

if (isMain) {
  runSelfCheck();
}
