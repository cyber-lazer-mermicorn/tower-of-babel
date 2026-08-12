# Advanced exhibit: energy-audited orbital integration (velocity-Verlet).
# Owns scientific-ML boundary: conservation drift diagnostics + deterministic steps.
# Toolchain: requires Julia. Evidence class remains honest when Julia is absent.

function verlet_orbit(steps::Int, dt::Float64)
    x, y = 1.0, 0.0
    vx, vy = 0.0, 1.0
    energy(x, y, vx, vy) = 0.5 * (vx^2 + vy^2) - 1.0 / sqrt(x^2 + y^2)

    e0 = energy(x, y, vx, vy)
    max_drift = 0.0

    for _ in 1:steps
        r2 = x^2 + y^2
        r3 = r2 * sqrt(r2)
        ax, ay = -x / r3, -y / r3

        x += vx * dt + 0.5 * ax * dt^2
        y += vy * dt + 0.5 * ay * dt^2

        r2n = x^2 + y^2
        r3n = r2n * sqrt(r2n)
        axn, ayn = -x / r3n, -y / r3n

        vx += 0.5 * (ax + axn) * dt
        vy += 0.5 * (ay + ayn) * dt

        drift = abs(energy(x, y, vx, vy) - e0)
        max_drift = max(max_drift, drift)
    end
    return max_drift
end

drift = verlet_orbit(200, 0.01)
@assert drift < 1e-3
println("advanced_orbital_verlet: ok max_drift=", drift)
