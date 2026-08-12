-- Advanced exhibit: pure capability-policy AST validation.
-- Owns correctness boundary: algebraic decisions, lexical path safety, deterministic receipt.

module Main where

import Data.Char (isAlphaNum)
import Data.List (intercalate)
import Data.Bits (xor)
import Data.Word (Word64)

data Action
  = Read FilePath
  | Write FilePath
  | Exec String
  deriving (Eq, Show)

data Decision = Allow | Deny String deriving (Eq, Show)

safePath :: FilePath -> Bool
safePath p =
  not (null p)
  && not (elem ".." (split p))
  && all okChar p
  where
    okChar c = isAlphaNum c || c `elem` "/_.-"
    split s = case break (== '/') s of
      (a, "")  -> [a]
      (a, _:b) -> a : split b

decide :: Action -> Decision
decide (Read p)
  | safePath p = Allow
  | otherwise  = Deny "unsafe read path"
decide (Write p)
  | safePath p && take 6 p == "/tmp/" = Allow
  | safePath p = Deny "write outside /tmp"
  | otherwise  = Deny "unsafe write path"
decide (Exec cmd)
  | cmd `elem` ["search", "summarize", "echo"] = Allow
  | otherwise = Deny "exec not allowlisted"

fnv :: String -> Word64
fnv s = go 0xcbf29ce484222325 s
  where
    go h [] = h
    go h (c:cs) = go ((h `xor` fromIntegral (fromEnum c)) * 0x100000001b3) cs

receipt :: [Action] -> ([Decision], Word64)
receipt acts =
  let ds = map decide acts
      payload = intercalate "|" (map show ds)
  in (ds, fnv payload)

main :: IO ()
main = do
  let acts =
        [ Read "/data/doc.txt"
        , Write "/tmp/out.txt"
        , Write "/etc/passwd"
        , Exec "search"
        , Exec "rm"
        ]
      (ds, dig) = receipt acts
      expected =
        [ Allow
        , Allow
        , Deny "write outside /tmp"
        , Allow
        , Deny "exec not allowlisted"
        ]
  if ds == expected
    then putStrLn $ "advanced_ast_validator: ok digest=" ++ show dig
    else error $ "unexpected decisions: " ++ show ds
