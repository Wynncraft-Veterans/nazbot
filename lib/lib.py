def unwrap[T](v: T | None) -> T:
    assert v is not None
    return v