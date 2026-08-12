;; Advanced exhibit: capability- and fuel-bounded tool sandbox sketch.
;; Memory bounds + explicit export surface. Host must enforce fuel/capabilities.
(module
  (memory (export "memory") 1)
  (global $fuel (mut i32) (i32.const 1000))
  (global $denied (mut i32) (i32.const 0))

  (func $check_fuel (param $cost i32) (result i32)
    (local $f i32)
    global.get $fuel
    local.set $f
    local.get $f
    local.get $cost
    i32.lt_u
    if
      i32.const 1
      global.set $denied
      i32.const 0
      return
    end
    local.get $f
    local.get $cost
    i32.sub
    global.set $fuel
    i32.const 1)

  (func (export "limited_add") (param i32 i32) (result i32)
    (local $ok i32)
    i32.const 1
    call $check_fuel
    local.set $ok
    local.get $ok
    i32.eqz
    if
      i32.const -1
      return
    end
    local.get 0
    local.get 1
    i32.add)

  (func (export "denied_count") (result i32)
    global.get $denied)

  (func (export "remaining_fuel") (result i32)
    global.get $fuel))
