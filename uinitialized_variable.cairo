func bar() -> (res):
    alloc_locals
    local x
    local y = 2
    local z
    local b
    assert b = 2
    local a
    a = 3
    assert x * x = 25
    return (res=x)
end

@foobar
func main():
    return ()

end
