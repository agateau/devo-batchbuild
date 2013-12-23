tst_equal() {
    local actual=$1
    local expected=$2
    if [ "$actual" = "$expected" ] ; then
        return 0
    fi
    tst_fail "'$actual' (actual) != '$expected' (expected)"
    return 1
}

tst_fail() {
    echo "TEST: $* FAIL" 1>&2
    return 1
}

tst_ok() {
    echo "TEST: $* OK" 1>&2
    return 0
}

assert() {
    if $* ; then
        tst_ok $*
        return 0
    fi
    tst_fail "$* failed"
    return 1
}
