# datact - data-aware synchronization in PRISM models

This tool provides a slight extension of the PRISM input language which allows
us to exchange data on synchronization by attaching an integer value to the
corresponding synchronization action. Consider the following example:

```
module sender
    s : [0..2] init 0;

    [] s = 0 -> 0.5:(s' = 1) + 0.5:(s' = 2);
    [a] s > 0 & a = s -> true;
endmodule

module receiver
    r : [0..2] init 0;

    [a] r = 0 -> (r' = a);
endmodule
```

The `sender` module sends either 1 or 2 over the action `a` via the assignment
`a = s`. Upon synchronization, the `receiver` module stores the data attached to
action `a` in its local variable `r`.

## Usage

```
datact <MODEL> <DOMAIN> [<DOM-FILE>]
```

Assuming each action in `<MODEL>` has type `[1 .. <DOMAIN>]`, `datact`
translates the given `<MODEL>` into a standard PRISM model without data-aware
synchronization.

Optionally, specific actions can be given a domain different than `<DOMAIN>` by
specifying a `<DOM-FILE>`. A `<DOM-FILE>` is a CSV-file with format
`<ACTION>, <DOMAIN>`.
