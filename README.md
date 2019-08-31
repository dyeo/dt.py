# dt.py
## Datatag Python Reference Implementation

### What is Datatag?

Datatag is yet-another file format. The goal of which is:
1. To be simple to write.
2. To be quick to parse.
3. To be accessible to both programmers and non-programmers.

Coming from a background of game development, there's plenty of options for storing user-configurable data, but nothing that sufficiently meets the above three criteria. Datatags is a working specification that intends to solve these three issues.

### Example Datatag (.dt) file

```; This is a comment
a_bool: true ; This is also a comment
a_byte: 0x01
a_int: 2
a_short: 3s
a_long: 4l
a_double: 5.0
a_float: 6.0f
a_char: '7'
a_string: "eight"
a_array: [ 9 10 11 12 ]
a_object:
{
	a: 0
	b: { c: 0 }
	d: 0
	e: [1 2 3 4] ; you can nest arrays in objects
	f: [ {a: 0} {a: 1} {a: 2} {a: 3} ] ; you can nest objects in arrays
}```

### Types

Datatags support the following primitive types:
* *booleans*: Either `true` or `false`. 
* *bytes*: A hexadecimal value, in the format `0x##`.
* *shorts*: A regular integral (discrete) value, proceeded by a lower- or uppercase `s`. 
* *integers*: A regular integral (discrete) value. 
* *longs*: A regular integral (discrete) value, proceeded by a lower- or uppercase `l`. 
* *floats*: A real number that contains a decimal point (`.`), proceeded by a lower- or uppercase `f`. Only has to contain a single digit on either side of the decimal to be understood.
* *doubles*: A real number that contains a decimal point (`.`), optionally proceeded by a lower- or uppercase `d`. Only has to contain a single digit on either side of the decimal to be understood.
* *characters*: A single character in single quotes (`''`), or an escaped character (escaped using `\`).
* *strings*: A line of text in double quotes (`""`). Double quotes used in the string must be escaped using a `\`.
* *arrays*: A list of values of another type, enclosed with square braces (`[]`) and seperated by whitespace.
* *objects*: A collection of key-value pairs, encapsulated in a single value. Objects follow the same rules as regular datatag entries, but are enclosed in curly braces (`{}`).