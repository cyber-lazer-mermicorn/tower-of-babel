# Easy exhibit: matrix multiply shape. Teaches Julia numerical syntax.
A = [1.0 2.0; 3.0 4.0]
b = [1.0, 1.0]
y = A * b
@assert y ≈ [3.0, 7.0]
println("easy_matrix: ok")
