import micro_enum

state = micro_enum.enum(
    A = 1,
    B = 2,
    C = 3,
    Z = -1
    )

print(state)
print(type(state))

print(state.A)
print(type(state.A))

print(state.A.name)
print(state.A.value)

state.A.value = 9
