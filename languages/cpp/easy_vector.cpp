// Easy exhibit: RAII vector push. Teaches ownership basics only.
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v;
    v.push_back(1);
    v.push_back(2);
    if (v.size() != 2 || v[0] != 1) {
        return 1;
    }
    std::cout << "easy_vector: ok\n";
    return 0;
}
