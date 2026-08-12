-- Easy exhibit: algebraic data type + fold. Teaches purity basics.
data Tree a = Leaf a | Node (Tree a) (Tree a)

size :: Tree a -> Int
size (Leaf _)   = 1
size (Node l r) = size l + size r

main :: IO ()
main = do
  let t = Node (Leaf 1) (Leaf 2)
  if size t == 2 then putStrLn "easy_tree: ok" else error "size mismatch"
